"""
Comprehensive test suite for Apex News Ninja API.
Tests authentication, news fetching, preferences, and WhatsApp integration.
"""
import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime
from faker import Faker
from unittest.mock import patch, AsyncMock, MagicMock

# Set test environment variables before importing app
import os

os.environ.update({
    "MONGODB_URL": "mongodb://localhost:27017",
    "MONGODB_DB_NAME": "apex_news_ninja_test",
    "REDIS_URL": "redis://localhost:6379/1",
    "JWT_SECRET_KEY": "test-secret-key-32-chars-minimum-for-security!!",
    "JWT_REFRESH_SECRET_KEY": "test-refresh-secret-32-chars-minimum-for-security!!",
    "NEWSAPI_KEY": "test_newsapi_key",
    "WAWP_API_KEY": "test_wawp_key",
    "WAWP_API_URL": "https://api.test.wawp.io/v1/send",
    "DEBUG": "True"
})

from app.main import app
from app.database import Database
from app.models.user_model import UserInDB
from app.models.news_model import ArticleInDB, ArticleCreate

fake = Faker()


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Setup and teardown test database."""
    # Connect to test database
    await Database.connect()
    db = Database.get_db()

    yield db

    # Cleanup: Drop test database after tests
    await db.client.drop_database("apex_news_ninja_test")
    await Database.disconnect()


@pytest.fixture
async def client():
    """HTTP client for API testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user():
    """Create a test user."""
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": "TestPass123!",
        "full_name": fake.name(),
        "whatsapp_number": "+1234567890"
    }


@pytest.fixture
async def authenticated_client(client: AsyncClient, test_user: dict):
    """HTTP client with authenticated user."""
    # Register user
    await client.post("/api/v1/auth/register", json=test_user)

    # Login to get tokens
    response = await client.post("/api/v1/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })

    data = response.json()
    access_token = data["data"]["access_token"]

    # Add auth header
    client.headers["Authorization"] = f"Bearer {access_token}"

    return client


@pytest.fixture
async def sample_articles():
    """Create sample articles for testing."""
    articles = []
    categories = ["technology", "business", "science"]

    for i in range(10):
        article = ArticleCreate(
            title=f"Test Article {i}: {fake.sentence()}",
            description=fake.text(max_nb_chars=200),
            content=fake.text(max_nb_chars=1000),
            url=fake.url(),
            image_url=fake.image_url(),
            source=fake.company(),
            author=fake.name(),
            category=categories[i % 3],
            published_at=datetime.utcnow()
        )
        articles.append(article)

    return articles


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication endpoints."""

    async def test_register_success(self, client: AsyncClient, test_user: dict):
        """Test successful user registration."""
        response = await client.post("/api/v1/auth/register", json=test_user)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "user_id" in data["data"]

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: dict):
        """Test registration with duplicate email fails."""
        # Register first time
        await client.post("/api/v1/auth/register", json=test_user)

        # Try to register again
        response = await client.post("/api/v1/auth/register", json=test_user)

        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"].lower()

    async def test_register_weak_password(self, client: AsyncClient, test_user: dict):
        """Test registration with weak password fails."""
        test_user["password"] = "weak"

        response = await client.post("/api/v1/auth/register", json=test_user)

        assert response.status_code == 422  # Validation error

    async def test_login_success(self, client: AsyncClient, test_user: dict):
        """Test successful login."""
        # Register user first
        await client.post("/api/v1/auth/register", json=test_user)

        # Login
        response = await client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials fails."""
        response = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "WrongPass123!"
        })

        assert response.status_code == 401

    async def test_refresh_token_success(self, client: AsyncClient, test_user: dict):
        """Test token refresh."""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })

        refresh_token = login_response.json()["data"]["refresh_token"]

        # Refresh tokens
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    async def test_refresh_token_reuse_fails(self, client: AsyncClient, test_user: dict):
        """Test that refresh token can only be used once."""
        # Register and login
        await client.post("/api/v1/auth/register", json=test_user)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })

        refresh_token = login_response.json()["data"]["refresh_token"]

        # First refresh succeeds
        await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

        # Second refresh with same token fails (token rotation)
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })

        assert response.status_code == 401


# =============================================================================
# NEWS FEED TESTS
# =============================================================================

@pytest.mark.asyncio
class TestNewsFeed:
    """Test news feed endpoints."""

    async def test_get_feed_requires_auth(self, client: AsyncClient):
        """Test that feed endpoint requires authentication."""
        response = await client.get("/api/v1/news/feed")

        assert response.status_code == 401

    async def test_get_feed_success(
            self,
            authenticated_client: AsyncClient,
            sample_articles: list
    ):
        """Test successful feed retrieval."""
        # Insert sample articles into database
        db = Database.get_db()
        for article in sample_articles:
            article_in_db = ArticleInDB.from_create(article)
            await db.articles.insert_one(article_in_db.to_dict())

        # Get feed
        response = await authenticated_client.get("/api/v1/news/feed")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "articles" in data["data"]
        assert len(data["data"]["articles"]) > 0

    async def test_get_feed_with_filters(
            self,
            authenticated_client: AsyncClient,
            sample_articles: list
    ):
        """Test feed with category filter."""
        # Insert articles
        db = Database.get_db()
        for article in sample_articles:
            article_in_db = ArticleInDB.from_create(article)
            await db.articles.insert_one(article_in_db.to_dict())

        # Get filtered feed
        response = await authenticated_client.get(
            "/api/v1/news/feed?categories=technology"
        )

        assert response.status_code == 200
        data = response.json()
        articles = data["data"]["articles"]

        # All articles should be technology category
        assert all(a["category"] == "technology" for a in articles)

    async def test_get_feed_pagination(
            self,
            authenticated_client: AsyncClient,
            sample_articles: list
    ):
        """Test feed pagination."""
        # Insert articles
        db = Database.get_db()
        for article in sample_articles:
            article_in_db = ArticleInDB.from_create(article)
            await db.articles.insert_one(article_in_db.to_dict())

        # Get first page
        response1 = await authenticated_client.get(
            "/api/v1/news/feed?page=1&page_size=5"
        )

        # Get second page
        response2 = await authenticated_client.get(
            "/api/v1/news/feed?page=2&page_size=5"
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        articles1 = response1.json()["data"]["articles"]
        articles2 = response2.json()["data"]["articles"]

        # Pages should have different articles
        assert len(articles1) == 5
        assert len(articles2) > 0
        assert articles1[0]["id"] != articles2[0]["id"]

    async def test_track_article_view(
            self,
            authenticated_client: AsyncClient,
            sample_articles: list
    ):
        """Test article view tracking."""
        # Insert article
        db = Database.get_db()
        article = sample_articles[0]
        article_in_db = ArticleInDB.from_create(article)
        result = await db.articles.insert_one(article_in_db.to_dict())
        article_id = str(result.inserted_id)

        # Track view
        response = await authenticated_client.post(
            f"/api/v1/news/article/{article_id}/view"
        )

        assert response.status_code == 200

        # Verify view count increased
        updated_article = await db.articles.find_one({"_id": article_id})
        assert updated_article["view_count"] == 1


# =============================================================================
# PREFERENCES TESTS
# =============================================================================

@pytest.mark.asyncio
class TestPreferences:
    """Test user preferences endpoints."""

    async def test_get_preferences_default(self, authenticated_client: AsyncClient):
        """Test getting default preferences."""
        response = await authenticated_client.get("/api/v1/preferences")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "categories" in data["data"]
        assert "digest_enabled" in data["data"]

    async def test_update_preferences(self, authenticated_client: AsyncClient):
        """Test updating preferences."""
        updates = {
            "categories": ["technology", "science"],
            "keywords": ["AI", "machine learning"],
            "digest_enabled": True,
            "max_articles": 15
        }

        response = await authenticated_client.put("/api/v1/preferences", json=updates)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # Verify updates
        get_response = await authenticated_client.get("/api/v1/preferences")
        prefs = get_response.json()["data"]

        assert set(prefs["categories"]) == set(updates["categories"])
        assert set(prefs["keywords"]) == set(updates["keywords"])
        assert prefs["digest_enabled"] == updates["digest_enabled"]
        assert prefs["max_articles"] == updates["max_articles"]

    async def test_reset_preferences(self, authenticated_client: AsyncClient):
        """Test resetting preferences to defaults."""
        # Update preferences
        await authenticated_client.put("/api/v1/preferences", json={
            "categories": ["technology"],
            "keywords": ["test"]
        })

        # Reset
        response = await authenticated_client.post("/api/v1/preferences/reset")

        assert response.status_code == 200

        # Verify reset
        get_response = await authenticated_client.get("/api/v1/preferences")
        prefs = get_response.json()["data"]

        assert prefs["categories"] == []
        assert prefs["keywords"] == []


# =============================================================================
# WHATSAPP INTEGRATION TESTS
# =============================================================================

@pytest.mark.asyncio
class TestWhatsApp:
    """Test WhatsApp digest endpoints."""

    @patch('app.services.notification_service.NotificationService._send_whatsapp_message')
    async def test_send_digest_success(
            self,
            mock_send: AsyncMock,
            authenticated_client: AsyncClient,
            sample_articles: list
    ):
        """Test sending digest (mocked WhatsApp API)."""
        mock_send.return_value = True

        # Insert articles
        db = Database.get_db()
        for article in sample_articles:
            article_in_db = ArticleInDB.from_create(article)
            await db.articles.insert_one(article_in_db.to_dict())

        # Send digest
        response = await authenticated_client.post("/api/v1/whatsapp/send-digest")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert mock_send.called

    async def test_send_digest_no_phone(self, client: AsyncClient, test_user: dict):
        """Test sending digest fails without WhatsApp number."""
        # Register user without WhatsApp number
        user_no_phone = test_user.copy()
        user_no_phone["whatsapp_number"] = ""

        await client.post("/api/v1/auth/register", json=user_no_phone)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": user_no_phone["email"],
            "password": user_no_phone["password"]
        })

        token = login_response.json()["data"]["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"

        # Try to send digest
        response = await client.post("/api/v1/whatsapp/send-digest")

        assert response.status_code == 400

    async def test_update_whatsapp_number(self, authenticated_client: AsyncClient):
        """Test updating WhatsApp number."""
        new_number = "+19876543210"

        response = await authenticated_client.post(
            "/api/v1/whatsapp/update-phone",
            params={"phone_number": new_number}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["phone_number"] == new_number

    async def test_digest_preview(
            self,
            authenticated_client: AsyncClient,
            sample_articles: list
    ):
        """Test digest preview."""
        # Insert articles
        db = Database.get_db()
        for article in sample_articles:
            article_in_db = ArticleInDB.from_create(article)
            await db.articles.insert_one(article_in_db.to_dict())

        # Get preview
        response = await authenticated_client.get("/api/v1/whatsapp/digest-preview")

        assert response.status_code == 200
        data = response.json()
        assert "articles" in data["data"]
        assert data["data"]["article_count"] > 0


# =============================================================================
# HEALTH & METRICS TESTS
# =============================================================================

@pytest.mark.asyncio
class TestHealthMetrics:
    """Test health and metrics endpoints."""

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    async def test_metrics_endpoint(self, client: AsyncClient):
        """Test metrics endpoint."""
        response = await client.get("/metrics")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])