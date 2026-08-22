from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("data_quality_tasks.id"), nullable=True, index=True)

    feature = Column(String(100), nullable=False, default="data_extraction")
    model = Column(String(100), nullable=False)

    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_usd = Column(Numeric(10, 6), default=0)

    success = Column(Boolean, default=True)
    error_message = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    task = relationship("DataQualityTask")
