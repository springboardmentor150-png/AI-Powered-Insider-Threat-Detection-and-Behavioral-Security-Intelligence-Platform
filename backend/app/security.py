from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from app.auth import decode_token


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    token = authorization.replace("Bearer ", "", 1).strip()

    try:
        payload = decode_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return payload

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def require_role(*allowed_roles):
    def checker(user=Depends(get_current_user)):
        user_role = str(user.get("role", "")).lower().replace(" ", "_")
        normalized_allowed = [str(r).lower().replace(" ", "_") for r in allowed_roles]

        role_aliases = {
            "admin": ["admin", "administrator", "system_administrator"],
            "administrator": ["admin", "administrator", "system_administrator"],
            "system_administrator": ["admin", "administrator", "system_administrator"],
            "analyst": ["analyst", "security_analyst"],
            "security_analyst": ["analyst", "security_analyst"],
            "soc_engineer": ["soc_engineer", "soc engineer"],
            "security_manager": ["security_manager", "security manager"],
        }

        user_aliases = role_aliases.get(user_role, [user_role])
        is_allowed = (
            user_role in normalized_allowed
            or user.get("role") in allowed_roles
            or any(alias in normalized_allowed for alias in user_aliases)
        )

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this action"
            )

        return user

    return checker
