"""
ITBIS seed script — run once to populate PostgreSQL + MongoDB.

Usage:
    cd backend
    python seed.py

Requires backend/.env with valid DB credentials.
Safe to re-run: existing records are skipped (idempotent).
"""
import asyncio
import sys
from datetime import datetime, timezone

sys.path.insert(0, ".")

from app.auth import hash_password
from app.database import AsyncSessionLocal, Base, close_mongo, engine, get_mongo_db
from app.models import (
    Alert,
    AlertStatusEnum,
    Employee,
    Incident,
    IncidentStatusEnum,
    RiskLevelEnum,
    RoleEnum,
    SeverityEnum,
    User,
    UserStatusEnum,
)
from app.mongo import COLLECTION, insert_many_logs
from sqlalchemy import select


# ── Platform users ─────────────────────────────────────────────────────────────

USERS = [
    {"email": "admin@northwind.co",       "password": "Admin@1234",   "role": RoleEnum.administrator},
    {"email": "priya.raman@northwind.co", "password": "Manager@1234", "role": RoleEnum.security_manager},
    {"email": "karen.blake@northwind.co", "password": "Manager@1234", "role": RoleEnum.security_manager},
    {"email": "jonas.hale@northwind.co",  "password": "Analyst@1234", "role": RoleEnum.security_analyst},
    {"email": "mei.tanaka@northwind.co",  "password": "Soc@12345678", "role": RoleEnum.soc_engineer},
    {"email": "omar.said@northwind.co",   "password": "Analyst@1234", "role": RoleEnum.security_analyst},
    {"email": "dieter.roth@northwind.co", "password": "Admin@1234",   "role": RoleEnum.administrator},
]

# ── Employees ─────────────────────────────────────────────────────────────────

EMPLOYEES = [
    {
        "employee_id": "EMP-1042", "name": "Ana Delgado",
        "email": "ana.delgado@northwind.co", "department": "Finance",
        "designation": "Senior Accountant", "manager": "Priya Raman",
        "risk_level": RiskLevelEnum.critical, "risk_score": 92,
        "location": "Madrid, ES", "joined_at": datetime(2019, 4, 8, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1103", "name": "Marcus Chen",
        "email": "marcus.chen@northwind.co", "department": "Engineering",
        "designation": "Staff Engineer", "manager": "Dieter Roth",
        "risk_level": RiskLevelEnum.high, "risk_score": 78,
        "location": "Austin, US", "joined_at": datetime(2021, 1, 19, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1188", "name": "Sofia Ibrahim",
        "email": "sofia.ibrahim@northwind.co", "department": "Sales",
        "designation": "Account Executive", "manager": "Karen Blake",
        "risk_level": RiskLevelEnum.high, "risk_score": 71,
        "location": "Dubai, AE", "joined_at": datetime(2022, 7, 4, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1211", "name": "Tom Averill",
        "email": "tom.averill@northwind.co", "department": "IT Operations",
        "designation": "Systems Administrator", "manager": "Dieter Roth",
        "risk_level": RiskLevelEnum.medium, "risk_score": 54,
        "location": "Manchester, UK", "joined_at": datetime(2018, 11, 27, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1274", "name": "Leah Okonkwo",
        "email": "leah.okonkwo@northwind.co", "department": "Human Resources",
        "designation": "HR Business Partner", "manager": "Priya Raman",
        "risk_level": RiskLevelEnum.medium, "risk_score": 47,
        "location": "Lagos, NG", "joined_at": datetime(2020, 9, 15, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1309", "name": "Ravi Menon",
        "email": "ravi.menon@northwind.co", "department": "Engineering",
        "designation": "Data Engineer", "manager": "Dieter Roth",
        "risk_level": RiskLevelEnum.low, "risk_score": 22,
        "location": "Bengaluru, IN", "joined_at": datetime(2023, 2, 6, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1355", "name": "Grace Lindqvist",
        "email": "grace.lindqvist@northwind.co", "department": "Legal",
        "designation": "Counsel", "manager": "Karen Blake",
        "risk_level": RiskLevelEnum.low, "risk_score": 15,
        "location": "Stockholm, SE", "joined_at": datetime(2022, 3, 21, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1402", "name": "Yusuf Demir",
        "email": "yusuf.demir@northwind.co", "department": "Finance",
        "designation": "Financial Analyst", "manager": "Priya Raman",
        "risk_level": RiskLevelEnum.medium, "risk_score": 58,
        "location": "Istanbul, TR", "joined_at": datetime(2021, 6, 30, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1466", "name": "Nina Petrova",
        "email": "nina.petrova@northwind.co", "department": "Sales",
        "designation": "Sales Engineer", "manager": "Karen Blake",
        "risk_level": RiskLevelEnum.low, "risk_score": 31,
        "location": "Warsaw, PL", "joined_at": datetime(2023, 8, 14, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1501", "name": "Kwame Asante",
        "email": "kwame.asante@northwind.co", "department": "Engineering",
        "designation": "Security Engineer", "manager": "Dieter Roth",
        "risk_level": RiskLevelEnum.low, "risk_score": 18,
        "location": "Accra, GH", "joined_at": datetime(2024, 1, 10, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1522", "name": "Fatima Al-Hassan",
        "email": "fatima.alhassan@northwind.co", "department": "Finance",
        "designation": "Compliance Officer", "manager": "Priya Raman",
        "risk_level": RiskLevelEnum.medium, "risk_score": 45,
        "location": "Riyadh, SA", "joined_at": datetime(2022, 11, 1, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1537", "name": "Lucas Ferreira",
        "email": "lucas.ferreira@northwind.co", "department": "Sales",
        "designation": "Regional Director", "manager": "Karen Blake",
        "risk_level": RiskLevelEnum.high, "risk_score": 67,
        "location": "Sao Paulo, BR", "joined_at": datetime(2020, 5, 19, tzinfo=timezone.utc),
    },
]

# ── Alerts ─────────────────────────────────────────────────────────────────────

ALERTS = [
    {
        "alert_id": "ALR-4401", "employee_id": "EMP-1042",
        "severity": SeverityEnum.critical,
        "message": "Mass data staging followed by unregistered USB mount",
        "status": AlertStatusEnum.investigating,
        "rule": "ITBIS-R014 · Exfiltration staging chain",
        "narrative": "412 finance forecast files were pulled at 02:14 UTC, then an unregistered 128 GB USB device was mounted 17 minutes later on the same host.",
        "assigned_to": RoleEnum.security_analyst,
        "created_at": datetime(2026, 9, 3, 2, 35, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4402", "employee_id": "EMP-1103",
        "severity": SeverityEnum.high,
        "message": "Self-granted production database privileges",
        "status": AlertStatusEnum.open,
        "rule": "ITBIS-R008 · Privilege self-escalation",
        "narrative": "An automation token added the account to prod-db-readers with no matching change ticket.",
        "assigned_to": RoleEnum.soc_engineer,
        "created_at": datetime(2026, 9, 2, 18, 7, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4403", "employee_id": "EMP-1188",
        "severity": SeverityEnum.high,
        "message": "Customer pipeline export sent to personal mailbox",
        "status": AlertStatusEnum.investigating,
        "rule": "ITBIS-R003 · Sensitive data to personal domain",
        "narrative": "A 3.1 MB CRM pipeline export was mailed to a personal address. The account is inside a flagged retention window.",
        "assigned_to": RoleEnum.security_analyst,
        "created_at": datetime(2026, 9, 2, 16, 50, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4404", "employee_id": "EMP-1211",
        "severity": SeverityEnum.medium,
        "message": "VPN access from previously unseen hosting provider",
        "status": AlertStatusEnum.open,
        "rule": "ITBIS-R021 · Anomalous network origin",
        "narrative": "Session originated from a datacentre ASN in Germany. No travel record and no prior sessions from this ASN.",
        "assigned_to": RoleEnum.soc_engineer,
        "created_at": datetime(2026, 9, 2, 13, 20, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4405", "employee_id": "EMP-1042",
        "severity": SeverityEnum.critical,
        "message": "740 MB archive uploaded to external transfer service",
        "status": AlertStatusEnum.open,
        "rule": "ITBIS-R002 · Unsanctioned egress channel",
        "narrative": "Archive size and destination are both outside policy. DLP inspection was bypassed.",
        "assigned_to": RoleEnum.security_manager,
        "created_at": datetime(2026, 8, 29, 19, 30, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4406", "employee_id": "EMP-1274",
        "severity": SeverityEnum.low,
        "message": "Repeated failed logins before successful SSO",
        "status": AlertStatusEnum.resolved,
        "rule": "ITBIS-R031 · Credential friction",
        "narrative": "Four failed attempts then success from the usual managed workstation. Closed as benign.",
        "assigned_to": RoleEnum.security_analyst,
        "created_at": datetime(2026, 9, 2, 9, 5, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4407", "employee_id": "EMP-1402",
        "severity": SeverityEnum.medium,
        "message": "Off-hours bulk export of vendor payment records",
        "status": AlertStatusEnum.investigating,
        "rule": "ITBIS-R011 · Off-baseline data access",
        "narrative": "86 vendor payment rows exported at 22:58 UTC. Volume is within role norms but the access hour is 2.5 sigma above baseline.",
        "assigned_to": RoleEnum.security_analyst,
        "created_at": datetime(2026, 9, 1, 23, 2, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4408", "employee_id": "EMP-1103",
        "severity": SeverityEnum.high,
        "message": "Impossible travel — concurrent VPN sessions",
        "status": AlertStatusEnum.open,
        "rule": "ITBIS-R017 · Impossible travel",
        "narrative": "Two authenticated sessions nine minutes apart from geographically incompatible origins.",
        "assigned_to": RoleEnum.soc_engineer,
        "created_at": datetime(2026, 8, 28, 3, 25, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4409", "employee_id": "EMP-1537",
        "severity": SeverityEnum.high,
        "message": "Bulk CRM export before scheduled departure",
        "status": AlertStatusEnum.investigating,
        "rule": "ITBIS-R003 · Pre-departure data access spike",
        "narrative": "Lucas Ferreira exported 1,200 CRM contacts 3 days before his last working day.",
        "assigned_to": RoleEnum.security_manager,
        "created_at": datetime(2026, 9, 1, 10, 14, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4410", "employee_id": "EMP-1309",
        "severity": SeverityEnum.informational,
        "message": "First-time use of approved artifact store",
        "status": AlertStatusEnum.resolved,
        "rule": "ITBIS-R044 · New tool adoption",
        "narrative": "Baseline enrichment event only. No policy violation detected.",
        "assigned_to": RoleEnum.soc_engineer,
        "created_at": datetime(2026, 9, 2, 8, 45, tzinfo=timezone.utc),
    },
]

# ── Incidents ──────────────────────────────────────────────────────────────────

INCIDENTS = [
    {
        "incident_id": "INV-221", "title": "Finance forecast exfiltration chain",
        "employee_id": "EMP-1042", "alert_id": "ALR-4401",
        "status": IncidentStatusEnum.in_progress, "severity": SeverityEnum.critical,
        "opened_at": datetime(2026, 9, 3, 3, 10, tzinfo=timezone.utc),
        "notes": "USB device serial captured. Imaging in progress.",
    },
    {
        "incident_id": "INV-222", "title": "Prod database privilege escalation",
        "employee_id": "EMP-1103", "alert_id": "ALR-4402",
        "status": IncidentStatusEnum.triage, "severity": SeverityEnum.high,
        "opened_at": datetime(2026, 9, 2, 18, 40, tzinfo=timezone.utc), "notes": "",
    },
    {
        "incident_id": "INV-223", "title": "CRM export to personal mailbox",
        "employee_id": "EMP-1188", "alert_id": "ALR-4403",
        "status": IncidentStatusEnum.awaiting_review, "severity": SeverityEnum.high,
        "opened_at": datetime(2026, 9, 2, 17, 15, tzinfo=timezone.utc),
        "notes": "HR notified. Legal hold placed on mailbox.",
    },
    {
        "incident_id": "INV-224", "title": "Off-hours vendor payment exports",
        "employee_id": "EMP-1402", "alert_id": "ALR-4407",
        "status": IncidentStatusEnum.in_progress, "severity": SeverityEnum.medium,
        "opened_at": datetime(2026, 9, 1, 23, 30, tzinfo=timezone.utc), "notes": "",
    },
]

# ── Activity Logs (MongoDB) ────────────────────────────────────────────────────

ACTIVITY_LOGS = [
    {"log_id": "LOG-9001", "employee_id": "EMP-1042", "event_type": "file_download",
     "timestamp": "2026-09-03T02:14:00Z", "host": "FIN-WKS-08", "ip": "10.22.4.91",
     "details": "Downloaded 412 files (1.8 GB) from /finance/forecasts outside working hours."},
    {"log_id": "LOG-9002", "employee_id": "EMP-1042", "event_type": "usb_connect",
     "timestamp": "2026-09-03T02:31:00Z", "host": "FIN-WKS-08", "ip": "10.22.4.91",
     "details": "Unregistered mass-storage device (SanDisk Ultra, 128 GB) mounted."},
    {"log_id": "LOG-9003", "employee_id": "EMP-1103", "event_type": "privilege_change",
     "timestamp": "2026-09-02T18:05:00Z", "host": "ENG-BUILD-02", "ip": "10.31.9.14",
     "details": "Added self to group 'prod-db-readers' via automation token."},
    {"log_id": "LOG-9004", "employee_id": "EMP-1188", "event_type": "email_external",
     "timestamp": "2026-09-02T16:44:00Z", "host": "SAL-LAP-17", "ip": "10.44.2.7",
     "details": "Sent pipeline export (3.1 MB) to personal address s.ibrahim@fastmail.com."},
    {"log_id": "LOG-9005", "employee_id": "EMP-1211", "event_type": "vpn_access",
     "timestamp": "2026-09-02T13:12:00Z", "host": "ITO-JUMP-01", "ip": "88.198.44.10",
     "details": "VPN session from new ASN (Hetzner, DE) - no prior history for this account."},
    {"log_id": "LOG-9006", "employee_id": "EMP-1274", "event_type": "login",
     "timestamp": "2026-09-02T09:02:00Z", "host": "HR-WKS-03", "ip": "10.12.7.33",
     "details": "SSO login succeeded after 4 failed attempts."},
    {"log_id": "LOG-9007", "employee_id": "EMP-1309", "event_type": "file_upload",
     "timestamp": "2026-09-02T08:41:00Z", "host": "ENG-WKS-21", "ip": "10.31.9.55",
     "details": "Uploaded 12 MB dataset to approved internal artifact store."},
    {"log_id": "LOG-9008", "employee_id": "EMP-1402", "event_type": "file_download",
     "timestamp": "2026-09-01T22:58:00Z", "host": "FIN-WKS-12", "ip": "10.22.4.60",
     "details": "Bulk export of vendor payment records (86 rows)."},
    {"log_id": "LOG-9009", "employee_id": "EMP-1042", "event_type": "login",
     "timestamp": "2026-09-01T21:47:00Z", "host": "UNKNOWN", "ip": "77.90.14.201",
     "details": "Login from unmanaged device fingerprint."},
    {"log_id": "LOG-9010", "employee_id": "EMP-1466", "event_type": "logout",
     "timestamp": "2026-09-01T18:30:00Z", "host": "SAL-LAP-04", "ip": "10.44.2.19",
     "details": "Normal session end."},
    {"log_id": "LOG-9011", "employee_id": "EMP-1103", "event_type": "file_download",
     "timestamp": "2026-09-01T17:22:00Z", "host": "ENG-BUILD-02", "ip": "10.31.9.14",
     "details": "Cloned 3 private repositories to local disk."},
    {"log_id": "LOG-9012", "employee_id": "EMP-1355", "event_type": "login",
     "timestamp": "2026-09-01T09:15:00Z", "host": "LEG-LAP-02", "ip": "10.55.1.8",
     "details": "Routine SSO login from managed laptop."},
    {"log_id": "LOG-9013", "employee_id": "EMP-1188", "event_type": "usb_connect",
     "timestamp": "2026-08-31T20:10:00Z", "host": "SAL-LAP-17", "ip": "10.44.2.7",
     "details": "Approved encrypted USB token mounted for signing."},
    {"log_id": "LOG-9014", "employee_id": "EMP-1211", "event_type": "privilege_change",
     "timestamp": "2026-08-31T15:48:00Z", "host": "ITO-JUMP-01", "ip": "10.9.0.4",
     "details": "Granted temporary domain-admin (ticket CHG-8842, approved)."},
    {"log_id": "LOG-9015", "employee_id": "EMP-1274", "event_type": "email_external",
     "timestamp": "2026-08-31T11:05:00Z", "host": "HR-WKS-03", "ip": "10.12.7.33",
     "details": "Sent offer letter PDF to candidate domain."},
    {"log_id": "LOG-9016", "employee_id": "EMP-1402", "event_type": "vpn_access",
     "timestamp": "2026-08-30T23:40:00Z", "host": "FIN-WKS-12", "ip": "10.22.4.60",
     "details": "VPN session at 23:40 local - 2.5 sigma above baseline hours."},
    {"log_id": "LOG-9017", "employee_id": "EMP-1309", "event_type": "login",
     "timestamp": "2026-08-30T08:12:00Z", "host": "ENG-WKS-21", "ip": "10.31.9.55",
     "details": "Routine login, MFA satisfied via hardware key."},
    {"log_id": "LOG-9018", "employee_id": "EMP-1042", "event_type": "email_external",
     "timestamp": "2026-08-29T19:26:00Z", "host": "FIN-WKS-08", "ip": "10.22.4.91",
     "details": "Zip archive (740 MB) sent to external file-transfer service."},
    {"log_id": "LOG-9019", "employee_id": "EMP-1466", "event_type": "file_upload",
     "timestamp": "2026-08-29T14:03:00Z", "host": "SAL-LAP-04", "ip": "10.44.2.19",
     "details": "Uploaded demo assets to shared drive."},
    {"log_id": "LOG-9020", "employee_id": "EMP-1103", "event_type": "vpn_access",
     "timestamp": "2026-08-28T03:19:00Z", "host": "ENG-BUILD-02", "ip": "203.0.113.44",
     "details": "Concurrent VPN sessions from two countries within 9 minutes."},
    {"log_id": "LOG-9021", "employee_id": "EMP-1537", "event_type": "file_download",
     "timestamp": "2026-09-01T10:05:00Z", "host": "SAL-LAP-22", "ip": "10.44.3.15",
     "details": "Exported 1,200 CRM contacts to CSV (22 MB)."},
    {"log_id": "LOG-9022", "employee_id": "EMP-1537", "event_type": "email_external",
     "timestamp": "2026-09-01T10:32:00Z", "host": "SAL-LAP-22", "ip": "10.44.3.15",
     "details": "CRM export forwarded to personal Gmail account."},
    {"log_id": "LOG-9023", "employee_id": "EMP-1522", "event_type": "login",
     "timestamp": "2026-09-02T07:15:00Z", "host": "FIN-WKS-22", "ip": "10.22.5.10",
     "details": "Routine SSO login from managed workstation."},
    {"log_id": "LOG-9024", "employee_id": "EMP-1501", "event_type": "login",
     "timestamp": "2026-09-03T08:00:00Z", "host": "ENG-WKS-33", "ip": "10.31.10.5",
     "details": "MFA-verified login from corporate VPN."},
]


# ── Seed functions ─────────────────────────────────────────────────────────────

async def seed_postgres():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Users
        for u in USERS:
            existing = await db.execute(select(User).where(User.email == u["email"]))
            if existing.scalar_one_or_none():
                continue
            db.add(User(
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
                status=UserStatusEnum.active,
                last_login=datetime(2026, 9, 3, 7, 0, tzinfo=timezone.utc),
            ))
        await db.commit()
        print(f"  Users seeded ({len(USERS)} records)")

        # Employees
        for e in EMPLOYEES:
            existing = await db.execute(
                select(Employee).where(Employee.employee_id == e["employee_id"])
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Employee(**e, is_active=True))
        await db.commit()
        print(f"  Employees seeded ({len(EMPLOYEES)} records)")

        # Alerts
        for a in ALERTS:
            existing = await db.execute(
                select(Alert).where(Alert.alert_id == a["alert_id"])
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Alert(**a))
        await db.commit()
        print(f"  Alerts seeded ({len(ALERTS)} records)")

        # Incidents
        for i in INCIDENTS:
            existing = await db.execute(
                select(Incident).where(Incident.incident_id == i["incident_id"])
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Incident(**i))
        await db.commit()
        print(f"  Incidents seeded ({len(INCIDENTS)} records)")


async def seed_mongo():
    db = get_mongo_db()
    existing_count = await db[COLLECTION].count_documents({})
    if existing_count > 0:
        print(f"  Activity logs already present ({existing_count} docs) - skipping")
        return
    inserted = await insert_many_logs(ACTIVITY_LOGS)
    print(f"  Activity logs seeded ({inserted} documents)")


async def main():
    print("\nITBIS seed script\n")
    print("PostgreSQL:")
    await seed_postgres()
    print("\nMongoDB:")
    await seed_mongo()
    await engine.dispose()
    await close_mongo()
    print("\nSeed complete.\n")
    print("Demo credentials:")
    print("  admin@northwind.co          / Admin@1234   (Administrator)")
    print("  priya.raman@northwind.co    / Manager@1234 (Security Manager)")
    print("  karen.blake@northwind.co    / Manager@1234 (Security Manager)")
    print("  jonas.hale@northwind.co     / Analyst@1234 (Security Analyst)")
    print("  mei.tanaka@northwind.co     / Soc@12345678 (SOC Engineer)")


if __name__ == "__main__":
    asyncio.run(main())
