from datetime import datetime, timedelta
from app.models import Employee
from app.risk_scoring import calculate_risk_score
from app.database import mongo_db

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
        "department": employee.department,
        "department_avg_score": round(peer_avg, 1),
        "deviation_from_peers": round(employee_score - peer_avg, 1),
        "peer_count": len(peer_scores),
    }

def get_risk_trend(employee_id: str, days: int = 30) -> list[dict]:
    cutoff = datetime.utcnow() - timedelta(days=days)

    if mongo_db is not None:
        try:
            anomalies = mongo_db["rule_anomalies"].find({
                "employee_id": employee_id,
                "detected_at": {"$gte": cutoff}
            })
            daily_counts = {}
            for a in anomalies:
                detected = a.get("detected_at")
                if hasattr(detected, "date"):
                    key = str(detected.date())
                else:
                    key = str(detected)[:10]
                daily_counts[key] = daily_counts.get(key, 0) + 1
            return sorted(
                [{"date": k, "anomaly_count": v} for k, v in daily_counts.items()],
                key=lambda x: x["date"]
            )
        except Exception:
            pass

    # Demo trend fallback
    base = {
        "EMP-1001": [1, 2, 3, 4, 6, 8, 9],
        "EMP-1002": [0, 1, 1, 2, 2, 3, 2],
        "EMP-1003": [0, 0, 1, 0, 1, 0, 1],
        "EMP-1004": [1, 1, 2, 3, 3, 4, 5],
        "EMP-1005": [1, 2, 2, 4, 5, 6, 7],
    }.get(employee_id, [0, 1, 0, 1, 2, 1, 2])
    today = datetime.utcnow().date()
    return [
        {"date": str(today - timedelta(days=len(base)-1-i)), "anomaly_count": v}
        for i, v in enumerate(base)
    ]
