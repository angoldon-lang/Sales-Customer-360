from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.data_importer import DataImportService
from app.auth import get_current_user_optional
from app.models.user import User

router = APIRouter()


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
