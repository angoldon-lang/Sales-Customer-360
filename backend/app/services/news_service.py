from sqlalchemy.orm import Session
from app.models.news import NewsItem, NewsStatus
from app.schemas.news import NewsItemCreate, NewsItemUpdate
from typing import List, Optional


class NewsService:
    """Service for news item CRUD operations."""

    @staticmethod
    def create_news(db: Session, news: NewsItemCreate) -> NewsItem:
        """Create a new news item."""
        db_news = NewsItem(
            company_id=news.company_id,
            title=news.title,
            source=news.source,
            url=news.url,
            summary=news.summary,
            category=news.category,
            relevance_score=news.relevance_score,
            urgency_score=news.urgency_score,
            commercial_score=news.commercial_score,
            risk_score=news.risk_score,
            confidence_score=news.confidence_score,
            published_date=news.published_date,
            status=NewsStatus.NEW.value,
        )
        db.add(db_news)
        db.commit()
        db.refresh(db_news)
        return db_news

    @staticmethod
    def get_news(db: Session, news_id: int) -> Optional[NewsItem]:
        """Get news item by ID."""
        return db.query(NewsItem).filter(NewsItem.id == news_id).first()

    @staticmethod
    def get_news_by_url(db: Session, url: str) -> Optional[NewsItem]:
        """Get news item by URL (for deduplication)."""
        return db.query(NewsItem).filter(NewsItem.url == url).first()

    @staticmethod
    def get_news_for_company(
        db: Session,
        company_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[NewsItem]:
        """Get news items for a company."""
        query = db.query(NewsItem).filter(NewsItem.company_id == company_id)
        if status:
            query = query.filter(NewsItem.status == status)
        return query.order_by(NewsItem.published_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_news_by_status(
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[NewsItem]:
        """Get news items by status."""
        return (
            db.query(NewsItem)
            .filter(NewsItem.status == status)
            .order_by(NewsItem.published_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_news(db: Session, news_id: int, news_update: NewsItemUpdate) -> Optional[NewsItem]:
        """Update a news item."""
        db_news = db.query(NewsItem).filter(NewsItem.id == news_id).first()
        if not db_news:
            return None

        update_data = news_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_news, field, value)

        db.commit()
        db.refresh(db_news)
        return db_news

    @staticmethod
    def approve_news(db: Session, news_id: int) -> Optional[NewsItem]:
        """Approve a news item."""
        return NewsService.update_news(db, news_id, NewsItemUpdate(status=NewsStatus.APPROVED.value))

    @staticmethod
    def reject_news(db: Session, news_id: int) -> Optional[NewsItem]:
        """Reject a news item."""
        return NewsService.update_news(db, news_id, NewsItemUpdate(status=NewsStatus.REJECTED.value))

    @staticmethod
    def delete_news(db: Session, news_id: int) -> bool:
        """Delete a news item."""
        db_news = db.query(NewsItem).filter(NewsItem.id == news_id).first()
        if not db_news:
            return False
        db.delete(db_news)
        db.commit()
        return True
