from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token
from app.auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["auth"])

ALLOWED_ROLES = ["security_analyst", "soc_engineer", "security_manager", "admin"]

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = hash_password(user.password)
    new_user = User(email=user.email, password_hash=hashed_pwd, role=user.role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user.id}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    token = create_token(user_id=db_user.id, role=db_user.role)
    return {"access_token": token, "token_type": "bearer"}
