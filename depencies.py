from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from database import SessionLocal
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from models import User, OrganizationUser, SupplierUser
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from schemas import OrganizationUserSchema, SupplierUserSchema
from uuid import UUID
from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY is not set in the environment variables.")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    user_uuid: Optional[str] = None
    exp: Optional[int] = None  
    
def get_db():
    db = SessionLocal()  
    try:
        yield db 
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "sub": data.get("sub")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> str:
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		user_uuid: str = payload.get("sub")
		if user_uuid is None:
			raise HTTPException(status_code=401, detail="Token missing 'sub' field")		

		return user_uuid
	except ExpiredSignatureError:
		raise HTTPException(status_code=401, detail="Token has expired")
	except InvalidTokenError:
		raise HTTPException(status_code=401, detail="Invalid token")
	except PyJWTError:
		raise HTTPException(status_code=401, detail="Token is invalid")
	except Exception as e:
		raise HTTPException(status_code=401, detail=f"Token error: {str(e)}")
    
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
	try:
		user_uuid = verify_token(token)
		user = db.query(User).filter(User.uuid == user_uuid).first()
		if not user:
			raise HTTPException(status_code=400, detail="User not authenticated")
		return user
	except:
		raise HTTPException(status_code=401, detail="Unauthenticated request")
		
def verify_user_in_organization(organization_uuid: UUID, user_uuid: UUID, db: Session = Depends(get_db)):
	try:
		organization_user = db.query(OrganizationUserSchema).filter(
			OrganizationUserSchema.user_uuid == user_uuid,
			OrganizationUserSchema.organization_uuid == organization_uuid
		).first()
		if not organization_user:
			raise HTTPException(status_code=400, detail="User not in organization")
		return True
	except: 
		raise HTTPException(status_code=401, detail="User not in organization")

def verify_user_in_supplier(supplier_uuid: UUID, user_uuid: UUID, db: Session = Depends(get_db)):
	try:
		supplier_user = db.query(SupplierUserSchema).filter(
			SupplierUserSchema.user_uuid == user_uuid,
			SupplierUserSchema.supplier_uuid == supplier_uuid
		).first()
		if not supplier_user:
			raise HTTPException(status_code=400, detail="User not in supplier")
		return True
	except: 
		raise HTTPException(status_code=401, detail="User not in supplier")
	

def create_organization_user(organization_uuid: UUID, user_uuid: UUID, db: Session = Depends(get_db)):
	try: 
		new_organization_user = OrganizationUser(
			user_uuid=user_uuid,
			organization_uuid=organization_uuid
		)
		db.add(new_organization_user)
		db.commit()
		db.refresh(new_organization_user)
	except:
		raise HTTPException(status_code=401, detail="User not added into organization users")
