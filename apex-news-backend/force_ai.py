import asyncio
import logging
import time
from app.database import Database
from app.services.ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def force_process_news():
    print("-" * 50)
    print("FORCE STARTING AI ANALYSIS (Super Slow Mode)")
    print("   Target: 20 Articles")
    print("   Speed: 1 Article every 15 seconds")
    print("-" * 50)
    
    # Initial cool-down to let the previous errors clear
    print("Waiting 10 seconds before starting to clear previous limits...")
    time.sleep(10)

    try:
        await Database.connect()
        db = Database.get_db()
        ai = AIService()

        # 1. Find articles needing AI
        query = {
            "$or": [
                {"ai_processed": False},
                {"ai_processed": {"$exists": False}},
                {"summary": None},
                {"summary": ""}
            ]
        }
        
        # Get 20 pending articles
        cursor = db.articles.find(query).limit(20)
        articles = await cursor.to_list(length=20)

        print(f"Found {len(articles)} articles waiting for AI...")

        if len(articles) == 0:
            print("No pending articles found!")
            return

        success_count = 0
        
        # 2. Process with MANDATORY DELAYS
        for i, article in enumerate(articles):
            print(f"\n[{i+1}/{len(articles)}] Analyzing: {article['title'][:40]}...")
            
            try:
                # Context for AI
                content_context = article.get('description') or article.get('content') or ""
                
                # CALL AI
                analysis = await ai.analyze_article(article['title'], content_context)
                
                if analysis:
                    await db.articles.update_one(
                        {"_id": article["_id"]},
                        {
                            "$set": {
                                "ai_processed": True,
                                "sentiment": analysis.get("sentiment", "Neutral"),
                                "summary": analysis.get("summary", "No summary provided."),
                                "key_points": analysis.get("key_points", [])
                            }
                        }
                    )
                    print(f"   SUCCESS! Sentiment: {analysis.get('sentiment')}")
                    success_count += 1
                else:
                    print("   FAILED: Rate limit or error occurred.")

            except Exception as e:
                print(f"   CRITICAL ERROR: {e}")

            # === MANDATORY PAUSE ===
            # We wait 15 seconds regardless of success or failure
            # This prevents the loop from hammering the API
            print("   Pausing 15s to respect API limits...")
            time.sleep(15)

        print("-" * 50)
        print(f"JOB COMPLETE. Processed {success_count}/{len(articles)} articles.")
        print("-" * 50)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        await Database.disconnect()

if __name__ == "__main__":
    asyncio.run(force_process_news())