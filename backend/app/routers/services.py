from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.service import Service, ServiceCategory, ServiceLevel

router = APIRouter()


@router.get("")
def list_services(
    category_id: int | None = None,
    business_unit: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Service).filter(Service.is_active == True)

    if category_id:
        query = query.filter(Service.category_id == category_id)
    if business_unit:
        query = query.filter(Service.business_unit == business_unit)

    total = query.count()
    services = query.order_by(Service.name).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "services": [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category.name if s.category else None,
                "business_unit": s.business_unit,
                "billing_type": s.billing_type,
                "indicative_price": float(s.indicative_price) if s.indicative_price else None,
                "is_recommended": s.is_recommended,
            }
            for s in services
        ]
    }


@router.get("/{service_id}")
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    levels = db.query(ServiceLevel).filter(ServiceLevel.service_id == service_id).all()

    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "category": service.category.name if service.category else None,
        "business_unit": service.business_unit,
        "service_type": service.service_type,
        "billing_type": service.billing_type,
        "indicative_price": float(service.indicative_price) if service.indicative_price else None,
        "margin_expectation": service.margin_expectation,
        "is_recommended": service.is_recommended,
        "levels": [
            {
                "id": l.id,
                "name": l.name,
                "sla_response": l.sla_response,
                "sla_resolution": l.sla_resolution,
                "price": float(l.price) if l.price else None,
            }
            for l in levels
        ],
        "compatible_products": [
            {"id": p.id, "name": p.name, "sku": p.sku}
            for p in service.compatible_products
        ],
        "created_at": service.created_at,
    }


@router.post("")
def create_service(
    name: str,
    category_id: int,
    business_unit: str,
    db: Session = Depends(get_db)
):
    category = db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    new_service = Service(
        name=name,
        category_id=category_id,
        business_unit=business_unit,
        is_active=True
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return {
        "id": new_service.id,
        "name": new_service.name,
        "business_unit": new_service.business_unit,
        "created_at": new_service.created_at
    }


@router.get("/categories/list")
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(ServiceCategory).all()
    return [{"id": c.id, "name": c.name} for c in categories]
