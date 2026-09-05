# backend/app/routes/ai_routes.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db, doc_db
from app.models import Employee, Alert, User
from app.schemas import AIAnalysisResult
from app.auth import get_current_user
from app.ml_engine.anomaly_detector import anomaly_detector
from app.ml_engine.risk_scorer import risk_scorer
from app.ml_engine.threat_explainer import threat_explainer

router = APIRouter(prefix="/ai", tags=["AI & Behavioral Threat Intelligence"])

@router.post("/analyze/{employee_id}", response_model=AIAnalysisResult)
def analyze_employee_behavior(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee {employee_id} not found")

    # 1. Fetch recent activity telemetry from Document DB
    logs = doc_db.activity_logs.find(query={"employee_id": employee_id}, limit=50)
    baseline = doc_db.behavioral_baselines.find_one({"employee_id": employee_id}) or {}

    # 2. Run Isolation Forest Anomaly Detection
    is_anomaly, anomaly_score, indicators = anomaly_detector.detect_anomalies(logs, baseline)

    # 3. Compute Composite Risk Score
    final_risk, threat_level, top_factors = risk_scorer.compute_risk(
        base_employee_risk=emp.baseline_risk_score or 15.0,
        anomaly_detected=is_anomaly,
        anomaly_score=anomaly_score,
        indicators=indicators,
        logs=logs
    )

    # 4. Generate AI Threat Narrative and MITRE Mapping
    explanation = threat_explainer.generate_explanation(
        employee_name=emp.name,
        employee_id=emp.employee_id,
        department=emp.department,
        risk_score=final_risk,
        threat_level=threat_level,
        indicators=indicators,
        logs=logs
    )

    # Update employee's current risk score
    emp.baseline_risk_score = final_risk
    if threat_level == "CRITICAL":
        emp.status = "UNDER_REVIEW"
    db.commit()

    # Automatically trigger Alert if High/Critical threat
    if threat_level in ["HIGH", "CRITICAL"]:
        existing_recent_alert = db.query(Alert).filter(
            Alert.employee_id == employee_id,
            Alert.is_acknowledged == False,
            Alert.severity == threat_level
        ).first()
        if not existing_recent_alert:
            alert_code = f"ALT-{uuid.uuid4().hex[:6].upper()}"
            alert = Alert(
                alert_code=alert_code,
                employee_id=employee_id,
                severity=threat_level,
                title=f"AI Behavioral Anomaly: {top_factors[0] if top_factors else 'Abnormal activity pattern'}",
                message=explanation["narrative"],
                anomaly_type=explanation["mitre_mapping"][0]["name"] if explanation["mitre_mapping"] else "BEHAVIORAL_DEVIATION",
                risk_score=final_risk
            )
            db.add(alert)
            db.commit()

    return {
        "employee_id": employee_id,
        "overall_risk_score": final_risk,
        "threat_level": threat_level,
        "anomaly_detected": is_anomaly,
        "anomaly_score": round(anomaly_score, 3),
        "top_risk_factors": top_factors,
        "mitre_mapping": explanation["mitre_mapping"],
        "recommended_actions": explanation["recommended_actions"],
        "ai_narrative": explanation["narrative"],
        "analyzed_event_count": len(logs)
    }

@router.post("/analyze-all")
def analyze_all_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Batch runs the AI engine over all registered employees."""
    employees = db.query(Employee).all()
    results = []
    for emp in employees:
        logs = doc_db.activity_logs.find(query={"employee_id": emp.employee_id}, limit=30)
        baseline = doc_db.behavioral_baselines.find_one({"employee_id": emp.employee_id}) or {}
        is_anomaly, anomaly_score, indicators = anomaly_detector.detect_anomalies(logs, baseline)
        final_risk, threat_level, top_factors = risk_scorer.compute_risk(
            base_employee_risk=emp.baseline_risk_score or 15.0,
            anomaly_detected=is_anomaly,
            anomaly_score=anomaly_score,
            indicators=indicators,
            logs=logs
        )
        emp.baseline_risk_score = final_risk
        results.append({
            "employee_id": emp.employee_id,
            "name": emp.name,
            "department": emp.department,
            "risk_score": final_risk,
            "threat_level": threat_level,
            "anomaly_detected": is_anomaly
        })
    db.commit()
    return {
        "total_analyzed": len(results),
        "summary": results
    }
