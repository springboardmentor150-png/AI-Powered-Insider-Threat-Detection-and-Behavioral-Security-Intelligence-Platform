from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token
from app.auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["auth"])

ROLE_MAP = {
    "admin": "ADMIN",
    "soc_engineer": "SOC_ENGINEER",
    "security_analyst": "SECURITY_ANALYST", 
    "security_manager": "SECURITY_MANAGER",
    "manager": "SECURITY_MANAGER",
}

class UserSignup(BaseModel):
    email: str
    password: str
    role: str = "SECURITY_ANALYST"

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = hash_password(user.password)
    role_to_use = ROLE_MAP.get(str(user.role).lower(), "SECURITY_ANALYST")
    
    new_user = User(email=user.email, password_hash=hashed_pwd, role=role_to_use)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user.id}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not verify_password(user.password, str(db_user.password_hash)):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    raw_role = str(db_user.role).lower()
    normalized_role = ROLE_MAP.get(raw_role, raw_role.upper())
    
    token = create_token(user_id=int(str(db_user.id)), role=normalized_role)
    return {"access_token": token, "token_type": "bearer"}
