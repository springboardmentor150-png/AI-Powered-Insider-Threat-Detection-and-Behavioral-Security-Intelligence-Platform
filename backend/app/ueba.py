from datetime import datetime, timedelta
from .database import mongo_db
from .models import Employee
from .risk_scoring import calculate_risk_score

def compare_to_peers(db, employee_id: str) -> dict:
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        return {"employee_id": employee_id, "note": "Employee not found"}
    peers = db.query(Employee).filter(
        Employee.department == employee.department,
        Employee.employee_id != employee_id
    ).all()
    employee_score = calculate_risk_score(employee_id)["risk_score"]
    peer_scores = [calculate_risk_score(p.employee_id)["risk_score"] for p in peers]
    if not peer_scores:
        return {"employee_id": employee_id, "note": "No peers in department for comparison"}
    peer_avg = sum(peer_scores) / len(peer_scores)
    return {
        "employee_id": employee_id,
        "employee_score": employee_score,
        "department_avg_score": round(peer_avg, 1),
        "deviation_from_peers": round(employee_score - peer_avg, 1),
        "peer_count": len(peer_scores),
    }

def get_risk_trend(employee_id: str, days: int = 30) -> list[dict]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    anomalies = mongo_db["rule_anomalies"].find({
        "employee_id": employee_id,
        "detected_at": {"$gte": cutoff}
    })
    daily_counts = {}
    for a in anomalies:
        day_key = str(a["detected_at"].date())
        daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
    return sorted(
        [{"date": k, "anomaly_count": v} for k, v in daily_counts.items()],
        key=lambda x: x["date"]
    )
