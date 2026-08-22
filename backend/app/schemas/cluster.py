from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ClusterRecipientBase(BaseModel):
    email: str
    name: Optional[str] = None
    active: bool = True


class ClusterRecipientCreate(ClusterRecipientBase):
    pass


class ClusterRecipientResponse(ClusterRecipientBase):
    id: int
    cluster_id: int

    class Config:
        from_attributes = True


class ClusterBase(BaseModel):
    cluster_name: str
    description: Optional[str] = None
    frequency: str = "weekly"
    min_relevance_score: int = 5
    report_type: str = "complete"
    topics: Optional[str] = None


class ClusterCreate(ClusterBase):
    recipients: Optional[List[ClusterRecipientCreate]] = []


class ClusterUpdate(BaseModel):
    cluster_name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[str] = None
    min_relevance_score: Optional[int] = None
    report_type: Optional[str] = None
    topics: Optional[str] = None


class ClusterResponse(ClusterBase):
    id: int
    recipients: List[ClusterRecipientResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
