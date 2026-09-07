"""
FastAPI dependency functions for authentication and role-based access control.

Usage in a router:
    current_user = Depends(get_current_user)          # any authenticated user
    _            = Depends(require_role("Administrator"))
    _            = Depends(require_any_role("Administrator", "Security Manager"))
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import decode_access_token
from app.database import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Return the authenticated User or raise 401."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email: str | None = payload.get("sub")
        if not email:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exc
    if user.status.value == "Suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended. Contact an administrator.",
        )
    return user


def require_role(*roles: str):
    """
    Dependency factory — allow access only to users whose role is in *roles*.

    Example:
        Depends(require_role("Administrator"))
        Depends(require_role("Administrator", "Security Manager"))
    """
    async def _check(current: User = Depends(get_current_user)) -> User:
        if current.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current.role.value}' is not permitted for this action.",
            )
        return current
    return _check
