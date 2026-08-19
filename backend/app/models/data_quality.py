from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class DataQualityStatus(str, enum.Enum):
    TO_VALIDATE = "to_validate"
    VALIDATED = "validated"
    DOUBTFUL = "doubtful"
    DISCARDED = "discarded"


class DataQualityTask(Base):
    __tablename__ = "data_quality_tasks"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)

    task_type = Column(String(50), nullable=False)

    extracted_customer = Column(String(255))
    corrected_customer = Column(String(255))

    extracted_product = Column(String(255))
    corrected_product = Column(String(255))
    product_id = Column(Integer, ForeignKey("products.id"))

    extracted_vendor = Column(String(100))
    corrected_vendor = Column(String(100))
    vendor_id = Column(Integer, ForeignKey("product_vendors.id"))

    amount = Column(Integer)
    sale_date = Column(DateTime)
    contract_expiry_date = Column(DateTime)

    account_owner_id = Column(Integer, ForeignKey("users.id"))
    source_document = Column(String(255))
    source_document_url = Column(String(500))

    status = Column(
        Enum(DataQualityStatus, name="data_quality_status"),
        default=DataQualityStatus.TO_VALIDATE,
        index=True
    )

    validation_notes = Column(Text)
    sales_notes = Column(Text)

    validated_by_id = Column(Integer, ForeignKey("users.id"))
    validated_at = Column(DateTime)

    metadata = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="data_quality_tasks")
    product = relationship("Product")
    vendor = relationship("ProductVendor")
    account_owner = relationship("User", foreign_keys=[account_owner_id])
    validated_by = relationship("User", foreign_keys=[validated_by_id])
    validations = relationship("DataQualityValidation", back_populates="task", cascade="all, delete-orphan")


class DataQualityValidation(Base):
    __tablename__ = "data_quality_validations"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("data_quality_tasks.id"), nullable=False)

    field_name = Column(String(100), nullable=False)
    original_value = Column(Text)
    corrected_value = Column(Text)

    validation_rule = Column(String(255))
    is_valid = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("DataQualityTask", back_populates="validations")
