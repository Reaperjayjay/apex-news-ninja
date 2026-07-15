"""
Main FastAPI application for Vercel Serverless Deployment.
Lightweight setup: Includes optional background scheduler for local dev.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Database
from app.services.news_scheduler import NewsScheduler
from app.routes import auth, news, preferences

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager: Handles Database connection.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} in Serverless Mode")
    try:
        await Database.connect()
        logger.info("MongoDB connection established")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield  # Application runs

    # Shutdown
    try:
        await Database.disconnect()
        logger.info("Database disconnected")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Apex News Ninja API (Serverless)",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- CORS FIX IS HERE ---
# You MUST list the specific domains. No "*" allowed with credentials.
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://apex-ninja-spark.vercel.app",  # Your Frontend URL
    "https://apex-ninja-spark.vercel.app/"  # Trailing slash variation
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
app.include_router(preferences.router, prefix="/api/v1/preferences", tags=["Preferences"])


# --- VERCEL CRON TRIGGER ---
@app.get("/api/cron/update-news")
async def trigger_news_update(authorization: str = Header(None)):
    """
    CRON ENDPOINT: Called by Vercel every hour.
    Triggers: 1. News Fetch, 2. AI Analysis, 3. Cleanup
    """
    # 1. Security Check
    expected_secret = settings.cron_secret
    # If no secret is set in env, we skip the check (be careful!)
    if expected_secret and authorization != f"Bearer {expected_secret}":
        logger.warning(f"Unauthorized Cron Attempt. Auth provided: {authorization}")
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info("Cron Trigger Received: Starting Update...")

    # 2. Fetch News
    fetch_summary = await NewsScheduler.trigger_fetch_now()
    
    # 3. Run AI Analysis
    ai_summary = {"processed": 0}
    if Database.client:
        db = Database.client[settings.mongodb_db_name]
        if hasattr(NewsScheduler, 'process_ai_queue'):
             ai_summary = await NewsScheduler.process_ai_queue(db)

    # 4. Run Cleanup (Optional: Keeps DB small)
    cleanup_summary = await NewsScheduler.trigger_cleanup()
    
    return {
        "status": "success", 
        "fetch_summary": fetch_summary, 
        "ai_summary": ai_summary,
        "cleanup": cleanup_summary
    }


@app.get("/", include_in_schema=False)
async def root():
    return {
        "status": "online",
        "service": settings.app_name,
        "mode": "serverless"
    }


@app.get("/health")
async def health_check():
    """Simple health check for monitoring."""
    try:
        # We need to make sure Database.client is initialized
        if Database.client:
            await Database.client.admin.command('ping')
            return {"status": "healthy", "database": "connected"}
        else:
             return {"status": "unhealthy", "database": "disconnected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)