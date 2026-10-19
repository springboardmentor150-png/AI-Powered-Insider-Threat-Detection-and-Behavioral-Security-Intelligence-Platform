import json
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, Employee, Alert, Incident, BehavioralBaseline, RiskScoreHistory, Notification, InvestigationNote, AuditLog
from app.mongodb import mongo_service
from app.auth import hash_password

logger = logging.getLogger("itbis.seed")


def seed_initial_data(db: Session):
    try:
        now = datetime.now(timezone.utc)

        admin_user = db.query(User).filter(func.lower(User.email) == "admin@itbis.cyber").first()
        if not admin_user:
            logger.info("Seeding default Admin SOC account...")
            admin_user = User(
                email="admin@itbis.cyber",
                password_hash=hash_password("AdminPassword123!"),
                role="ADMIN"
            )
            db.add(admin_user)

        analyst_user = db.query(User).filter(func.lower(User.email) == "analyst@itbis.cyber").first()
        if not analyst_user:
            logger.info("Seeding default Analyst SOC account...")
            analyst_user = User(
                email="analyst@itbis.cyber",
                password_hash=hash_password("AnalystPassword123!"),
                role="ANALYST"
            )
            db.add(analyst_user)

        manager_user = db.query(User).filter(func.lower(User.email).in_(["manager@itbis.cyber", "manager@itbis.com"])).first()
        if not manager_user:
            logger.info("Seeding default Security Manager account...")
            manager_user = User(
                email="manager@itbis.cyber",
                password_hash=hash_password("ManagerPassword123!"),
                role="SECURITY_MANAGER"
            )
            db.add(manager_user)

        engineer_user = db.query(User).filter(func.lower(User.email) == "engineer@itbis.cyber").first()
        if not engineer_user:
            logger.info("Seeding default SOC Engineer account...")
            engineer_user = User(
                email="engineer@itbis.cyber",
                password_hash=hash_password("EngineerPassword123!"),
                role="SOC_ENGINEER"
            )
            db.add(engineer_user)

        db.commit()

        # ============================================================
        # 1. PostgreSQL Enterprise Employees & Entities
        # ============================================================
        employee_count = db.query(Employee).count()
        if employee_count == 0:
            logger.info("Initializing enterprise employee dataset in PostgreSQL...")

            employees_data = [
                {
                    "employee_id": "CYB-1042",
                    "name": "Sarah Connor",
                    "email": "s.connor@enterprise.corp",
                    "department": "Cybersecurity",
                    "designation": "Senior Security Engineer",
                    "manager_name": "David Vance (CISO)",
                    "employment_type": "Full-time",
                    "work_location": "Hyderabad",
                    "joining_date": "2021-03-15",
                    "years_of_experience": 7,
                    "education": "M.Tech Cybersecurity",
                    "previous_role": "SOC Analyst II",
                    "skills": "SIEM, IAM, Network Security, Threat Hunting",
                    "professional_summary": "7+ years defending enterprise infrastructure, managing SIEM pipelines and privileged access governance.",
                    "device_info": "MacBook Pro M3 (SEC-D-991)",
                    "access_privileges": "SIEM_ADMIN, IAM_READ, VAULT_READ",
                    "risk_score": 24,
                    "risk_level": "LOW",
                    "status": "ACTIVE",
                },
                {
                    "employee_id": "FIN-2187",
                    "name": "Alexander Hayes",
                    "email": "a.hayes@enterprise.corp",
                    "department": "Finance",
                    "designation": "Financial Analyst",
                    "manager_name": "Arthur Miller (VP Finance)",
                    "employment_type": "Full-time",
                    "work_location": "Hyderabad",
                    "joining_date": "2022-06-01",
                    "years_of_experience": 5,
                    "education": "MBA Finance",
                    "previous_role": "Junior Treasury Analyst",
                    "skills": "Financial Analysis, Excel, ERP, SAP, Budgeting",
                    "professional_summary": "5 years in corporate treasury and financial reporting. Handles quarterly forecasting and ERP ledgers.",
                    "device_info": "ThinkPad X1 Carbon (FIN-D-102)",
                    "access_privileges": "ERP_FINANCE, SHAREPOINT_CONFIDENTIAL",
                    "risk_score": 78,
                    "risk_level": "HIGH",
                    "status": "UNDER_REVIEW",
                },
                {
                    "employee_id": "IT-3064",
                    "name": "Marcus Vance",
                    "email": "m.vance@enterprise.corp",
                    "department": "IT",
                    "designation": "Systems Administrator",
                    "manager_name": "Rachel Lin (VP Tech Ops)",
                    "employment_type": "Full-time",
                    "work_location": "Hyderabad",
                    "joining_date": "2020-09-10",
                    "years_of_experience": 8,
                    "education": "B.Tech Computer Science",
                    "previous_role": "Infrastructure Engineer",
                    "skills": "Linux, Cloud Infrastructure, Active Directory, LDAP, Terraform",
                    "professional_summary": "8 years managing core directory services, Linux server clusters, and enterprise identity federation.",
                    "device_info": "Dell Precision 5570 (IT-D-303)",
                    "access_privileges": "ACTIVE_DIRECTORY_ADMIN, LINUX_ROOT, CLOUD_OPS",
                    "risk_score": 85,
                    "risk_level": "CRITICAL",
                    "status": "FLAGGED",
                },
                {
                    "employee_id": "HR-4128",
                    "name": "Samantha Wright",
                    "email": "s.wright@enterprise.corp",
                    "department": "HR",
                    "designation": "HR Operations Specialist",
                    "manager_name": "Rachel Adams (Chief People Officer)",
                    "employment_type": "Full-time",
                    "work_location": "Hyderabad",
                    "joining_date": "2023-01-20",
                    "years_of_experience": 4,
                    "education": "MBA HR",
                    "previous_role": "Talent Operations Associate",
                    "skills": "HRIS, Payroll, Employee Operations, Workday",
                    "professional_summary": "4 years overseeing employee onboarding, compensation workflows, and HRIS data governance.",
                    "device_info": "MacBook Air M2 (HR-D-210)",
                    "access_privileges": "WORKDAY_HRIS, PAYROLL_READ",
                    "risk_score": 18,
                    "risk_level": "LOW",
                    "status": "ACTIVE",
                },
                {
                    "employee_id": "DEV-5271",
                    "name": "Vikram Malhotra",
                    "email": "v.malhotra@enterprise.corp",
                    "department": "DevOps",
                    "designation": "DevOps Engineer",
                    "manager_name": "Sarah Lin (VP Engineering)",
                    "employment_type": "Full-time",
                    "work_location": "Hyderabad",
                    "joining_date": "2021-11-05",
                    "years_of_experience": 6,
                    "education": "B.Tech Information Technology",
                    "previous_role": "Site Reliability Engineer",
                    "skills": "AWS, Docker, Kubernetes, CI/CD, Helm, Prometheus",
                    "professional_summary": "6 years building resilient cloud deployments, Kubernetes runtime orchestration, and automated CI/CD pipelines.",
                    "device_info": "Ubuntu DevStation (ENG-D-119)",
                    "access_privileges": "KUBERNETES_CLUSTER_ADMIN, AWS_PROD_DEPLOY",
                    "risk_score": 42,
                    "risk_level": "MEDIUM",
                    "status": "ACTIVE",
                },
                {
                    "employee_id": "CMP-6385",
                    "name": "Claire Dupont",
                    "email": "c.dupont@enterprise.corp",
                    "department": "Compliance",
                    "designation": "Compliance Analyst",
                    "manager_name": "Arthur Vance (General Counsel)",
                    "employment_type": "Full-time",
                    "work_location": "Hyderabad",
                    "joining_date": "2022-04-12",
                    "years_of_experience": 6,
                    "education": "MBA Compliance",
                    "previous_role": "Internal Auditor",
                    "skills": "GRC, Auditing, Policy Management, ISO 27001, SOC2",
                    "professional_summary": "6 years conducting internal security audits, regulatory compliance checks, and enterprise risk governance.",
                    "device_info": "Surface Pro 9 (CMP-D-512)",
                    "access_privileges": "AUDIT_VAULT, GRC_PORTAL",
                    "risk_score": 12,
                    "risk_level": "LOW",
                    "status": "ACTIVE",
                },
            ]

            created_employees = []
            for emp_dict in employees_data:
                emp = Employee(**emp_dict)
                db.add(emp)
                created_employees.append(emp)

            db.commit()
            for emp in created_employees:
                db.refresh(emp)

            # Seed Baselines in PostgreSQL
            baselines = [
                (created_employees[0], 8, 17, 45, 500, ["SEC-D-991"], ["192.168.1.10", "10.0.1.5"]),
                (created_employees[1], 9, 18, 0, 300, ["FIN-D-102"], ["192.168.1.15", "10.0.2.20"]),
                (created_employees[2], 8, 17, 0, 1000, ["IT-D-303"], ["192.168.1.25", "10.0.3.10"]),
                (created_employees[3], 9, 18, 30, 200, ["HR-D-210"], ["192.168.1.40", "10.0.4.15"]),
                (created_employees[4], 10, 19, 0, 800, ["ENG-D-119"], ["192.168.1.50", "10.0.5.30"]),
                (created_employees[5], 9, 17, 30, 250, ["CMP-D-512"], ["192.168.1.60", "10.0.6.25"]),
            ]

            for emp, s_hr, e_hr, _, dl_limit, devs, ips in baselines:
                bl = BehavioralBaseline(
                    employee_id=emp.id,
                    normal_start_hour=s_hr,
                    normal_end_hour=e_hr,
                    usual_devices=json.dumps(devs),
                    usual_ips=json.dumps(ips),
                    usual_resources=json.dumps(["internal-portal", "erp", "gitlab", "email"]),
                    usual_download_limit_mb=dl_limit,
                    total_activities_sampled=15,
                    last_baseline_update=now,
                )
                db.add(bl)

            # Seed Risk Score Histories in PostgreSQL
            histories = [
                (created_employees[1], [
                    (42, "LOW", ["Normal baseline activity"], now - timedelta(days=5)),
                    (51, "MEDIUM", ["Off-hours access query"], now - timedelta(days=3)),
                    (64, "HIGH", ["Unusual device + high volume download"], now - timedelta(days=1)),
                    (78, "HIGH", ["Off-hours mass exfiltration from untrusted IP"], now - timedelta(hours=2)),
                ]),
                (created_employees[2], [
                    (35, "LOW", ["Standard IT management"], now - timedelta(days=4)),
                    (60, "HIGH", ["Privilege elevation to Domain Admin"], now - timedelta(days=2)),
                    (85, "CRITICAL", ["Unauthorized root elevation + massive data transfer"], now - timedelta(hours=5)),
                ]),
            ]

            for emp, points in histories:
                for score, tier, factors, ts in points:
                    rh = RiskScoreHistory(
                        employee_id=emp.id,
                        score=score,
                        risk_level=tier,
                        contributing_factors=json.dumps(factors),
                        calculated_at=ts,
                    )
                    db.add(rh)

            # Seed Alerts in PostgreSQL
            alert1 = Alert(
                employee_id=created_employees[1].id,
                title="Suspicious Off-Hours Confidential File Download",
                message="FIN-2187 logged in at 02:15 AM from untrusted IP 198.51.100.77 and downloaded Q3_budget.xlsx (3.4 MB) from SharePoint.",
                category="DATA_EXFILTRATION",
                severity="HIGH",
                status="OPEN",
                risk_score=78,
                created_at=now - timedelta(hours=2),
            )
            db.add(alert1)

            alert2 = Alert(
                employee_id=created_employees[2].id,
                title="Critical Unauthorized Domain Privilege Escalation",
                message="IT-3064 executed unauthorized administrative role elevation on core Active Directory controller outside standard change window.",
                category="PRIVILEGE_ESCALATION",
                severity="CRITICAL",
                status="OPEN",
                risk_score=85,
                created_at=now - timedelta(hours=5),
            )
            db.add(alert2)

            db.commit()
            db.refresh(alert1)
            db.refresh(alert2)

            # Seed Incidents in PostgreSQL
            inc1 = Incident(
                employee_id=created_employees[1].id,
                alert_id=alert1.id,
                title="INC-1024: Potential Financial Data Exfiltration",
                description="Forensic investigation initiated for off-hours download of Q3 confidential financial records by FIN-2187.",
                severity="HIGH",
                status="INVESTIGATING",
                created_at=now - timedelta(hours=1),
            )
            db.add(inc1)

            inc2 = Incident(
                employee_id=created_employees[2].id,
                alert_id=alert2.id,
                title="INC-1025: Critical Active Directory Compromise Investigation",
                description="Investigating suspicious root privilege elevation and subsequent LDAP queries by IT-3064.",
                severity="CRITICAL",
                status="OPEN",
                created_at=now - timedelta(hours=4),
            )
            db.add(inc2)

            # Seed Analyst Notes in PostgreSQL
            note1 = InvestigationNote(
                employee_id=created_employees[1].id,
                incident_id=None,
                author_email="analyst@itbis.cyber",
                note_text="Spoke with Finance Director. FIN-2187 was not authorized to work at 02:15 AM. Device IP traces to an external VPN exit node.",
                created_at=now - timedelta(minutes=45),
            )
            db.add(note1)

            # Seed Notifications in PostgreSQL
            n1 = Notification(
                title="High-Risk Alert Triggered",
                message="FIN-2187 triggered alert: Suspicious Off-Hours Confidential File Download",
                alert_id=alert1.id,
                is_read=False,
                created_at=now - timedelta(hours=2),
            )
            n2 = Notification(
                title="Critical Incident Opened",
                message="INC-1025 opened for IT-3064 regarding Active Directory privilege elevation",
                alert_id=alert2.id,
                is_read=False,
                created_at=now - timedelta(hours=4),
            )
            db.add(n1)
            db.add(n2)

            # Seed Analyst Audit Log in PostgreSQL
            audit1 = AuditLog(
                user_email="system@itbis.cyber",
                action="INITIALIZE_SEED_DATA",
                target_type="SYSTEM",
                details="Enterprise telemetry datasets and baseline norms successfully populated."
            )
            db.add(audit1)

            db.commit()
            logger.info("PostgreSQL dataset initialized successfully.")

        # ============================================================
        # 2. Seed Realistic Activity Telemetry in MongoDB (All 8 Event Types)
        # ============================================================
        mongo_activity_count = mongo_service.count_activities()
        if mongo_activity_count == 0:
            logger.info("Seeding realistic role-specific activity telemetry into MongoDB (8 Event Types)...")

            sample_activities = [
                # ----------------- CYB-1042 (Cybersecurity) -----------------
                {
                    "employee_id": "CYB-1042",
                    "event_type": "login",
                    "action": "Authenticated to SIEM SOC Gateway",
                    "resource": "https://siem.enterprise.corp/console",
                    "timestamp": (now - timedelta(days=2, hours=3)).isoformat(),
                    "device": "SEC-D-991",
                    "ip_address": "192.168.1.10",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"auth_method": "FIDO2_MFA", "session_id": "sess-sec-901"},
                },
                {
                    "employee_id": "CYB-1042",
                    "event_type": "remote_access",
                    "action": "SSH Session to Threat Intelligence Collector",
                    "resource": "ssh://threat-intel-01.corp",
                    "timestamp": (now - timedelta(days=1, hours=4)).isoformat(),
                    "device": "SEC-D-991",
                    "ip_address": "192.168.1.10",
                    "location": "Hyderabad",
                    "risk_weight": 5,
                    "is_suspicious": False,
                    "details": {"port": 22, "protocol": "SSH-2.0", "target_node": "ti-collector-01"},
                },
                {
                    "employee_id": "CYB-1042",
                    "event_type": "file_upload",
                    "action": "Uploaded Threat Signature IOC Rule Bundle",
                    "resource": "https://threatintel.enterprise.corp/rules/yara-2026-q3.yar",
                    "timestamp": (now - timedelta(days=1, hours=2)).isoformat(),
                    "device": "SEC-D-991",
                    "ip_address": "192.168.1.10",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"rule_count": 48, "file_name": "yara-2026-q3.yar", "classification": "Confidential"},
                },

                # ----------------- FIN-2187 (Finance) -----------------
                {
                    "employee_id": "FIN-2187",
                    "event_type": "login",
                    "action": "Routine Login to Finance Workstation",
                    "resource": "workstation://fin-laptop-02",
                    "timestamp": (now - timedelta(days=3, hours=9)).isoformat(),
                    "device": "FIN-D-102",
                    "ip_address": "192.168.1.15",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"login_time": "09:05", "os": "Windows 11 Enterprise"},
                },
                {
                    "employee_id": "FIN-2187",
                    "event_type": "file_download",
                    "action": "Downloaded Monthly General Ledger",
                    "resource": "SharePoint://Finance/GL_2026_August.xlsx",
                    "timestamp": (now - timedelta(days=2, hours=6)).isoformat(),
                    "device": "FIN-D-102",
                    "ip_address": "192.168.1.15",
                    "location": "Hyderabad",
                    "risk_weight": 5,
                    "is_suspicious": False,
                    "details": {"file_name": "GL_2026_August.xlsx", "size_mb": 4.2, "classification": "Internal"},
                },
                {
                    "employee_id": "FIN-2187",
                    "event_type": "login",
                    "action": "Off-Hours Remote Gateway Access",
                    "resource": "https://vpn.enterprise.corp",
                    "timestamp": (now - timedelta(hours=2, minutes=20)).isoformat(),
                    "device": "ROG-Strix-Laptop (Unenrolled)",
                    "ip_address": "198.51.100.77",
                    "location": "External Network / Unknown",
                    "risk_weight": 35,
                    "is_suspicious": True,
                    "anomaly_reasons": ["Off-Hours Access (02:15 AM)", "Foreign Device Hardware", "Untrusted Public IP"],
                    "details": {"login_time": "02:15 AM", "vpn_client": "OpenVPN 2.5", "auth_factor": "Password_Only"},
                },
                {
                    "employee_id": "FIN-2187",
                    "event_type": "file_download",
                    "action": "Exfiltrated Confidential Executive Budget Archive",
                    "resource": "SharePoint://Confidential/Q3_budget.xlsx",
                    "timestamp": (now - timedelta(hours=2, minutes=15)).isoformat(),
                    "device": "ROG-Strix-Laptop (Unenrolled)",
                    "ip_address": "198.51.100.77",
                    "location": "External Network",
                    "risk_weight": 45,
                    "is_suspicious": True,
                    "anomaly_reasons": ["Confidential Document Query", "Download to Unmanaged Device"],
                    "details": {"file_name": "Q3_budget.xlsx", "size_mb": 3.4, "source_system": "SharePoint", "classification": "Confidential"},
                },
                {
                    "employee_id": "FIN-2187",
                    "event_type": "usb_connect",
                    "action": "Removable Flash Drive Connected to Workstation",
                    "resource": "USB://Kingston_DataTraveler_64GB",
                    "timestamp": (now - timedelta(hours=1, minutes=50)).isoformat(),
                    "device": "FIN-D-102",
                    "ip_address": "192.168.1.15",
                    "location": "Hyderabad",
                    "risk_weight": 40,
                    "is_suspicious": True,
                    "anomaly_reasons": ["Unapproved USB Mass Storage Device", "High Data Exfiltration Vector"],
                    "details": {"vendor_id": "0951", "product_id": "1666", "serial": "001A92B3C4D5"},
                },

                # ----------------- IT-3064 (IT Systems) -----------------
                {
                    "employee_id": "IT-3064",
                    "event_type": "login",
                    "action": "VPN Access from Standard Workstation",
                    "resource": "vpn://internal-gateway",
                    "timestamp": (now - timedelta(days=2, hours=8)).isoformat(),
                    "device": "IT-D-303",
                    "ip_address": "192.168.1.25",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"auth": "RADIUS_MFA", "client_version": "v3.4.1"},
                },
                {
                    "employee_id": "IT-3064",
                    "event_type": "privilege_change",
                    "action": "Elevated User Account to Domain Admins Group",
                    "resource": "ActiveDirectory://DC-01/DomainAdmins",
                    "timestamp": (now - timedelta(hours=5, minutes=10)).isoformat(),
                    "device": "IT-D-303",
                    "ip_address": "192.168.1.25",
                    "location": "Hyderabad",
                    "risk_weight": 55,
                    "is_suspicious": True,
                    "anomaly_reasons": ["Unapproved Privilege Elevation", "Outside Change Management Window"],
                    "details": {"target_account": "m.vance_admin", "granted_group": "Domain Admins", "tool": "PowerShell_AD_Module"},
                },
                {
                    "employee_id": "IT-3064",
                    "event_type": "data_transfer",
                    "action": "Bulk Active Directory NTDS Database Extraction",
                    "resource": "C:\\Windows\\NTDS\\ntds.dit",
                    "timestamp": (now - timedelta(hours=5)).isoformat(),
                    "device": "IT-D-303",
                    "ip_address": "192.168.1.25",
                    "location": "Hyderabad",
                    "risk_weight": 50,
                    "is_suspicious": True,
                    "anomaly_reasons": ["Shadow Copy Extraction of Password Hashes", "Mass Volume Transfer"],
                    "details": {"target_file": "ntds.dit", "size_mb": 1200, "protocol": "SMBv3"},
                },
                {
                    "employee_id": "IT-3064",
                    "event_type": "remote_access",
                    "action": "RDP Connection to Primary Domain Controller",
                    "resource": "rdp://dc01.ad.enterprise.corp",
                    "timestamp": (now - timedelta(hours=5, minutes=25)).isoformat(),
                    "device": "IT-D-303",
                    "ip_address": "192.168.1.25",
                    "location": "Hyderabad",
                    "risk_weight": 15,
                    "is_suspicious": False,
                    "details": {"session_type": "RDP", "target_host": "dc01.ad.enterprise.corp"},
                },

                # ----------------- HR-4128 (HR Operations) -----------------
                {
                    "employee_id": "HR-4128",
                    "event_type": "login",
                    "action": "HR Portal Session",
                    "resource": "https://workday.corp/hris",
                    "timestamp": (now - timedelta(days=1, hours=5)).isoformat(),
                    "device": "HR-D-210",
                    "ip_address": "192.168.1.40",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"portal": "Workday", "module": "Employee_Records"},
                },
                {
                    "employee_id": "HR-4128",
                    "event_type": "email_activity",
                    "action": "Dispatched Benefits Enrollment Announcement",
                    "resource": "Exchange://Mailbox/All-Employees-List",
                    "timestamp": (now - timedelta(days=1, hours=3)).isoformat(),
                    "device": "HR-D-210",
                    "ip_address": "192.168.1.40",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"recipients_count": 450, "attachment": "benefits_guide_2026.pdf"},
                },
                {
                    "employee_id": "HR-4128",
                    "event_type": "file_upload",
                    "action": "Uploaded Updated Q3 Employee Handbook",
                    "resource": "SharePoint://HR/Policies/Handbook_2026.pdf",
                    "timestamp": (now - timedelta(hours=18)).isoformat(),
                    "device": "HR-D-210",
                    "ip_address": "192.168.1.40",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"file_name": "Handbook_2026.pdf", "size_mb": 5.8},
                },

                # ----------------- DEV-5271 (DevOps) -----------------
                {
                    "employee_id": "DEV-5271",
                    "event_type": "login",
                    "action": "AWS Management Console SSO Login",
                    "resource": "https://aws.amazon.com/console",
                    "timestamp": (now - timedelta(days=1, hours=7)).isoformat(),
                    "device": "ENG-D-119",
                    "ip_address": "192.168.1.50",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"iam_role": "DevOpsEngineerRole", "region": "ap-south-1"},
                },
                {
                    "employee_id": "DEV-5271",
                    "event_type": "remote_access",
                    "action": "Kubernetes Cluster Ingress via Kubectl",
                    "resource": "k8s://prod-cluster-01.corp",
                    "timestamp": (now - timedelta(hours=6)).isoformat(),
                    "device": "ENG-D-119",
                    "ip_address": "192.168.1.50",
                    "location": "Hyderabad",
                    "risk_weight": 10,
                    "is_suspicious": False,
                    "details": {"namespace": "production-api", "command": "kubectl rollout restart deployment/api-gateway"},
                },
                {
                    "employee_id": "DEV-5271",
                    "event_type": "data_transfer",
                    "action": "Synchronized Container Build Registry Cache",
                    "resource": "s3://prod-docker-cache-bucket/layers",
                    "timestamp": (now - timedelta(hours=4)).isoformat(),
                    "device": "ENG-D-119",
                    "ip_address": "192.168.1.50",
                    "location": "Hyderabad",
                    "risk_weight": 5,
                    "is_suspicious": False,
                    "details": {"image": "itbis-backend:v1.0.4", "size_mb": 340},
                },

                # ----------------- CMP-6385 (Compliance) -----------------
                {
                    "employee_id": "CMP-6385",
                    "event_type": "login",
                    "action": "GRC Compliance Portal Authentication",
                    "resource": "https://grc.enterprise.corp",
                    "timestamp": (now - timedelta(days=2, hours=2)).isoformat(),
                    "device": "CMP-D-512",
                    "ip_address": "192.168.1.60",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"audit_module": "ISO27001_Readiness"},
                },
                {
                    "employee_id": "CMP-6385",
                    "event_type": "file_download",
                    "action": "Exported SOC2 Evidence Inventory",
                    "resource": "GRC://Reports/SOC2_Evidence_2026.pdf",
                    "timestamp": (now - timedelta(days=1, hours=2)).isoformat(),
                    "device": "CMP-D-512",
                    "ip_address": "192.168.1.60",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"file_name": "SOC2_Evidence_2026.pdf", "size_mb": 1.8},
                },
                {
                    "employee_id": "CMP-6385",
                    "event_type": "email_activity",
                    "action": "Sent External Audit Evidence Request to PwC",
                    "resource": "Exchange://Mailbox/External-Audit-Team",
                    "timestamp": (now - timedelta(hours=8)).isoformat(),
                    "device": "CMP-D-512",
                    "ip_address": "192.168.1.60",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"recipient": "audit.team@pwc.com", "subject": "Q3 SOC2 Audit Evidence Packet"},
                },

                # ----------------- Additional 7-Day & 30-Day Telemetry History -----------------
                {
                    "employee_id": "CYB-1042",
                    "event_type": "data_transfer",
                    "action": "Automated SIEM SOC Log Ingestion Sync",
                    "resource": "s3://siem-event-lake/q3-logs",
                    "timestamp": (now - timedelta(days=4, hours=4)).isoformat(),
                    "device": "SEC-D-991",
                    "ip_address": "192.168.1.10",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"transferred_gb": 12.4, "status": "completed"},
                },
                {
                    "employee_id": "CYB-1042",
                    "event_type": "privilege_change",
                    "action": "Rotated SOC API Access Key Token",
                    "resource": "Vault://secret/soc-api-tokens",
                    "timestamp": (now - timedelta(days=18, hours=4)).isoformat(),
                    "device": "SEC-D-991",
                    "ip_address": "192.168.1.10",
                    "location": "Hyderabad",
                    "risk_weight": 5,
                    "is_suspicious": False,
                    "details": {"key_id": "soc-key-2026", "action": "rotate"},
                },
                {
                    "employee_id": "FIN-2187",
                    "event_type": "login",
                    "action": "SAP ERP Month-End Reconciliation Session",
                    "resource": "https://erp.enterprise.corp/finance",
                    "timestamp": (now - timedelta(days=10, hours=2)).isoformat(),
                    "device": "FIN-D-102",
                    "ip_address": "192.168.1.15",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"module": "General_Ledger", "session_length": "3h 20m"},
                },
                {
                    "employee_id": "IT-3064",
                    "event_type": "usb_connect",
                    "action": "IT Authorized Diagnostic Flash Drive Insertion",
                    "resource": "USB://SanDisk_Ultra_128GB",
                    "timestamp": (now - timedelta(days=6, hours=7)).isoformat(),
                    "device": "IT-D-303",
                    "ip_address": "192.168.1.25",
                    "location": "Hyderabad",
                    "risk_weight": 10,
                    "is_suspicious": False,
                    "details": {"purpose": "Hardware Diagnostic Check", "ticket_id": "IT-9921"},
                },
                {
                    "employee_id": "IT-3064",
                    "event_type": "data_transfer",
                    "action": "Disaster Recovery Database Cross-Region Replication",
                    "resource": "db://dc01-backup.corp/ad-dr-backup",
                    "timestamp": (now - timedelta(days=25, hours=6)).isoformat(),
                    "device": "IT-D-303",
                    "ip_address": "192.168.1.25",
                    "location": "Hyderabad",
                    "risk_weight": 10,
                    "is_suspicious": False,
                    "details": {"destination": "ap-southeast-1", "backup_size_gb": 4.5},
                },
                {
                    "employee_id": "HR-4128",
                    "event_type": "file_download",
                    "action": "Exported Quarterly Department Headcount Statistics",
                    "resource": "Workday://Reports/Headcount_Q3_2026.csv",
                    "timestamp": (now - timedelta(days=15, hours=8)).isoformat(),
                    "device": "HR-D-210",
                    "ip_address": "192.168.1.40",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"rows_count": 520, "classification": "Internal"},
                },
                {
                    "employee_id": "DEV-5271",
                    "event_type": "file_upload",
                    "action": "Pushed Helm Chart Definition to Production Artifact Registry",
                    "resource": "harbor.corp/charts/itbis-stack:v1.2",
                    "timestamp": (now - timedelta(days=5, hours=3)).isoformat(),
                    "device": "ENG-D-119",
                    "ip_address": "192.168.1.50",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"repo": "charts/itbis-stack", "version": "1.2.0"},
                },
                {
                    "employee_id": "DEV-5271",
                    "event_type": "remote_access",
                    "action": "Terraform Cloud Automated Infrastructure Apply",
                    "resource": "app.terraform.io/enterprise-corp/infra-prod",
                    "timestamp": (now - timedelta(days=22, hours=3)).isoformat(),
                    "device": "ENG-D-119",
                    "ip_address": "192.168.1.50",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"run_id": "run-tx901", "resources_modified": 3},
                },
                {
                    "employee_id": "CMP-6385",
                    "event_type": "file_upload",
                    "action": "Uploaded ISO 27001 Internal Security Audit Evidence Package",
                    "resource": "GRC://Evidence/ISO27001_Audit_Pkg_2026.zip",
                    "timestamp": (now - timedelta(days=12, hours=5)).isoformat(),
                    "device": "CMP-D-512",
                    "ip_address": "192.168.1.60",
                    "location": "Hyderabad",
                    "risk_weight": 0,
                    "is_suspicious": False,
                    "details": {"package_size_mb": 14.5, "auditor": "Internal"},
                },
            ]

            for act in sample_activities:
                mongo_service.insert_activity_log(act)

            logger.info("Successfully seeded %d activity telemetry records into MongoDB!", len(sample_activities))

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
