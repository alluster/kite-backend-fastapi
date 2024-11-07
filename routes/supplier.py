from fastapi import APIRouter, Depends, HTTPException, status, Query
from depencies import get_db, get_current_user, verify_user_in_organization
from models import User, Supplier, SupplierUser, OrganizationUser
from schemas import SupplierCreate, SupplierResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

router = APIRouter()
class SupplierUserRole(str):
	admin = "admin"
	visitor = "visitor"
	user = "user"
	
@router.post("/supplier", response_model=SupplierResponse)
async def create_supplier(
    supplier: SupplierCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
): 
	user_in_organization: bool = Depends(lambda: verify_user_in_organization(supplier.organization_uuid, current_user))

	if not user_in_organization:
		raise HTTPException(status_code=401, detail="User not in organization")
		
	new_supplier = Supplier(
        name=supplier.name,
		owner_uuid=current_user.uuid,  
		organization_uuid=supplier.organization_uuid,
		data=supplier.data
	)
	db.add(new_supplier)
	db.commit()
	db.refresh(new_supplier) 
	
	supplier_user = SupplierUser(
		supplier_uuid=new_supplier.uuid,
		user_uuid=current_user.uuid,
	)
	db.add(supplier_user)
	db.commit()

	return new_supplier

@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(
    organization_uuid: UUID = Query(..., description="UUID of the organization to filter suppliers by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_in_org = db.query(OrganizationUser).filter(
        OrganizationUser.user_uuid == current_user.uuid,
        OrganizationUser.organization_uuid == organization_uuid
    ).first()

    if not user_in_org:
        raise HTTPException(status_code=403, detail="User does not belong to the specified organization.")

    suppliers = db.query(Supplier).join(SupplierUser).filter(
        SupplierUser.user_uuid == current_user.uuid,
        Supplier.organization_uuid == organization_uuid
    ).all()

    if not suppliers:
        raise HTTPException(status_code=404, detail="No suppliers found for the user in this organization.")

    return suppliers

@router.get("/suppliers{supplier_uuid}", response_model=SupplierResponse)
async def get_supplier_by_uuid(
    supplier_uuid: UUID,
    organization_uuid: UUID = Query(..., description="UUID of the organization to get supplier by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_in_org = db.query(OrganizationUser).filter(
        OrganizationUser.user_uuid == current_user.uuid,
        OrganizationUser.organization_uuid == organization_uuid
    ).first()

    if not user_in_org:
        raise HTTPException(status_code=403, detail="User does not belong to the specified organization.")

    supplier = db.query(Supplier).join(SupplierUser).filter(
        SupplierUser.user_uuid == current_user.uuid,
        Supplier.organization_uuid == organization_uuid,
        Supplier.uuid == supplier_uuid
    ).first()

    if not supplier:
        raise HTTPException(status_code=404, detail="No supplier found for the user in this organization.")

    return supplier