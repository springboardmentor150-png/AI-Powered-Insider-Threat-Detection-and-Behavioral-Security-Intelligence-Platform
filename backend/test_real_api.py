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
from app.models import Base, User, Employee, Alert, Incident
from app.main import app

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8002
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


class TestRealAPIs(unittest.TestCase):
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

        # Create test analyst and obtain token
        signup_payload = {
            "email": "test_analyst@itbis.com",
            "password": "Password123!",
            "role": "security_analyst"
        }
        make_request("POST", "/auth/signup", data=signup_payload)
        status, login_data = make_request("POST", "/auth/login", data={
            "email": "test_analyst@itbis.com",
            "password": "Password123!"
        })
        cls.token = login_data.get("access_token")

        # Create test admin and obtain token
        signup_admin = {
            "email": "test_admin@itbis.com",
            "password": "Password123!",
            "role": "admin"
        }
        make_request("POST", "/auth/signup", data=signup_admin)
        status_adm, login_adm = make_request("POST", "/auth/login", data={
            "email": "test_admin@itbis.com",
            "password": "Password123!"
        })
        cls.admin_token = login_adm.get("access_token")

    @classmethod
    def tearDownClass(cls):
        cls.server_thread.stop()

    def test_01_unauthenticated_requests_blocked(self):
        endpoints = ["/dashboard/summary", "/employees", "/alerts", "/incidents"]
        for ep in endpoints:
            status, data = make_request("GET", ep, token=None)
            self.assertEqual(status, 401, f"Endpoint {ep} allowed unauthenticated access")
            self.assertIn("detail", data)

    def test_02_dashboard_summary(self):
        status, data = make_request("GET", "/dashboard/summary", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("total_employees", data)
        self.assertIn("active_monitoring", data)
        self.assertIn("high_risk_employees", data)
        self.assertIn("open_alerts", data)
        self.assertGreaterEqual(data["total_employees"], 0)

    def test_03_get_employees_paginated(self):
        status, data = make_request("GET", "/employees?page=1&limit=5", token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["limit"], 5)
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertIsInstance(data["items"], list)

    def test_04_create_employee_and_get_by_id(self):
        new_emp = {
            "employee_id": "EMP-9999",
            "name": "David Sterling",
            "email": "d.sterling@enterprise.corp",
            "department": "Security",
            "designation": "Staff Detection Engineer",
            "manager_name": "Sarah Lin",
            "device_info": "MacBook Pro M3",
            "access_privileges": "ELEVATED",
            "risk_score": 75,
            "status": "ACTIVE"
        }
        status, created = make_request("POST", "/employees", data=new_emp, token=self.admin_token)
        self.assertEqual(status, 201)
        self.assertEqual(created["employee_id"], "EMP-9999")
        self.assertEqual(created["risk_level"], "HIGH")

        # Get by ID (Analyst can read)
        status_get, fetched = make_request("GET", "/employees/EMP-9999", token=self.token)
        self.assertEqual(status_get, 200)
        self.assertEqual(fetched["employee"]["employee_id"], "EMP-9999")
        self.assertEqual(fetched["employee"]["name"], "David Sterling")

    def test_05_update_and_delete_employee(self):
        update_data = {
            "designation": "Principal Detection Engineer",
            "risk_score": 90
        }
        status, updated = make_request("PUT", "/employees/EMP-9999", data=update_data, token=self.admin_token)
        self.assertEqual(status, 200)
        self.assertEqual(updated["designation"], "Principal Detection Engineer")
        self.assertEqual(updated["risk_level"], "CRITICAL")

        # Delete
        status_del, del_msg = make_request("DELETE", "/employees/EMP-9999", token=self.admin_token)
        self.assertEqual(status_del, 200)

        # Verify 404 on subsequent get
        status_not_found, _ = make_request("GET", "/employees/EMP-9999", token=self.token)
        self.assertEqual(status_not_found, 404)

    def test_06_alerts_and_incidents(self):
        # Alerts
        status_alerts, alerts = make_request("GET", "/alerts?limit=10", token=self.token)
        self.assertEqual(status_alerts, 200)
        self.assertIn("items", alerts)
        self.assertIn("total", alerts)

        # Incidents
        status_inc, incidents = make_request("GET", "/incidents?limit=10", token=self.token)
        self.assertEqual(status_inc, 200)
        self.assertIn("items", incidents)
        self.assertIn("total", incidents)


if __name__ == "__main__":
    unittest.main()
