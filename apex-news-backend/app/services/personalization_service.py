"""
Personalization service for building customized news feeds.
Applies user preferences, filters, and ranking algorithms.
"""
import logging
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PersonalizationService:
    """
    Service for personalizing news feeds based on user preferences.
    """

    @staticmethod
    async def build_feed_query(
            db: AsyncIOMotorDatabase,
            user_id: str,
            categories: Optional[str] = None,
            sources: Optional[str] = None,
            keywords: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build MongoDB query for personalized feed.

        Args:
            db: Database connection
            user_id: User ID
            categories: Comma-separated category filters
            sources: Comma-separated source filters
            keywords: Comma-separated keyword filters

        Returns:
            MongoDB query dict
        """
        query: Dict[str, Any] = {}

        # Get user preferences
        prefs = await db.user_preferences.find_one({"user_id": user_id})

        if not prefs:
            # Default query if no preferences set
            return query

        # Apply category filters
        category_list = []
        if categories:
            category_list = [c.strip().lower() for c in categories.split(",")]
        elif prefs.get("categories"):
            category_list = prefs["categories"]

        if category_list:
            query["category"] = {"$in": category_list}

        # Apply source filters
        source_list = []
        if sources:
            source_list = [s.strip() for s in sources.split(",")]
        elif prefs.get("sources"):
            source_list = prefs["sources"]

        if source_list:
            query["source"] = {"$in": source_list}

        # Apply keyword filters (match in title or description)
        keyword_list = []
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(",")]
        elif prefs.get("keywords"):
            keyword_list = prefs["keywords"]

        if keyword_list:
            keyword_conditions = [
                {"title": {"$regex": kw, "$options": "i"}} for kw in keyword_list
            ]
            keyword_conditions.extend([
                {"description": {"$regex": kw, "$options": "i"}} for kw in keyword_list
            ])
            query["$or"] = keyword_conditions

        # Apply exclude keywords (using $and to combine with existing query)
        exclude_keywords = prefs.get("exclude_keywords", [])
        if exclude_keywords:
            exclude_conditions = []
            for keyword in exclude_keywords:
                exclude_conditions.append({"title": {"$not": {"$regex": keyword, "$options": "i"}}})
                exclude_conditions.append({"description": {"$not": {"$regex": keyword, "$options": "i"}}})
            
            if "$and" in query:
                query["$and"].extend(exclude_conditions)
            else:
                # Wrap existing query in $and with exclude conditions
                existing_query = query.copy()
                query.clear()
                query["$and"] = [existing_query] + exclude_conditions

        # Only show recent articles (last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        query["published_at"] = {"$gte": cutoff_date}

        logger.debug(f"Built feed query for user {user_id}: {query}")

        return query

    @staticmethod
    async def get_recommended_articles(
            db: AsyncIOMotorDatabase,
            user_id: str,
            limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get AI-recommended articles based on user reading history.
        Simple implementation: articles similar to what user has viewed.

        Args:
            db: Database connection
            user_id: User ID
            limit: Max articles to return

        Returns:
            List of article documents
        """
        # Get user's viewed articles
        viewed_cursor = db.analytics.find({
            "user_id": user_id,
            "event_type": "view"
        }).sort("timestamp", -1).limit(50)

        viewed_events = await viewed_cursor.to_list(length=50)

        if not viewed_events:
            # No history, return trending articles
            return await PersonalizationService._get_trending_articles(db, limit)

        # Get categories and sources from viewed articles
        article_ids = [event["article_id"] for event in viewed_events]
        
        # Convert string IDs to ObjectId
        from bson import ObjectId
        article_oids = []
        for aid in article_ids:
            try:
                article_oids.append(ObjectId(aid))
            except Exception:
                logger.warning(f"Invalid article ID in personalization: {aid}")
                continue
        
        if not article_oids:
            return await PersonalizationService._get_trending_articles(db, limit)
        
        viewed_articles = await db.articles.find({
            "_id": {"$in": article_oids}
        }).to_list(length=50)

        # Extract preferences from history
        categories = set()
        sources = set()

        for article in viewed_articles:
            if article.get("category"):
                categories.add(article["category"])
            if article.get("source"):
                sources.add(article["source"])

        # Build recommendation query
        query = {
            "_id": {"$nin": article_oids},  # Exclude already viewed
            "$or": [
                {"category": {"$in": list(categories)}},
                {"source": {"$in": list(sources)}}
            ],
            "published_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
        }

        # Get recommended articles sorted by engagement
        recommended = await db.articles.find(query).sort([
            ("view_count", -1),
            ("published_at", -1)
        ]).limit(limit).to_list(length=limit)

        logger.info(f"Generated {len(recommended)} recommendations for user {user_id}")

        return recommended

    @staticmethod
    async def _get_trending_articles(
            db: AsyncIOMotorDatabase,
            limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get trending articles (most viewed/clicked in last 24 hours).

        Args:
            db: Database connection
            limit: Max articles to return

        Returns:
            List of trending article documents
        """
        cutoff_date = datetime.utcnow() - timedelta(hours=24)

        trending = await db.articles.find({
            "published_at": {"$gte": cutoff_date}
        }).sort([
            ("view_count", -1),
            ("click_count", -1),
            ("published_at", -1)
        ]).limit(limit).to_list(length=limit)

        return trending