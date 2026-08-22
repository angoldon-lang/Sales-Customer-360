from sqlalchemy.orm import Session
from app.models.company import Company, CompanyStatus
from app.schemas.company import CompanyCreate, CompanyUpdate
from typing import List, Optional


class CompanyService:
    """Service for company CRUD operations."""

    @staticmethod
    def create_company(db: Session, company: CompanyCreate) -> Company:
        """Create a new company."""
        db_company = Company(
            company_name=company.company_name,
            vat_number=company.vat_number,
            website=company.website,
            sector=company.sector,
            country=company.country,
            status=company.status,
        )
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company

    @staticmethod
    def get_company(db: Session, company_id: int) -> Optional[Company]:
        """Get company by ID."""
        return db.query(Company).filter(Company.id == company_id).first()

    @staticmethod
    def get_company_by_name(db: Session, name: str) -> Optional[Company]:
        """Get company by name."""
        return db.query(Company).filter(Company.company_name == name).first()

    @staticmethod
    def get_companies(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Company]:
        """Get companies with optional filtering."""
        query = db.query(Company)
        if status:
            query = query.filter(Company.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_company(db: Session, company_id: int, company_update: CompanyUpdate) -> Optional[Company]:
        """Update a company."""
        db_company = db.query(Company).filter(Company.id == company_id).first()
        if not db_company:
            return None

        update_data = company_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_company, field, value)

        db.commit()
        db.refresh(db_company)
        return db_company

    @staticmethod
    def delete_company(db: Session, company_id: int) -> bool:
        """Delete a company."""
        db_company = db.query(Company).filter(Company.id == company_id).first()
        if not db_company:
            return False
        db.delete(db_company)
        db.commit()
        return True
