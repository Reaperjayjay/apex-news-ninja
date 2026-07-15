import json
import logging
import asyncio
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Initialize the new Client
        if not settings.gemini_api_key:
            logger.warning("AI Service initialized without API Key")
            self.client = None
        else:
            self.client = genai.Client(api_key=settings.gemini_api_key)

        # UPDATED: Using the model confirmed by your script
        self.model_name = "models/gemini-2.0-flash" 

    async def analyze_article(self, title: str, content: str = None) -> dict:
        """
        Analyzes an article using the new Google GenAI SDK.
        """
        if not self.client:
            return None

        text_to_analyze = content if content else title
        safe_content = text_to_analyze[:3000]

        prompt = f"""
        Analyze this financial news article.
        
        Title: {title}
        Content: {safe_content}

        Return a JSON object with these exact keys:
        - summary: A 2-sentence executive summary.
        - sentiment: "Bullish", "Bearish", or "Neutral".
        - key_points: A list of 3 key takeaways.
        """

        try:
            # Run in executor to avoid blocking the server
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json" 
                    )
                )
            )

            # Parse the response
            if response.text:
                return json.loads(response.text)
            
            return None

        except Exception as e:
            logger.error(f"AI Analysis failed for article '{title[:20]}...': {e}")
            return None