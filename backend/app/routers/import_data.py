from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.services.data_importer import DataImportService
from app.services import ai_extraction
from app.auth import get_current_user_optional
from app.models.user import User
from app.models.data_quality import DataQualityTask, DataQualityStatus

router = APIRouter()


class ExtractTextRequest(BaseModel):
    text: str
    source_document: str | None = None


@router.post("/csv")
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_optional),
):
    """Import CSV file and create data quality tasks."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        content = await file.read()
        csv_content = content.decode("utf-8")

        result = DataImportService.import_csv(csv_content, db)
        return result

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk-assign-customer")
def bulk_assign_customer(
    task_ids: list[int],
    customer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_optional),
):
    """Assign customer to multiple data quality tasks."""
    result = DataImportService.bulk_assign_customer(db, task_ids, customer_id)
    return result


@router.get("/suggest-customers")
def suggest_customers(
    extracted_name: str,
    limit: int = 5,
    db: Session = Depends(get_db),
):
    """Suggest customers matching extracted name."""
    matches = DataImportService.suggest_customer_matches(db, extracted_name, limit)
    return {"suggestions": matches}


@router.get("/stats")
def get_import_stats(db: Session = Depends(get_db)):
    """Get data import statistics."""
    stats = DataImportService.get_import_stats(db)
    return stats


@router.post("/extract-text")
def extract_text(
    request: ExtractTextRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_optional),
):
    """
    Accept any unstructured text (pasted email, note, scanned document text, etc.)
    and use Claude to extract structured sales data into a Data Quality task
    for manual validation.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")

    try:
        result = ai_extraction.extract_sales_data(request.text, db)
    except ai_extraction.AIExtractionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    extracted = result["extracted"]

    from datetime import datetime

    def _parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None

    task = DataQualityTask(
        customer_id=None,
        task_type="ai_extraction",
        extracted_customer=extracted.get("customer_name"),
        extracted_product=extracted.get("product_name"),
        extracted_vendor=extracted.get("vendor_name"),
        amount=int(extracted["amount"]) if extracted.get("amount") is not None else None,
        sale_date=_parse_date(extracted.get("sale_date")),
        contract_expiry_date=_parse_date(extracted.get("contract_expiry_date")),
        source_document=request.source_document,
        sales_notes=extracted.get("notes"),
        status=DataQualityStatus.TO_VALIDATE,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return {
        "task_id": task.id,
        "extracted": extracted,
        "usage": result["usage"],
    }


@router.get("/ai-usage/stats")
def get_ai_usage_stats(db: Session = Depends(get_db)):
    """Real-time AI extraction cost counter (today / this month / all-time)."""
    return ai_extraction.get_usage_stats(db)
