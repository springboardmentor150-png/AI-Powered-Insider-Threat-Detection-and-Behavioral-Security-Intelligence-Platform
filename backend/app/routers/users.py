"""
/users router  (platform console accounts — Admin only)

GET   /users            — list all platform users
POST  /users            — invite / create a user
PATCH /users/{user_id}  — update role or status
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password
from app.database import get_db
from app.dependencies import require_role
from app.models import User, UserStatusEnum
from app.schemas import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
async def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("Administrator")),
):
    """List all platform console accounts. Administrator only."""
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("Administrator")),
):
    """Invite / create a new console user. Administrator only."""
    dup = await db.execute(select(User).where(User.email == body.email))
    if dup.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists.",
        )

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,  # type: ignore[arg-type]
        status=UserStatusEnum.invited,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _current=Depends(require_role("Administrator")),
):
    """Update a user's role or status. Administrator only."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if body.role is not None:
        user.role = body.role  # type: ignore[assignment]
    if body.status is not None:
        user.status = body.status  # type: ignore[assignment]

    await db.flush()
    await db.refresh(user)
    return user
