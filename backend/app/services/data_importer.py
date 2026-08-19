import csv
from io import StringIO, BytesIO
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.data_quality import DataQualityTask, DataQualityStatus
from app.models.customer import Customer


class DataImportService:
    """Service for importing data from Excel/CSV and creating data quality tasks."""

    @staticmethod
    def import_csv(
        csv_content: str,
        db: Session,
        delimiter: str = ",",
        skip_header: bool = True,
    ) -> dict:
        """
        Import CSV data and create data quality tasks.

        Expected CSV format:
        - customer_name: Extracted customer name
        - product: Extracted product name
        - vendor: Vendor/manufacturer
        - amount: Sale amount
        - sale_date: YYYY-MM-DD
        - contract_expiry: YYYY-MM-DD (optional)
        - source_document: Document reference
        """
        reader = csv.DictReader(StringIO(csv_content), delimiter=delimiter)
        if not reader:
            return {"error": "Invalid CSV format"}

        created_tasks = 0
        errors = []
        row_num = 2 if skip_header else 1

        for row in reader:
            try:
                customer_name = row.get("customer_name", "").strip()
                product = row.get("product", "").strip()
                vendor = row.get("vendor", "").strip()
                amount_str = row.get("amount", "").strip()
                sale_date_str = row.get("sale_date", "").strip()
                contract_expiry_str = row.get("contract_expiry", "").strip()
                source_doc = row.get("source_document", "").strip()

                if not customer_name or not product:
                    errors.append(f"Row {row_num}: Missing customer_name or product")
                    row_num += 1
                    continue

                amount = None
                if amount_str:
                    try:
                        amount = int(float(amount_str))
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid amount '{amount_str}'")

                sale_date = None
                if sale_date_str:
                    try:
                        sale_date = datetime.strptime(sale_date_str, "%Y-%m-%d")
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid sale_date '{sale_date_str}'")

                contract_expiry = None
                if contract_expiry_str:
                    try:
                        contract_expiry = datetime.strptime(contract_expiry_str, "%Y-%m-%d")
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid contract_expiry '{contract_expiry_str}'")

                task = DataQualityTask(
                    customer_id=None,
                    task_type="csv_import",
                    extracted_customer=customer_name,
                    extracted_product=product,
                    extracted_vendor=vendor if vendor else None,
                    amount=amount,
                    sale_date=sale_date,
                    contract_expiry_date=contract_expiry,
                    source_document=source_doc,
                    status=DataQualityStatus.TO_VALIDATE,
                )
                db.add(task)
                created_tasks += 1

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")

            row_num += 1

        db.commit()

        return {
            "created_tasks": created_tasks,
            "errors": errors,
            "total_rows_processed": row_num - 2 if skip_header else row_num - 1
        }

    @staticmethod
    def bulk_assign_customer(
        db: Session,
        task_ids: list[int],
        customer_id: int,
    ) -> dict:
        """Assign customer to multiple data quality tasks."""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"error": "Customer not found"}

        tasks = db.query(DataQualityTask).filter(DataQualityTask.id.in_(task_ids)).all()
        if not tasks:
            return {"error": "No tasks found"}

        updated_count = 0
        for task in tasks:
            if not task.customer_id:
                task.customer_id = customer_id
                updated_count += 1

        db.commit()

        return {
            "updated_count": updated_count,
            "total_tasks": len(tasks)
        }

    @staticmethod
    def suggest_customer_matches(
        db: Session,
        extracted_name: str,
        limit: int = 5,
    ) -> list[dict]:
        """
        Suggest customers matching extracted name using fuzzy matching.
        """
        from difflib import SequenceMatcher

        customers = db.query(Customer).filter(Customer.status == "active").all()

        matches = []
        for customer in customers:
            ratio = SequenceMatcher(None, extracted_name.lower(), customer.name.lower()).ratio()
            if ratio > 0.6:
                matches.append({
                    "customer_id": customer.id,
                    "customer_name": customer.name,
                    "vat_number": customer.vat_number,
                    "confidence": round(ratio * 100, 2)
                })

        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches[:limit]

    @staticmethod
    def get_import_stats(db: Session) -> dict:
        """Get statistics about data imports."""
        total_tasks = db.query(DataQualityTask).count()
        imported_tasks = db.query(DataQualityTask).filter(
            DataQualityTask.task_type == "csv_import"
        ).count()
        awaiting_customer_assignment = db.query(DataQualityTask).filter(
            DataQualityTask.customer_id == None
        ).count()

        return {
            "total_tasks": total_tasks,
            "imported_from_csv": imported_tasks,
            "awaiting_customer_assignment": awaiting_customer_assignment,
        }
