from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, SignupResponse, TokenResponse
from app.auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    email_clean = data.email.strip().lower()
    existing_user = db.query(User).filter(func.lower(User.email) == email_clean).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = hash_password(data.password)

    user = User(
        email=data.email.strip(),
        password_hash=hashed_password,
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    from app.audit import log_action
    log_action(
        db=db,
        user_id=user.id,
        action="CREATE_USER",
        details=f"New operator account registered: {user.email} (Role: {user.role})",
        user_email=user.email,
        target_type="USER",
        target_id=str(user.id),
    )

    return {
        "message": "User created successfully",
        "id": user.id,
        "email": user.email,
        "role": user.role
    }


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    email_clean = data.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email_clean).first()
    if not user:
        user = db.query(User).filter(User.email == data.email.strip()).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_token(user_id=user.id, role=user.role)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }


@router.get("/test")
def auth_test():
    return {"message": "Authentication route is working"}
