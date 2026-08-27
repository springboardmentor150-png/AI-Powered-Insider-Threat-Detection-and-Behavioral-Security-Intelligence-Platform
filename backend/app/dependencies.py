from fastapi import Header, HTTPException

from .jwt_auth import decode_access_token


def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header",
        )

    token = authorization.replace("Bearer ", "", 1)

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    return payload


def require_role(*allowed_roles):
    def checker(authorization: str | None = Header(default=None)):
        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization header required",
            )

        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header",
            )

        token = authorization.replace("Bearer ", "", 1)

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