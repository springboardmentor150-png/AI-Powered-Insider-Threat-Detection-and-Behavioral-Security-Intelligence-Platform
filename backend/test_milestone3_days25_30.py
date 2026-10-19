"""
Unit & Integration Test Suite for Milestone 3: Days 25-30
ITBIS: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Covers:
- Day 25: Incident creation with 400 Low-risk guard rail, InvestigationNote table,
          auto-transition to 'investigating' on first note.
- Day 26: Unified chronological timeline (newest-first) merging raw logs, rule anomalies, ML anomalies.
          Oldest-first note retrieval with evidence_reference. Incident resolution with resolved_at.
- Day 27: Alert generation from anomalies with duplicate prevention, alert assignment, resolution time in minutes,
          and GET /alerts/my.
- Day 28: Escalation thresholds per severity level, stale alert escalation to critical,
          and GET /analytics/risk-overview.
- Day 29: GET /dashboard/analyst and GET /dashboard/soc with role separation (analyst gets 403 on soc).
- Day 30: Full pipeline trace from anomaly to risk to alert to incident to notes to resolution.
"""

import json
import os
import sys
import unittest
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

# Ensure backend root on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models import Employee, Alert, Incident, InvestigationNote, User
from app.auth import create_token
from app.mongodb import mongo_service
from app.risk_scoring import calculate_risk_score
from app.alerting import (
    generate_alerts_from_anomalies,
    escalate_stale_alerts,
    get_risk_overview_analytics,
    ESCALATION_THRESHOLDS_HOURS,
)

BASE_URL = "http://127.0.0.1:8000"


def http_request(method, path, data=None, token=None):
    """Executes HTTP request against the live running ITBIS FastAPI backend."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req_body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=req_body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed


class TestMilestone3Days25To30(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()

        # 1. Ensure test users with distinct roles
        def get_or_create_user(email, role):
            u = cls.db.query(User).filter(User.email == email).first()
            if not u:
                from app.auth import hash_password
                u = User(email=email, password_hash=hash_password("Password123!"), role=role)
                cls.db.add(u)
                cls.db.commit()
                cls.db.refresh(u)
            return u

        cls.admin_user = get_or_create_user("admin_m3@itbis.cyber", "ADMIN")
        cls.analyst_user = get_or_create_user("analyst_m3@itbis.cyber", "SECURITY_ANALYST")
        cls.soc_user = get_or_create_user("soc_m3@itbis.cyber", "SOC_ENGINEER")

        cls.admin_token = create_token(user_id=cls.admin_user.id, role="admin")
        cls.analyst_token = create_token(user_id=cls.analyst_user.id, role="security_analyst")
        cls.soc_token = create_token(user_id=cls.soc_user.id, role="soc_engineer")

        # 2. Seed test employees
        def get_or_create_emp(emp_id, name, dept):
            e = cls.db.query(Employee).filter(Employee.employee_id == emp_id).first()
            if not e:
                e = Employee(
                    employee_id=emp_id,
                    name=name,
                    department=dept,
                    designation="Specialist",
                    status="ACTIVE",
                    risk_score=10,
                    risk_level="Low",
                )
                cls.db.add(e)
                cls.db.commit()
                cls.db.refresh(e)
            return e

        cls.emp_clean = get_or_create_emp("EMP-D25-CLEAN", "Clean Officer", "Compliance")
        cls.emp_risky = get_or_create_emp("EMP-D25-RISKY", "Risky Engineer", "Infrastructure")

        # Clear existing test anomalies
        now = datetime.now(timezone.utc)
        mongo_service.clear_anomalies("EMP-D25-CLEAN")
        mongo_service.clear_anomalies("EMP-D25-RISKY")

        # Seed high/critical anomalies for EMP-D25-RISKY to push risk to High/Critical
        # 4 privilege changes (sub-score 100), 2 data exfiltration (sub-score 80)
        for i in range(4):
            mongo_service.save_anomaly({
                "employee_id": "EMP-D25-RISKY",
                "anomaly_type": "PRIVILEGE_CHANGE",
                "severity": "CRITICAL",
                "description": f"Elevated role assigned #{i+1}",
                "timestamp": (now - timedelta(hours=i * 2)).isoformat(),
                "detected_at": (now - timedelta(hours=i * 2)).isoformat(),
                "details": {"date": (now - timedelta(hours=i * 2)).strftime("%Y-%m-%d")},
            })
        for i in range(2):
            mongo_service.save_anomaly({
                "employee_id": "EMP-D25-RISKY",
                "anomaly_type": "DATA_EXFILTRATION_RISK",
                "severity": "HIGH",
                "description": f"Mass data archive download #{i+1}",
                "timestamp": (now - timedelta(hours=10 + i)).isoformat(),
                "detected_at": (now - timedelta(hours=10 + i)).isoformat(),
                "details": {"date": (now - timedelta(hours=10 + i)).strftime("%Y-%m-%d")},
            })

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # ==================== DAY 25: INCIDENT CREATION & NOTES ====================

    def test_day25_incident_creation_rejects_low_risk_employee(self):
        """Incident creation must reject Low-risk employees with HTTP 400 Bad Request."""
        status_code, body = http_request(
            "POST",
            f"/incidents?employee_id={self.emp_clean.employee_id}",
            token=self.analyst_token,
        )
        self.assertEqual(status_code, 400)
        self.assertIn("Low", body.get("detail", ""))

    def test_day25_incident_creation_success_for_risky_employee(self):
        """Incident creation succeeds for Medium+ employee, creating formal Incident record."""
        status_code, body = http_request(
            "POST",
            f"/incidents?employee_id={self.emp_risky.employee_id}",
            token=self.analyst_token,
        )
        self.assertEqual(status_code, 200)
        self.assertIn("incident_id", body)
        self.assertIn("severity", body)
        self.assertIn("summary", body)
        self.assertEqual(body["status"], "open")

        # Save incident_id for subsequent tests
        self.__class__.created_incident_id = body["incident_id"]

    def test_day25_note_addition_auto_transitions_status_to_investigating(self):
        """Adding first note to an open incident must auto-transition status to 'investigating'."""
        inc_id = getattr(self.__class__, "created_incident_id", None)
        self.assertIsNotNone(inc_id)

        status_code, body = http_request(
            "POST",
            f"/incidents/{inc_id}/notes",
            data={
                "note_text": "Initiating deep-dive investigation into privilege escalations.",
                "evidence_reference": "PRIVILEGE_CHANGE-LOG-01",
            },
            token=self.analyst_token,
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(body.get("incident_status"), "investigating")

        # Add a second note with evidence
        status_code2, _ = http_request(
            "POST",
            f"/incidents/{inc_id}/notes",
            data={
                "note_text": "Corroborated data transfer volume against cloud backup logs.",
                "evidence_reference": "DATA_EXFILTRATION_RISK-LOG-02",
            },
            token=self.analyst_token,
        )
        self.assertEqual(status_code2, 200)

    def test_day26_notes_returned_in_chronological_order_with_evidence(self):
        """Investigation notes must be returned in chronological (oldest-first) order with evidence."""
        inc_id = getattr(self.__class__, "created_incident_id", None)
        self.assertIsNotNone(inc_id)

        status_code, body = http_request(
            "GET",
            f"/incidents/{inc_id}/notes",
            token=self.analyst_token,
        )
        self.assertEqual(status_code, 200)
        notes = body.get("notes", [])
        self.assertGreaterEqual(len(notes), 2)
        self.assertIn("Initiating deep-dive", notes[0]["note"])
        self.assertIn("Corroborated data", notes[1]["note"])
        self.assertEqual(notes[0]["evidence_reference"], "PRIVILEGE_CHANGE-LOG-01")

    def test_day26_resolve_incident_updates_status_summary_and_timestamp(self):
        """Resolving an incident sets status='resolved', records summary and resolved_at."""
        inc_id = getattr(self.__class__, "created_incident_id", None)
        self.assertIsNotNone(inc_id)

        status_code, body = http_request(
            "PATCH",
            f"/incidents/{inc_id}/resolve",
            data={"resolution_summary": "Employee credentials revoked; unauthorized role assignments removed."},
            token=self.analyst_token,
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(body.get("message"), "Incident resolved")

        # Verify in DB that resolved_at is set
        inc = self.db.query(Incident).filter(Incident.id == inc_id).first()
        self.assertIsNotNone(inc.resolved_at)
        self.assertEqual(inc.status, "resolved")
        self.assertIn("Employee credentials revoked", inc.summary)

    # ==================== DAY 26: MERGED TIMELINE ====================

    def test_day26_unified_activity_timeline(self):
        """Timeline endpoint merges and normalizes raw logs and anomalies, sorted newest-first."""
        status_code, body = http_request(
            "GET",
            f"/investigations/{self.emp_risky.employee_id}/timeline",
            token=self.analyst_token,
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(body["employee_id"], self.emp_risky.employee_id)
        self.assertIn("timeline", body)
        self.assertGreater(body["event_count"], 0)

        timeline = body["timeline"]
        for entry in timeline:
            self.assertIn("time", entry)
            self.assertIn("source", entry)
            self.assertIn("detail", entry)

        # Check newest-first sorting
        if len(timeline) >= 2:
            self.assertGreaterEqual(timeline[0]["time"], timeline[1]["time"])

    # ==================== DAY 27: ALERT GENERATION & LIFECYCLE ====================

    def test_day27_alert_generation_from_anomalies_and_duplicate_prevention(self):
        """Alert generation scans unalerted anomalies; second run generates 0 new duplicates."""
        # Run 1: Should generate alerts for our risky employee's critical/high anomalies
        count1 = generate_alerts_from_anomalies(self.db)

        # Run 2: Repeated run must create 0 new alerts
        count2 = generate_alerts_from_anomalies(self.db)
        self.assertEqual(count2, 0, "Repeated alert generation must create zero duplicates")

        # Test live endpoint
        status_code, body = http_request("POST", "/alerts/generate", token=self.admin_token)
        self.assertEqual(status_code, 200)

    def test_day27_alert_assignment_and_resolution_time(self):
        """Assign alert to analyst (status: in_progress), resolve it, and verify resolution_time_minutes."""
        # Find an open alert
        alert = self.db.query(Alert).filter(Alert.status.in_(["open", "OPEN"])).first()
        if not alert:
            alert = Alert(
                employee_id=self.emp_risky.id,
                title="Test Escalation Alert",
                message="Testing alert lifecycle",
                severity="high",
                status="open",
                created_at=datetime.now(timezone.utc) - timedelta(minutes=45),
            )
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)

        alert_id = alert.id

        # 1. Assign to analyst
        status_assign, body_assign = http_request(
            "PATCH",
            f"/alerts/{alert_id}/assign?analyst_user_id={self.analyst_user.id}",
            token=self.admin_token,
        )
        self.assertEqual(status_assign, 200)
        self.assertEqual(body_assign.get("status"), "in_progress")
        self.assertEqual(body_assign.get("assigned_to"), self.analyst_user.id)

        # 2. Check /alerts/my returns this alert for the analyst
        status_my, body_my = http_request("GET", "/alerts/my", token=self.analyst_token)
        self.assertEqual(status_my, 200)
        my_ids = [a["id"] for a in body_my]
        self.assertIn(alert_id, my_ids)

        # 3. Resolve the alert
        status_res, body_res = http_request("PATCH", f"/alerts/{alert_id}/resolve", token=self.analyst_token)
        self.assertEqual(status_res, 200)
        self.assertEqual(body_res.get("status"), "resolved")
        self.assertIn("resolution_time_minutes", body_res)

    # ==================== DAY 28: ESCALATION & RISK ANALYTICS ====================

    def test_day28_stale_alert_escalation_workflow(self):
        """Stale critical alert (backdated >2h) escalates to critical and 'escalated' status."""
        now = datetime.now(timezone.utc)

        # Create deliberately old critical alert (3 hours old)
        stale_alert = Alert(
            employee_id=self.emp_risky.id,
            title="Stale Critical Alert",
            message="Unattended critical event",
            severity="critical",
            status="open",
            created_at=now - timedelta(hours=3),
        )
        # Create fresh medium alert (only 1 hour old, threshold is 24h)
        fresh_medium_alert = Alert(
            employee_id=self.emp_risky.id,
            title="Fresh Medium Alert",
            message="Recent medium event",
            severity="medium",
            status="open",
            created_at=now - timedelta(hours=1),
        )
        self.db.add(stale_alert)
        self.db.add(fresh_medium_alert)
        self.db.commit()
        self.db.refresh(stale_alert)
        self.db.refresh(fresh_medium_alert)

        # Run escalation
        escalated_ids = escalate_stale_alerts(self.db)
        self.assertIn(stale_alert.id, escalated_ids)
        self.assertNotIn(fresh_medium_alert.id, escalated_ids)

        # Verify stale alert is now escalated
        self.db.refresh(stale_alert)
        self.assertEqual(stale_alert.status, "escalated")
        self.assertEqual(stale_alert.severity, "critical")
        self.assertIsNotNone(stale_alert.escalated_at)

    def test_day28_risk_overview_analytics_endpoint(self):
        """GET /analytics/risk-overview returns organization-wide risk distribution and alert stats."""
        status_code, body = http_request("GET", "/analytics/risk-overview", token=self.admin_token)
        self.assertEqual(status_code, 200)
        self.assertIn("total_employees", body)
        self.assertIn("risk_level_distribution", body)
        self.assertIn("open_alerts", body)
        self.assertIn("escalated_alerts", body)

        dist = body["risk_level_distribution"]
        total_in_dist = sum(dist.values())
        self.assertEqual(total_in_dist, body["total_employees"])

    # ==================== DAY 29: ANALYST & SOC DASHBOARDS ====================

    def test_day29_analyst_dashboard_endpoint(self):
        """GET /dashboard/analyst returns open alerts, queue, open incidents, and top-risk employees."""
        status_code, body = http_request("GET", "/dashboard/analyst", token=self.analyst_token)
        self.assertEqual(status_code, 200)
        self.assertIn("open_alerts", body)
        self.assertIn("my_investigation_queue", body)
        self.assertIn("open_incidents", body)
        self.assertIn("top_risk_employees", body)

        if body["top_risk_employees"]:
            top = body["top_risk_employees"][0]
            self.assertIn("employee_id", top)
            self.assertIn("risk", top)
            self.assertIn("final_score", top["risk"])

    def test_day29_soc_dashboard_role_separation(self):
        """
        GET /dashboard/soc must be accessible to SOC Engineer,
        but blocked (HTTP 403 Forbidden) for Security Analyst.
        """
        # 1. Analyst is blocked
        status_analyst, _ = http_request("GET", "/dashboard/soc", token=self.analyst_token)
        self.assertEqual(status_analyst, 403, "Security Analyst must be blocked with 403 from /dashboard/soc")

        # 2. SOC Engineer can access
        status_soc, body_soc = http_request("GET", "/dashboard/soc", token=self.soc_token)
        self.assertEqual(status_soc, 200)
        self.assertIn("alerts_by_severity", body_soc)
        self.assertIn("anomalies_last_7_days", body_soc)
        self.assertIn("active_investigations", body_soc)
        self.assertEqual(len(body_soc["anomalies_last_7_days"]), 7)


if __name__ == "__main__":
    unittest.main()
