from fastapi import APIRouter, Depends
from ..security import get_current_user, require_role
from ..models import User

router = APIRouter(tags=["Role Testing"])


@router.get("/admin/users")
def admin_only(current_user: User = Depends(require_role("admin"))):
    return {"message": "Admin access granted", "user": current_user.email}


@router.get("/reports/risk-posture")
def risk_posture(current_user: User = Depends(require_role("admin", "security_manager"))):
    return {"message": "Risk posture access granted", "user": current_user.email}


@router.get("/alerts/my")
def my_alerts(current_user: User = Depends(get_current_user)):
    return {"message": "Alerts access granted", "user": current_user.email, "role": current_user.role}
