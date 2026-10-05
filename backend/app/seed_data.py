# backend/app/seed_data.py
from datetime import datetime, timedelta
from app.database import engine, Base, SessionLocal, mongo_db
from app.models import User, Employee, Incident, Alert, Evidence, AuditLog
from app.auth import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Users (All 4 RBAC Roles)
        existing_user = db.query(User).first()
        if not existing_user:
            default_password = hash_password("Security@123")
            users = [
                User(email="admin@itbis.security", password_hash=default_password, full_name="Sarah Connor (Administrator)", role="admin", is_active=True),
                User(email="analyst@itbis.security", password_hash=default_password, full_name="Alex Rivera (Lead Threat Analyst)", role="security_analyst", is_active=True),
                User(email="manager@itbis.security", password_hash=default_password, full_name="Marcus Vance (SOC Director)", role="security_manager", is_active=True),
                User(email="soc@itbis.security", password_hash=default_password, full_name="Priya Sharma (SOC Engineer)", role="soc_engineer", is_active=True),
            ]
            db.add_all(users)
            db.commit()
            print("[INFO] Seeded default users (Admin, Analyst, Manager, SOC).")

        # 2. Seed Employees
        existing_emp = db.query(Employee).first()
        if not existing_emp:
            employees = [
                # Engineering peers (Elena & Liam)
                Employee(
                    employee_id="EMP1001",
                    name="Elena Rostova",
                    department="Engineering",
                    designation="Senior Backend Architect",
                    device_info="MacBook Pro M3 - Host: elena-mbp-eng",
                    access_privileges="CORE_REPO_RW, PROD_READONLY, K8S_DEV",
                    status="ACTIVE",
                    baseline_risk_score=18.5
                ),
                Employee(
                    employee_id="EMP1005",
                    name="Liam O'Connor",
                    department="Engineering",
                    designation="Frontend Developer",
                    device_info="MacBook Air - Host: liam-fe-08",
                    access_privileges="FRONTEND_REPO_RW, FIGMA_ORG",
                    status="ACTIVE",
                    baseline_risk_score=12.0
                ),
                # Finance (Jonathan)
                Employee(
                    employee_id="EMP1002",
                    name="Jonathan Hayes",
                    department="Finance",
                    designation="Senior Financial Analyst",
                    device_info="Dell XPS 15 - Host: jhayes-fin-02",
                    access_privileges="FINANCE_PORTAL, ERP_GL_READ, STRIPE_DASHBOARD",
                    status="ACTIVE",
                    baseline_risk_score=78.0
                ),
                # Cloud Ops (Devon)
                Employee(
                    employee_id="EMP1003",
                    name="Devon Miller",
                    department="Cloud Ops",
                    designation="Principal DevOps Engineer",
                    device_info="ThinkPad P1 - Host: devon-ops-linux",
                    access_privileges="AWS_ADMIN_SUPER, ROOT_SSH_BASTION, VAULT_OPERATOR",
                    status="UNDER_REVIEW",
                    baseline_risk_score=89.5
                ),
                # HR (Amina)
                Employee(
                    employee_id="EMP1004",
                    name="Amina Al-Mansoor",
                    department="Human Resources",
                    designation="Talent Acquisition Director",
                    device_info="Lenovo ThinkPad - Host: amina-hr-01",
                    access_privileges="WORKDAY_ADMIN, GREENHOUSE_RW",
                    status="ACTIVE",
                    baseline_risk_score=14.0
                ),
                # IT Ops (Sophia)
                Employee(
                    employee_id="EMP1006",
                    name="Sophia Chen",
                    department="IT Ops",
                    designation="Database Administrator",
                    device_info="Precision 5570 - Host: sophia-dba-01",
                    access_privileges="POSTGRES_SUPERUSER, SNOWFLAKE_ADMIN",
                    status="ACTIVE",
                    baseline_risk_score=45.0
                ),
                # Solo Department (Legal - 0 peers edge case testing)
                Employee(
                    employee_id="EMP1008",
                    name="Zoe Washington",
                    department="Legal",
                    designation="Chief Compliance Officer",
                    device_info="Dell Latitude - Host: zoe-legal-01",
                    access_privileges="LEGAL_DOCS_READ",
                    status="ACTIVE",
                    baseline_risk_score=8.0
                )
            ]
            db.add_all(employees)
            db.commit()
            print(f"[INFO] Seeded {len(employees)} corporate employees.")

        # 3. Seed Milestone 2 / 3 Rule & ML Anomalies Collections
        now = datetime.utcnow()
        # Always ensure rich rule anomalies exist
        mongo_db["rule_anomalies"].delete_many({})
        rule_anomalies = [
            # Critical employee: Devon Miller (EMP1003) -> score ~86.1 (critical >= 75)
            {"employee_id": "EMP1003", "anomaly_type": "privilege_change", "severity": "critical", "detected_at": now - timedelta(days=2)},
            {"employee_id": "EMP1003", "anomaly_type": "privilege_change", "severity": "critical", "detected_at": now - timedelta(days=2, hours=1)},
            {"employee_id": "EMP1003", "anomaly_type": "privilege_change", "severity": "critical", "detected_at": now - timedelta(days=2, hours=2)},
            {"employee_id": "EMP1003", "anomaly_type": "data_exfiltration", "severity": "critical", "detected_at": now - timedelta(days=2, hours=4)},
            {"employee_id": "EMP1003", "anomaly_type": "data_exfiltration", "severity": "critical", "detected_at": now - timedelta(days=2, hours=5)},
            {"employee_id": "EMP1003", "anomaly_type": "unusual_hours", "severity": "high", "detected_at": now - timedelta(days=3)},
            {"employee_id": "EMP1003", "anomaly_type": "unusual_ip", "severity": "high", "detected_at": now - timedelta(days=3, hours=3)},
            {"employee_id": "EMP1003", "anomaly_type": "mass_download", "severity": "high", "detected_at": now - timedelta(days=5)},

            # High risk employee: Jonathan Hayes (EMP1002) -> score ~53.5 (high >= 50)
            {"employee_id": "EMP1002", "anomaly_type": "privilege_change", "severity": "medium", "detected_at": now - timedelta(days=1)},
            {"employee_id": "EMP1002", "anomaly_type": "data_exfiltration", "severity": "high", "detected_at": now - timedelta(days=1, hours=2)},
            {"employee_id": "EMP1002", "anomaly_type": "unusual_access", "severity": "medium", "detected_at": now - timedelta(days=4)},
            {"employee_id": "EMP1002", "anomaly_type": "unusual_time", "severity": "medium", "detected_at": now - timedelta(days=4, hours=2)},
            {"employee_id": "EMP1002", "anomaly_type": "unusual_device", "severity": "medium", "detected_at": now - timedelta(days=4, hours=4)},

            # Medium risk employee: Sophia Chen (EMP1006) -> score ~32.0 (medium >= 25)
            {"employee_id": "EMP1006", "anomaly_type": "unusual_volume", "severity": "medium", "detected_at": now - timedelta(days=6)},
            {"employee_id": "EMP1006", "anomaly_type": "unusual_query", "severity": "medium", "detected_at": now - timedelta(days=6, hours=2)},

            # Low risk employee: Elena (EMP1001) -> score ~3.5 (low < 25)
            {"employee_id": "EMP1001", "anomaly_type": "minor_timing", "severity": "low", "detected_at": now - timedelta(days=12)},
        ]
        mongo_db["rule_anomalies"].insert_many(rule_anomalies)

        mongo_db["ml_anomalies"].delete_many({})
        ml_anomalies = [
            {"employee_id": "EMP1003", "is_anomaly": True, "anomaly_score": 0.94, "detected_at": now - timedelta(days=2)},
            {"employee_id": "EMP1003", "is_anomaly": True, "anomaly_score": 0.91, "detected_at": now - timedelta(days=2, hours=3)},
            {"employee_id": "EMP1003", "is_anomaly": True, "anomaly_score": 0.88, "detected_at": now - timedelta(days=3)},
            {"employee_id": "EMP1003", "is_anomaly": True, "anomaly_score": 0.85, "detected_at": now - timedelta(days=4)},
            {"employee_id": "EMP1002", "is_anomaly": True, "anomaly_score": 0.76, "detected_at": now - timedelta(days=1)},
            {"employee_id": "EMP1002", "is_anomaly": True, "anomaly_score": 0.71, "detected_at": now - timedelta(days=2)},
            {"employee_id": "EMP1006", "is_anomaly": False, "anomaly_score": 0.32, "detected_at": now - timedelta(days=6)},
            {"employee_id": "EMP1001", "is_anomaly": False, "anomaly_score": 0.12, "detected_at": now - timedelta(days=12)},
        ]
        mongo_db["ml_anomalies"].insert_many(ml_anomalies)

        # 4. Seed Activity Logs
        if mongo_db["activity_logs"].count_documents() == 0:
            logs = [
                {"employee_id": "EMP1003", "event_type": "login", "details": {"ip": "185.220.101.5", "off_hours": True}, "timestamp": now - timedelta(days=2, hours=6)},
                {"employee_id": "EMP1003", "event_type": "privilege_escalation", "details": {"cmd": "sudo su"}, "timestamp": now - timedelta(days=2, hours=5)},
                {"employee_id": "EMP1003", "event_type": "database_dump", "details": {"rows": 12000}, "timestamp": now - timedelta(days=2, hours=4)},
                {"employee_id": "EMP1002", "event_type": "file_download", "details": {"file": "payroll.xlsx", "size_mb": 140}, "timestamp": now - timedelta(days=1)},
                {"employee_id": "EMP1001", "event_type": "git_commit", "details": {"lines": 45}, "timestamp": now - timedelta(hours=5)}
            ]
            mongo_db["activity_logs"].insert_many(logs)

        # 5. Seed Initial Alerts
        existing_alert = db.query(Alert).first()
        if not existing_alert:
            alerts = [
                Alert(
                    alert_code="ALT-10082",
                    employee_id="EMP1003",
                    severity="critical",
                    message="Tor exit node login followed by sudo privilege escalation and customer secret keys query.",
                    status="open",
                    risk_score=92.5
                ),
                Alert(
                    alert_code="ALT-10083",
                    employee_id="EMP1002",
                    severity="high",
                    message="Unauthorized Kingston USB storage device mounted after unredacted payroll file download.",
                    status="open",
                    risk_score=78.0
                ),
                Alert(
                    alert_code="ALT-10084",
                    employee_id="EMP1006",
                    severity="medium",
                    message="Database read volume exceeded 3x normal hourly baseline during maintenance.",
                    status="assigned",
                    risk_score=45.0
                )
            ]
            db.add_all(alerts)
            db.commit()

        # 6. Seed Initial Incident & Evidence
        existing_inc = db.query(Incident).first()
        if not existing_inc:
            inc = Incident(
                incident_code="INC-2026-001",
                employee_id="EMP1003",
                title="Cloud Infrastructure Compromise & Data Exfiltration",
                severity="critical",
                status="investigating",
                summary="Auto-created from risk score 92.5",
                assigned_to="analyst@itbis.security"
            )
            db.add(inc)
            db.commit()
            db.refresh(inc)

            ev1 = Evidence(
                incident_id=inc.id,
                note="Tor exit node IP 185.220.101.5 confirmed in firewall flow telemetry.",
                added_by=1
            )
            ev2 = Evidence(
                incident_id=inc.id,
                note="AWS IAM credentials for shadow_admin_backdoor revoked by Cloud Security team.",
                added_by=2
            )
            db.add_all([ev1, ev2])
            db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()