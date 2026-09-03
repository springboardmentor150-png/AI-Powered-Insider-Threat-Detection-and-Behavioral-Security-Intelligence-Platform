"""
Security core: password hashing, JWT issuing/decoding, and role-based access control.

This is the single most security-critical file in the project - it's the reason
the rest of the platform can trust who is making each request.
"""

import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-to-a-long-random-string-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "8"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------- Passwords ----------

def hash_password(password: str) -> str:
    """One-way hash a plain password. The plain text is never stored anywhere."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a login attempt against the stored hash without ever un-scrambling it."""
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT ----------

def create_access_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user(authorization: str = Header(...)) -> dict:
    """Reads the Authorization header, expects 'Bearer <token>', and decodes it."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed token")
    token = authorization.replace("Bearer ", "", 1)
    return decode_token(token)


def require_role(*allowed_roles: str):
    """
    Returns a FastAPI dependency that only lets through the given roles.
    Usage: user = Depends(require_role("admin", "security_manager"))
    """

    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{current_user['role']}' is not authorized for this action",
            )
        return current_user

    return role_checker
