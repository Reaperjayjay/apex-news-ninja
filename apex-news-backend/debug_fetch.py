import asyncio
import sys
import os
import traceback

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

from app.database import Database
from app.services.news_scheduler import NewsScheduler

async def main():
    print("=== STEP 1: Initializing Database ===", flush=True)
    try:
        await Database.connect()
        print("=== STEP 2: Database Connected ===", flush=True)
    except Exception as e:
        print(f"!!! Database connection failed: {e}", flush=True)
        traceback.print_exc()
        return

    print("=== STEP 3: Triggering News Fetch ===", flush=True)
    try:
        summary = await NewsScheduler.trigger_fetch_now()
        print("=== STEP 4: Fetch Completed ===", flush=True)
        print(f"Summary: {summary}", flush=True)
    except Exception as e:
        print(f"!!! Fetch Failed with Exception: {e}", flush=True)
        traceback.print_exc()
    finally:
        print("=== STEP 5: Disconnecting ===", flush=True)
        await Database.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
