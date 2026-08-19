from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Numeric, Table, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# Association table for Service <-> Product mapping
service_product_association = Table(
    'service_product_association',
    Base.metadata,
    Column('service_id', Integer, ForeignKey('services.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True)
)


class ServiceCategory(Base):
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    services = relationship("Service", back_populates="category")


class ServiceLevel(Base):
    __tablename__ = "service_levels"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"))

    name = Column(String(50), nullable=False)
    sla_response = Column(String(50))
    sla_resolution = Column(String(50))
    price = Column(Numeric(12, 2))

    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    service = relationship("Service", back_populates="levels")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("service_categories.id"))

    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)

    business_unit = Column(String(100))
    owner_id = Column(Integer, ForeignKey("users.id"))

    service_type = Column(String(50))
    billing_type = Column(String(50))

    indicative_price = Column(Numeric(12, 2))
    price_range_min = Column(Numeric(12, 2))
    price_range_max = Column(Numeric(12, 2))

    margin_expectation = Column(Integer)

    is_active = Column(Boolean, default=True)
    is_recommended = Column(Boolean, default=False)

    metadata = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("ServiceCategory", back_populates="services")
    owner = relationship("User", foreign_keys=[owner_id])
    levels = relationship("ServiceLevel", back_populates="service", cascade="all, delete-orphan")
    compatible_products = relationship(
        "Product",
        secondary=service_product_association,
        backref="services"
    )
    opportunities = relationship("Opportunity", back_populates="service")
