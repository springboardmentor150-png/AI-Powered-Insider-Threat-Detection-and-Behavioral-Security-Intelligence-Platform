from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Employee, ActivityLog, BehavioralBaseline
from app.schemas import (
    BehaviorAnalysisResponse,
    BehavioralBaselineResponse,
    DetectedAnomalySignal,
)
from app.security import get_current_user
from app.services.baseline_engine import get_or_create_baseline, get_baseline_status_message
from app.services.anomaly_detection import evaluate_activity_anomalies

from app.services.ueba_engine import calculate_ueba_profile

router = APIRouter(prefix="/behavior-analysis", tags=["Behavior Analysis"])


@router.get("/{employee_id}", response_model=BehaviorAnalysisResponse)
def get_behavior_analysis(
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
            detail=f"Employee '{employee_id}' not found"
        )

    baseline = get_or_create_baseline(db, employee)
    status_msg = get_baseline_status_message(baseline)
    has_sufficient = (baseline.total_activities_sampled >= 5)

    baseline_res = BehavioralBaselineResponse(
        id=baseline.id,
        employee_id=employee.id,
        employee_identifier=employee.employee_id,
        employee_name=employee.name,
        normal_start_hour=baseline.normal_start_hour,
        normal_end_hour=baseline.normal_end_hour,
        usual_devices=baseline.usual_devices,
        usual_ips=baseline.usual_ips,
        usual_resources=baseline.usual_resources,
        usual_download_limit_mb=baseline.usual_download_limit_mb,
        total_activities_sampled=baseline.total_activities_sampled,
        last_baseline_update=baseline.last_baseline_update,
        status_message=status_msg,
    )

    # Calculate rich UEBA Intelligence Profile (Individual, Peer, Trend, Entity, Threat Prediction)
    ueba_data = calculate_ueba_profile(db, employee)

    # Evaluate recent 20 activities from MongoDB to aggregate detected anomalies
    from app.mongodb import mongo_service
    mongo_logs = mongo_service.query_activity_logs(employee_id=employee.employee_id, limit=20)["items"]

    all_anomalies = []
    for act in mongo_logs:
        if act.get("is_suspicious") or act.get("risk_weight", 0) >= 30:
            reasons = act.get("anomaly_reasons", [])
            for r in reasons:
                all_anomalies.append(DetectedAnomalySignal(
                    anomaly_type=act.get("event_type", "ANOMALY").upper(),
                    severity="CRITICAL" if act.get("risk_weight", 0) >= 80 else "HIGH",
                    description=r,
                    risk_contribution=min(40, act.get("risk_weight", 20)),
                    observed_value=str(act.get("device") or act.get("ip_address") or act.get("action")),
                    expected_baseline=f"{baseline.normal_start_hour}:00–{baseline.normal_end_hour}:00, Enrolled Hardware",
                ))

    deviation_score = min(100, sum(a.risk_contribution for a in all_anomalies[:5])) if all_anomalies else 0

    return BehaviorAnalysisResponse(
        employee=employee,
        baseline=baseline_res,
        has_sufficient_history=has_sufficient,
        status_summary=status_msg,
        recent_anomalies=all_anomalies[:10],
        total_anomalies_detected=len(all_anomalies),
        behavior_deviation_score=deviation_score,
        individual_metrics=ueba_data.get("individual_metrics"),
        peer_comparison=ueba_data.get("peer_comparison"),
        trend_analysis=ueba_data.get("trend_analysis"),
        entity_analytics=ueba_data.get("entity_analytics"),
        threat_prediction=ueba_data.get("threat_prediction"),
    )


@router.get("/{employee_id}/peer-comparison")
def get_peer_comparison(
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    profile = calculate_ueba_profile(db, employee)
    return profile.get("peer_comparison")


@router.get("/{employee_id}/threat-prediction")
def get_threat_prediction(
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    profile = calculate_ueba_profile(db, employee)
    return profile.get("threat_prediction")

