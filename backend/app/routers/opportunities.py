from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.customer import Customer
from app.models.service import Service
from app.models.product import Product

router = APIRouter()


@router.get("")
def list_opportunities(
    customer_id: int | None = None,
    status: OpportunityStatus | None = None,
    priority: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity)

    if customer_id:
        query = query.filter(Opportunity.customer_id == customer_id)
    if status:
        query = query.filter(Opportunity.status == status)
    if priority:
        query = query.filter(Opportunity.priority == priority)

    total = query.count()
    opportunities = query.order_by(Opportunity.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "opportunities": [
            {
                "id": o.id,
                "customer_id": o.customer_id,
                "service_id": o.service_id,
                "title": o.title,
                "priority": o.priority,
                "status": o.status,
                "estimated_value": float(o.estimated_value) if o.estimated_value else None,
                "created_at": o.created_at,
            }
            for o in opportunities
        ]
    }


@router.get("/{opportunity_id}")
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    return {
        "id": opp.id,
        "customer_id": opp.customer_id,
        "product_id": opp.product_id,
        "service_id": opp.service_id,
        "title": opp.title,
        "description": opp.description,
        "trigger": opp.trigger,
        "motivation": opp.motivation,
        "priority": opp.priority,
        "status": opp.status,
        "estimated_value": float(opp.estimated_value) if opp.estimated_value else None,
        "estimated_margin": opp.estimated_margin,
        "notes": opp.notes,
        "created_at": opp.created_at,
        "updated_at": opp.updated_at,
    }


@router.post("")
def create_opportunity(
    customer_id: int,
    product_id: int,
    service_id: int,
    title: str,
    trigger: str,
    priority: str = "medium",
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    new_opp = Opportunity(
        customer_id=customer_id,
        product_id=product_id,
        service_id=service_id,
        title=title,
        trigger=trigger,
        priority=priority,
        status=OpportunityStatus.NEW
    )
    db.add(new_opp)
    db.commit()
    db.refresh(new_opp)

    return {
        "id": new_opp.id,
        "title": new_opp.title,
        "status": new_opp.status,
        "created_at": new_opp.created_at
    }


@router.put("/{opportunity_id}")
def update_opportunity_status(
    opportunity_id: int,
    status: OpportunityStatus,
    notes: str | None = None,
    db: Session = Depends(get_db)
):
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    opp.status = status
    if notes:
        opp.notes = notes

    db.commit()
    db.refresh(opp)

    return {"id": opp.id, "status": opp.status, "updated_at": opp.updated_at}
