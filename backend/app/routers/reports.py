from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.services.report_service import ReportService
from app.services.cluster_service import ClusterService
from app.services.news_service import NewsService
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse
from app.core.report_generator import ReportGenerator
from app.core.email_delivery import EmailDelivery
from typing import List

router = APIRouter()


@router.post("/", response_model=ReportResponse)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    """Create a new report."""
    db_report = ReportService.create_report(db, report)
    return db_report


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """Get a specific report."""
    report = ReportService.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/cluster/{cluster_id}", response_model=List[ReportResponse])
def get_reports_for_cluster(
    cluster_id: int,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get reports for a specific cluster."""
    reports = ReportService.get_reports_for_cluster(db, cluster_id, skip=skip, limit=limit, status=status)
    return reports


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    report_update: ReportUpdate,
    db: Session = Depends(get_db),
):
    """Update a report."""
    report = ReportService.update_report(db, report_id, report_update)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """Delete a report."""
    success = ReportService.delete_report(db, report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": "deleted"}


@router.post("/cluster/{cluster_id}/generate")
async def generate_report_for_cluster(
    cluster_id: int,
    days: int = 7,
    db: Session = Depends(get_db),
):
    """Generate a report for a cluster."""
    cluster = ClusterService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # Get period
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=days)

    # Get companies in cluster
    companies_in_cluster = [cc.company for cc in cluster.companies]
    company_ids = [c.id for c in companies_in_cluster]

    # Get approved news for these companies in the period
    news_items = db.query(NewsService).filter(
        NewsService.company_id.in_(company_ids),
        NewsService.published_date >= period_start,
        NewsService.status == "approved",
    ).all()

    # Generate report
    subject, body_html, body_text = ReportGenerator.generate_report(
        cluster,
        news_items,
        period_start,
        period_end,
    )

    # Create report
    from app.schemas.report import ReportCreate
    report_create = ReportCreate(
        cluster_id=cluster_id,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        status="draft",
        period_start=period_start,
        period_end=period_end,
    )
    db_report = ReportService.create_report(db, report_create)

    return {
        "report_id": db_report.id,
        "status": db_report.status,
        "subject": subject,
        "news_count": len(news_items),
    }


@router.post("/{report_id}/send")
async def send_report(report_id: int, db: Session = Depends(get_db)):
    """Send a report to cluster recipients."""
    report = ReportService.get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Get cluster recipients
    cluster = report.cluster
    active_recipients = [r.email for r in cluster.recipients if r.active]

    if not active_recipients:
        raise HTTPException(status_code=400, detail="No active recipients configured for this cluster")

    # Send email
    email_delivery = EmailDelivery()
    success = await email_delivery.send(
        active_recipients,
        report.subject,
        report.body_text,
        report.body_html,
    )

    if success:
        # Mark report as sent
        ReportService.mark_sent(db, report_id)
        return {"status": "sent"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send email")
