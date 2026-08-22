from sqlalchemy import Column, Integer, DateTime, Enum as SQLEnum, Text, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class ReportStatus(str, enum.Enum):
    DRAFT = "draft"
    READY = "ready"
    SENT = "sent"
    FAILED = "failed"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=False)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.DRAFT, index=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relazioni
    cluster = relationship("Cluster", back_populates="reports")
