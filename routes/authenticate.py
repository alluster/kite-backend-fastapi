from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from depencies import get_db, verify_password, create_access_token, hash_password, verify_user_in_organization, get_current_user
from models import User
from datetime import timedelta
from pydantic import BaseModel
from schemas import UserCreate, UserSchema, ActiveTeamCreate
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
	user: UserSchema
	access_token: str
	token_type: str

class ProfileResponse(BaseModel):
    user: UserSchema
    
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login", response_model=UserResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    token_data = {"sub": str(user.uuid)}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"user": user, "access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=TokenResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    token_data = {"sub": str(user.uuid)}
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
	existing_user = db.query(User).filter(User.email == user_create.email).first()
	if existing_user:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Email already registered"
		)

	hashed_password = hash_password(user_create.password)

	new_user = User(
		email=user_create.email,
		hashed_password=hashed_password,
		first_name=user_create.first_name,
		last_name=user_create.last_name
	)

	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	token_data = {"sub": str(new_user.uuid)}
      
	access_token = create_access_token(
		data=token_data,
		expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	)
      
	return {"user": new_user, "access_token": access_token, "token_type": "bearer"}

@router.post("/activeTeam")
async def active_team(
    active_team: ActiveTeamCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
	user_in_organization: bool = Depends(lambda: verify_user_in_organization(active_team.organization_uuid, current_user))
	if not user_in_organization:
		raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not belong to this organization."
        )
	current_user.active_organization_uuid = active_team.organization_uuid
	db.commit()
	db.refresh(current_user)
	return {"message": "Active organization updated successfully."} 


@router.post("/user", response_model=UserResponse)
async def get_user(
	db: Session = Depends(get_db),
	current_user: User = Depends(get_current_user)    
):
	user = db.query(User).filter(User.uuid == current_user.uuid).first()

	if not current_user:
		raise HTTPException(status_code=401, detail="User not authenticated.")
     
	token_data = {"sub": str(user.uuid)}
	access_token = create_access_token(
		data=token_data,
		expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	)

	return {"user": user, "access_token": access_token, "token_type": "bearer"}	
        