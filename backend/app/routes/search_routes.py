from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, Alert, Incident, User
from app.schemas import GlobalSearchResponse, SearchMatchItem
from app.security import get_current_user
from app.mongodb import mongo_service

router = APIRouter(prefix="/search", tags=["Global Search"])


@router.get("", response_model=GlobalSearchResponse)
def search_global(
    q: str = Query(..., min_length=1, description="Search term across entities"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Unified global search querying across:
    - Employees (PostgreSQL)
    - Alerts (PostgreSQL)
    - Incidents (PostgreSQL)
    - Activity Telemetry (MongoDB)
    """
    query_str = q.strip().lower()
    matches: List[SearchMatchItem] = []

    # 1. Search Employees
    emp_query = db.query(Employee).filter(
        (Employee.employee_id.ilike(f"%{query_str}%"))
        | (Employee.name.ilike(f"%{query_str}%"))
        | (Employee.department.ilike(f"%{query_str}%"))
        | (Employee.designation.ilike(f"%{query_str}%"))
        | (Employee.email.ilike(f"%{query_str}%"))
    ).limit(5).all()

    for emp in emp_query:
        matches.append(SearchMatchItem(
            category="EMPLOYEE",
            id=emp.employee_id,
            title=f"{emp.name} ({emp.employee_id})",
            subtitle=f"{emp.designation or 'Staff'} • {emp.department or 'Operations'} • Risk: {emp.risk_score}",
            severity=emp.risk_level,
            link=f"/investigations?employee_id={emp.employee_id}",
        ))

    # 2. Search Alerts
    alert_query = db.query(Alert).filter(
        (Alert.title.ilike(f"%{query_str}%"))
        | (Alert.category.ilike(f"%{query_str}%"))
        | (Alert.message.ilike(f"%{query_str}%"))
    ).limit(5).all()

    for al in alert_query:
        matches.append(SearchMatchItem(
            category="ALERT",
            id=str(al.id),
            title=f"Alert #{al.id}: {al.title}",
            subtitle=f"Category: {al.category} • Status: {al.status}",
            severity=al.severity,
            link="/alerts",
        ))

    # 3. Search Incidents
    inc_query = db.query(Incident).filter(
        (Incident.title.ilike(f"%{query_str}%"))
        | (Incident.description.ilike(f"%{query_str}%"))
    ).limit(5).all()

    for inc in inc_query:
        matches.append(SearchMatchItem(
            category="INCIDENT",
            id=str(inc.id),
            title=f"INC-{inc.id}: {inc.title}",
            subtitle=f"Status: {inc.status} • Severity: {inc.severity}",
            severity=inc.severity,
            link="/incidents",
        ))

    # 4. Search MongoDB Telemetry
    mongo_res = mongo_service.query_activity_logs(search=query_str, limit=5)["items"]
    for act in mongo_res:
        matches.append(SearchMatchItem(
            category="ACTIVITY",
            id=str(act.get("id", "")),
            title=f"{act.get('event_type', '').title()}: {act.get('action', '')}",
            subtitle=f"Subject: {act.get('employee_id')} • Node: {act.get('device', 'Local')} • IP: {act.get('ip_address', '10.0.0.0')}",
            severity="CRITICAL" if act.get("risk_weight", 0) >= 80 else ("HIGH" if act.get("risk_weight", 0) >= 40 else "LOW"),
            link=f"/activity-logs?search={act.get('employee_id')}",
        ))

    return GlobalSearchResponse(
        query=q,
        results=matches,
        total_matches=len(matches),
    )
