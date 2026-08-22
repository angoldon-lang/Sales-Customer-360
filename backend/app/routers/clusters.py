from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.cluster_service import ClusterService
from app.schemas.cluster import ClusterCreate, ClusterUpdate, ClusterResponse, ClusterRecipientCreate
from typing import List

router = APIRouter()


@router.post("/", response_model=ClusterResponse)
def create_cluster(cluster: ClusterCreate, db: Session = Depends(get_db)):
    """Create a new cluster."""
    db_cluster = ClusterService.create_cluster(db, cluster)
    return db_cluster


@router.get("/", response_model=List[ClusterResponse])
def list_clusters(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all clusters."""
    clusters = ClusterService.get_clusters(db, skip=skip, limit=limit)
    return clusters


@router.get("/{cluster_id}", response_model=ClusterResponse)
def get_cluster(cluster_id: int, db: Session = Depends(get_db)):
    """Get a specific cluster."""
    cluster = ClusterService.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster


@router.put("/{cluster_id}", response_model=ClusterResponse)
def update_cluster(
    cluster_id: int,
    cluster_update: ClusterUpdate,
    db: Session = Depends(get_db),
):
    """Update a cluster."""
    cluster = ClusterService.update_cluster(db, cluster_id, cluster_update)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster


@router.delete("/{cluster_id}")
def delete_cluster(cluster_id: int, db: Session = Depends(get_db)):
    """Delete a cluster."""
    success = ClusterService.delete_cluster(db, cluster_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return {"status": "deleted"}


@router.post("/{cluster_id}/companies/{company_id}")
def add_company_to_cluster(
    cluster_id: int,
    company_id: int,
    db: Session = Depends(get_db),
):
    """Add company to cluster."""
    success = ClusterService.add_company_to_cluster(db, company_id, cluster_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add company to cluster")
    return {"status": "added"}


@router.delete("/{cluster_id}/companies/{company_id}")
def remove_company_from_cluster(
    cluster_id: int,
    company_id: int,
    db: Session = Depends(get_db),
):
    """Remove company from cluster."""
    success = ClusterService.remove_company_from_cluster(db, company_id, cluster_id)
    if not success:
        raise HTTPException(status_code=404, detail="Company not in cluster")
    return {"status": "removed"}


@router.post("/{cluster_id}/recipients", response_model=dict)
def add_recipient(
    cluster_id: int,
    recipient: ClusterRecipientCreate,
    db: Session = Depends(get_db),
):
    """Add recipient to cluster."""
    db_recipient = ClusterService.add_recipient(db, cluster_id, recipient)
    if not db_recipient:
        raise HTTPException(status_code=400, detail="Failed to add recipient")
    return {"status": "added", "recipient_id": db_recipient.id}


@router.delete("/{cluster_id}/recipients/{recipient_id}")
def remove_recipient(
    cluster_id: int,
    recipient_id: int,
    db: Session = Depends(get_db),
):
    """Remove recipient from cluster."""
    success = ClusterService.remove_recipient(db, recipient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return {"status": "removed"}
