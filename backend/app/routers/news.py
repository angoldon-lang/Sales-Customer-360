from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.news_service import NewsService
from app.schemas.news import NewsItemCreate, NewsItemUpdate, NewsItemResponse
from typing import List

router = APIRouter()


@router.post("/", response_model=NewsItemResponse)
def create_news(news: NewsItemCreate, db: Session = Depends(get_db)):
    """Create a new news item."""
    db_news = NewsService.create_news(db, news)
    return db_news


@router.get("/{news_id}", response_model=NewsItemResponse)
def get_news(news_id: int, db: Session = Depends(get_db)):
    """Get a specific news item."""
    news = NewsService.get_news(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return news


@router.get("/company/{company_id}", response_model=List[NewsItemResponse])
def get_news_for_company(
    company_id: int,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get news items for a specific company."""
    news_items = NewsService.get_news_for_company(db, company_id, status=status, skip=skip, limit=limit)
    return news_items


@router.get("/status/{status}", response_model=List[NewsItemResponse])
def get_news_by_status(
    status: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get news items by status."""
    news_items = NewsService.get_news_by_status(db, status, skip=skip, limit=limit)
    return news_items


@router.put("/{news_id}", response_model=NewsItemResponse)
def update_news(
    news_id: int,
    news_update: NewsItemUpdate,
    db: Session = Depends(get_db),
):
    """Update a news item."""
    news = NewsService.update_news(db, news_id, news_update)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return news


@router.post("/{news_id}/approve")
def approve_news(news_id: int, db: Session = Depends(get_db)):
    """Approve a news item."""
    news = NewsService.approve_news(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return {"status": "approved"}


@router.post("/{news_id}/reject")
def reject_news(news_id: int, db: Session = Depends(get_db)):
    """Reject a news item."""
    news = NewsService.reject_news(db, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    return {"status": "rejected"}


@router.delete("/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db)):
    """Delete a news item."""
    success = NewsService.delete_news(db, news_id)
    if not success:
        raise HTTPException(status_code=404, detail="News item not found")
    return {"status": "deleted"}
