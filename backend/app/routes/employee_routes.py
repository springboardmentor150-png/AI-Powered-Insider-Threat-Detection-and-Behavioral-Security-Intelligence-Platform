from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Employee, Alert, Incident
from app.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeDetailResponse,
    PaginatedEmployeesResponse,
    AlertResponse,
    IncidentResponse,
)
from app.security import get_current_user, require_role

router = APIRouter(prefix="/employees", tags=["Employees"])


def compute_risk_level(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    return "LOW"


@router.get("", response_model=PaginatedEmployeesResponse)
def get_employees(
    search: Optional[str] = None,
    department: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Employee)

    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Employee.name.ilike(search_pattern),
                Employee.employee_id.ilike(search_pattern),
                Employee.email.ilike(search_pattern),
                Employee.designation.ilike(search_pattern),
            )
        )

    if department and department != "ALL":
        query = query.filter(Employee.department == department)

    if risk_level and risk_level != "ALL":
        query = query.filter(Employee.risk_level == risk_level)

    if status and status != "ALL":
        query = query.filter(Employee.status == status)

    total = query.count()
    offset = (page - 1) * limit
    items = query.order_by(Employee.risk_score.desc(), Employee.id.asc()).offset(offset).limit(limit).all()

    return PaginatedEmployeesResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )


@router.get("/{employee_id}", response_model=EmployeeDetailResponse)
def get_employee_by_id(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if employee_id.isdigit() else False,
        )
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with identifier '{employee_id}' not found"
        )

    alerts = db.query(Alert).filter(Alert.employee_id == employee.id).order_by(Alert.created_at.desc()).all()
    incidents = db.query(Incident).filter(Incident.employee_id == employee.id).order_by(Incident.created_at.desc()).all()
    from app.models import BehavioralBaseline, RiskScoreHistory
    from app.schemas import BehavioralBaselineResponse, RiskScoreHistoryResponse, MongoActivityItem
    from app.services.baseline_engine import get_or_create_baseline, get_baseline_status_message
    from app.mongodb import mongo_service
    from app.routes.alert_routes import to_alert_response
    from app.routes.incident_routes import to_incident_response

    raw_mongo_activities = mongo_service.query_activity_logs(employee_id=employee.employee_id, limit=20)["items"]
    activities = [
        MongoActivityItem(
            id=str(a.get("id", "")),
            employee_id=str(a.get("employee_id", employee.employee_id)),
            event_type=str(a.get("event_type", "login")),
            action=a.get("action"),
            resource=a.get("resource"),
            timestamp=str(a.get("timestamp", "")),
            device=a.get("device"),
            ip_address=a.get("ip_address"),
            location=a.get("location"),
            risk_weight=int(a.get("risk_weight", 0)),
            is_suspicious=bool(a.get("is_suspicious", False)),
            anomaly_reasons=a.get("anomaly_reasons", []),
            is_test_event=bool(a.get("is_test_event", False)),
            details=a.get("details", {}),
        )
        for a in raw_mongo_activities
    ]

    baseline_obj = get_or_create_baseline(db, employee)
    status_msg = get_baseline_status_message(baseline_obj)
    baseline_res = BehavioralBaselineResponse(
        id=baseline_obj.id,
        employee_id=employee.id,
        employee_identifier=employee.employee_id,
        employee_name=employee.name,
        normal_start_hour=baseline_obj.normal_start_hour,
        normal_end_hour=baseline_obj.normal_end_hour,
        usual_devices=baseline_obj.usual_devices,
        usual_ips=baseline_obj.usual_ips,
        usual_resources=baseline_obj.usual_resources,
        usual_download_limit_mb=baseline_obj.usual_download_limit_mb,
        total_activities_sampled=baseline_obj.total_activities_sampled,
        last_baseline_update=baseline_obj.last_baseline_update,
        status_message=status_msg,
    )

    risk_hist_objs = db.query(RiskScoreHistory).filter(RiskScoreHistory.employee_id == employee.id).order_by(RiskScoreHistory.calculated_at.desc()).limit(20).all()

    return {
        "employee": employee,
        "alerts": [to_alert_response(a) for a in alerts],
        "incidents": [to_incident_response(i) for i in incidents],
        "recent_activities": activities,
        "baseline": baseline_res,
        "risk_history": [RiskScoreHistoryResponse.model_validate(r) for r in risk_hist_objs],
    }



@router.post("", status_code=status.HTTP_201_CREATED, response_model=EmployeeResponse)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "security_manager")),
):
    existing = db.query(Employee).filter(Employee.employee_id == data.employee_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee ID '{data.employee_id}' is already registered."
        )

    manager_name = data.manager_name
    if data.manager_id is not None:
        mgr = db.query(Employee).filter(Employee.id == data.manager_id).first()
        if not mgr:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Manager with ID '{data.manager_id}' does not exist."
            )
        if not manager_name:
            manager_name = mgr.name

    risk_level = data.risk_level or compute_risk_level(data.risk_score or 0)

    employee = Employee(
        employee_id=data.employee_id,
        name=data.name,
        email=data.email,
        department=data.department,
        designation=data.designation,
        manager_id=data.manager_id,
        manager_name=manager_name,
        employment_type=data.employment_type or "Full-time",
        work_location=data.work_location or "Hyderabad",
        joining_date=data.joining_date or "2022-01-15",
        years_of_experience=data.years_of_experience if data.years_of_experience is not None else 5,
        education=data.education or "B.Tech Computer Science",
        previous_role=data.previous_role,
        skills=data.skills,
        professional_summary=data.professional_summary,
        device_info=data.device_info,
        access_privileges=data.access_privileges or "STANDARD",
        risk_score=data.risk_score or 0,
        risk_level=risk_level,
        status=data.status or "ACTIVE",
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "security_manager")),
):
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if employee_id.isdigit() else False,
        )
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with identifier '{employee_id}' not found"
        )

    update_data = data.model_dump(exclude_unset=True)

    if "manager_id" in update_data:
        if update_data["manager_id"] is not None:
            mgr = db.query(Employee).filter(Employee.id == update_data["manager_id"]).first()
            if not mgr:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Manager with ID '{update_data['manager_id']}' does not exist."
                )
            if "manager_name" not in update_data or not update_data["manager_name"]:
                employee.manager_name = mgr.name
        else:
            if "manager_name" not in update_data:
                employee.manager_name = None

    for field, value in update_data.items():
        setattr(employee, field, value)

    if "risk_score" in update_data and "risk_level" not in update_data:
        employee.risk_level = compute_risk_level(employee.risk_score)

    db.commit()
    db.refresh(employee)

    return employee


@router.get("/{employee_id}/direct-reports", response_model=List[EmployeeResponse])
def get_direct_reports(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if employee_id.isdigit() else False,
        )
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with identifier '{employee_id}' not found"
        )

    return db.query(Employee).filter(Employee.manager_id == employee.id).all()


@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "security_manager")),
):
    employee = db.query(Employee).filter(
        or_(
            Employee.employee_id == employee_id,
            Employee.id == int(employee_id) if employee_id.isdigit() else False,
        )
    ).first()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with identifier '{employee_id}' not found"
        )

    db.delete(employee)
    db.commit()

    return {"message": f"Employee '{employee_id}' successfully removed."}
