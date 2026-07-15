"""
Authentication routes: register, login, google auth, refresh tokens, logout.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.config import settings
from app.database import get_database
from app.models.user_model import UserCreate, UserLogin, UserInDB, TokenRefresh
from app.utils.jwt_handler import JWTHandler
from app.utils.vibe_guard import limiter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def register(
        request: Request,
        user: UserCreate,
        db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user account.

    - **username**: Unique username (3-50 chars, alphanumeric + underscore)
    - **email**: Valid email address (unique)
    - **password**: Min 8 chars with uppercase, lowercase, and digit
    """
    # Check if user already exists
    try:
        existing_user = await db.users.find_one({
            "$or": [
                {"email": user.email.lower()},
                {"username": user.username.lower()}
            ]
        })
    except Exception as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration service temporarily unavailable"
        )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Create user document
    user_in_db = UserInDB(
        **user.model_dump(exclude={"password"}),
        hashed_password=UserInDB.hash_password(user.password)
    )

    # Insert into database
    result = await db.users.insert_one(user_in_db.to_dict())

    # Create initial preferences
    from app.models.user_model import UserPreferences
    preferences = UserPreferences(user_id=str(result.inserted_id))
    await db.user_preferences.insert_one(preferences.model_dump())

    logger.info(f"New user registered: {user.email}")

    # Send Welcome Message (background task recommended for production)
    try:
        from app.services.notification_service import NotificationService
        notification_service = NotificationService(db)
        await notification_service.send_welcome_message(str(result.inserted_id))
    except Exception as e:
        logger.error(f"Failed to send welcome message: {e}")

    return {
        "status": "success",
        "message": "User registered successfully",
        "data": {"user_id": str(result.inserted_id)}
    }


@router.post("/login", response_model=dict)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def login(
        request: Request,
        credentials: UserLogin,
        db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Authenticate user and return JWT tokens.

    Returns access token (30min) and refresh token (7 days).
    """
    # Find user by email (case-insensitive search)
    try:
        user_doc = await db.users.find_one({"email": credentials.email.lower()})
    except Exception as e:
        logger.error(f"Database error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not UserInDB.verify_password(credentials.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account is active
    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    # Create token payload
    token_data = {
        "sub": str(user_doc["_id"]),
        "email": user_doc["email"]
    }

    # Generate tokens
    access_token = JWTHandler.create_access_token(token_data)
    refresh_token, jti, expires = JWTHandler.create_refresh_token(token_data)

    # Update last login
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    logger.info(f"User logged in: {credentials.email}")

    return {
        "status": "success",
        "message": "Login successful",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
    }


@router.post("/google", response_model=dict)
@limiter.limit("5/minute")  # Rate limit: 5 requests per minute per IP
async def google_login(
    request: Request,
    data: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Secure Google Login with Rate Limiting and Token Verification.
    Validates the token with Google servers to prevent spoofing.
    """
    token = data.get("token")
    
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    try:
        # 1. Verify the token with Google (Stateless verification)
        # This ensures the token was signed by Google's private key
        id_info = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        # 2. Extract verified info
        email = id_info.get("email")
        name = id_info.get("name")
        picture = id_info.get("picture")

        if not email:
            raise HTTPException(status_code=400, detail="Invalid Google Token")
        
        # 3. Check if user exists
        existing_user = await db.users.find_one({"email": email})
        
        if existing_user:
            user_id = str(existing_user["_id"])
            # Optional: Update profile picture if changed
            if picture and existing_user.get("profile_image") != picture:
                 await db.users.update_one(
                    {"_id": existing_user["_id"]},
                    {"$set": {"profile_image": picture}}
                )
        else:
            # 4. Create new user (If unique index allows)
            new_user = {
                "email": email,
                "username": email.split("@")[0], # Fallback username
                "full_name": name,
                "profile_image": picture,
                "is_active": True,
                "auth_provider": "google",
                "created_at": datetime.utcnow(),
                "last_login": datetime.utcnow(),
                # Default preferences
                "preferences": {
                    "categories": ["tech", "ai", "crypto"],
                    "theme": "dark"
                }
            }
            result = await db.users.insert_one(new_user)
            user_id = str(result.inserted_id)
            
            # Create user preferences document
            from app.models.user_model import UserPreferences
            preferences = UserPreferences(user_id=user_id)
            await db.user_preferences.insert_one(preferences.model_dump())

        # 5. Generate Access Token (JWT)
        # We need a dict payload for create_access_token
        token_payload = {"sub": user_id, "email": email}
        access_token = JWTHandler.create_access_token(token_payload)
        
        return {
            "status": "success",
            "message": "Google login successful",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "email": email,
                    "full_name": name,
                    "picture": picture
                }
            }
        }

    except ValueError:
        # This catches fake tokens generated by scripts
        raise HTTPException(status_code=401, detail="Invalid Google Token")
    except Exception as e:
        logger.error(f"Google Auth Error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/refresh", response_model=dict)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def refresh_token(
        request: Request,
        token_data: TokenRefresh,
        db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Refresh access token using refresh token.
    Implements token rotation: old refresh token is blacklisted.
    """
    result = await JWTHandler.rotate_refresh_token(db, token_data.refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    access_token, new_refresh_token, user_id = result

    logger.info(f"Token refreshed for user: {user_id}")

    return {
        "status": "success",
        "message": "Token refreshed successfully",
        "data": {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }
    }


@router.post("/logout", response_model=dict)
async def logout(
        request: Request,
        token_data: TokenRefresh,
        db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Logout user by blacklisting refresh token.
    """
    payload = JWTHandler.verify_refresh_token(token_data.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    jti = payload.get("jti")
    exp_timestamp = payload.get("exp", 0)
    expires_at = datetime.fromtimestamp(exp_timestamp)

    await JWTHandler.blacklist_refresh_token(db, jti, expires_at)

    logger.info(f"User logged out: {payload.get('email')}")

    return {
        "status": "success",
        "message": "Logged out successfully",
        "data": None
    }