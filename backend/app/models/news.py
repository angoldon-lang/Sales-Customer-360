from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class NewsCategory(str, enum.Enum):
    INVESTMENT = "investment"
    ACQUISITION = "acquisition"
    MERGER = "merger"
    PARTNERSHIP = "partnership"
    NEW_OFFICE = "new_office"
    INDUSTRIAL_PLAN = "industrial_plan"
    FINANCIAL_RESULTS = "financial_results"
    CRISIS = "crisis"
    MANAGEMENT_CHANGE = "management_change"
    CYBER_INCIDENT = "cyber_incident"
    DATA_BREACH = "data_breach"
    OPERATIONAL_ISSUE = "operational_issue"
    TENDER = "tender"
    DIGITAL_PROJECT = "digital_project"
    OTHER = "other"


class NewsStatus(str, enum.Enum):
    NEW = "new"
    APPROVED = "approved"
    REJECTED = "rejected"
    DUPLICATE = "duplicate"
    NEEDS_REVIEW = "needs_review"
    SENT = "sent"


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    source = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False, unique=True, index=True)
    published_date = Column(DateTime, nullable=True, index=True)
    summary = Column(Text, nullable=True)
    category = Column(SQLEnum(NewsCategory), default=NewsCategory.OTHER)

    # Scoring (1-10)
    relevance_score = Column(Integer, default=5)
    urgency_score = Column(Integer, default=5)
    commercial_score = Column(Integer, default=5)
    risk_score = Column(Integer, default=5)
    confidence_score = Column(Integer, default=5)

    status = Column(SQLEnum(NewsStatus), default=NewsStatus.NEW, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relazioni
    company = relationship("Company", back_populates="news_items")
