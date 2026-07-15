"""
News fetchers for GNews, CryptoCompare, and RSS.
"""
import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

import httpx
import feedparser
from motor.motor_asyncio import AsyncIOMotorDatabase
import pymongo 

from app.config import settings
from app.sources.sources_config import (
    NewsNiche, SourceType, get_source_config, get_all_niches
)
from app.models.news_model import ArticleCreate, ArticleInDB

logger = logging.getLogger(__name__)


class BaseNewsFetcher(ABC):
    """
    Base fetcher with common functionality for all news sources.
    """

    def __init__(self, niche: NewsNiche, db: AsyncIOMotorDatabase):
        self.niche = niche
        self.db = db
        self.config = get_source_config(niche)
        self.timeout = 30
        self._last_request_time: Optional[datetime] = None

    async def _make_request(
            self,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict]:
        """Make HTTP request with error handling."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Request failed for {self.niche.value}: {e}")
                return None

    async def _deduplicate_and_store(self, articles: List[ArticleCreate]) -> int:
        """
        Check for duplicates and store new articles.
        Implements 'Top 3 Only' strategy for AI processing to save quota.
        """
        stored_count = 0
        ai_queued_count = 0 
        AI_LIMIT_PER_BATCH = 3 

        for article in articles:
            try:
                # Convert to DB model with content hash
                article_in_db = ArticleInDB.from_create(article)

                # Check if article exists (by content_hash)
                existing = await self.db.articles.find_one({
                    "content_hash": article_in_db.content_hash
                })

                if existing:
                    continue

                # Prepare the document
                doc = article_in_db.to_dict()

                # --- OPTIMIZATION: TOP 3 STRATEGY ---
                if ai_queued_count < AI_LIMIT_PER_BATCH:
                    # Priority Article: Mark for AI Processing
                    doc["ai_processed"] = False
                    doc["sentiment"] = "Neutral"
                    doc["summary"] = None
                    ai_queued_count += 1
                else:
                    # Standard Article: Skip AI to save quota
                    doc["ai_processed"] = True
                    doc["sentiment"] = "Neutral"
                    # Fallback to description so the UI isn't empty
                    doc["summary"] = doc.get("description") or "No summary available."

                # Store new article
                await self.db.articles.insert_one(doc)
                stored_count += 1
            
            except pymongo.errors.DuplicateKeyError:
                continue
            except Exception as e:
                logger.error(f"Failed to store article [{self.niche.value}]: {e}")
                continue

        return stored_count

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        if not date_str: return datetime.utcnow()
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except Exception:
            return datetime.utcnow()

    @abstractmethod
    async def fetch_and_store(self) -> Dict[str, Any]:
        """Fetch articles and store in database."""
        pass


class GNewsFetcher(BaseNewsFetcher):
    """
    Fetcher for GNews API (Replaces NewsAPI).
    """

    async def fetch_and_store(self) -> Dict[str, Any]:
        start_time = datetime.utcnow()

        # Get API key
        api_key_env = self.config.get("api_key_env", "gnews_api_key")
        api_key = getattr(settings, api_key_env, None)
        
        if not api_key:
            return {"niche": self.niche.value, "success": False, "error": "API key missing"}

        params = self.config.get("params", {}).copy()
        # GNews uses 'token' parameter
        params["token"] = api_key

        data = await self._make_request(
            self.config.get("endpoint"),
            params=params
        )

        if not data:
            return {"niche": self.niche.value, "success": False, "error": "No response"}
            
        if "errors" in data:
            return {"niche": self.niche.value, "success": False, "error": str(data["errors"])}

        articles = []
        for item in data.get("articles", []):
            try:
                if not item.get("url"): continue

                article = ArticleCreate(
                    title=item.get("title", "Untitled"),
                    description=item.get("description", ""),
                    content=item.get("content", ""),
                    url=item["url"],
                    image_url=item.get("image"), # GNews uses 'image'
                    source=item.get("source", {}).get("name", "GNews"),
                    author=None, # GNews rarely provides authors
                    category=self.niche.value,
                    published_at=self._parse_date(item.get("publishedAt"))
                )
                articles.append(article)
            except Exception:
                continue

        stored_count = await self._deduplicate_and_store(articles)
        elapsed = (datetime.utcnow() - start_time).total_seconds()

        return {
            "niche": self.niche.value,
            "success": True,
            "fetched": len(articles),
            "stored": stored_count,
            "duplicates": len(articles) - stored_count,
            "duration_seconds": elapsed
        }


class RSSFetcher(BaseNewsFetcher):
    """
    Fetcher for RSS feeds (Used for Forex).
    """

    async def fetch_and_store(self) -> Dict[str, Any]:
        start_time = datetime.utcnow()
        
        # Parse RSS Feed
        feed = feedparser.parse(self.config.get("endpoint"))

        if feed.bozo and not feed.entries:
            return {"niche": self.niche.value, "success": False, "error": "RSS Parse Error"}

        articles = []
        for entry in feed.entries:
            try:
                # Basic image extraction for RSS
                image_url = None
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                elif 'enclosures' in entry:
                    for enc in entry.enclosures:
                        if 'image' in enc.type:
                            image_url = enc.href
                            break

                article = ArticleCreate(
                    title=entry.get('title', 'Untitled'),
                    description=entry.get('summary', '')[:500],
                    content=None,
                    url=entry.get('link', ''),
                    image_url=image_url,
                    source=feed.feed.get('title', 'RSS Source'),
                    author=entry.get('author', ''),
                    category=self.niche.value,
                    published_at=self._parse_date(entry.get('published', entry.get('updated')))
                )
                articles.append(article)
            except Exception:
                continue

        stored_count = await self._deduplicate_and_store(articles)
        elapsed = (datetime.utcnow() - start_time).total_seconds()

        return {
            "niche": self.niche.value,
            "success": True,
            "fetched": len(articles),
            "stored": stored_count,
            "duplicates": len(articles) - stored_count,
            "duration_seconds": elapsed
        }


class CryptoCompareAPIFetcher(BaseNewsFetcher):
    """
    Fetcher for CryptoCompare API.
    """

    async def fetch_and_store(self) -> Dict[str, Any]:
        start_time = datetime.utcnow()

        api_key = getattr(settings, self.config.get("api_key_env", "cryptocompare_api_key"), None)
        if not api_key:
            return {"niche": self.niche.value, "success": False, "error": "API key missing"}

        params = self.config.get("params", {}).copy()
        headers = {"authorization": f"Apikey {api_key}"}

        data = await self._make_request(
            self.config.get("endpoint"),
            params=params,
            headers=headers
        )

        if not data or "Data" not in data:
            return {"niche": self.niche.value, "success": False, "error": data.get("Message", "Unknown Error")}

        articles = []
        for item in data.get("Data", []):
            try:
                article = ArticleCreate(
                    title=item.get("title", "Untitled"),
                    description=item.get("body", "")[:500],
                    content=item.get("body"),
                    url=item.get("url", item.get("guid", "")),
                    image_url=item.get("imageurl"),
                    source=item.get("source_info", {}).get("name", "CryptoCompare"),
                    author=None,
                    category=self.niche.value,
                    published_at=datetime.fromtimestamp(item.get("published_on", datetime.utcnow().timestamp()))
                )
                articles.append(article)
            except Exception:
                continue

        stored_count = await self._deduplicate_and_store(articles)
        elapsed = (datetime.utcnow() - start_time).total_seconds()

        return {
            "niche": self.niche.value,
            "success": True,
            "fetched": len(articles),
            "stored": stored_count,
            "duplicates": len(articles) - stored_count,
            "duration_seconds": elapsed
        }


class NewsFetcherFactory:
    """
    Factory to create appropriate fetcher for each niche.
    """

    @staticmethod
    def create_fetcher(niche: NewsNiche, db: AsyncIOMotorDatabase) -> BaseNewsFetcher:
        config = get_source_config(niche)
        source_type = config.get("source_type")

        if source_type == SourceType.GNEWS:
            return GNewsFetcher(niche, db)
        elif source_type == SourceType.RSS:
            return RSSFetcher(niche, db)
        elif source_type == SourceType.CRYPTO_COMPARE_API:
            return CryptoCompareAPIFetcher(niche, db)
        else:
            raise ValueError(f"Unknown source type: {source_type}")

    @staticmethod
    async def fetch_all_niches(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
        """
        Fetch articles from all niches SEQUENTIALLY to respect API Rate Limits.
        """
        start_time = datetime.utcnow()
        all_niches = get_all_niches()
        
        results = []
        clean_results = []
        errors = []
        total_fetched = 0
        total_stored = 0
        total_duplicates = 0

        # IMPORTANT: Loop through niches one by one instead of parallel
        for niche in all_niches:
            try:
                # 1. Fetch
                fetcher = NewsFetcherFactory.create_fetcher(niche, db)
                result = await fetcher.fetch_and_store()
                
                # 2. Log Result
                results.append(result)
                if isinstance(result, dict):
                    clean_results.append(result)
                    if result.get("success"):
                        total_fetched += result.get("fetched", 0)
                        total_stored += result.get("stored", 0)
                        total_duplicates += result.get("duplicates", 0)
                    else:
                        errors.append(f"{result.get('niche')}: {result.get('error')}")
                elif isinstance(result, Exception):
                    errors.append(str(result))

                # 3. CRITICAL PAUSE: 1.5s delay to keep GNews happy
                await asyncio.sleep(1.5)

            except Exception as e:
                logger.error(f"Error processing niche {niche}: {e}")
                errors.append(f"{niche}: {str(e)}")

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_niches": len(all_niches),
            "total_fetched": total_fetched,
            "total_stored": total_stored,
            "total_duplicates": total_duplicates,
            "errors_count": len(errors),
            "errors": errors,
            "duration_seconds": elapsed,
            "niche_results": clean_results
        }
        
        logger.info(f"All niches fetch complete: {summary}")
        return summary