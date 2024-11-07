from fastapi import APIRouter, Depends, HTTPException, status, Query
from depencies import get_db, get_current_user, verify_user_in_organization
from models import User, RFP, OrganizationUser, Organization
from schemas import RFPCreate, RFPResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

router = APIRouter()

@router.post("/rfp", response_model=RFPResponse)
async def create_rfp(
    rfp: RFPCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
): 
	user_in_organization: bool = Depends(lambda: verify_user_in_organization(rfp.organization_uuid, current_user))

	if not user_in_organization:
		raise HTTPException(status_code=401, detail="User not in organization")
		
	new_rfp = RFP(
		owner_uuid=current_user.uuid,  
		organization_uuid=rfp.organization_uuid,
		data=rfp.data
	)
	db.add(new_rfp)
	db.commit()
	db.refresh(new_rfp) 
	return new_rfp

@router.get("/rfp", response_model=List[RFPResponse])
async def get_rfps(
    organization_uuid: UUID = Query(..., description="Organization UUID to define organization"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
	user_in_organization: bool = Depends(lambda: verify_user_in_organization(organization_uuid, current_user))

	if not user_in_organization:
		raise HTTPException(status_code=401, detail="User not in organization")
          
	rfps = db.query(RFP).filter(
		RFP.organization_uuid == organization_uuid
    ).all()

	if not rfps:
		raise HTTPException(status_code=404, detail="No rfps found for the user.")

	return rfps

@router.get("/rfp/{rfp_uuid}", response_model=RFPResponse)
async def get_rfp_with_id(
    rfp_uuid: UUID,
	organization_uuid: UUID = Query(..., description="Organization UUID to define organization"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
	user_in_organization: bool = Depends(lambda: verify_user_in_organization(organization_uuid, current_user))

	if not user_in_organization:
		raise HTTPException(status_code=401, detail="User not in organization")
	
	rfp = db.query(RFP).filter(
		RFP.uuid == rfp_uuid
	).first()

	if not rfp:
		raise HTTPException(status_code=404, detail="No rfp found for the user.")

	return rfp