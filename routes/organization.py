from fastapi import APIRouter, Depends, HTTPException, status
from depencies import get_db, get_current_user
from models import User, Organization, OrganizationUser
from schemas import OrganizationCreate, OrganizationResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID


router = APIRouter()

@router.post("/organization", response_model=OrganizationResponse)
async def create_organization(
    organization: OrganizationCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    new_organization = Organization(
        name=organization.name,
        owner_uuid=current_user.uuid  
    )
    db.add(new_organization)
    db.commit()
    db.refresh(new_organization)

    organization_user = OrganizationUser(
        organization_uuid=new_organization.uuid,
        user_uuid=current_user.uuid
    )
    db.add(organization_user)
    db.commit()
    return new_organization

@router.get("/organization", response_model=List[OrganizationResponse])
async def get_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    organizations = db.query(Organization).join(OrganizationUser).filter(
        OrganizationUser.user_uuid == current_user.uuid
    ).all()

    if not organizations:
        raise HTTPException(status_code=404, detail="No organizations found for the user.")

    return organizations

@router.get("/organization/{organization_uuid}", response_model=OrganizationResponse)
async def get_organization_with_id(
    organization_uuid: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    organizations = db.query(Organization).join(OrganizationUser).filter(
        OrganizationUser.user_uuid == current_user.uuid,
        Organization.uuid == organization_uuid
    ).first()

    if not organizations:
        raise HTTPException(status_code=404, detail="No organization found for the user.")

    return organizations