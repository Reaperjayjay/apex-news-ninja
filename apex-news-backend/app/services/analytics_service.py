"""
Analytics service for tracking user interactions and generating insights.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.news_model import ArticleAnalytics

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service for tracking and analyzing user behavior.
    """

    @staticmethod
    async def track_event(
            db: AsyncIOMotorDatabase,
            user_id: str,
            article_id: str,
            event_type: str,
            metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track user interaction event.

        Args:
            db: Database connection
            user_id: User ID
            article_id: Article ID
            event_type: Event type (view, click, share, bookmark)
            metadata: Additional event data

        Returns:
            True if tracked successfully
        """
        try:
            event = ArticleAnalytics(
                user_id=user_id,
                article_id=article_id,
                event_type=event_type,
                metadata=metadata or {}
            )

            await db.analytics.insert_one(event.to_dict())

            logger.debug(f"Tracked {event_type} event: user={user_id}, article={article_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return False

    @staticmethod
    async def get_user_reading_stats(
            db: AsyncIOMotorDatabase,
            user_id: str,
            days: int = 30
    ) -> Dict[str, Any]:
        """
        Get user reading statistics.

        Args:
            db: Database connection
            user_id: User ID
            days: Number of days to analyze

        Returns:
            Statistics dict
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get all user events
        events_cursor = db.analytics.find({
            "user_id": user_id,
            "timestamp": {"$gte": cutoff_date}
        })

        events = await events_cursor.to_list(length=None)

        # Calculate statistics
        total_views = sum(1 for e in events if e["event_type"] == "view")
        total_clicks = sum(1 for e in events if e["event_type"] == "click")

        # Get category distribution
        article_ids = [e["article_id"] for e in events if e["event_type"] == "view"]
        
        # Convert string IDs to ObjectId
        article_oids = []
        for aid in article_ids:
            try:
                article_oids.append(ObjectId(aid))
            except Exception:
                logger.warning(f"Invalid article ID in analytics: {aid}")
                continue
        
        if not article_oids:
            return {
                "period_days": days,
                "total_views": total_views,
                "total_clicks": total_clicks,
                "engagement_rate": 0,
                "top_categories": [],
                "top_sources": [],
                "average_daily_reads": 0
            }
        
        articles = await db.articles.find({"_id": {"$in": article_oids}}).to_list(length=None)

        category_counts: Dict[str, int] = {}
        source_counts: Dict[str, int] = {}

        for article in articles:
            category = article.get("category", "unknown")
            source = article.get("source", "unknown")

            category_counts[category] = category_counts.get(category, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1

        return {
            "period_days": days,
            "total_views": total_views,
            "total_clicks": total_clicks,
            "engagement_rate": (total_clicks / total_views * 100) if total_views > 0 else 0,
            "top_categories": sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_sources": sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "average_daily_reads": total_views / days
        }

    @staticmethod
    async def get_trending_topics(
            db: AsyncIOMotorDatabase,
            hours: int = 24,
            limit: int = 10
    ) -> list:
        """
        Get trending topics based on view/click counts.

        Args:
            db: Database connection
            hours: Time window in hours
            limit: Max topics to return

        Returns:
            List of trending topics with counts
        """
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)

        # Aggregate most viewed articles
        pipeline = [
            {"$match": {"published_at": {"$gte": cutoff_date}}},
            {"$group": {
                "_id": "$category",
                "total_views": {"$sum": "$view_count"},
                "total_clicks": {"$sum": "$click_count"},
                "article_count": {"$sum": 1}
            }},
            {"$sort": {"total_views": -1}},
            {"$limit": limit}
        ]

        trending = await db.articles.aggregate(pipeline).to_list(length=limit)

        return [
            {
                "topic": t["_id"],
                "views": t["total_views"],
                "clicks": t["total_clicks"],
                "articles": t["article_count"]
            }
            for t in trending
        ]