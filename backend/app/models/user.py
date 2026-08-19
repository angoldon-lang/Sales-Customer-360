from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


role_permission_association = Table(
    'role_permission_association',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    resource = Column(String(100))
    action = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))

    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255))

    hashed_password = Column(String(255), nullable=False)

    business_unit = Column(String(100))
    team = Column(String(100))
    region = Column(String(100))

    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
