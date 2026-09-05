# backend/app/seed_data.py
from datetime import datetime, timedelta
from app.database import engine, Base, SessionLocal, doc_db
from app.models import User, Employee, Incident, Alert, AuditLog
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
                    employee_id="EMP1002",
                    name="Jonathan Hayes",
                    department="Finance",
                    designation="Senior Financial Analyst",
                    device_info="Dell XPS 15 - Host: jhayes-fin-02",
                    access_privileges="FINANCE_PORTAL, ERP_GL_READ, STRIPE_DASHBOARD",
                    status="ACTIVE",
                    baseline_risk_score=78.0 # Simulated high risk
                ),
                Employee(
                    employee_id="EMP1003",
                    name="Devon Miller",
                    department="Cloud Ops",
                    designation="Principal DevOps Engineer",
                    device_info="ThinkPad P1 - Host: devon-ops-linux",
                    access_privileges="AWS_ADMIN_SUPER, ROOT_SSH_BASTION, VAULT_OPERATOR",
                    status="UNDER_REVIEW",
                    baseline_risk_score=89.5 # Simulated critical risk
                ),
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
                Employee(
                    employee_id="EMP1006",
                    name="Sophia Chen",
                    department="IT Ops",
                    designation="Database Administrator",
                    device_info="Precision 5570 - Host: sophia-dba-01",
                    access_privileges="POSTGRES_SUPERUSER, SNOWFLAKE_ADMIN",
                    status="ACTIVE",
                    baseline_risk_score=45.0
                )
            ]
            db.add_all(employees)
            db.commit()
            print(f"[INFO] Seeded {len(employees)} corporate employees.")

            # Seed Document Store Baselines
            for emp in employees:
                doc_db.behavioral_baselines.insert_one({
                    "employee_id": emp.employee_id,
                    "avg_daily_events": 30,
                    "avg_daily_download_mb": 25.0,
                    "allowed_devices": [emp.device_info],
                    "typical_work_hours": "09:00 - 18:00 UTC",
                    "last_updated": datetime.utcnow().isoformat()
                })

        # 3. Seed Document Store Activity Logs
        if doc_db.activity_logs.count_documents() == 0:
            now = datetime.utcnow()
            initial_logs = [
                # Normal logs for Elena
                {"employee_id": "EMP1001", "event_type": "login", "details": {"ip_address": "10.14.2.19", "device": "elena-mbp-eng"}, "timestamp": now - timedelta(hours=8)},
                {"employee_id": "EMP1001", "event_type": "git_commit", "details": {"repo": "auth-service", "lines": 82}, "timestamp": now - timedelta(hours=6)},
                {"employee_id": "EMP1001", "event_type": "file_download", "details": {"file_name": "api_spec_v2.json", "size_mb": 3.4}, "timestamp": now - timedelta(hours=4)},
                
                # Suspicious logs for Jonathan Hayes (Finance)
                {"employee_id": "EMP1002", "event_type": "login", "details": {"ip_address": "192.168.1.104", "device": "jhayes-fin-02", "is_off_hours": True}, "timestamp": now - timedelta(hours=22)},
                {"employee_id": "EMP1002", "event_type": "file_download", "details": {"file_name": "q3_q4_unredacted_payroll.xlsx", "size_mb": 145.0, "is_confidential": True}, "timestamp": now - timedelta(hours=21, minutes=45)},
                {"employee_id": "EMP1002", "event_type": "usb_connect", "details": {"vendor_id": "Kingston_DT_64G", "serial": "KDT-88219"}, "timestamp": now - timedelta(hours=21, minutes=30)},

                # Highly critical compromised scenario for Devon Miller
                {"employee_id": "EMP1003", "event_type": "login", "details": {"ip_address": "185.220.101.5", "geo_country": "TOR_EXIT", "is_off_hours": True}, "timestamp": now - timedelta(hours=14)},
                {"employee_id": "EMP1003", "event_type": "privilege_escalation", "details": {"command": "sudo -i", "sudo": True}, "timestamp": now - timedelta(hours=13, minutes=50)},
                {"employee_id": "EMP1003", "event_type": "database_query", "details": {"table_name": "customer_secrets", "rows_accessed": 12000}, "timestamp": now - timedelta(hours=13, minutes=40)},
                {"employee_id": "EMP1003", "event_type": "file_download", "details": {"file_name": "vault_secrets_backup.tar.gz", "size_mb": 350.0, "is_confidential": True}, "timestamp": now - timedelta(hours=13, minutes=30)}
            ]
            doc_db.activity_logs.insert_many(initial_logs)
            print("[INFO] Seeded realistic activity telemetry in document store.")

        # 4. Seed Initial Alerts
        existing_alert = db.query(Alert).first()
        if not existing_alert:
            alerts = [
                Alert(
                    alert_code="ALT-10082",
                    employee_id="EMP1003",
                    severity="CRITICAL",
                    title="Suspicious Off-Hours Root Privilege Escalation & Database Dump",
                    message="Employee Devon Miller triggered critical alerts: Tor exit node IP login followed by sudo escalation and 12,000 secret keys query.",
                    anomaly_type="PRIVILEGE_ESCALATION",
                    risk_score=92.5,
                    is_acknowledged=False,
                    is_escalated=True
                ),
                Alert(
                    alert_code="ALT-10083",
                    employee_id="EMP1002",
                    severity="HIGH",
                    title="Removable USB Mass Storage Connected Post-Download",
                    message="Unapproved Kingston USB device connected after downloading confidential unredacted payroll document.",
                    anomaly_type="USB_EXFILTRATION",
                    risk_score=78.0,
                    is_acknowledged=False,
                    is_escalated=False
                ),
                Alert(
                    alert_code="ALT-10084",
                    employee_id="EMP1006",
                    severity="MEDIUM",
                    title="Elevated Read Volume on Production DB Replica",
                    message="Database read volume exceeded 3x normal hourly baseline during maintenance window.",
                    anomaly_type="DATABASE_SCRAPING",
                    risk_score=45.0,
                    is_acknowledged=True,
                    is_escalated=False
                )
            ]
            db.add_all(alerts)
            db.commit()

        # 5. Seed Initial Incident
        existing_inc = db.query(Incident).first()
        if not existing_inc:
            incident = Incident(
                incident_code="INC-2026-001",
                employee_id="EMP1003",
                title="Active Cloud Infrastructure Compromise & Data Exfiltration",
                description="Devon Miller's account was observed executing unauthorized sudo commands and dumping customer vault credentials via Tor exit node.",
                severity="CRITICAL",
                status="INVESTIGATING",
                assigned_to="analyst@itbis.security",
                mitre_attack_technique="T1078 / T1548 - Valid Accounts & Privilege Escalation",
                ai_summary="AI Analysis confirms high-confidence credential compromise. Recommend immediate session revocation and AWS IAM key rotation."
            )
            db.add(incident)
            db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
