from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReportBase(BaseModel):
    cluster_id: int
    subject: str
    body_html: str
    body_text: str
    status: str = "draft"
    period_start: datetime
    period_end: datetime


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    status: Optional[str] = None
    sent_at: Optional[datetime] = None


class ReportResponse(ReportBase):
    id: int
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
