"""
Database connection and index management for MongoDB using Motor (async driver).
Creates required indexes on startup and provides connection lifecycle hooks.
"""
import logging
import certifi
from pathlib import Path
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.errors import CollectionInvalid

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """
    Async MongoDB connection manager with index creation.
    Singleton pattern ensures single connection pool across app lifecycle.
    """

    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls) -> None:
        """
        Establish MongoDB connection and create indexes.
        Called once during application startup.
        """
        try:
            logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")

            # Build connection options
            client_options = {
                "maxPoolSize": settings.mongodb_max_pool_size,
                "minPoolSize": settings.mongodb_min_pool_size,
                "serverSelectionTimeoutMS": 30000,  # Increased timeout for SSL handshake
                "connectTimeoutMS": 30000,
            }
            
            # MongoDB Atlas (mongodb+srv://) always requires TLS
            if "mongodb+srv://" in settings.mongodb_url:
                client_options["tls"] = True
                # Try to use certifi CA bundle, but allow fallback
                try:
                    ca_file = certifi.where()
                    if ca_file and Path(ca_file).exists():
                        client_options["tlsCAFile"] = ca_file
                        logger.debug(f"Using CA file: {ca_file}")
                    else:
                        logger.warning("certifi CA file not found, using system defaults")
                except Exception as e:
                    logger.warning(f"Could not set CA file: {e}, using system defaults")
                
                # Additional TLS options for better compatibility
                client_options["tlsAllowInvalidCertificates"] = False
                client_options["tlsAllowInvalidHostnames"] = False
                
            elif "ssl=true" in settings.mongodb_url or "tls=true" in settings.mongodb_url:
                client_options["tls"] = True
                try:
                    ca_file = certifi.where()
                    if ca_file and Path(ca_file).exists():
                        client_options["tlsCAFile"] = ca_file
                except Exception:
                    pass
            
            logger.debug(f"MongoDB connection options: {list(client_options.keys())}")
            
            cls.client = AsyncIOMotorClient(
                settings.mongodb_url,
                **client_options
            )

            # Verify connection with longer timeout
            await cls.client.admin.command("ping")
            cls.db = cls.client[settings.mongodb_db_name]

            logger.info(f"Connected to MongoDB database: {settings.mongodb_db_name}")

            # Create indexes for optimal query performance
            await cls._create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            logger.error(
                "Troubleshooting tips:\n"
                "1. Ensure certifi is up to date: pip install --upgrade certifi\n"
                "2. Check MongoDB Atlas IP whitelist includes your IP\n"
                "3. Verify MongoDB connection string is correct\n"
                "4. Try updating pymongo: pip install --upgrade pymongo motor"
            )
            raise

    @classmethod
    async def disconnect(cls) -> None:
        """
        Close MongoDB connection.
        Called during application shutdown.
        """
        if cls.client:
            logger.info("Closing MongoDB connection")
            cls.client.close()
            cls.client = None
            cls.db = None

    @classmethod
    async def _create_indexes(cls) -> None:
        """
        Create all required indexes for collections.
        Indexes improve query performance and enforce uniqueness constraints.
        """
        if cls.db is None:
            raise RuntimeError("Database not connected")

        try:
            # Users collection indexes
            await cls._create_collection_indexes(
                "users",
                [
                    IndexModel([("email", ASCENDING)], unique=True, name="email_unique"),
                    IndexModel([("username", ASCENDING)], unique=True, name="username_unique"),
                    IndexModel([("created_at", DESCENDING)], name="created_at_desc"),
                ]
            )

            # News articles collection indexes
            await cls._create_collection_indexes(
                "articles",
                [
                    # Deduplication index - SHA256 hash of title+source+published_at
                    IndexModel(
                        [("content_hash", ASCENDING)],
                        unique=True,
                        name="content_hash_unique"
                    ),
                    # Query performance indexes
                    IndexModel(
                        [("published_at", DESCENDING)],
                        name="published_at_desc"
                    ),
                    IndexModel([("category", ASCENDING)], name="category_asc"),
                    IndexModel([("source", ASCENDING)], name="source_asc"),
                    # Compound index for personalized feeds
                    IndexModel(
                        [("category", ASCENDING), ("published_at", DESCENDING)],
                        name="category_published"
                    ),
                    # TTL index for automatic expiry (30 days default)
                    IndexModel(
                        [("published_at", ASCENDING)],
                        expireAfterSeconds=settings.news_retention_days * 86400,
                        name="ttl_expiry"
                    ),
                ]
            )

            # User preferences collection indexes
            await cls._create_collection_indexes(
                "user_preferences",
                [
                    IndexModel([("user_id", ASCENDING)], unique=True, name="user_id_unique"),
                ]
            )

            # Analytics collection indexes
            await cls._create_collection_indexes(
                "analytics",
                [
                    IndexModel([("user_id", ASCENDING)], name="user_id_asc"),
                    IndexModel([("article_id", ASCENDING)], name="article_id_asc"),
                    IndexModel([("timestamp", DESCENDING)], name="timestamp_desc"),
                    IndexModel(
                        [("user_id", ASCENDING), ("event_type", ASCENDING)],
                        name="user_event"
                    ),
                ]
            )

            # Token blacklist collection indexes (for revoked refresh tokens)
            await cls._create_collection_indexes(
                "token_blacklist",
                [
                    IndexModel([("token_jti", ASCENDING)], unique=True, name="token_jti_unique"),
                    # TTL index for automatic cleanup after refresh token expires
                    IndexModel(
                        [("expires_at", ASCENDING)],
                        expireAfterSeconds=0,
                        name="ttl_cleanup"
                    ),
                ]
            )

            logger.info("All database indexes created successfully")

        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise

    @classmethod
    async def _create_collection_indexes(
            cls,
            collection_name: str,
            indexes: list[IndexModel]
    ) -> None:
        """
        Create indexes for a specific collection.

        Args:
            collection_name: Name of the MongoDB collection
            indexes: List of IndexModel objects to create
        """
        try:
            collection = cls.db[collection_name]

            # Create collection if it doesn't exist
            try:
                await cls.db.create_collection(collection_name)
            except CollectionInvalid:
                pass  # Collection already exists

            # Create all indexes
            if indexes:
                await collection.create_indexes(indexes)
                logger.info(f"Created {len(indexes)} indexes for collection '{collection_name}'")

        except Exception as e:
            logger.error(f"Failed to create indexes for '{collection_name}': {e}")
            raise

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """
        Get the database instance for dependency injection.

        Returns:
            AsyncIOMotorDatabase: The connected database instance

        Raises:
            RuntimeError: If database is not connected
        """
        if cls.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls.db


# Dependency for FastAPI route injection
async def get_database() -> AsyncIOMotorDatabase:
    """
    FastAPI dependency that provides database access to routes.

    Usage:
        @router.get("/example")
        async def example(db: AsyncIOMotorDatabase = Depends(get_database)):
            result = await db.collection.find_one(...)
    """
    return Database.get_db()