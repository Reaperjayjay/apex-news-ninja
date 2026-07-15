"""Fetch news immediately for demo"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.services.news_fetchers import NewsFetcherFactory

async def main():
    print("\n🥷 Fetching news from all 10 sources...")
    print("This takes 30-60 seconds...\n")
    
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    result = await NewsFetcherFactory.fetch_all_niches(db)
    
    print("\n✅ DONE!")
    print(f"Fetched: {result['total_fetched']} articles")
    print(f"Stored: {result['total_stored']} new articles")
    print(f"Duplicates: {result['total_duplicates']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())