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
from app.database import engine, SessionLocal
from app.models import Base
from app.main import app

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8003
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


class TestE2EFullFlow(unittest.TestCase):
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

    @classmethod
    def tearDownClass(cls):
        cls.server_thread.stop()

    def test_full_pipeline(self):
        # 1. Health Probe
        status, health = make_request("GET", "/")
        self.assertEqual(status, 200)
        self.assertEqual(health.get("status"), "ITBIS backend is running")

        # 2. Signup User (Admin)
        admin_email = f"admin_{int(time.time())}@itbis.corp"
        status, signup_res = make_request("POST", "/auth/signup", data={
            "email": admin_email,
            "password": "StrongPassword123!",
            "role": "admin"
        })
        self.assertEqual(status, 201)
        self.assertEqual(signup_res["email"], admin_email)
        self.assertNotIn("password", signup_res)
        self.assertNotIn("password_hash", signup_res)

        # 3. Login User
        status, login_res = make_request("POST", "/auth/login", data={
            "email": admin_email,
            "password": "StrongPassword123!"
        })
        self.assertEqual(status, 200)
        token = login_res.get("access_token")
        self.assertTrue(token)
        self.assertEqual(login_res["user"]["email"], admin_email)

        # 4. Security Guard - Missing / Invalid Token
        status, err = make_request("GET", "/dashboard/summary", token=None)
        self.assertEqual(status, 401)

        status, err = make_request("GET", "/dashboard/summary", token="bad_token_123")
        self.assertEqual(status, 401)

        # 5. Dashboard Summary
        status, summary = make_request("GET", "/dashboard/summary", token=token)
        self.assertEqual(status, 200)
        self.assertGreaterEqual(summary["total_employees"], 1)
        self.assertGreaterEqual(summary["active_monitoring"], 1)
        self.assertGreaterEqual(summary["high_risk_employees"], 0)
        self.assertGreaterEqual(summary["open_alerts"], 0)

        # 6. Monitored Employees Pagination & Filtering
        status, emps = make_request("GET", "/employees?page=1&limit=5", token=token)
        self.assertEqual(status, 200)
        self.assertEqual(emps["page"], 1)
        self.assertEqual(emps["limit"], 5)
        self.assertIsInstance(emps["items"], list)
        self.assertGreaterEqual(emps["total"], 1)

        # 7. Create Monitored Employee
        emp_id = f"EMP-{int(time.time()) % 10000:04d}"
        status, created_emp = make_request("POST", "/employees", data={
            "employee_id": emp_id,
            "name": "Rachel Zane",
            "email": "r.zane@enterprise.corp",
            "department": "Legal & Compliance",
            "designation": "Associate Counsel",
            "manager_name": "Claire Dupont",
            "device_info": "MacBook Air M2",
            "access_privileges": "STANDARD",
            "risk_score": 85,
            "status": "ACTIVE"
        }, token=token)
        self.assertEqual(status, 201)
        self.assertEqual(created_emp["employee_id"], emp_id)
        self.assertEqual(created_emp["risk_level"], "CRITICAL") # 85 >= 80

        # 8. Get Employee Dossier
        status, dossier = make_request("GET", f"/employees/{emp_id}", token=token)
        self.assertEqual(status, 200)
        self.assertEqual(dossier["employee"]["name"], "Rachel Zane")
        self.assertIsInstance(dossier["alerts"], list)
        self.assertIsInstance(dossier["incidents"], list)

        # 9. Update Employee
        status, updated_emp = make_request("PUT", f"/employees/{emp_id}", data={
            "risk_score": 45,
            "status": "UNDER_REVIEW"
        }, token=token)
        self.assertEqual(status, 200)
        self.assertEqual(updated_emp["risk_score"], 45)
        self.assertEqual(updated_emp["risk_level"], "MEDIUM")
        self.assertEqual(updated_emp["status"], "UNDER_REVIEW")

        # 10. Alerts Listing
        status, alerts = make_request("GET", "/alerts?limit=5", token=token)
        self.assertEqual(status, 200)
        self.assertIsInstance(alerts["items"], list)

        # 11. Incidents Listing
        status, incidents = make_request("GET", "/incidents?limit=5", token=token)
        self.assertEqual(status, 200)
        self.assertIsInstance(incidents["items"], list)

        # 12. Delete Monitored Employee
        status, del_res = make_request("DELETE", f"/employees/{emp_id}", token=token)
        self.assertEqual(status, 200)

        # Verify 404 after deletion
        status, _ = make_request("GET", f"/employees/{emp_id}", token=token)
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
