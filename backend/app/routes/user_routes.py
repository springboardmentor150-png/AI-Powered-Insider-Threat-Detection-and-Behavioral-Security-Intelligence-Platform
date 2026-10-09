from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserCreate
from app.auth import require_role, hash_password
from app.audit import log_audit

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), _: dict = Depends(require_role("ADMIN"))):
    return db.query(User).all()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_role("ADMIN"))):
    CANONICAL_ROLES = ["ADMIN", "SOC_ENGINEER", "SECURITY_ANALYST", "SECURITY_MANAGER"]
    if user.role.upper() not in CANONICAL_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(CANONICAL_ROLES)}")

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = hash_password(user.password)
    new_user = User(email=user.email, password_hash=hashed_pwd, role=user.role.upper())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    log_audit(db, int(current_user.get("sub", 0)), "CREATED_USER", user.email, f"Assigned role: {user.role.upper()}")
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_role("ADMIN"))):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
         raise HTTPException(status_code=404, detail="User not found")
         
    if user.email != db_user.email:
        existing = db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
    
    db_user.email = user.email
    db_user.role = user.role.upper()
    if user.password:
        db_user.password_hash = hash_password(user.password)
        
    db.commit()
    db.refresh(db_user)
    log_audit(db, int(current_user.get("sub", 0)), "UPDATED_USER", user.email, f"Role mapped to {user.role.upper()}")
    return db_user
