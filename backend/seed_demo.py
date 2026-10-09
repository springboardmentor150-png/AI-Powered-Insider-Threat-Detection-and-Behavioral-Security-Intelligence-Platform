import os
import sys
from datetime import datetime, timezone, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app.models import User, Employee, Alert, Incident
from app.auth import hash_password
from app.mongo_database import db, activity_logs_collection
from app.analytics import generate_baseline, detect_anomalies, calculate_risk_score

def reset_and_seed():
    print("Resetting database...")
    # Recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Reset Mongo
    print("Resetting MongoDB...")
    db.activity_logs.delete_many({})
    db.baselines.delete_many({})
    db.risk_scores.delete_many({})

    db_session = SessionLocal()
    try:
        # User Accounts
        print("Creating demo accounts...")
        accounts = [
            ("admin@itbis.demo", "demo123", "ADMIN"),
            ("manager@itbis.demo", "demo123", "SECURITY_MANAGER"),
            ("analyst@itbis.demo", "demo123", "SECURITY_ANALYST"),
            ("soc@itbis.demo", "demo123", "SOC_ENGINEER")
        ]
        users = []
        for email, pwd, role in accounts:
            u = User(email=email, password_hash=hash_password(pwd), role=role)
            db_session.add(u)
            users.append(u)
        db_session.commit()

        admin_user = users[0]
        manager_user = users[1]

        # Employees
        print("Creating employees...")
        departments = ["Finance", "Engineering", "HR", "Operations", "Sales", "IT", "Legal", "Marketing", "Facilities"]
        designations = ["Analyst", "Developer", "Manager", "Technician", "Executive", "Sysadmin", "Director", "Consultant"]
        devices = ["MacBook Pro", "Dell XPS", "ThinkPad", "MacBook Air", "Chromebook", "Linux Workstation"]
        privileges = ["Standard", "High", "Elevated", "Root"]
        
        employees_data = []
        for i in range(1, 31):
            emp_id = f"EMP-{i:03d}"
            name = f"Test Employee {i}"
            dept = departments[i % len(departments)]
            desig = designations[i % len(designations)]
            device = devices[i % len(devices)]
            priv = privileges[i % len(privileges)]
            
            employees_data.append({
                "employee_id": emp_id,
                "name": name,
                "department": dept,
                "designation": desig,
                "manager_id": manager_user.id,
                "device_info": device,
                "access_privileges": priv
            })
        
        for ed in employees_data:
            e = Employee(**ed)
            db_session.add(e)
        db_session.commit()

        # Seed Activity Logs
        print("Seeding activity logs...")
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        
        def insert_log(emp_id, event, offset_hours, details, is_abnormal=False):
            ts = base_time + timedelta(hours=offset_hours)
            if is_abnormal:
                ts = datetime.now(timezone.utc) - timedelta(hours=1)
            activity_logs_collection.insert_one({
                "employee_id": emp_id,
                "event_type": event,
                "timestamp": ts,
                "details": details
            })

        # Normal activity for all 30
        for i in range(24):
            for emp in employees_data:
                emp_id = emp["employee_id"]
                insert_log(emp_id, "login", i*6, {"device": emp["device_info"], "ip": "10.0.0.1"})
                insert_log(emp_id, "file_access", i*6 + 1, {"count": 2})

        # Risky Activity for 10 endpoints
        print("Generating anomalous behavior for HIGH RISK endpoints...")
        risky_employees = employees_data[-10:] # Last 10 employees
        for risk_emp in risky_employees:
            r_id = risk_emp["employee_id"]
            insert_log(r_id, "login", 0, {"device": "Unknown-Device", "ip": "192.168.100.50"}, is_abnormal=True)
            insert_log(r_id, "file_download", 0, {"count": 60, "device": "Unknown-Device", "folder": "/confidential/"}, is_abnormal=True)
            
            if int(r_id.split("-")[1]) % 2 == 0:
                insert_log(r_id, "unauthorized_access", 0, {"status": "denied", "target": "/etc/shadow"}, is_abnormal=True)

        # Generate Baselines
        print("Running behavioral pipelines for all 30 records...")
        for ed in employees_data:
            generate_baseline(ed["employee_id"])
            anoms = detect_anomalies(ed["employee_id"], db_session)
            calculate_risk_score(ed["employee_id"])
            
        # Seed incidents for all alerts
        alerts = db_session.query(Alert).all()
        for idx, a in enumerate(alerts):
            status = "investigating" if idx % 2 == 0 else "open"
            assignee = manager_user.id if idx % 2 == 0 else admin_user.id
            inc = Incident(
                alert_id=a.id,
                assigned_to=assignee,
                status=status,
                notes=f"Auto-escalated Incident INC-{idx+1} during batch threat parsing."
            )
            db_session.add(inc)
            
        db_session.commit()
        print(f"Seeded {len(alerts)} Alerts and Incidents")
            
        print("Seeding complete! Demo environment ready.")

    finally:
        db_session.close()

if __name__ == "__main__":
    reset_and_seed()
