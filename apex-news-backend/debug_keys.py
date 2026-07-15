import os
from app.config import settings
import google.generativeai as genai

print("-" * 30)
print("DEBUGGING API KEYS")
print("-" * 30)

# 1. Check if loading from Config
key = settings.gemini_api_key
masked_key = f"{key[:5]}...{key[-5:]}" if key else "None"

print(f"1. Key in settings:   {masked_key}")

if not key:
    print("[ERROR] Python cannot find the key in app/config.py")
    print("   -> Check your .env file format.")
    print("   -> Ensure there are NO spaces: GEMINI_API_KEY=AIza...")
    print("   -> Ensure the .env file is in the root directory.")
else:
    print("[SUCCESS] Key found in config!")

    # 2. Test the connection to Google
    print("\n2. Testing Google Gemini Connection...")
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'System Operational'")
        print(f"[SUCCESS] AI Responded: {response.text.strip()}")
    except Exception as e:
        print(f"[ERROR] CONNECTION FAILED: {e}")

print("-" * 30)