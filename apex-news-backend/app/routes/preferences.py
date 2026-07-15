"""
User preferences routes for managing news feed customization.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from app.config import settings

from app.database import get_database
from app.models.user_model import UserPreferences, UserPreferencesUpdate
from app.utils.vibe_guard import limiter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=dict)
async def get_preferences(
        request: Request,
        db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get current user preferences.

    Returns user's news feed preferences including categories, sources,
    keywords, and digest settings.
    """
    user_id = request.state.user_id

    prefs = await db.user_preferences.find_one({"user_id": user_id})

    if not prefs:
        # Create default preferences if not exists
        default_prefs = UserPreferences(user_id=user_id)
        await db.user_preferences.insert_one(default_prefs.model_dump())
        prefs = default_prefs.model_dump()

    # Remove MongoDB _id for clean response
    prefs.pop("_id", None)

    return {
        "status": "success",
        "message": "Preferences retrieved successfully",
        "data": prefs
    }


@router.put("/", response_model=dict)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def update_preferences(
        request: Request,
        updates: UserPreferencesUpdate,
        db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update user preferences.

    Updates news feed customization including:
    - Categories to follow
    - Preferred sources
    - Keywords to include/exclude
    - Digest settings (enabled, frequency, time)
    """
    user_id = request.state.user_id

    # Build update document (only include non-None fields)
    update_data = {
        k: v for k, v in updates.model_dump().items()
        if v is not None
    }

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid updates provided"
        )

    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()

    # Update preferences
    result = await db.user_preferences.update_one(
        {"user_id": user_id},
        {"$set": update_data},
        upsert=True
    )

    # Also update digest_enabled in user document for quick access
    if "digest_enabled" in update_data:
        try:
            from bson import ObjectId
            user_oid = ObjectId(user_id)
            await db.users.update_one(
                {"_id": user_oid},
                {"$set": {"digest_enabled": update_data["digest_enabled"]}}
            )
        except Exception as e:
            logger.warning(f"Failed to update user digest_enabled: {e}")

    logger.info(f"Preferences updated for user {user_id}")

    return {
        "status": "success",
        "message": "Preferences updated successfully",
        "data": {
            "modified_count": result.modified_count,
            "updated_fields": list(update_data.keys())
        }
    }


@router.post("/reset", response_model=dict)
async def reset_preferences(
        request: Request,
        db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Reset user preferences to defaults.

    Clears all customizations and restores default settings.
    """
    user_id = request.state.user_id

    # Create default preferences
    default_prefs = UserPreferences(user_id=user_id)

    # Replace existing preferences
    await db.user_preferences.replace_one(
        {"user_id": user_id},
        default_prefs.model_dump(),
        upsert=True
    )

    logger.info(f"Preferences reset to defaults for user {user_id}")

    return {
        "status": "success",
        "message": "Preferences reset to defaults",
        "data": None
    }


@router.get("/suggested", response_model=dict)
async def get_suggested_preferences(
        request: Request,
        db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get AI-suggested preferences based on reading history.

    Analyzes user's past behavior to suggest categories and sources
    they might be interested in.
    """
    user_id = request.state.user_id

    from app.services.analytics_service import AnalyticsService

    # Get user reading stats
    stats = await AnalyticsService.get_user_reading_stats(db, user_id, days=30)

    suggestions = {
        "recommended_categories": [cat for cat, _ in stats.get("top_categories", [])[:5]],
        "recommended_sources": [src for src, _ in stats.get("top_sources", [])[:5]],
        "current_engagement_rate": stats.get("engagement_rate", 0),
        "reading_insights": {
            "total_articles_read": stats.get("total_views", 0),
            "average_daily_reads": round(stats.get("average_daily_reads", 0), 2),
            "most_active_category": stats.get("top_categories", [("general", 0)])[0][0]
        }
    }

    return {
        "status": "success",
        "message": "Preference suggestions generated",
        "data": suggestions
    }

