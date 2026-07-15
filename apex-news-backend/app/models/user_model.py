"""
User data models for request/response validation and database operations.
Combines Pydantic for API validation with utility functions for MongoDB.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from passlib.context import CryptContext

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)  # Used for WhatsApp too

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Ensure username contains only alphanumeric and underscores."""
        if not v.replace("_", "").isalnum():
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v.lower()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase for consistency."""
        return v.lower()


class UserCreate(UserBase):
    """Model for user registration requests."""
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Enforce password complexity requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Model for user login requests."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Model for user data in API responses (excludes password)."""
    id: str = Field(..., alias="_id")
    created_at: datetime
    is_active: bool = True
    digest_enabled: bool = True

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class UserInDB(UserBase):
    """
    Internal model representing user document in MongoDB.
    Includes hashed password and metadata.
    """
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    digest_enabled: bool = True
    last_login: Optional[datetime] = None

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain-text password using bcrypt.

        Args:
            password: Plain-text password

        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against a hashed password.

        Args:
            plain_password: Plain-text password to verify
            hashed_password: Hashed password from database

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    def to_dict(self) -> dict:
        """
        Convert model to dictionary for MongoDB insertion.

        Returns:
            Dictionary representation without Pydantic metadata
        """
        data = self.model_dump(exclude={"id"})
        return data


class TokenResponse(BaseModel):
    """Model for JWT token responses."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class TokenRefresh(BaseModel):
    """Model for refresh token requests."""
    refresh_token: str


class UserPreferences(BaseModel):
    """
    Model for user news preferences and notification settings.
    Stored in separate collection for flexible schema evolution.
    """
    user_id: str
    categories: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    digest_enabled: bool = True
    digest_frequency: str = "daily"  # daily, weekly, custom
    digest_time: str = "08:00"
    max_articles: int = 10
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("categories", "sources", "keywords", "exclude_keywords")
    @classmethod
    def normalize_lists(cls, v: list[str]) -> list[str]:
        """Normalize list items to lowercase and remove duplicates."""
        return list(set(item.strip().lower() for item in v if item.strip()))


class UserPreferencesUpdate(BaseModel):
    """Model for updating user preferences (all fields optional)."""
    categories: Optional[list[str]] = None
    sources: Optional[list[str]] = None
    keywords: Optional[list[str]] = None
    exclude_keywords: Optional[list[str]] = None
    digest_enabled: Optional[bool] = None
    digest_frequency: Optional[str] = None
    digest_time: Optional[str] = None
    max_articles: Optional[int] = None