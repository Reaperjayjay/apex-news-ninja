"""
News feed endpoints with personalization, search, and analytics tracking.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pymongo import DESCENDING
from typing import Optional

from app.config import settings
from app.database import get_database
from app.models.news_model import ArticleResponse, ArticleAnalytics
from app.services.personalization_service import PersonalizationService
from app.services.analytics_service import AnalyticsService
from app.utils.vibe_guard import limiter
from app.utils.jwt_handler import JWTHandler
from app.services.news_scheduler import NewsScheduler

router = APIRouter()
logger = logging.getLogger(__name__)

# --- LOCAL AUTH DEPENDENCY ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Validates the token and retrieves the current user."""
    payload = JWTHandler.verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

# --- HELPER: Convert Database IDs to Strings ---
def serialize_mongo(obj):
    """Recursively convert ObjectId to string to prevent JSON errors."""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        return {k: serialize_mongo(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_mongo(i) for i in obj]
    return obj
# -----------------------------------------------

@router.get("/trigger-fetch", response_model=dict)
async def trigger_news_fetch(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Manually trigger news fetch for all niches."""
    try:
        # 1. Run the fetch logic
        summary = await NewsScheduler.trigger_fetch_now()
        
        # 2. Sanitize the result
        safe_summary = serialize_mongo(summary)

        return {
            "status": "success",
            "message": "News fetch triggered successfully",
            "data": safe_summary
        }
    except Exception as e:
        import sys
        import traceback
        traceback.print_exc(file=sys.stderr)
        logger.error(f"Failed to trigger news fetch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/feed", response_model=dict)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def get_personalized_feed(
        request: Request,
        categories: Optional[str] = None,
        sources: Optional[str] = None,
        keywords: Optional[str] = None, # <--- Search keywords come here
        page: int = 1,
        page_size: int = 20,
        db: AsyncIOMotorDatabase = Depends(get_database),
        current_user: dict = Depends(get_current_user)
):
    """Get personalized news feed with search capability."""
    user_id = str(current_user["_id"])

    # 1. Start with Personalization Query
    query = await PersonalizationService.build_feed_query(
        db, user_id, categories, sources, keywords
    )

    # 2. Explicit Search Logic (Ensures Search Bar works)
    if keywords:
        search_regex = {"$regex": keywords, "$options": "i"}
        
        keyword_filter = {
            "$or": [
                {"title": search_regex},
                {"description": search_regex}
            ]
        }
        
        # Combine existing personalization with search
        if query:
            query = {"$and": [query, keyword_filter]}
        else:
            query = keyword_filter

    # Pagination
    skip = (page - 1) * page_size

    try:
        # Sort by published_at DESC so newest news is first
        cursor = db.articles.find(query).sort("published_at", DESCENDING).skip(skip).limit(page_size)
        articles = await cursor.to_list(length=page_size)
        total = await db.articles.count_documents(query)
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch articles"
        )

    # Format response
    article_responses = [
        ArticleResponse(
            _id=str(doc["_id"]),
            **{k: v for k, v in doc.items() if k != "_id"}
        )
        for doc in articles
    ]

    return {
        "status": "success",
        "message": "Feed retrieved successfully",
        "data": {
            "items": [a.model_dump() for a in article_responses], # Frontend expects "items" or "articles"
            "articles": [a.model_dump() for a in article_responses], # Keeping both for compatibility
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": total > (page * page_size),
            "has_previous": page > 1
        }
    }


@router.post("/article/{article_id}/view", response_model=dict)
@limiter.limit(f"{settings.rate_limit_per_hour}/hour")
async def track_article_view(
        request: Request,
        article_id: str,
        db: AsyncIOMotorDatabase = Depends(get_database),
        current_user: dict = Depends(get_current_user)
):
    """Track article view event."""
    user_id = str(current_user["_id"])

    await AnalyticsService.track_event(
        db, user_id, article_id, "view"
    )

    try:
        article_oid = ObjectId(article_id)
        await db.articles.update_one(
            {"_id": article_oid},
            {"$inc": {"view_count": 1}}
        )
    except Exception:
        pass 

    return {
        "status": "success",
        "message": "View tracked",
        "data": None
    }