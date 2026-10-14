from app.database import SessionLocal
from app.models import Alert, Incident
from sqlalchemy import inspect
from app.main import app

db = SessionLocal()

try:
    print("=== Alert records ===")
    print("Total alerts:", db.query(Alert).count())

    for alert in db.query(Alert).order_by(Alert.id).limit(10).all():
        print({
            "id": alert.id,
            "incident_id": alert.incident_id,
            "employee_id": alert.employee_id,
            "severity": alert.severity,
            "status": alert.status,
            "assigned_to": alert.assigned_to,
            "created_at": str(alert.created_at),
        })

    print("\n=== Alert database columns ===")
    inspector = inspect(db.get_bind())
    print([column["name"] for column in inspector.get_columns("alerts")])

    print("\n=== Existing alert and analytics routes ===")
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            if "alert" in route.path.lower() or "analytics" in route.path.lower():
                print(sorted(route.methods), route.path)

finally:
    db.close()
