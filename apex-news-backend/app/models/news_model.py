"""
News article models for API validation and database storage.
Includes normalization and deduplication logic via content hashing.
"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict
import hashlib
import re


# -------------------------------------------------------
# Base Article Model
# -------------------------------------------------------
class ArticleBase(BaseModel):
    """Base article model with core fields."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    content: Optional[str] = None
    url: HttpUrl
    image_url: Optional[HttpUrl] = None
    source: str = Field(..., min_length=1, max_length=100)
    author: Optional[str] = Field(None, max_length=200)
    category: str = Field(default="general", max_length=50)
    published_at: datetime

    # ---------------------------
    # NORMALIZE TEXT FIELDS
    # ---------------------------
    @field_validator("title", "description")
    def clean_text(cls, v: Optional[str]):
        """Remove excessive whitespace and normalize text."""
        if not v:
            return v
        return re.sub(r"\s+", " ", v.strip())

    @field_validator("category")
    def normalize_category(cls, v: str):
        return v.strip().lower()


# -------------------------------------------------------
# Article Create Model
# -------------------------------------------------------
class ArticleCreate(ArticleBase):
    """Model for creating new articles with deduplication hashing."""

    def generate_content_hash(self) -> str:
        canonical_title = self.title.lower().strip()
        canonical_source = self.source.lower().strip()
        canonical_date = self.published_at.strftime("%Y-%m-%d")

        hash_input = f"{canonical_title}|{canonical_source}|{canonical_date}"
        return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


# -------------------------------------------------------
# Article Stored in DB
# -------------------------------------------------------
class ArticleInDB(ArticleBase):
    """Internal representation of article stored in MongoDB."""

    content_hash: str = Field(..., min_length=64, max_length=64)
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    view_count: int = 0
    click_count: int = 0
    
    # --- AI FIELDS (Stored in DB) ---
    summary: Optional[str] = None
    sentiment: Optional[str] = None  # "Bullish", "Bearish", "Neutral"
    key_points: List[str] = Field(default_factory=list)
    ai_processed: bool = False

    @classmethod
    def from_create(cls, article: ArticleCreate) -> "ArticleInDB":
        return cls(
            **article.model_dump(),
            content_hash=article.generate_content_hash()
        )

    def to_dict(self) -> dict:
        data = self.model_dump()
        if data.get("url"):
            data["url"] = str(data["url"])
        if data.get("image_url"):
            data["image_url"] = str(data["image_url"])
        return data


# -------------------------------------------------------
# Article Response for API
# -------------------------------------------------------
class ArticleResponse(ArticleBase):
    id: str = Field(..., alias="_id")
    fetched_at: datetime
    view_count: int = 0
    click_count: int = 0

    # --- AI FIELDS (Sent to Frontend) ---
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    key_points: List[str] = Field(default_factory=list)
    ai_processed: bool = False

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


# -------------------------------------------------------
# Paginated Feed Response
# -------------------------------------------------------
class ArticlesFeedResponse(BaseModel):
    articles: List[ArticleResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


# -------------------------------------------------------
# Article Analytics
# -------------------------------------------------------
class ArticleAnalytics(BaseModel):
    user_id: str
    article_id: str
    event_type: str  # view, click, share, bookmark
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict] = None

    def to_dict(self):
        return self.model_dump()


# -------------------------------------------------------
# Feed Query Parameters
# -------------------------------------------------------
class FeedQuery(BaseModel):
    categories: Optional[List[str]] = None
    sources: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    exclude_keywords: Optional[List[str]] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    sort_by: str = Field(
        default="published_at",
        pattern=r"^(published_at|view_count|click_count)$"
    )

    sort_order: str = Field(
        default="desc",
        pattern=r"^(asc|desc)$"
    )

    @field_validator("categories", "sources", "keywords", "exclude_keywords")
    @classmethod
    def normalize_filter_lists(cls, v):
        if not v:
            return v
        return [item.strip().lower() for item in v if item.strip()]