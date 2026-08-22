from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.importer import CompanyImporter, CompanyImportError
from app.services.company_service import CompanyService
from app.services.cluster_service import ClusterService
from app.schemas.company import CompanyResponse
from typing import List

router = APIRouter()


@router.post("/companies/csv", response_model=dict)
async def import_companies_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Import companies from CSV file."""
    try:
        content = await file.read()
        companies_data = CompanyImporter.import_from_csv(content)
    except CompanyImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    imported = []
    failed = []

    for company_data in companies_data:
        try:
            # Check if company already exists
            existing = CompanyService.get_company_by_name(db, company_data["company_name"])
            if existing:
                failed.append(
                    {
                        "company_name": company_data["company_name"],
                        "error": "Company already exists",
                    }
                )
                continue

            # Create company
            from app.schemas.company import CompanyCreate
            company_create = CompanyCreate(
                company_name=company_data["company_name"],
                vat_number=company_data.get("vat_number"),
                status="needs_review" if not company_data.get("vat_number") else "active",
            )
            db_company = CompanyService.create_company(db, company_create)

            # Handle clusters
            clusters_str = company_data.get("cluster", "Default")
            if clusters_str:
                cluster_names = [c.strip() for c in clusters_str.split(",")]
                for cluster_name in cluster_names:
                    if cluster_name:
                        # Get or create cluster
                        cluster = ClusterService.get_cluster_by_name(db, cluster_name)
                        if not cluster:
                            from app.schemas.cluster import ClusterCreate
                            cluster_create = ClusterCreate(cluster_name=cluster_name)
                            cluster = ClusterService.create_cluster(db, cluster_create)

                        # Associate company with cluster
                        ClusterService.add_company_to_cluster(db, db_company.id, cluster.id)

            imported.append(
                {
                    "id": db_company.id,
                    "company_name": db_company.company_name,
                    "vat_number": db_company.vat_number,
                }
            )

        except Exception as e:
            failed.append(
                {
                    "company_name": company_data.get("company_name"),
                    "error": str(e),
                }
            )

    return {
        "imported": len(imported),
        "failed": len(failed),
        "companies": imported,
        "errors": failed if failed else None,
    }


@router.post("/companies/excel", response_model=dict)
async def import_companies_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Import companies from Excel file."""
    try:
        content = await file.read()
        companies_data = CompanyImporter.import_from_excel(content)
    except CompanyImportError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    # Reuse CSV import logic
    imported = []
    failed = []

    for company_data in companies_data:
        try:
            existing = CompanyService.get_company_by_name(db, company_data["company_name"])
            if existing:
                failed.append(
                    {
                        "company_name": company_data["company_name"],
                        "error": "Company already exists",
                    }
                )
                continue

            from app.schemas.company import CompanyCreate
            company_create = CompanyCreate(
                company_name=company_data["company_name"],
                vat_number=company_data.get("vat_number"),
                status="needs_review" if not company_data.get("vat_number") else "active",
            )
            db_company = CompanyService.create_company(db, company_create)

            clusters_str = company_data.get("cluster", "Default")
            if clusters_str:
                cluster_names = [c.strip() for c in clusters_str.split(",")]
                for cluster_name in cluster_names:
                    if cluster_name:
                        cluster = ClusterService.get_cluster_by_name(db, cluster_name)
                        if not cluster:
                            from app.schemas.cluster import ClusterCreate
                            cluster_create = ClusterCreate(cluster_name=cluster_name)
                            cluster = ClusterService.create_cluster(db, cluster_create)

                        ClusterService.add_company_to_cluster(db, db_company.id, cluster.id)

            imported.append(
                {
                    "id": db_company.id,
                    "company_name": db_company.company_name,
                    "vat_number": db_company.vat_number,
                }
            )

        except Exception as e:
            failed.append(
                {
                    "company_name": company_data.get("company_name"),
                    "error": str(e),
                }
            )

    return {
        "imported": len(imported),
        "failed": len(failed),
        "companies": imported,
        "errors": failed if failed else None,
    }
