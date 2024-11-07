from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
import enum



Base = declarative_base()

class OrganizationUserRole(str, enum.Enum):
	admin = "admin"
	visitor = "visitor"
	user = "user"	

class SupplierUserRole(str, enum.Enum):
	admin = "admin"
	visitor = "visitor"
	user = "user"	


class CustomBase(Base):
	__abstract__ = True 
	created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
	updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
class User(CustomBase):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True, index=True)
	uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
	email = Column(String, unique=True, index=True)
	first_name = Column(String)
	last_name = Column(String)
	hashed_password = Column(String, nullable=False)
	active_organization_uuid = Column(UUID(as_uuid=True), ForeignKey('organizations.uuid'))
	active_organization = relationship("Organization", foreign_keys=[active_organization_uuid])

	owned_invitations = relationship("Invitation", back_populates="owner")
	owned_rfps = relationship("RFP", back_populates="owner")
	owned_suppliers = relationship("Supplier", back_populates="owner")
	suppliers = relationship(
		"Supplier", 
		secondary="supplier_users", 
		back_populates="users"
	)
	organizations = relationship(
		"Organization", 
		secondary="organization_users", 
		back_populates="users"
	)

class Invitation(CustomBase):
	__tablename__ = 'invitations'

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, nullable=False, index=True)
	organization_uuid = Column(UUID(as_uuid=True), ForeignKey('organizations.uuid'), nullable=False)
	status = Column(String, default="pending")
	owner_uuid = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))

	owner = relationship("User", back_populates="owned_invitations")
	organization = relationship("Organization", back_populates="invitations")


class Organization(CustomBase):
	__tablename__ = 'organizations'

	id = Column(Integer, primary_key=True, index=True)
	uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True) 
	name = Column(String, index=True)
	owner_uuid = Column(UUID(as_uuid=True), ForeignKey('users.uuid'), nullable=False)
	users = relationship(
		"User", 
		secondary="organization_users", 
		back_populates="organizations",
	)
	invitations = relationship("Invitation", back_populates="organization") 
	rfps = relationship("RFP", back_populates="organization")
	suppliers = relationship("Supplier", back_populates="organization")

class OrganizationUser(CustomBase):
    __tablename__ = 'organization_users'

    id = Column(Integer, primary_key=True, index=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey('users.uuid'), nullable=False)  
    organization_uuid = Column(UUID(as_uuid=True), ForeignKey('organizations.uuid'), nullable=False)

class SupplierUser(CustomBase):
	__tablename__ = 'supplier_users'

	id = Column(Integer, primary_key=True, index=True)
	user_uuid = Column(UUID(as_uuid=True), ForeignKey('users.uuid'), nullable=False)  
	supplier_uuid = Column(UUID(as_uuid=True), ForeignKey('suppliers.uuid'), nullable=False)

class RFP(CustomBase):
	__tablename__ = 'rfps'

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, index=True)
	uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)	
	organization_uuid = Column(UUID(as_uuid=True), ForeignKey('organizations.uuid'), nullable=False)
	owner_uuid = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))
	data = Column(JSON, nullable=True)

	organization = relationship("Organization", back_populates="rfps")
	owner = relationship("User", back_populates="owned_rfps")

class Supplier(CustomBase):
	__tablename__ = 'suppliers'

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, index=True)
	uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)	
	organization_uuid = Column(UUID(as_uuid=True), ForeignKey('organizations.uuid'), nullable=False)
	owner_uuid = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))
	logo_url = Column(String, index=True)
	data = Column(JSON, nullable=True)
	users = relationship(
		"User", 
		secondary="supplier_users", 
		back_populates="suppliers",
	)
	organization = relationship("Organization", back_populates="suppliers")
	owner = relationship("User", back_populates="owned_suppliers")


