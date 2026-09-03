from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt_auth import decode_access_token


security = HTTPBearer()


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

        if payload.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Not authorized for this action",
            )

        return payload

    return checker