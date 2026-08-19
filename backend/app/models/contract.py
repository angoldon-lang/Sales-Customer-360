from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"))

    contract_number = Column(String(100), unique=True, index=True)
    description = Column(Text)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    renewal_date = Column(DateTime, index=True)

    annual_value = Column(Numeric(12, 2))
    payment_frequency = Column(String(50))

    status = Column(String(50), default="active")
    is_auto_renewal = Column(Boolean, default=False)

    vendor_contact = Column(String(255))
    notes = Column(Text)
    metadata = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="contracts")
    product = relationship("Product", back_populates="contracts")
    service = relationship("Service")
    renewals = relationship("ContractRenewal", back_populates="contract", cascade="all, delete-orphan")


class ContractRenewal(Base):
    __tablename__ = "contract_renewals"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)

    renewal_date = Column(DateTime, nullable=False, index=True)
    status = Column(String(50), default="pending")

    new_value = Column(Numeric(12, 2))
    renewal_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contract = relationship("Contract", back_populates="renewals")
