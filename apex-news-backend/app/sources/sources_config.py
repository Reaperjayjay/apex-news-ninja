"""
News sources configuration.
GNews (API) for most niches + CryptoCompare + RSS for Forex.
"""
from typing import Dict, Any, List
from enum import Enum


class NewsNiche(str, Enum):
    TECH = "tech"
    BUSINESS = "business"
    SPORTS = "sports"
    AI = "ai"
    WORLD = "world"
    POLITICS = "politics"
    HEALTH = "health"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"   
    CRYPTO = "crypto"
    FOREX = "forex"


class SourceType(str, Enum):
    GNEWS = "gnews"
    RSS = "rss"
    CRYPTO_COMPARE_API = "crypto_compare_api"


# Configuration for all niches
SOURCES_CONFIG: Dict[NewsNiche, Dict[str, Any]] = {
    # --- GNEWS NICHES ---
    
    NewsNiche.TECH: {
        "name": "Tech News",
        "source_type": SourceType.GNEWS,
        "endpoint": "https://gnews.io/api/v4/top-headlines",
        "params": {"topic": "technology", "lang": "en", "max": 10},
        "api_key_env": "gnews_api_key"
    },

    NewsNiche.BUSINESS: {
        "name": "Business News",
        "source_type": SourceType.GNEWS,
        "endpoint": "https://gnews.io/api/v4/top-headlines",
        "params": {"topic": "business", "lang": "en", "max": 10},
        "api_key_env": "gnews_api_key"
    },

    NewsNiche.SPORTS: {
        "name": "Sports News",
        "source_type": SourceType.GNEWS,
        "endpoint": "https://gnews.io/api/v4/top-headlines",
        "params": {"topic": "sports", "lang": "en", "max": 10},
        "api_key_env": "gnews_api_key"
    },

    NewsNiche.AI: {
        "name": "AI News",
        "source_type": SourceType.GNEWS,
        "endpoint": "https://gnews.io/api/v4/search",
        "params": {"q": "artificial intelligence OR machine learning", "lang": "en", "sortby": "publishedAt", "max": 10},
        "api_key_env": "gnews_api_key"
    },

    NewsNiche.WORLD: {
        "name": "World News",
        "source_type": SourceType.GNEWS,
        "endpoint": "https://gnews.io/api/v4/top-headlines",
        "params": {"topic": "world", "lang": "en", "max": 10},
        "api_key_env": "gnews_api_key"
    },

    NewsNiche.POLITICS: {
        "name": "Politics News",
        "source_type": SourceType.GNEWS,
        "endpoint": "https://gnews.io/api/v4/search",
        "params": {"q": "politics", "lang": "en", "max": 10},
        "api_key_env": "gnews_api_key"
    },

    NewsNiche.HEALTH: {
        "name": "Health News",
        "source_type": SourceType.GNEWS,
        "endpoint": "https://gnews.io/api/v4/top-headlines",
        "params": {"topic": "health", "lang": "en", "max": 10},
        "api_key_env": "gnews_api_key"
    },

    NewsNiche.ENTERTAINMENT: {
        "name": "Entertainment News",
        "source_type": SourceType.GNEWS,
        "endpoint": "https://gnews.io/api/v4/top-headlines",
        "params": {"topic": "entertainment", "lang": "en", "max": 10},
        "api_key_env": "gnews_api_key"
    },

    NewsNiche.EDUCATION: {  
        "name": "Education News",
        "source_type": SourceType.GNEWS,
        "endpoint": "https://gnews.io/api/v4/search",
        "params": {"q": "education technology OR edtech OR higher education", "lang": "en", "max": 10},
        "api_key_env": "gnews_api_key"
    },

    # --- SPECIALTY NICHES ---

    NewsNiche.CRYPTO: {
        "name": "Crypto News",
        "source_type": SourceType.CRYPTO_COMPARE_API,
        "endpoint": "https://min-api.cryptocompare.com/data/v2/news/",
        "params": {"lang": "EN", "sortOrder": "latest"},
        "api_key_env": "cryptocompare_api_key"
    },

    NewsNiche.FOREX: {
        "name": "Forex News",
        "source_type": SourceType.RSS,
        "endpoint": "https://www.investing.com/rss/news_1.rss",
        "params": {},
        "api_key_env": None
    }
}

def get_source_config(niche: NewsNiche) -> Dict[str, Any]:
    return SOURCES_CONFIG.get(niche, {})

def get_all_niches() -> List[NewsNiche]:
    return list(SOURCES_CONFIG.keys())