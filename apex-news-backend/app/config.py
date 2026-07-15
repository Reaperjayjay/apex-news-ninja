"""
Configuration management for Apex News Ninja using Pydantic BaseSettings.
Handles environment variables, validation, and type-safe access for FastAPI.
"""

from typing import List, Optional
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


# Define the base directory to make .env path consistent
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to ApexNewsNinja_Backend/


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic validation to ensure required fields and correct types.
    """

    # -------------------------------------------------------------------------
    # APPLICATION
    # -------------------------------------------------------------------------
    app_name: str = Field(default="Apex News Ninja", env="APP_NAME")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # -------------------------------------------------------------------------
    # SERVER
    # -------------------------------------------------------------------------
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # -------------------------------------------------------------------------
    # DATABASE (MongoDB)
    # -------------------------------------------------------------------------
    mongodb_url: str = Field(..., env="MONGODB_URL")
    mongodb_db_name: str = Field(default="apex_news_ninja", env="MONGODB_DB_NAME")
    mongodb_max_pool_size: int = Field(default=10, env="MONGODB_MAX_POOL_SIZE")
    mongodb_min_pool_size: int = Field(default=2, env="MONGODB_MIN_POOL_SIZE")

    # -------------------------------------------------------------------------
    # JWT
    # -------------------------------------------------------------------------
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_refresh_secret_key: str = Field(..., env="JWT_REFRESH_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # -------------------------------------------------------------------------
    # GOOGLE AUTH (ADDED)
    # -------------------------------------------------------------------------
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")

    # -------------------------------------------------------------------------
    # RATE LIMITING
    # -------------------------------------------------------------------------
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")

    # -------------------------------------------------------------------------
    # NEWS API KEYS (UPDATED FOR GNEWS)
    # -------------------------------------------------------------------------
    # Replaced newsapi_key with gnews_api_key
    gnews_api_key: str = Field(default="", env="GNEWS_API_KEY")
    
    # Keep Crypto Key
    cryptocompare_api_key: str = Field(default="", env="CRYPTOCOMPARE_API_KEY")
    
    # Optional: FMP Key (Forex uses RSS now, so this is optional)
    fmp_api_key: Optional[str] = Field(default="", env="FMP_API_KEY")

    # -------------------------------------------------------------------------
    # AI & SERVERLESS
    # -------------------------------------------------------------------------
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    cron_secret: Optional[str] = Field(default=None, env="CRON_SECRET")

    # -------------------------------------------------------------------------
    # NEWS SETTINGS
    # -------------------------------------------------------------------------
    news_retention_days: int = Field(default=7, env="NEWS_RETENTION_DAYS")
    scheduler_enabled: bool = Field(default=True, env="SCHEDULER_ENABLED")

    # -------------------------------------------------------------------------
    # SECURITY / CORS
    # -------------------------------------------------------------------------
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], env="CORS_ORIGINS")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"], env="ALLOWED_HOSTS")
    
    # Sentry (Optional)
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    sentry_environment: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(default=0.1, env="SENTRY_TRACES_SAMPLE_RATE")

    # -------------------------------------------------------------------------
    # VALIDATORS
    # -------------------------------------------------------------------------
    @field_validator("jwt_secret_key", "jwt_refresh_secret_key")
    @classmethod
    def validate_secret_length(cls, v: str) -> str:
        """Ensure JWT secrets are sufficiently long and trimmed."""
        v = v.strip()
        if len(v) < 32:
            raise ValueError("JWT secret keys must be at least 32 characters long")
        return v

    @field_validator("cors_origins", "allowed_hosts", mode="before")
    @classmethod
    def split_comma_separated(cls, v):
        """Convert comma-separated env values to lists."""
        if isinstance(v, str):
            if not v:
                return []
            if v == "*":
                return ["*"]
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Create a global instance that can be imported across your FastAPI project
settings = Settings()