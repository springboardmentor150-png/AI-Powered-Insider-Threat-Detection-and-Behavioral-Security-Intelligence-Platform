from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt_auth import decode_access_token


security = HTTPBearer()

ROLE_ALIASES = {
    # Analyst aliases
    "analyst": "security_analyst",
    "security_analyst": "security_analyst",
    "security analyst": "security_analyst",

    # SOC Engineer aliases
    "soc": "soc_engineer",
    "soc_engineer": "soc_engineer",
    "soc engineer": "soc_engineer",

    # Security Manager aliases
    "manager": "security_manager",
    "security_manager": "security_manager",
    "security manager": "security_manager",

    # Admin aliases
    "admin": "admin",
    "administrator": "admin",
}


def canonical_role(role: str | None) -> str:
    """Normalize role string to canonical form for robust RBAC authorization."""
    if not role:
        return ""
    normalized = str(role).lower().strip().replace("-", "_")
    return ROLE_ALIASES.get(normalized, normalized)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    return payload


def require_role(*allowed_roles):
    normalized_allowed = {canonical_role(r) for r in allowed_roles}

    def checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
        token = credentials.credentials

        try:
            payload = decode_access_token(token)
        except Exception:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
            )

        user_role = canonical_role(payload.get("role"))

        if user_role not in normalized_allowed:
            raise HTTPException(
                status_code=403,
                detail="Not authorized for this action",
            )

        return payload

    return checker