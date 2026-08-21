from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="category")


class ProductVendor(Base):
    __tablename__ = "product_vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(50), unique=True)
    website = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="vendor")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    vendor_id = Column(Integer, ForeignKey("product_vendors.id"))

    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), unique=True, index=True)
    description = Column(Text)

    product_type = Column(String(50))
    license_type = Column(String(50))

    list_price = Column(Numeric(12, 2))
    margin_expectation = Column(Integer)

    is_active = Column(Integer, default=1)

    custom_metadata = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("ProductCategory", back_populates="products")
    vendor = relationship("ProductVendor", back_populates="products")
    contracts = relationship("Contract", back_populates="product")
