from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversion import ConversionRule, ConversionLog
from app.services.conversion_engine import ConversionEngineService

router = APIRouter()


@router.get("/rules")
def list_conversion_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ConversionRule).filter(ConversionRule.is_active == True)
    total = query.count()
    rules = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "trigger_product_id": r.trigger_product_id,
                "recommended_service_id": r.recommended_service_id,
                "priority": r.priority,
                "months_lookback": r.months_lookback,
                "requires_no_service": r.requires_no_service,
                "is_active": r.is_active,
                "created_at": r.created_at,
            }
            for r in rules
        ]
    }


@router.post("/rules")
def create_conversion_rule(
    name: str,
    description: str,
    trigger_product_id: int,
    recommended_service_id: int,
    priority: str = "medium",
    months_lookback: int = 36,
    requires_no_service: bool = True,
    db: Session = Depends(get_db)
):
    result = ConversionEngineService.create_rule(
        db=db,
        name=name,
        description=description,
        trigger_product_id=trigger_product_id,
        recommended_service_id=recommended_service_id,
        priority=priority,
        months_lookback=months_lookback,
        requires_no_service=requires_no_service
    )
    return result


@router.get("/rules/{rule_id}")
def get_conversion_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(ConversionRule).filter(ConversionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    return {
        "id": rule.id,
        "name": rule.name,
        "description": rule.description,
        "trigger_product_id": rule.trigger_product_id,
        "recommended_service_id": rule.recommended_service_id,
        "priority": rule.priority,
        "months_lookback": rule.months_lookback,
        "requires_no_service": rule.requires_no_service,
        "is_active": rule.is_active,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at,
    }


@router.post("/run")
def run_conversion_engine(
    customer_id: int | None = None,
    db: Session = Depends(get_db)
):
    result = ConversionEngineService.run_conversion_engine(
        db=db,
        customer_id=customer_id
    )
    return result


@router.get("/stats")
def get_conversion_stats(db: Session = Depends(get_db)):
    stats = ConversionEngineService.get_conversion_stats(db)
    return stats


@router.get("/logs")
def list_conversion_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    customer_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(ConversionLog)

    if customer_id:
        query = query.filter(ConversionLog.customer_id == customer_id)

    total = query.count()
    logs = query.order_by(ConversionLog.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": [
            {
                "id": l.id,
                "rule_id": l.rule_id,
                "customer_id": l.customer_id,
                "opportunity_id": l.opportunity_id,
                "trigger_product_name": l.trigger_product_name,
                "status": l.status,
                "created_at": l.created_at,
            }
            for l in logs
        ]
    }
