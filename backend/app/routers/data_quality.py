from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app.models.data_quality import DataQualityTask, DataQualityStatus, DataQualityValidation
from app.models.customer import Customer

router = APIRouter()


class DataQualityTaskCreate(BaseModel):
    task_type: str
    extracted_customer: str
    amount: Optional[int] = None
    sale_date: Optional[datetime] = None
    source_document: Optional[str] = None

    class Config:
        from_attributes = True


class DataQualityTaskUpdate(BaseModel):
    corrected_customer: Optional[str] = None
    corrected_product: Optional[str] = None
    corrected_vendor: Optional[str] = None
    status: Optional[str] = None
    validation_notes: Optional[str] = None
    sales_notes: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/tasks")
def list_data_quality_tasks(
    status: DataQualityStatus | None = None,
    customer_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(DataQualityTask)

    if status:
        query = query.filter(DataQualityTask.status == status)
    if customer_id:
        query = query.filter(DataQualityTask.customer_id == customer_id)

    total = query.count()
    tasks = query.order_by(desc(DataQualityTask.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "tasks": [
            {
                "id": t.id,
                "customer_id": t.customer_id,
                "task_type": t.task_type,
                "extracted_customer": t.extracted_customer,
                "corrected_customer": t.corrected_customer,
                "extracted_product": t.extracted_product,
                "corrected_product": t.corrected_product,
                "amount": t.amount,
                "sale_date": t.sale_date,
                "status": t.status,
                "created_at": t.created_at,
                "source_document": t.source_document,
            }
            for t in tasks
        ]
    }


@router.post("/tasks")
def create_data_quality_task(
    task: DataQualityTaskCreate,
    customer_id: int,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    new_task = DataQualityTask(
        customer_id=customer_id,
        task_type=task.task_type,
        extracted_customer=task.extracted_customer,
        amount=task.amount,
        sale_date=task.sale_date,
        source_document=task.source_document,
        status=DataQualityStatus.TO_VALIDATE
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {
        "id": new_task.id,
        "customer_id": new_task.customer_id,
        "task_type": new_task.task_type,
        "status": new_task.status,
        "created_at": new_task.created_at
    }


@router.get("/tasks/{task_id}")
def get_data_quality_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(DataQualityTask).filter(DataQualityTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": task.id,
        "customer_id": task.customer_id,
        "task_type": task.task_type,
        "extracted_customer": task.extracted_customer,
        "corrected_customer": task.corrected_customer,
        "extracted_product": task.extracted_product,
        "corrected_product": task.corrected_product,
        "extracted_vendor": task.extracted_vendor,
        "corrected_vendor": task.corrected_vendor,
        "amount": task.amount,
        "sale_date": task.sale_date,
        "contract_expiry_date": task.contract_expiry_date,
        "status": task.status,
        "validation_notes": task.validation_notes,
        "sales_notes": task.sales_notes,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


@router.put("/tasks/{task_id}")
def update_data_quality_task(
    task_id: int,
    update: DataQualityTaskUpdate,
    db: Session = Depends(get_db)
):
    task = db.query(DataQualityTask).filter(DataQualityTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if update.corrected_customer:
        task.corrected_customer = update.corrected_customer
    if update.corrected_product:
        task.corrected_product = update.corrected_product
    if update.corrected_vendor:
        task.corrected_vendor = update.corrected_vendor
    if update.status:
        task.status = update.status
    if update.validation_notes:
        task.validation_notes = update.validation_notes
    if update.sales_notes:
        task.sales_notes = update.sales_notes

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    return {
        "id": task.id,
        "status": task.status,
        "updated_at": task.updated_at
    }


@router.get("/dashboard/stats")
def get_data_quality_stats(db: Session = Depends(get_db)):
    total = db.query(DataQualityTask).count()
    to_validate = db.query(DataQualityTask).filter(
        DataQualityTask.status == DataQualityStatus.TO_VALIDATE
    ).count()
    validated = db.query(DataQualityTask).filter(
        DataQualityTask.status == DataQualityStatus.VALIDATED
    ).count()
    doubtful = db.query(DataQualityTask).filter(
        DataQualityTask.status == DataQualityStatus.DOUBTFUL
    ).count()
    discarded = db.query(DataQualityTask).filter(
        DataQualityTask.status == DataQualityStatus.DISCARDED
    ).count()

    return {
        "total": total,
        "to_validate": to_validate,
        "validated": validated,
        "doubtful": doubtful,
        "discarded": discarded,
        "validation_rate": round((validated / total * 100) if total > 0 else 0, 2)
    }
