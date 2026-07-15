import asyncio
from app.database import Database

async def update_retention_rule():
    print("UPDATING DATABASE RETENTION POLICY...")
    
    # Connect using the settings we just updated
    await Database.connect()
    db = Database.get_db()
    
    try:
        # 1. Drop the old index (if it exists)
        # We look for the index named "ttl_expiry"
        await db.articles.drop_index("ttl_expiry")
        print("Old 30-day retention rule removed.")
    except Exception as e:
        print(f"Note: Old index not found (this is fine): {e}")

    # 2. Re-create the index
    # This reads your new config (7 days) and creates the fresh index
    await Database._create_indexes()
    print("NEW 7-Day Auto-Delete Rule applied successfully!")

    await Database.disconnect()

if __name__ == "__main__":
    asyncio.run(update_retention_rule())