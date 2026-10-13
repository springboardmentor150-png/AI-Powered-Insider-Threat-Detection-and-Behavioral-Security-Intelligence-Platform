from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Incident, Evidence
from app.risk_scoring import calculate_risk_score

router = APIRouter(prefix="/investigation", tags=["Threat Investigation"])

@router.post("/incidents/create-from-risk/{employee_id}")
def create_incident_from_risk(employee_id: str, db: Session = Depends(get_db)):
    risk = calculate_risk_score(employee_id)
    if risk["risk_category"] not in ("high", "critical"):
        raise HTTPException(status_code=400, detail="Risk level too low to warrant an incident")

    incident = Incident(
        employee_id=employee_id,
        severity=risk["risk_category"],
        summary=f"Auto-created from risk score {risk['risk_score']}"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.get("/incidents")
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.id.desc()).all()

@router.get("/incidents/{incident_id}/timeline")
def get_incident_timeline(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Demo timeline representing the merged activity/anomaly investigation view.
    timeline = [
        {"type": "activity", "timestamp": "09:10", "detail": "Login"},
        {"type": "activity", "timestamp": "09:25", "detail": "File Access"},
        {"type": "anomaly", "timestamp": "09:42", "detail": "Unusual Download"},
        {"type": "anomaly", "timestamp": "10:05", "detail": "Privilege Change"},
        {"type": "anomaly", "timestamp": "10:20", "detail": "Data Exfiltration"},
    ]
    return {"incident_id": incident_id, "employee_id": incident.employee_id, "timeline": timeline}

@router.post("/incidents/{incident_id}/evidence")
def add_evidence(incident_id: int, note: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    evidence = Evidence(incident_id=incident_id, note=note)
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence

@router.patch("/incidents/{incident_id}/status")
def update_incident_status(incident_id: int, status: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if status not in {"open", "investigating", "resolved"}:
        raise HTTPException(status_code=400, detail="Invalid status")
    incident.status = status
    db.commit()
    db.refresh(incident)
    return incident
