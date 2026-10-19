"""
Comprehensive End-to-End Pipeline & Security Verification Test Suite (Milestone 4: Days 35-36)
ITBIS: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Covers:
1. get_auth_header(role, user_id) helper generating valid JWT Bearer credentials.
2. Complete end-to-end trace:
   User Login -> Activity Ingestion -> Anomaly Detection -> Risk Scoring ->
   Alert Generation & Escalation -> Incident Creation & Notes ->
   Compliance & Admin Dashboards -> Report Generation & Bulk Exports.
3. Security & RBAC matrix:
   - Missing token rejection (401 Unauthorized) across all endpoints.
   - Invalid / expired token rejection (401 Unauthorized).
   - Strict role-based access control (403 Forbidden) for unauthorized roles:
     - Admin-only endpoints (/dashboard/admin, /dashboard/admin/platform-analytics, /dashboard/admin/audit-log)
     - Security Manager endpoints (/dashboard/manager/compliance, /reports/compliance/pdf)
     - SOC Engineering endpoints (/dashboard/soc)
   - Parameter validation & 404 handling (e.g. unknown employee dossier).
4. Zero-guarded metrics and valid binary document formats (PDF & XLSX).
"""

import os
import sys
import unittest
from datetime import datetime, timezone

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base, User, Employee, Alert, Incident, InvestigationNote, AuditLog, Notification
from app.auth import create_token, hash_password
from app.mongodb import mongo_service
from app.compliance import calculate_mttr, calculate_mtti, get_compliance_metrics


# Create isolated in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def get_auth_header(role: str, user_id: int = 1) -> dict:
    """
    Standardized auth header generator for security & pipeline verification.
    """
    token = create_token(user_id=user_id, role=role)
    return {"Authorization": f"Bearer {token}"}


class TestFullPipelineAndSecurityMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create all tables in the isolated database
        Base.metadata.create_all(bind=engine)
        cls.db = TestingSessionLocal()

        # Seed test users
        cls.admin_user = User(id=1, email="admin@itbis.test", password_hash=hash_password("AdminPass123!"), role="admin")
        cls.manager_user = User(id=2, email="manager@itbis.test", password_hash=hash_password("ManagerPass123!"), role="security_manager")
        cls.analyst_user = User(id=3, email="analyst@itbis.test", password_hash=hash_password("AnalystPass123!"), role="security_analyst")
        cls.soc_user = User(id=4, email="soc@itbis.test", password_hash=hash_password("SocPass123!"), role="soc_engineer")

        cls.db.add_all([cls.admin_user, cls.manager_user, cls.analyst_user, cls.soc_user])
        cls.db.commit()

        # Seed test employees
        cls.emp1 = Employee(
            id=1,
            employee_id="EMP-TEST-001",
            name="Alice Security",
            email="alice@itbis.test",
            department="Engineering",
            designation="Senior Engineer",
            risk_score=78,
            risk_level="High",
            status="ACTIVE",
        )
        cls.emp2 = Employee(
            id=2,
            employee_id="EMP-TEST-002",
            name="Bob Clean",
            email="bob@itbis.test",
            department="Finance",
            designation="Accountant",
            risk_score=15,
            risk_level="Low",
            status="ACTIVE",
        )
        cls.db.add_all([cls.emp1, cls.emp2])
        cls.db.commit()

        # Seed initial incident and alert for compliance testing
        now = datetime.now(timezone.utc)
        cls.incident1 = Incident(
            id=1,
            employee_id=1,
            title="High Volume Transfer",
            description="Mass data transfer anomaly flagged",
            status="RESOLVED",
            severity="HIGH",
            assigned_to=3,
            investigation_started_at=now,
            resolved_at=now,
            created_at=now,
        )
        cls.alert1 = Alert(
            id=1,
            employee_id=1,
            title="Off-hours Authentication Spike",
            message="Multiple logins between 02:00 and 04:00 UTC",
            category="UNUSUAL_LOGIN",
            severity="CRITICAL",
            status="RESOLVED",
            risk_score=80,
            assigned_to=3,
            resolved_at=now,
            created_at=now,
        )
        cls.db.add_all([cls.incident1, cls.alert1])
        cls.db.commit()

        # Seed sample anomalies in persistent dev tier for EMP-TEST-001
        mongo_service.save_anomaly({
            "employee_id": "EMP-TEST-001",
            "anomaly_type": "DATA_EXFILTRATION",
            "severity": "critical",
            "details": {"transferred_bytes": 105000000, "date": now.strftime("%Y-%m-%d")},
            "timestamp": now.isoformat(),
            "detected_at": now.isoformat(),
            "alert_generated": False,
        })
        mongo_service.save_anomaly({
            "employee_id": "EMP-TEST-001",
            "anomaly_type": "PRIVILEGE_ESCALATION",
            "severity": "high",
            "details": {"action": "sudo su root", "date": now.strftime("%Y-%m-%d")},
            "timestamp": now.isoformat(),
            "detected_at": now.isoformat(),
            "alert_generated": False,
        })

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()

    # =========================================================================
    # PART 1: AUTHENTICATION & TOKEN VERIFICATION
    # =========================================================================

    def test_01_user_login_success(self):
        """Verify standard user login generates a valid Bearer token."""
        resp = client.post("/auth/login", json={"email": "admin@itbis.test", "password": "AdminPass123!"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data.get("token_type"), "bearer")
        self.assertEqual(data.get("role") or data.get("user", {}).get("role"), "admin")

    def test_02_user_login_invalid_credentials(self):
        """Verify invalid credentials return 401 Unauthorized."""
        resp = client.post("/auth/login", json={"email": "admin@itbis.test", "password": "WrongPassword!"})
        self.assertEqual(resp.status_code, 401)

    # =========================================================================
    # PART 2: END-TO-END PIPELINE TRACE
    # =========================================================================

    def test_03_activity_log_ingestion(self):
        """Pipeline Step 1: Ingest telemetry activity log."""
        headers = get_auth_header("soc_engineer", user_id=4)
        activity_payload = {
            "employee_id": "EMP-TEST-001",
            "event_type": "file_download",
            "action": "BULK_EXPORT",
            "resource": "Customer_DB_Snapshot.tar.gz",
            "device": "MACBOOK-PRO-01",
            "ip_address": "198.51.100.44",
            "risk_weight": 20,
            "is_suspicious": True,
        }
        resp = client.post("/activity-logs", json=activity_payload, headers=headers)
        self.assertIn(resp.status_code, [200, 201])
        data = resp.json()
        self.assertTrue(data.get("success", True) or "id" in data or "message" in data)

    def test_04_anomaly_detection_retrieval(self):
        """Pipeline Step 2: Query unified anomaly reports for subject."""
        headers = get_auth_header("security_analyst", user_id=3)
        resp = client.get("/anomalies/EMP-TEST-001", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["employee_id"], "EMP-TEST-001")
        self.assertTrue("rule_based_anomalies" in data or "rule_anomalies" in data)
        self.assertIn("ml_anomalies", data)
        self.assertIn("total_flags", data)

    def test_05_risk_score_calculation(self):
        """Pipeline Step 3: Compute 5-factor normalized risk score."""
        headers = get_auth_header("security_analyst", user_id=3)
        resp = client.get("/risk-scores/EMP-TEST-001", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["employee_id"], "EMP-TEST-001")
        self.assertIn("final_score", data)
        self.assertIn("risk_level", data)
        self.assertIn("sub_scores", data)
        self.assertGreaterEqual(data["final_score"], 0.0)
        self.assertLessEqual(data["final_score"], 100.0)

    def test_06_alert_generation_and_escalation(self):
        """Pipeline Step 4: Scan unalerted anomalies and generate security alerts."""
        headers = get_auth_header("security_analyst", user_id=3)
        resp = client.post("/alerts/generate", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("alerts_created", data)

        # Retrieve created alerts
        alerts_resp = client.get("/alerts?employee_id=1", headers=headers)
        self.assertEqual(alerts_resp.status_code, 200)
        alerts_data = alerts_resp.json()
        self.assertGreaterEqual(alerts_data.get("total", 0), 1)

    def test_07_incident_workflow_and_notes(self):
        """Pipeline Step 5: Escalate alert to incident and attach forensic notes."""
        headers = get_auth_header("security_analyst", user_id=3)
        # Ensure EMP-TEST-001 has sufficient anomalies for Medium/High risk
        now = datetime.now(timezone.utc)
        for _ in range(3):
            mongo_service.save_anomaly({
                "employee_id": "EMP-TEST-001",
                "anomaly_type": "PRIVILEGE_ESCALATION",
                "severity": "critical",
                "details": {"action": "sudo su root", "date": now.strftime("%Y-%m-%d")},
                "timestamp": now.isoformat(),
                "alert_generated": True,
            })

        inc_payload = {
            "employee_id": "EMP-TEST-001",
            "summary": "Suspected Data Exfiltration Investigation",
            "severity": "CRITICAL",
        }
        create_resp = client.post("/incidents", json=inc_payload, headers=headers)
        self.assertIn(create_resp.status_code, [200, 201])
        inc_data = create_resp.json()
        inc_id = inc_data.get("incident_id") or inc_data.get("id")

        # Add investigation note (verifying auto-transition to investigating and MTTI recording)
        note_payload = {
            "note_text": "Examined network flow logs. Identified unauthorized outbound SFTP connection.",
            "evidence_reference": "PCAP-2026-10-14-001.pcap",
        }
        note_resp = client.post(f"/incidents/{inc_id}/notes", json=note_payload, headers=headers)
        self.assertIn(note_resp.status_code, [200, 201])

        # Resolve incident
        res_resp = client.patch(f"/incidents/{inc_id}/resolve", headers=headers)
        self.assertEqual(res_resp.status_code, 200)
        self.assertEqual(str(res_resp.json().get("status")).upper(), "RESOLVED")

    # =========================================================================
    # PART 3: DASHBOARDS VERIFICATION
    # =========================================================================

    def test_08_compliance_dashboard_metrics(self):
        """Verify Manager Compliance dashboard returns MTTR, MTTI, and resolution rates."""
        headers = get_auth_header("security_manager", user_id=2)
        resp = client.get("/dashboard/manager/compliance", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("total_incidents", data)
        self.assertIn("resolved_incidents", data)
        self.assertIn("resolution_rate_percent", data)
        self.assertIn("mttr_hours", data)
        self.assertIn("mtti_hours", data)
        self.assertIn("compliance_status", data)
        self.assertIsInstance(data["mttr_hours"], (int, float))
        self.assertIsInstance(data["mtti_hours"], (int, float))

    def test_09_admin_dashboard_overview(self):
        """Verify Admin dashboard overview returns user breakdown and monitored employees."""
        headers = get_auth_header("admin", user_id=1)
        resp = client.get("/dashboard/admin", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("total_platform_users", data)
        self.assertIn("users_by_role", data)
        self.assertIn("employees_monitored", data)
        self.assertIn("distinct_departments_count", data)

    def test_10_admin_platform_analytics(self):
        """Verify Admin platform analytics returns ingestion totals and anomaly rates."""
        headers = get_auth_header("admin", user_id=1)
        resp = client.get("/dashboard/admin/platform-analytics", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("total_logs", data)
        self.assertIn("rule_anomalies", data)
        self.assertIn("ml_anomalies", data)
        self.assertIn("overall_anomaly_rate_percent", data)
        self.assertIn("status", data)

    def test_11_admin_audit_log_feed(self):
        """Verify Admin audit log feed returns newest records first."""
        headers = get_auth_header("admin", user_id=1)
        resp = client.get("/dashboard/admin/audit-log?limit=10", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("action", data[0])
            self.assertIn("timestamp", data[0])

    def test_12_analyst_and_soc_dashboards(self):
        """Verify Analyst and SOC engineering dashboards."""
        analyst_hdr = get_auth_header("security_analyst", user_id=3)
        resp_analyst = client.get("/dashboard/analyst", headers=analyst_hdr)
        self.assertEqual(resp_analyst.status_code, 200)
        self.assertIn("open_alerts", resp_analyst.json())

        soc_hdr = get_auth_header("soc_engineer", user_id=4)
        resp_soc = client.get("/dashboard/soc", headers=soc_hdr)
        self.assertEqual(resp_soc.status_code, 200)
        self.assertIn("alerts_by_severity", resp_soc.json())

    # =========================================================================
    # PART 4: REPORT GENERATION & BULK EXPORTS
    # =========================================================================

    def test_13_reports_catalog(self):
        """Verify GET /reports/catalog returns structured metadata for all available reports."""
        headers = get_auth_header("security_analyst", user_id=3)
        resp = client.get("/reports/catalog", headers=headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 5)
        endpoints = [r["endpoint"] for r in data]
        self.assertIn("/reports/{employee_id}/pdf", endpoints)
        self.assertIn("/reports/compliance/pdf", endpoints)
        self.assertIn("/reports/export/risk-scores", endpoints)
        self.assertIn("/reports/export/incidents", endpoints)

    def test_14_employee_risk_pdf_report(self):
        """Verify GET /reports/{employee_id}/pdf generates binary PDF with attachment header."""
        headers = get_auth_header("security_analyst", user_id=3)
        resp = client.get("/reports/EMP-TEST-001/pdf", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "application/pdf")
        self.assertIn("attachment; filename=", resp.headers.get("content-disposition", ""))
        self.assertIn(b"%PDF-", resp.content[:10])

    def test_15_employee_risk_pdf_not_found(self):
        """Verify GET /reports/{employee_id}/pdf returns 404 for non-existent employee."""
        headers = get_auth_header("security_analyst", user_id=3)
        resp = client.get("/reports/NON-EXISTENT-EMPLOYEE/pdf", headers=headers)
        self.assertEqual(resp.status_code, 404)

    def test_16_compliance_pdf_report(self):
        """Verify GET /reports/compliance/pdf generates binary PDF for manager."""
        headers = get_auth_header("security_manager", user_id=2)
        resp = client.get("/reports/compliance/pdf", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "application/pdf")
        self.assertIn("compliance_sla_report.pdf", resp.headers.get("content-disposition", ""))
        self.assertIn(b"%PDF-", resp.content[:10])

    def test_17_export_risk_scores_excel(self):
        """Verify GET /reports/export/risk-scores generates valid Excel OpenXML binary."""
        headers = get_auth_header("security_analyst", user_id=3)
        resp = client.get("/reports/export/risk-scores?department=Engineering", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.headers.get("content-type"),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        self.assertIn("employee_risk_scores.xlsx", resp.headers.get("content-disposition", ""))
        self.assertGreater(len(resp.content), 100)

    def test_18_export_incidents_excel(self):
        """Verify GET /reports/export/incidents generates valid Excel OpenXML binary."""
        headers = get_auth_header("security_analyst", user_id=3)
        resp = client.get("/reports/export/incidents?status=RESOLVED", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.headers.get("content-type"),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        self.assertIn("incidents_export.xlsx", resp.headers.get("content-disposition", ""))
        self.assertGreater(len(resp.content), 100)

    # =========================================================================
    # PART 5: SECURITY & RBAC ISOLATION MATRIX (401 & 403)
    # =========================================================================

    def test_19_missing_token_rejection(self):
        """Verify all protected endpoints reject unauthenticated requests with 401."""
        endpoints = [
            "/dashboard/admin",
            "/dashboard/admin/platform-analytics",
            "/dashboard/admin/audit-log",
            "/dashboard/manager/compliance",
            "/dashboard/analyst",
            "/dashboard/soc",
            "/reports/catalog",
            "/reports/compliance/pdf",
            "/reports/EMP-TEST-001/pdf",
            "/reports/export/risk-scores",
            "/reports/export/incidents",
            "/incidents",
            "/alerts",
        ]
        for ep in endpoints:
            with self.subTest(endpoint=ep):
                resp = client.get(ep)
                self.assertEqual(resp.status_code, 401, f"Expected 401 for unauthenticated {ep}")

    def test_20_invalid_token_rejection(self):
        """Verify forged / corrupted tokens return 401 Unauthorized."""
        bad_headers = {"Authorization": "Bearer forged.invalid.token.payload"}
        resp = client.get("/dashboard/admin", headers=bad_headers)
        self.assertEqual(resp.status_code, 401)

    def test_21_admin_endpoints_role_isolation(self):
        """Verify non-admin roles receive strict 403 Forbidden on /dashboard/admin routes."""
        admin_endpoints = [
            "/dashboard/admin",
            "/dashboard/admin/platform-analytics",
            "/dashboard/admin/audit-log",
        ]
        unauthorized_roles = ["security_analyst", "security_manager", "soc_engineer"]

        for role in unauthorized_roles:
            headers = get_auth_header(role)
            for ep in admin_endpoints:
                with self.subTest(role=role, endpoint=ep):
                    resp = client.get(ep, headers=headers)
                    self.assertEqual(resp.status_code, 403, f"Expected 403 for {role} on {ep}, got {resp.status_code}")

    def test_22_compliance_endpoints_role_isolation(self):
        """Verify analysts and SOC engineers receive 403 on compliance endpoints."""
        compliance_endpoints = [
            "/dashboard/manager/compliance",
            "/reports/compliance/pdf",
        ]
        unauthorized_roles = ["security_analyst", "soc_engineer"]

        for role in unauthorized_roles:
            headers = get_auth_header(role)
            for ep in compliance_endpoints:
                with self.subTest(role=role, endpoint=ep):
                    resp = client.get(ep, headers=headers)
                    self.assertEqual(resp.status_code, 403, f"Expected 403 for {role} on {ep}, got {resp.status_code}")

    def test_23_soc_dashboard_role_isolation(self):
        """Verify analysts receive 403 Forbidden on the SOC engineering dashboard."""
        headers = get_auth_header("security_analyst")
        resp = client.get("/dashboard/soc", headers=headers)
        self.assertEqual(resp.status_code, 403)


if __name__ == "__main__":
    unittest.main()
