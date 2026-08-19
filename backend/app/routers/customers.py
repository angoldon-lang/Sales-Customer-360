from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.customer import Customer, CustomerAccount

router = APIRouter()


@router.get("")
def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Customer)

    if search:
        query = query.filter(Customer.name.ilike(f"%{search}%"))

    total = query.count()
    customers = query.order_by(Customer.name).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "customers": [
            {
                "id": c.id,
                "name": c.name,
                "vat_number": c.vat_number,
                "industry": c.industry,
                "country": c.country,
                "status": c.status,
                "data_quality_score": c.data_quality_score,
                "created_at": c.created_at,
            }
            for c in customers
        ]
    }


@router.get("/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    accounts = db.query(CustomerAccount).filter(CustomerAccount.customer_id == customer_id).all()

    return {
        "id": customer.id,
        "name": customer.name,
        "legal_name": customer.legal_name,
        "vat_number": customer.vat_number,
        "industry": customer.industry,
        "country": customer.country,
        "city": customer.city,
        "status": customer.status,
        "data_quality_score": customer.data_quality_score,
        "accounts": [
            {
                "id": a.id,
                "name": a.name,
                "business_unit": a.business_unit,
                "annual_value": a.annual_value,
                "renewal_date": a.renewal_date,
            }
            for a in accounts
        ],
        "created_at": customer.created_at,
        "updated_at": customer.updated_at,
    }


@router.post("")
def create_customer(name: str, vat_number: str | None = None, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.vat_number == vat_number).first() if vat_number else None
    if existing:
        raise HTTPException(status_code=409, detail="Customer with this VAT already exists")

    new_customer = Customer(name=name, vat_number=vat_number, status="active")
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)

    return {
        "id": new_customer.id,
        "name": new_customer.name,
        "vat_number": new_customer.vat_number,
        "created_at": new_customer.created_at
    }
