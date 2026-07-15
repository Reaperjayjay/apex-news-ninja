import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Services
from app.services.news_fetchers import NewsFetcherFactory 
from app.services.ai_service import AIService
from app.config import settings
from app.database import Database

logger = logging.getLogger(__name__)

class NewsScheduler:
    """
    Stateless scheduler methods for Vercel Cron.
    """

    @staticmethod
    async def trigger_fetch_now() -> Dict[str, Any]:
        """
        1. Fetches news from all 10 niches.
        2. Stores them in MongoDB.
        """
        logger.info("Triggering News Fetch Job...")
        
        if not Database.client:
            await Database.connect()
        db = Database.client[settings.mongodb_db_name]

        # Run the fetcher
        summary = await NewsFetcherFactory.fetch_all_niches(db)

        # Store history log
        await db.fetch_history.insert_one(summary)
        
        # --- FIX IS HERE ---
        # Convert MongoDB ObjectId to string so FastAPI can return it as JSON
        if "_id" in summary:
            summary["_id"] = str(summary["_id"])
        # -------------------
        
        return summary

    @staticmethod
    async def process_ai_queue(db) -> Dict[str, Any]:
        """
        Finds articles that haven't been analyzed yet and runs AI on them.
        """
        if not settings.gemini_api_key:
            logger.warning("Skipping AI: No API Key found.")
            return {"processed": 0, "error": "No API Key"}

        logger.info("Starting AI Processing Job...")
        ai_service = AIService()
        
        # 1. Find pending articles (Newest first)
        pending_articles = await db.articles.find(
            {"ai_processed": {"$ne": True}}
        ).sort("published_at", -1).limit(5).to_list(length=5)

        if not pending_articles:
            logger.info("No pending articles for AI.")
            return {"processed": 0}

        logger.info(f"Processing {len(pending_articles)} articles...")
        count = 0

        for article in pending_articles:
            analysis = await ai_service.analyze_article(
                title=article.get('title'),
                content=article.get('description') or article.get('content')
            )

            if analysis:
                await db.articles.update_one(
                    {"_id": article["_id"]},
                    {
                        "$set": {
                            "summary": analysis.get("summary"),
                            "sentiment": analysis.get("sentiment"),
                            "key_points": analysis.get("key_points", []),
                            "ai_processed": True
                        }
                    }
                )
                count += 1
            else:
                await db.articles.update_one(
                    {"_id": article["_id"]},
                    {"$set": {"ai_processed": True}}
                )

        logger.info(f"AI Job Complete. Processed {count} articles.")
        return {"processed": count}

    @staticmethod
    async def trigger_cleanup() -> Dict[str, Any]:
        logger.info("Starting Database Cleanup...")
        
        if not Database.client:
            await Database.connect()
        db = Database.client[settings.mongodb_db_name]

        cutoff_date = datetime.utcnow() - timedelta(days=settings.news_retention_days)

        result = await db.articles.delete_many({
            "published_at": {"$lt": cutoff_date}
        })
        
        logger.info(f"Deleted {result.deleted_count} old articles.")
        return {"deleted": result.deleted_count}