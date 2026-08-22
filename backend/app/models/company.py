from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class CompanyStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    NEEDS_REVIEW = "needs_review"
    ARCHIVED = "archived"


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    vat_number = Column(String(50), nullable=True, unique=True, index=True)
    website = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    status = Column(SQLEnum(CompanyStatus), default=CompanyStatus.ACTIVE, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relazioni
    clusters = relationship(
        "CompanyCluster",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )
    news_items = relationship(
        "NewsItem", back_populates="company", cascade="all, delete-orphan", lazy="select"
    )
