import os
import sys
import time
import json
import threading
import urllib.request
import urllib.error
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.database import engine
from app.models import Base
from app.main import app

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8004
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"


class UvicornServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        config = uvicorn.Config(app=app, host=SERVER_HOST, port=SERVER_PORT, log_level="error")
        self.server = uvicorn.Server(config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def make_request(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
            return status_code, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        status_code = e.code
        body = e.read().decode("utf-8")
        return status_code, json.loads(body) if body else {}


class TestFullITBISWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.server_thread = UvicornServerThread()
        cls.server_thread.start()
        for _ in range(20):
            try:
                urllib.request.urlopen(f"{BASE_URL}/", timeout=1)
                break
            except Exception:
                time.sleep(0.2)

        # Create analyst user
        cls.analyst_email = f"soc_lead_{int(time.time())}@itbis.corp"
        make_request("POST", "/auth/signup", data={
            "email": cls.analyst_email,
            "password": "SecurePassword123!",
            "role": "security_analyst"
        })
        status, login_res = make_request("POST", "/auth/login", data={
            "email": cls.analyst_email,
            "password": "SecurePassword123!"
        })
        cls.token = login_res.get("access_token")

    @classmethod
    def tearDownClass(cls):
        cls.server_thread.stop()

    def test_01_core_end_to_end_behavioral_threat_pipeline(self):
        emp_code = f"EMP-TEST-{int(time.time()*1000)%100000}"
        # 1. Create Monitored Employee: EMP-TEST
        emp_payload = {
            "employee_id": emp_code,
            "name": "Jordan Bellamy",
            "email": f"j.bellamy.{emp_code}@enterprise.corp",
            "department": "Engineering",
            "designation": "Staff Cloud Engineer",
            "manager_name": "Alexander Hayes",
            "device_info": "MacBook Pro M3 (SEC-DEV-771)",
            "access_privileges": "STANDARD",
            "risk_score": 15,
            "status": "ACTIVE"
        }
        status, emp_created = make_request("POST", "/employees", data=emp_payload, token=self.token)
        self.assertEqual(status, 201)
        self.assertEqual(emp_created["employee_id"], emp_code)
        db_emp_id = emp_created["id"]

        # 2. Ingest Normal Daytime Activity
        normal_act = {
            "employee_id": db_emp_id,
            "activity_type": "APPLICATION_ACCESS",
            "action": "View sprint backlog tickets",
            "resource": "https://jira.corp.internal/browse/ENG-204",
            "device_id": "MacBook Pro M3 (SEC-DEV-771)",
            "ip_address": "10.0.4.18",
            "location_network": "Corporate LAN",
            "is_success": True
        }
        status, act_res = make_request("POST", "/activity-logs", data=normal_act, token=self.token)
        self.assertEqual(status, 201)
        self.assertEqual(act_res["activity_type"], "APPLICATION_ACCESS")

        # Verify no critical alert was generated for normal activity
        status, alerts_after_normal = make_request("GET", f"/alerts?employee_id={db_emp_id}", token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(len(alerts_after_normal["items"]), 0, "Normal activity generated unexpected alert")

        # 3. Simulate Suspicious Test Activity (Off-hours + Mass Exfiltration + Unrecognized Device)
        test_suspicious = {
            "employee_id": emp_code,
            "activity_type": "FILE_DOWNLOAD",
            "action": "Mass Analytics Archive Download (5.2 GB)",
            "resource": "s3://analytics-archive/customer-pii-vault.tar.gz",
            "scenario": "SUSPICIOUS_OFFHOURS_EXFIL",
            "download_size_mb": 5200,
            "device_id": "UNKNOWN-NODE-EXT-99",
            "ip_address": "198.51.100.77"
        }
        status, sim_res = make_request("POST", "/activity-logs/test-event", data=test_suspicious, token=self.token)
        self.assertEqual(status, 201)
        self.assertTrue(sim_res["is_test_event"])
        self.assertGreaterEqual(sim_res["anomalies_detected"], 1)
        self.assertGreaterEqual(sim_res["calculated_risk_score"], 80)
        self.assertEqual(sim_res["risk_level"], "CRITICAL")
        self.assertTrue(sim_res["alert_created"])
        alert_id = sim_res["alert_id"]

        # 4. Verify Alert is immediately queryable via GET /alerts
        status, alert_detail = make_request("GET", f"/alerts/{alert_id}", token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(alert_detail["id"], alert_id)
        self.assertEqual(alert_detail["status"], "OPEN")
        self.assertEqual(alert_detail["severity"], "CRITICAL")
        self.assertEqual(alert_detail["category"], "DATA_EXFILTRATION")

        # 5. SOC Analyst Acknowledges Alert
        status, ack_alert = make_request("PATCH", f"/alerts/{alert_id}/acknowledge", token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(ack_alert["status"], "ACKNOWLEDGED")
        self.assertTrue(ack_alert["acknowledged_at"])

        # 6. SOC Analyst Escalates Alert to Incident
        status, inc_res = make_request("POST", f"/alerts/{alert_id}/create-incident", token=self.token)
        self.assertEqual(status, 200)
        incident_id = inc_res["id"]
        self.assertEqual(inc_res["alert_id"], alert_id)
        self.assertEqual(inc_res["status"], "OPEN")
        self.assertEqual(inc_res["severity"], "CRITICAL")

        # 7. Update Incident Status to INVESTIGATING
        status, upd_inc = make_request("PATCH", f"/incidents/{incident_id}/status", data={
            "status": "INVESTIGATING",
            "resolution_notes": "Forensic isolation initiated on endpoint UNKNOWN-NODE-EXT-99."
        }, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(upd_inc["status"], "INVESTIGATING")

        # 8. Resolve Incident
        status, resolved_inc = make_request("PATCH", f"/incidents/{incident_id}/status", data={
            "status": "RESOLVED",
            "resolution_notes": "Revoked temporary access token. Monitored employee contacted."
        }, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(resolved_inc["status"], "RESOLVED")
        self.assertTrue(resolved_inc["resolved_at"])

        # 9. Verify Employee Dossier Reflects Pipeline
        status, dossier = make_request("GET", f"/employees/{emp_code}", token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(dossier["employee"]["risk_score"], sim_res["calculated_risk_score"])
        self.assertEqual(dossier["employee"]["risk_level"], "CRITICAL")
        self.assertGreaterEqual(len(dossier["alerts"]), 1)
        self.assertGreaterEqual(len(dossier["incidents"]), 1)

        # 10. Verify Behavior Analysis Endpoint
        status, behavior = make_request("GET", f"/behavior-analysis/{emp_code}", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("baseline", behavior)
        self.assertIn("recent_anomalies", behavior)

        # 11. Verify Risk Scores Endpoint
        status, risk_scores = make_request("GET", "/risk-scores", token=self.token)
        self.assertEqual(status, 200)
        self.assertGreaterEqual(risk_scores["total"], 1)

        # 12. Verify Reports & Notifications
        status, rep = make_request("GET", "/reports/summary", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("total_monitored_employees", rep)

        status, notifs = make_request("GET", "/notifications", token=self.token)
        self.assertEqual(status, 200)
        self.assertIsInstance(notifs, list)


if __name__ == "__main__":
    unittest.main()
