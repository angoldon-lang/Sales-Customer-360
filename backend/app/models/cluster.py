from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class ReportFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReportType(str, enum.Enum):
    SYNTHETIC = "synthetic"  # breve sintesi
    COMPLETE = "complete"  # report completo
    ALERT = "alert"  # solo alert


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    cluster_name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(1000), nullable=True)
    frequency = Column(SQLEnum(ReportFrequency), default=ReportFrequency.WEEKLY)
    min_relevance_score = Column(Integer, default=5)  # 1-10
    report_type = Column(SQLEnum(ReportType), default=ReportType.COMPLETE)
    topics = Column(String(500), nullable=True)  # comma-separated topics
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relazioni
    recipients = relationship(
        "ClusterRecipient",
        back_populates="cluster",
        cascade="all, delete-orphan",
        lazy="select",
    )
    companies = relationship(
        "CompanyCluster", back_populates="cluster", cascade="all, delete-orphan", lazy="select"
    )
    reports = relationship("Report", back_populates="cluster", cascade="all, delete-orphan", lazy="select")


class ClusterRecipient(Base):
    __tablename__ = "cluster_recipients"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relazioni
    cluster = relationship("Cluster", back_populates="recipients")
