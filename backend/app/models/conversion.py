from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from datetime import datetime
from app.database import Base


class ConversionRule(Base):
    __tablename__ = "conversion_rules"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)

    trigger_product_id = Column(Integer, nullable=False, index=True)
    recommended_service_id = Column(Integer, nullable=False, index=True)

    months_lookback = Column(Integer, default=36)
    requires_no_service = Column(Boolean, default=True)

    priority = Column(String(50), default="medium")
    is_active = Column(Boolean, default=True)

    rule_config = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConversionLog(Base):
    __tablename__ = "conversion_logs"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, nullable=False, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    opportunity_id = Column(Integer, nullable=False, index=True)

    trigger_contract_id = Column(Integer)
    trigger_product_name = Column(String(255))

    status = Column(String(50), default="generated")

    created_at = Column(DateTime, default=datetime.utcnow)
