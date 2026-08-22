from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class CompanyCluster(Base):
    __tablename__ = "company_clusters"

    company_id = Column(Integer, ForeignKey("companies.id"), primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relazioni
    company = relationship("Company", back_populates="clusters")
    cluster = relationship("Cluster", back_populates="companies")
