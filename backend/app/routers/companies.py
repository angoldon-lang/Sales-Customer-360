from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.company_service import CompanyService
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from typing import List

router = APIRouter()


@router.post("/", response_model=CompanyResponse)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company."""
    db_company = CompanyService.create_company(db, company)
    return db_company


@router.get("/", response_model=List[CompanyResponse])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
):
    """List all companies."""
    companies = CompanyService.get_companies(db, skip=skip, limit=limit, status=status)
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get a specific company."""
    company = CompanyService.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db),
):
    """Update a company."""
    company = CompanyService.update_company(db, company_id, company_update)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete a company."""
    success = CompanyService.delete_company(db, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"status": "deleted"}
