from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    company_name: str
    vat_number: Optional[str] = None
    website: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    status: str = "active"


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    vat_number: Optional[str] = None
    website: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
