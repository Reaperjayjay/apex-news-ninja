import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.news_fetchers import fetch_and_store_news
from app.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def run_news_fetch_job():
    logger.info("Scheduled Job: Starting news fetch...")
    try:
        result = await fetch_and_store_news()
        logger.info(f"Scheduled Job Complete: {result}")
    except Exception as e:
        logger.error(f"Scheduled Job Failed: {e}")

def start_scheduler():
    if not settings.scheduler_enabled:
        logger.info("Scheduler is DISABLED in settings.")
        return

    if scheduler.running:
        return

    # Schedule the job to run every 4 hours
    scheduler.add_job(
        run_news_fetch_job,
        trigger=IntervalTrigger(hours=4),
        id="news_fetch_job",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started: News fetch running every 4 hours.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down.")