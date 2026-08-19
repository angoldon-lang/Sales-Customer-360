from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class OpportunityStatus(str, enum.Enum):
    NEW = "new"
    EVALUATING = "evaluating"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ALREADY_COVERED = "already_covered"
    POSTPONED = "postponed"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    account_owner_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String(255), nullable=False)
    description = Column(Text)

    trigger = Column(String(255))
    motivation = Column(Text)

    priority = Column(String(50), default="medium")
    status = Column(
        Enum(OpportunityStatus, name="opportunity_status"),
        default=OpportunityStatus.NEW,
        index=True
    )

    estimated_value = Column(Numeric(12, 2))
    estimated_margin = Column(Integer)

    notes = Column(Text)
    metadata = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="opportunities")
    product = relationship("Product")
    service = relationship("Service", back_populates="opportunities")
    account_owner = relationship("User", foreign_keys=[account_owner_id])
