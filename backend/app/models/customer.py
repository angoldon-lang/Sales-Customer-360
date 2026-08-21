from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255))
    vat_number = Column(String(50), unique=True, index=True)
    registration_number = Column(String(100), unique=True)

    industry = Column(String(100))
    sector = Column(String(100))
    country = Column(String(100))
    region = Column(String(100))
    city = Column(String(100))

    annual_revenue = Column(Integer)
    employee_count = Column(Integer)

    status = Column(String(50), default="active")
    data_quality_score = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contacts = relationship("CustomerContact", back_populates="customer", cascade="all, delete-orphan")
    accounts = relationship("CustomerAccount", back_populates="customer", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="customer")
    opportunities = relationship("Opportunity", back_populates="customer")
    data_quality_tasks = relationship("DataQualityTask", back_populates="customer")


class CustomerContact(Base):
    __tablename__ = "customer_contacts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    title = Column(String(100))
    email = Column(String(255), index=True)
    phone = Column(String(20))
    department = Column(String(100))
    is_primary = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="contacts")


class CustomerAccount(Base):
    __tablename__ = "customer_accounts"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    name = Column(String(255), nullable=False)
    account_owner_id = Column(Integer, ForeignKey("users.id"))
    co_owner_id = Column(Integer, ForeignKey("users.id"))

    business_unit = Column(String(100))
    team = Column(String(100))

    annual_value = Column(Integer, default=0)
    pipeline_value = Column(Integer, default=0)

    renewal_date = Column(DateTime)
    last_review_date = Column(DateTime)

    notes = Column(Text)
    custom_metadata = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="accounts")
    account_owner = relationship("User", foreign_keys=[account_owner_id])
    co_owner = relationship("User", foreign_keys=[co_owner_id])
