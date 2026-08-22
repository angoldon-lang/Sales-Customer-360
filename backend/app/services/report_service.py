from sqlalchemy.orm import Session
from app.models.report import Report, ReportStatus
from app.models.news import NewsItem
from app.schemas.report import ReportCreate, ReportUpdate
from typing import List, Optional


class ReportService:
    """Service for report CRUD operations."""

    @staticmethod
    def create_report(db: Session, report: ReportCreate) -> Report:
        """Create a new report."""
        db_report = Report(
            cluster_id=report.cluster_id,
            subject=report.subject,
            body_html=report.body_html,
            body_text=report.body_text,
            status=report.status,
            period_start=report.period_start,
            period_end=report.period_end,
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report

    @staticmethod
    def get_report(db: Session, report_id: int) -> Optional[Report]:
        """Get report by ID."""
        return db.query(Report).filter(Report.id == report_id).first()

    @staticmethod
    def get_reports_for_cluster(
        db: Session,
        cluster_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Report]:
        """Get reports for a cluster."""
        query = db.query(Report).filter(Report.cluster_id == cluster_id)
        if status:
            query = query.filter(Report.status == status)
        return query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_report(db: Session, report_id: int, report_update: ReportUpdate) -> Optional[Report]:
        """Update a report."""
        db_report = db.query(Report).filter(Report.id == report_id).first()
        if not db_report:
            return None

        update_data = report_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_report, field, value)

        db.commit()
        db.refresh(db_report)
        return db_report

    @staticmethod
    def mark_sent(db: Session, report_id: int) -> Optional[Report]:
        """Mark report as sent."""
        from datetime import datetime
        return ReportService.update_report(
            db, report_id, ReportUpdate(status=ReportStatus.SENT.value, sent_at=datetime.utcnow())
        )

    @staticmethod
    def delete_report(db: Session, report_id: int) -> bool:
        """Delete a report."""
        db_report = db.query(Report).filter(Report.id == report_id).first()
        if not db_report:
            return False
        db.delete(db_report)
        db.commit()
        return True
