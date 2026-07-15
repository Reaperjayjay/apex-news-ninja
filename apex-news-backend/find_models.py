import asyncio
from google import genai
from app.config import settings

async def list_all_models():
    # Print a header for clarity
    print("-" * 30)
    print("LISTING ALL AVAILABLE MODELS")
    print("-" * 30)
    
    # Verify the API Key exists
    if not settings.gemini_api_key:
        print("API Key not found in settings! Check your .env file.")
        return

    # Initialize the Client
    client = genai.Client(api_key=settings.gemini_api_key)
    
    try:
        # Retrieve the list of models
        # The new SDK returns an iterator of Model objects
        pager = client.models.list()
        
        print("Found the following models:")
        for model in pager:
            # We print the 'name' attribute directly. 
            # This will look like 'models/gemini-1.5-flash'
            print(f"   Model: {model.name}")
            
    except Exception as e:
        # Print any connection or parsing errors
        print(f"Error scanning models: {e}")

if __name__ == "__main__":
    asyncio.run(list_all_models())