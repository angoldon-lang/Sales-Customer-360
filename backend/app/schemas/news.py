from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NewsItemBase(BaseModel):
    company_id: int
    title: str
    source: str
    url: str
    summary: Optional[str] = None
    category: str = "other"
    relevance_score: int = 5
    urgency_score: int = 5
    commercial_score: int = 5
    risk_score: int = 5
    confidence_score: int = 5
    published_date: Optional[datetime] = None


class NewsItemCreate(NewsItemBase):
    pass


class NewsItemUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    relevance_score: Optional[int] = None
    urgency_score: Optional[int] = None
    commercial_score: Optional[int] = None
    risk_score: Optional[int] = None
    confidence_score: Optional[int] = None
    status: Optional[str] = None


class NewsItemResponse(NewsItemBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
