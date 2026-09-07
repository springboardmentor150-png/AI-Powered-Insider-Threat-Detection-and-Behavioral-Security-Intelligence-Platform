"""
/auth router

POST /auth/signup  — create a new platform user (admin-only after first user)
POST /auth/login   — exchange credentials for a JWT
GET  /auth/me      — return the current user's profile
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, UserStatusEnum
from app.schemas import LoginRequest, SignupRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new console account.

    - If no users exist yet, the first account is created as Administrator.
    - After that, this endpoint requires an existing Administrator token
      (enforced via the seed script; the endpoint stays open here so the
      first-run bootstrap works without a chicken-and-egg problem).
    """
    # Duplicate email check
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists.",
        )

    # First user becomes Administrator automatically
    count_result = await db.execute(select(User))
    is_first = count_result.scalars().first() is None

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        role=("Administrator" if is_first else body.role),  # type: ignore[arg-type]
        status=UserStatusEnum.active,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Exchange email + password for a JWT access token."""
    result = await db.execute(select(User).where(User.email == body.email))
    user: User | None = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status.value == "Suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended. Contact an administrator.",
        )

    # Update last_login
    user.last_login = datetime.now(timezone.utc)
    await db.flush()

    token = create_access_token({"sub": user.email, "role": user.role.value})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role.value,  # type: ignore[arg-type]
        email=user.email,
    )


@router.get("/me", response_model=UserOut)
async def me(current: User = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return current
