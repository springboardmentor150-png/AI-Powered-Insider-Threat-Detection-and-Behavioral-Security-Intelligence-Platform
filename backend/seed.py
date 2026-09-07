"""
ITBIS seed script — run once to populate PostgreSQL + MongoDB.

Usage:
    cd backend
    python seed.py

Requires the backend/.env file to exist with valid DB credentials.
Safe to re-run: existing records are skipped (upsert-style checks).
"""
import asyncio
import sys
from datetime import datetime, timezone

# Ensure app package is importable when running from backend/
sys.path.insert(0, ".")

from app.auth import hash_password
from app.database import AsyncSessionLocal, Base, close_mongo, engine, get_mongo_db
from app.models import Alert, Employee, Incident, User
from app.mongo import COLLECTION, insert_many_logs
from sqlalchemy import select


# ── Platform users ────────────────────────────────────────────────────────────

USERS = [
    {"email": "admin@northwind.co",       "password": "Admin@1234",   "role": "Administrator"},
    {"email": "priya.raman@northwind.co", "password": "Manager@1234", "role": "Security Manager"},
    {"email": "karen.blake@northwind.co", "password": "Manager@1234", "role": "Security Manager"},
    {"email": "jonas.hale@northwind.co",  "password": "Analyst@1234", "role": "Security Analyst"},
    {"email": "mei.tanaka@northwind.co",  "password": "Soc@12345678", "role": "SOC Engineer"},
    {"email": "omar.said@northwind.co",   "password": "Analyst@1234", "role": "Security Analyst"},
    {"email": "dieter.roth@northwind.co", "password": "Admin@1234",   "role": "Administrator"},
]

# ── Employees ─────────────────────────────────────────────────────────────────

EMPLOYEES = [
    {
        "employee_id": "EMP-1042",
        "name": "Ana Delgado",
        "email": "ana.delgado@northwind.co",
        "department": "Finance",
        "designation": "Senior Accountant",
        "manager": "Priya Raman",
        "risk_level": "Critical",
        "risk_score": 92,
        "location": "Madrid, ES",
        "joined_at": datetime(2019, 4, 8, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1103",
        "name": "Marcus Chen",
        "email": "marcus.chen@northwind.co",
        "department": "Engineering",
        "designation": "Staff Engineer",
        "manager": "Dieter Roth",
        "risk_level": "High",
        "risk_score": 78,
        "location": "Austin, US",
        "joined_at": datetime(2021, 1, 19, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1188",
        "name": "Sofia Ibrahim",
        "email": "sofia.ibrahim@northwind.co",
        "department": "Sales",
        "designation": "Account Executive",
        "manager": "Karen Blake",
        "risk_level": "High",
        "risk_score": 71,
        "location": "Dubai, AE",
        "joined_at": datetime(2022, 7, 4, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1211",
        "name": "Tom Averill",
        "email": "tom.averill@northwind.co",
        "department": "IT Operations",
        "designation": "Systems Administrator",
        "manager": "Dieter Roth",
        "risk_level": "Medium",
        "risk_score": 54,
        "location": "Manchester, UK",
        "joined_at": datetime(2018, 11, 27, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1274",
        "name": "Leah Okonkwo",
        "email": "leah.okonkwo@northwind.co",
        "department": "Human Resources",
        "designation": "HR Business Partner",
        "manager": "Priya Raman",
        "risk_level": "Medium",
        "risk_score": 47,
        "location": "Lagos, NG",
        "joined_at": datetime(2020, 9, 15, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1309",
        "name": "Ravi Menon",
        "email": "ravi.menon@northwind.co",
        "department": "Engineering",
        "designation": "Data Engineer",
        "manager": "Dieter Roth",
        "risk_level": "Low",
        "risk_score": 22,
        "location": "Bengaluru, IN",
        "joined_at": datetime(2023, 2, 6, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1355",
        "name": "Grace Lindqvist",
        "email": "grace.lindqvist@northwind.co",
        "department": "Legal",
        "designation": "Counsel",
        "manager": "Karen Blake",
        "risk_level": "Low",
        "risk_score": 15,
        "location": "Stockholm, SE",
        "joined_at": datetime(2022, 3, 21, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1402",
        "name": "Yusuf Demir",
        "email": "yusuf.demir@northwind.co",
        "department": "Finance",
        "designation": "Financial Analyst",
        "manager": "Priya Raman",
        "risk_level": "Medium",
        "risk_score": 58,
        "location": "Istanbul, TR",
        "joined_at": datetime(2021, 6, 30, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1466",
        "name": "Nina Petrova",
        "email": "nina.petrova@northwind.co",
        "department": "Sales",
        "designation": "Sales Engineer",
        "manager": "Karen Blake",
        "risk_level": "Low",
        "risk_score": 31,
        "location": "Warsaw, PL",
        "joined_at": datetime(2023, 8, 14, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1501",
        "name": "Kwame Asante",
        "email": "kwame.asante@northwind.co",
        "department": "Engineering",
        "designation": "Security Engineer",
        "manager": "Dieter Roth",
        "risk_level": "Low",
        "risk_score": 18,
        "location": "Accra, GH",
        "joined_at": datetime(2024, 1, 10, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1522",
        "name": "Fatima Al-Hassan",
        "email": "fatima.alhassan@northwind.co",
        "department": "Finance",
        "designation": "Compliance Officer",
        "manager": "Priya Raman",
        "risk_level": "Medium",
        "risk_score": 45,
        "location": "Riyadh, SA",
        "joined_at": datetime(2022, 11, 1, tzinfo=timezone.utc),
    },
    {
        "employee_id": "EMP-1537",
        "name": "Lucas Ferreira",
        "email": "lucas.ferreira@northwind.co",
        "department": "Sales",
        "designation": "Regional Director",
        "manager": "Karen Blake",
        "risk_level": "High",
        "risk_score": 67,
        "location": "São Paulo, BR",
        "joined_at": datetime(2020, 5, 19, tzinfo=timezone.utc),
    },
]

# ── Alerts ────────────────────────────────────────────────────────────────────

ALERTS = [
    {
        "alert_id": "ALR-4401",
        "employee_id": "EMP-1042",
        "severity": "Critical",
        "message": "Mass data staging followed by unregistered USB mount",
        "status": "Investigating",
        "rule": "ITBIS-R014 · Exfiltration staging chain",
        "narrative": "412 finance forecast files were pulled at 02:14 UTC, then an unregistered 128 GB USB device was mounted 17 minutes later on the same host.",
        "assigned_to": "Security Analyst",
        "created_at": datetime(2026, 9, 3, 2, 35, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4402",
        "employee_id": "EMP-1103",
        "severity": "High",
        "message": "Self-granted production database privileges",
        "status": "Open",
        "rule": "ITBIS-R008 · Privilege self-escalation",
        "narrative": "An automation token added the account to prod-db-readers with no matching change ticket.",
        "assigned_to": "SOC Engineer",
        "created_at": datetime(2026, 9, 2, 18, 7, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4403",
        "employee_id": "EMP-1188",
        "severity": "High",
        "message": "Customer pipeline export sent to personal mailbox",
        "status": "Investigating",
        "rule": "ITBIS-R003 · Sensitive data to personal domain",
        "narrative": "A 3.1 MB CRM pipeline export was mailed to a personal address. The account is inside a flagged retention window.",
        "assigned_to": "Security Analyst",
        "created_at": datetime(2026, 9, 2, 16, 50, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4404",
        "employee_id": "EMP-1211",
        "severity": "Medium",
        "message": "VPN access from previously unseen hosting provider",
        "status": "Open",
        "rule": "ITBIS-R021 · Anomalous network origin",
        "narrative": "Session originated from a datacentre ASN in Germany. No travel record and no prior sessions from this ASN.",
        "assigned_to": "SOC Engineer",
        "created_at": datetime(2026, 9, 2, 13, 20, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4405",
        "employee_id": "EMP-1042",
        "severity": "Critical",
        "message": "740 MB archive uploaded to external transfer service",
        "status": "Open",
        "rule": "ITBIS-R002 · Unsanctioned egress channel",
        "narrative": "Archive size and destination are both outside policy. DLP inspection was bypassed.",
        "assigned_to": "Security Manager",
        "created_at": datetime(2026, 8, 29, 19, 30, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4406",
        "employee_id": "EMP-1274",
        "severity": "Low",
        "message": "Repeated failed logins before successful SSO",
        "status": "Resolved",
        "rule": "ITBIS-R031 · Credential friction",
        "narrative": "Four failed attempts then success from the usual managed workstation. Closed as benign.",
        "assigned_to": "Security Analyst",
        "created_at": datetime(2026, 9, 2, 9, 5, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4407",
        "employee_id": "EMP-1402",
        "severity": "Medium",
        "message": "Off-hours bulk export of vendor payment records",
        "status": "Investigating",
        "rule": "ITBIS-R011 · Off-baseline data access",
        "narrative": "86 vendor payment rows exported at 22:58 UTC. Volume is within role norms but the access hour is 2.5 sigma above baseline.",
        "assigned_to": "Security Analyst",
        "created_at": datetime(2026, 9, 1, 23, 2, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4408",
        "employee_id": "EMP-1103",
        "severity": "High",
        "message": "Impossible travel — concurrent VPN sessions",
        "status": "Open",
        "rule": "ITBIS-R017 · Impossible travel",
        "narrative": "Two authenticated sessions nine minutes apart from geographically incompatible origins.",
        "assigned_to": "SOC Engineer",
        "created_at": datetime(2026, 8, 28, 3, 25, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4409",
        "employee_id": "EMP-1537",
        "severity": "High",
        "message": "Bulk CRM export before scheduled departure",
        "status": "Investigating",
        "rule": "ITBIS-R003 · Pre-departure data access spike",
        "narrative": "Lucas Ferreira exported 1,200 CRM contacts 3 days before his last working day.",
        "assigned_to": "Security Manager",
        "created_at": datetime(2026, 9, 1, 10, 14, tzinfo=timezone.utc),
    },
    {
        "alert_id": "ALR-4410",
        "employee_id": "EMP-1309",
        "severity": "Informational",
        "message": "First-time use of approved artifact store",
        "status": "Resolved",
        "rule": "ITBIS-R044 · New tool adoption",
        "narrative": "Baseline enrichment event only. No policy violation detected.",
        "assigned_to": "SOC Engineer",
        "created_at": datetime(2026, 9, 2, 8, 45, tzinfo=timezone.utc),
    },
]

# ── Incidents ─────────────────────────────────────────────────────────────────

INCIDENTS = [
    {
        "incident_id": "INV-221",
        "title": "Finance forecast exfiltration chain",
        "employee_id": "EMP-1042",
        "alert_id": "ALR-4401",
        "status": "In progress",
        "severity": "Critical",
        "opened_at": datetime(2026, 9, 3, 3, 10, tzinfo=timezone.utc),
        "notes": "USB device serial captured. Imaging in progress.",
    },
    {
        "incident_id": "INV-222",
        "title": "Prod database privilege escalation",
        "employee_id": "EMP-1103",
        "alert_id": "ALR-4402",
        "status": "Triage",
        "severity": "High",
        "opened_at": datetime(2026, 9, 2, 18, 40, tzinfo=timezone.utc),
        "notes": "",
    },
    {
        "incident_id": "INV-223",
        "title": "CRM export to personal mailbox",
        "employee_id": "EMP-1188",
        "alert_id": "ALR-4403",
        "status": "Awaiting review",
        "severity": "High",
        "opened_at": datetime(2026, 9, 2, 17, 15, tzinfo=timezone.utc),
        "notes": "HR notified. Legal hold placed on mailbox.",
    },
    {
        "incident_id": "INV-224",
        "title": "Off-hours vendor payment exports",
        "employee_id": "EMP-1402",
        "alert_id": "ALR-4407",
        "status": "In progress",
        "severity": "Medium",
        "opened_at": datetime(2026, 9, 1, 23, 30, tzinfo=timezone.utc),
        "notes": "",
    },
]

# ── Activity Logs (MongoDB) ────────────────────────────────────────────────────

ACTIVITY_LOGS = [
    {"log_id": "LOG-9001", "employee_id": "EMP-1042", "event_type": "file_download",
     "timestamp": "2026-09-03T02:14:00Z",
     "details": "Downloaded 412 files (1.8 GB) from /finance/forecasts outside working hours.",
     "host": "FIN-WKS-08", "ip": "10.22.4.91"},
    {"log_id": "LOG-9002", "employee_id": "EMP-1042", "event_type": "usb_connect",
     "timestamp": "2026-09-03T02:31:00Z",
     "details": "Unregistered mass-storage device (SanDisk Ultra, 128 GB) mounted.",
     "host": "FIN-WKS-08", "ip": "10.22.4.91"},
    {"log_id": "LOG-9003", "employee_id": "EMP-1103", "event_type": "privilege_change",
     "timestamp": "2026-09-02T18:05:00Z",
     "details": "Added self to group 'prod-db-readers' via automation token.",
     "host": "ENG-BUILD-02", "ip": "10.31.9.14"},
    {"log_id": "LOG-9004", "employee_id": "EMP-1188", "event_type": "email_external",
     "timestamp": "2026-09-02T16:44:00Z",
     "details": "Sent pipeline export (3.1 MB) to personal address s.ibrahim@fastmail.com.",
     "host": "SAL-LAP-17", "ip": "10.44.2.7"},
    {"log_id": "LOG-9005", "employee_id": "EMP-1211", "event_type": "vpn_access",
     "timestamp": "2026-09-02T13:12:00Z",
     "details": "VPN session from new ASN (Hetzner, DE) — no prior history for this account.",
     "host": "ITO-JUMP-01", "ip": "88.198.44.10"},
    {"log_id": "LOG-9006", "employee_id": "EMP-1274", "event_type": "login",
     "timestamp": "2026-09-02T09:02:00Z",
     "details": "SSO login succeeded after 4 failed attempts.",
     "host": "HR-WKS-03", "ip": "10.12.7.33"},
    {"log_id": "LOG-9007", "employee_id": "EMP-1309", "event_type": "file_upload",
     "timestamp": "2026-09-02T08:41:00Z",
     "details": "Uploaded 12 MB dataset to approved internal artifact store.",
     "host": "ENG-WKS-21", "ip": "10.31.9.55"},
    {"log_id": "LOG-9008", "employee_id": "EMP-1402", "event_type": "file_download",
     "timestamp": "2026-09-01T22:58:00Z",
     "details": "Bulk export of vendor payment records (86 rows).",
     "host": "FIN-WKS-12", "ip": "10.22.4.60"},
    {"log_id": "LOG-9009", "employee_id": "EMP-1042", "event_type": "login",
     "timestamp": "2026-09-01T21:47:00Z",
     "details": "Login from unmanaged device fingerprint.",
     "host": "UNKNOWN", "ip": "77.90.14.201"},
    {"log_id": "LOG-9010", "employee_id": "EMP-1466", "event_type": "logout",
     "timestamp": "2026-09-01T18:30:00Z",
     "details": "Normal session end.", "host": "SAL-LAP-04", "ip": "10.44.2.19"},
    {"log_id": "LOG-9011", "employee_id": "EMP-1103", "event_type": "file_download",
     "timestamp": "2026-09-01T17:22:00Z",
     "details": "Cloned 3 private repositories to local disk.",
     "host": "ENG-BUILD-02", "ip": "10.31.9.14"},
    {"log_id": "LOG-9012", "employee_id": "EMP-1355", "event_type": "login",
     "timestamp": "2026-09-01T09:15:00Z",
     "details": "Routine SSO login from managed laptop.",
     "host": "LEG-LAP-02", "ip": "10.55.1.8"},
    {"log_id": "LOG-9013", "employee_id": "EMP-1188", "event_type": "usb_connect",
     "timestamp": "2026-08-31T20:10:00Z",
     "details": "Approved encrypted USB token mounted for signing.",
     "host": "SAL-LAP-17", "ip": "10.44.2.7"},
    {"log_id": "LOG-9014", "employee_id": "EMP-1211", "event_type": "privilege_change",
     "timestamp": "2026-08-31T15:48:00Z",
     "details": "Granted temporary domain-admin (ticket CHG-8842, approved).",
     "host": "ITO-JUMP-01", "ip": "10.9.0.4"},
    {"log_id": "LOG-9015", "employee_id": "EMP-1274", "event_type": "email_external",
     "timestamp": "2026-08-31T11:05:00Z",
     "details": "Sent offer letter PDF to candidate domain.",
     "host": "HR-WKS-03", "ip": "10.12.7.33"},
    {"log_id": "LOG-9016", "employee_id": "EMP-1402", "event_type": "vpn_access",
     "timestamp": "2026-08-30T23:40:00Z",
     "details": "VPN session at 23:40 local — 2.5 sigma above baseline hours.",
     "host": "FIN-WKS-12", "ip": "10.22.4.60"},
    {"log_id": "LOG-9017", "employee_id": "EMP-1309", "event_type": "login",
     "timestamp": "2026-08-30T08:12:00Z",
     "details": "Routine login, MFA satisfied via hardware key.",
     "host": "ENG-WKS-21", "ip": "10.31.9.55"},
    {"log_id": "LOG-9018", "employee_id": "EMP-1042", "event_type": "email_external",
     "timestamp": "2026-08-29T19:26:00Z",
     "details": "Zip archive (740 MB) sent to external file-transfer service.",
     "host": "FIN-WKS-08", "ip": "10.22.4.91"},
    {"log_id": "LOG-9019", "employee_id": "EMP-1466", "event_type": "file_upload",
     "timestamp": "2026-08-29T14:03:00Z",
     "details": "Uploaded demo assets to shared drive.",
     "host": "SAL-LAP-04", "ip": "10.44.2.19"},
    {"log_id": "LOG-9020", "employee_id": "EMP-1103", "event_type": "vpn_access",
     "timestamp": "2026-08-28T03:19:00Z",
     "details": "Concurrent VPN sessions from two countries within 9 minutes.",
     "host": "ENG-BUILD-02", "ip": "203.0.113.44"},
    {"log_id": "LOG-9021", "employee_id": "EMP-1537", "event_type": "file_download",
     "timestamp": "2026-09-01T10:05:00Z",
     "details": "Exported 1,200 CRM contacts to CSV (22 MB).",
     "host": "SAL-LAP-22", "ip": "10.44.3.15"},
    {"log_id": "LOG-9022", "employee_id": "EMP-1537", "event_type": "email_external",
     "timestamp": "2026-09-01T10:32:00Z",
     "details": "CRM export forwarded to personal Gmail account.",
     "host": "SAL-LAP-22", "ip": "10.44.3.15"},
    {"log_id": "LOG-9023", "employee_id": "EMP-1522", "event_type": "login",
     "timestamp": "2026-09-02T07:15:00Z",
     "details": "Routine SSO login from managed workstation.",
     "host": "FIN-WKS-22", "ip": "10.22.5.10"},
    {"log_id": "LOG-9024", "employee_id": "EMP-1501", "event_type": "login",
     "timestamp": "2026-09-03T08:00:00Z",
     "details": "MFA-verified login from corporate VPN.",
     "host": "ENG-WKS-33", "ip": "10.31.10.5"},
]


# ── Seed functions ─────────────────────────────────────────────────────────────

async def seed_postgres():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # ── Users ──────────────────────────────────────────────────────────
        for u in USERS:
            existing = await db.execute(select(User).where(User.email == u["email"]))
            if existing.scalar_one_or_none():
                continue
            db.add(User(
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],  # type: ignore[arg-type]
                status="Active",  # type: ignore[arg-type]
                last_login=datetime(2026, 9, 3, 7, 0, tzinfo=timezone.utc),
            ))
        await db.commit()
        print(f"  ✓ Users seeded ({len(USERS)} records)")

        # ── Employees ──────────────────────────────────────────────────────
        for e in EMPLOYEES:
            existing = await db.execute(
                select(Employee).where(Employee.employee_id == e["employee_id"])
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Employee(**e, is_active=True))
        await db.commit()
        print(f"  ✓ Employees seeded ({len(EMPLOYEES)} records)")

        # ── Alerts ─────────────────────────────────────────────────────────
        for a in ALERTS:
            existing = await db.execute(
                select(Alert).where(Alert.alert_id == a["alert_id"])
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Alert(**a))
        await db.commit()
        print(f"  ✓ Alerts seeded ({len(ALERTS)} records)")

        # ── Incidents ──────────────────────────────────────────────────────
        for i in INCIDENTS:
            existing = await db.execute(
                select(Incident).where(Incident.incident_id == i["incident_id"])
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Incident(**i))
        await db.commit()
        print(f"  ✓ Incidents seeded ({len(INCIDENTS)} records)")


async def seed_mongo():
    db = get_mongo_db()

    # Only seed if collection is empty
    existing_count = await db[COLLECTION].count_documents({})
    if existing_count > 0:
        print(f"  ✓ Activity logs already present ({existing_count} docs) — skipping")
        return

    inserted = await insert_many_logs(ACTIVITY_LOGS)
    print(f"  ✓ Activity logs seeded ({inserted} documents)")


async def main():
    print("\n🌱 ITBIS seed script starting…\n")
    print("PostgreSQL:")
    await seed_postgres()
    print("\nMongoDB:")
    await seed_mongo()
    await engine.dispose()
    await close_mongo()
    print("\n✅ Seed complete.\n")
    print("Demo credentials:")
    print("  admin@northwind.co          / Admin@1234   (Administrator)")
    print("  priya.raman@northwind.co    / Manager@1234 (Security Manager)")
    print("  jonas.hale@northwind.co     / Analyst@1234 (Security Analyst)")
    print("  mei.tanaka@northwind.co     / Soc@12345678 (SOC Engineer)")


if __name__ == "__main__":
    asyncio.run(main())
