from sqlalchemy.orm import Session
from app.models.cluster import Cluster, ClusterRecipient
from app.models.company_cluster import CompanyCluster
from app.schemas.cluster import ClusterCreate, ClusterUpdate, ClusterRecipientCreate
from typing import List, Optional


class ClusterService:
    """Service for cluster CRUD operations."""

    @staticmethod
    def create_cluster(db: Session, cluster: ClusterCreate) -> Cluster:
        """Create a new cluster."""
        db_cluster = Cluster(
            cluster_name=cluster.cluster_name,
            description=cluster.description,
            frequency=cluster.frequency,
            min_relevance_score=cluster.min_relevance_score,
            report_type=cluster.report_type,
            topics=cluster.topics,
        )
        db.add(db_cluster)
        db.flush()

        # Add recipients
        for recipient in cluster.recipients or []:
            db_recipient = ClusterRecipient(
                cluster_id=db_cluster.id,
                email=recipient.email,
                name=recipient.name,
                active=recipient.active,
            )
            db.add(db_recipient)

        db.commit()
        db.refresh(db_cluster)
        return db_cluster

    @staticmethod
    def get_cluster(db: Session, cluster_id: int) -> Optional[Cluster]:
        """Get cluster by ID."""
        return db.query(Cluster).filter(Cluster.id == cluster_id).first()

    @staticmethod
    def get_cluster_by_name(db: Session, name: str) -> Optional[Cluster]:
        """Get cluster by name."""
        return db.query(Cluster).filter(Cluster.cluster_name == name).first()

    @staticmethod
    def get_clusters(db: Session, skip: int = 0, limit: int = 100) -> List[Cluster]:
        """Get all clusters."""
        return db.query(Cluster).offset(skip).limit(limit).all()

    @staticmethod
    def update_cluster(db: Session, cluster_id: int, cluster_update: ClusterUpdate) -> Optional[Cluster]:
        """Update a cluster."""
        db_cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
        if not db_cluster:
            return None

        update_data = cluster_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cluster, field, value)

        db.commit()
        db.refresh(db_cluster)
        return db_cluster

    @staticmethod
    def delete_cluster(db: Session, cluster_id: int) -> bool:
        """Delete a cluster."""
        db_cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
        if not db_cluster:
            return False
        db.delete(db_cluster)
        db.commit()
        return True

    @staticmethod
    def add_company_to_cluster(db: Session, company_id: int, cluster_id: int) -> bool:
        """Add company to cluster."""
        # Check if already exists
        existing = db.query(CompanyCluster).filter(
            CompanyCluster.company_id == company_id,
            CompanyCluster.cluster_id == cluster_id,
        ).first()

        if existing:
            return True

        db_association = CompanyCluster(company_id=company_id, cluster_id=cluster_id)
        db.add(db_association)
        db.commit()
        return True

    @staticmethod
    def remove_company_from_cluster(db: Session, company_id: int, cluster_id: int) -> bool:
        """Remove company from cluster."""
        db_association = db.query(CompanyCluster).filter(
            CompanyCluster.company_id == company_id,
            CompanyCluster.cluster_id == cluster_id,
        ).first()

        if not db_association:
            return False

        db.delete(db_association)
        db.commit()
        return True

    @staticmethod
    def add_recipient(db: Session, cluster_id: int, recipient: ClusterRecipientCreate) -> Optional[ClusterRecipient]:
        """Add recipient to cluster."""
        db_recipient = ClusterRecipient(
            cluster_id=cluster_id,
            email=recipient.email,
            name=recipient.name,
            active=recipient.active,
        )
        db.add(db_recipient)
        db.commit()
        db.refresh(db_recipient)
        return db_recipient

    @staticmethod
    def remove_recipient(db: Session, recipient_id: int) -> bool:
        """Remove recipient from cluster."""
        db_recipient = db.query(ClusterRecipient).filter(ClusterRecipient.id == recipient_id).first()
        if not db_recipient:
            return False
        db.delete(db_recipient)
        db.commit()
        return True
