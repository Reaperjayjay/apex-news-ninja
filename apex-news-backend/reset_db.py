from pymongo import MongoClient
from app.config import settings

def reset():
    print("-" * 30)
    print("RESETTING DATABASE (ApexNewsNinja)")
    print("-" * 30)

    # 1. Connect using the URL from your .env
    client = MongoClient(settings.mongodb_url)
    
    # 2. Explicitly select the 'ApexNewsNinja' database
    db = client["ApexNewsNinja"]

    # 3. Check and Delete
    try:
        count = db.articles.count_documents({})
        print(f"Current Articles found: {count}")

        if count > 0:
            db.articles.delete_many({})
            print(f"Deleted {count} articles. Database is now empty.")
        else:
            print("Database is already empty.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset()