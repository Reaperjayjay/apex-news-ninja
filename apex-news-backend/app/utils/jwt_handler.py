"""
JWT token creation, verification, and refresh logic.
Implements access + refresh token pattern with rotation and blacklisting.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
import uuid

from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings

logger = logging.getLogger(__name__)


class JWTHandler:
    """
    Handles JWT token operations including creation, verification,
    refresh token rotation, and blacklist management.
    """

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.

        Args:
            data: Payload data to encode (typically user_id, email)
            expires_delta: Custom expiration time, defaults to sources value

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()

        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        # Add standard JWT claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        # Encode token
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> tuple[str, str, datetime]:
        """
        Create a JWT refresh token with unique JTI for rotation tracking.

        Args:
            data: Payload data to encode

        Returns:
            Tuple of (token, jti, expiration_datetime)
        """
        to_encode = data.copy()

        # Generate unique token ID for blacklist tracking
        jti = str(uuid.uuid4())
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_refresh_secret_key,
            algorithm=settings.jwt_algorithm
        )

        return encoded_jwt, jti, expire

    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict]:
        """
        Verify and decode an access token.

        Args:
            token: JWT access token string

        Returns:
            Decoded payload dict if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )

            # Verify token type
            if payload.get("type") != "access":
                logger.warning("Invalid token type in access token verification")
                return None

            return payload

        except JWTError as e:
            logger.debug(f"Access token verification failed: {e}")
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[Dict]:
        """
        Verify and decode a refresh token.

        Args:
            token: JWT refresh token string

        Returns:
            Decoded payload dict if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_refresh_secret_key,
                algorithms=[settings.jwt_algorithm]
            )

            # Verify token type
            if payload.get("type") != "refresh":
                logger.warning("Invalid token type in refresh token verification")
                return None

            return payload

        except JWTError as e:
            logger.debug(f"Refresh token verification failed: {e}")
            return None

    @staticmethod
    async def blacklist_refresh_token(
            db: AsyncIOMotorDatabase,
            jti: str,
            expires_at: datetime
    ) -> bool:
        """
        Add a refresh token JTI to the blacklist.
        Used during logout and token rotation to invalidate old tokens.

        Args:
            db: Database connection
            jti: Unique token identifier
            expires_at: Token expiration datetime (for TTL index)

        Returns:
            True if blacklisted successfully, False otherwise
        """
        try:
            await db.token_blacklist.insert_one({
                "token_jti": jti,
                "blacklisted_at": datetime.utcnow(),
                "expires_at": expires_at
            })
            logger.info(f"Blacklisted refresh token: {jti}")
            return True

        except Exception as e:
            logger.error(f"Failed to blacklist token {jti}: {e}")
            return False

    @staticmethod
    async def is_token_blacklisted(db: AsyncIOMotorDatabase, jti: str) -> bool:
        """
        Check if a refresh token JTI is blacklisted.

        Args:
            db: Database connection
            jti: Unique token identifier

        Returns:
            True if token is blacklisted, False otherwise
        """
        try:
            result = await db.token_blacklist.find_one({"token_jti": jti})
            return result is not None

        except Exception as e:
            logger.error(f"Error checking token blacklist: {e}")
            # Fail secure: treat as blacklisted on error
            return True

    @staticmethod
    async def rotate_refresh_token(
            db: AsyncIOMotorDatabase,
            old_token: str
    ) -> Optional[tuple[str, str, str]]:
        """
        Rotate refresh token: verify old token, blacklist it, issue new tokens.
        Implements token rotation pattern for enhanced security.

        Args:
            db: Database connection
            old_token: Current refresh token to rotate

        Returns:
            Tuple of (access_token, new_refresh_token, user_id) if successful,
            None otherwise
        """
        # Verify old refresh token
        payload = JWTHandler.verify_refresh_token(old_token)
        if not payload:
            logger.warning("Invalid refresh token provided for rotation")
            return None

        # Check if token is already blacklisted
        jti = payload.get("jti")
        if not jti:
            logger.warning("Refresh token missing JTI claim")
            return None

        if await JWTHandler.is_token_blacklisted(db, jti):
            logger.warning(f"Attempted reuse of blacklisted token: {jti}")
            return None

        # Extract user data
        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id or not email:
            logger.warning("Refresh token missing required claims")
            return None

        # Blacklist old token
        old_expires = datetime.fromtimestamp(payload.get("exp", 0))
        await JWTHandler.blacklist_refresh_token(db, jti, old_expires)

        # Create new token pair
        token_data = {"sub": user_id, "email": email}

        new_access_token = JWTHandler.create_access_token(token_data)
        new_refresh_token, new_jti, new_expires = JWTHandler.create_refresh_token(token_data)

        logger.info(f"Rotated refresh token for user: {user_id}")

        return new_access_token, new_refresh_token, user_id