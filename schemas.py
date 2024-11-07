from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class InvitationSchema(BaseModel):
    id: int
    email: str
    status: str

    class Config:
        orm_mode = True  # Enable ORM mode for direct use of SQLAlchemy models

class SupplierSchema(BaseModel):
	id: int
	name: Optional[str]
	logo_url: Optional[str]
	data: Dict[str, Any] = Field(default_factory=dict)
	uuid: UUID

	class Config:
		orm_mode = True

class OrganizationSchema(BaseModel):
	id: int
	name: str
	uuid: UUID
	suppliers: List[SupplierSchema] = [] 

	class Config:
		orm_mode = True

class UserSchema(BaseModel):
	uuid: UUID
	email: EmailStr
	first_name: str
	last_name: str
	active_organization: Optional[OrganizationSchema] = None
	owned_invitations: List[InvitationSchema] = []
	owned_organizations: List[OrganizationSchema] = []
	organizations: List[OrganizationSchema] = []
	suppliers: List[SupplierSchema] = [] 
	class Config:
		orm_mode = True
        
class UserCreate(BaseModel):
	email: EmailStr
	first_name: str
	last_name: str
	password: str
	
class RFPResponse(BaseModel):
	uuid: UUID	
	data: Dict[str, Any] = Field(default_factory=dict)
	owner: UserSchema
	organization: OrganizationSchema

      
class RFPCreate(BaseModel):
	organization_uuid: UUID
	data: Optional[dict[str, Any]] = Field(default_factory=dict) 

class RFPSchema(BaseModel):
	data: Optional[dict[str, Any]] = Field(default_factory=dict) 
      
class SupplierResponse(BaseModel):
	uuid: UUID	
	name: str
	data: Optional[dict[str, Any]] = Field(default_factory=dict) 
	owner: UserSchema
	organization: OrganizationSchema


      
class SupplierCreate(BaseModel):
	name: str
	organization_uuid: UUID
	data: Optional[dict[str, Any]] = Field(default_factory=dict) 


class OrganizationCreate(BaseModel):
	name: str

class OrganizationResponse(BaseModel):
	name: str	
	uuid: UUID
	owner_uuid: UUID
	users: List[UserSchema] = [] 
	invitations: List[InvitationSchema] = [] 
	rfps: List[RFPSchema] = [] 
	suppliers: List[SupplierSchema] = [] 


class OrganizationSchema(BaseModel):
	name: str	
	owner_uuid: UUID
	users: List[UserSchema] = [] 
	invitations: List[InvitationSchema] = [] 
	rfps: List[RFPSchema] = [] 
	suppliers: List[SupplierSchema] = [] 

class OrganizationUserSchema(BaseModel):
	user_uuid: UUID
	organization_uuid: UUID

class OrganizationUserCreate(BaseModel):
	user_uuid: UUID
	organization_uuid: UUID
      
class ActiveTeamCreate(BaseModel):
	organization_uuid: UUID

class SupplierUserSchema(BaseModel):
	user_uuid: UUID
	supplier_uuid: UUID

class SupplierUserCreate(BaseModel):
	user_uuid: UUID
	supplier_uuid: UUID