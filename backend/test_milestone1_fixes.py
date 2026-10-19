import os
import sys
import time
import json
import threading
import urllib.request
import urllib.error
import unittest

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.database import engine, SessionLocal
from app.models import Base, Employee, User
from app.main import app
from app.auth import create_token

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8008
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
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return status_code, parsed


class TestMilestone1Fixes(unittest.TestCase):
    server_thread = None

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.server_thread = UvicornServerThread()
        cls.server_thread.start()

        # Wait for server to start
        for _ in range(30):
            try:
                code, _ = make_request("GET", "/health")
                if code == 200:
                    break
            except Exception:
                pass
            time.sleep(0.2)

        # Generate tokens
        cls.admin_token = create_token(user_id=1, role="Administrator")
        cls.sec_mgr_token = create_token(user_id=2, role="Security Manager")
        cls.analyst_token = create_token(user_id=3, role="Security Analyst")

    @classmethod
    def tearDownClass(cls):
        if cls.server_thread:
            cls.server_thread.stop()

    def test_01_analyst_forbidden_on_put_and_patch(self):
        """Security Analyst must receive HTTP 403 on PUT and PATCH employee updates."""
        # Check on an existing or test employee
        status_put, body_put = make_request(
            "PUT",
            "/employees/CYB-1042",
            data={"department": "Analyst Tampering Test"},
            token=self.analyst_token,
        )
        self.assertEqual(status_put, 403, f"Expected 403 on PUT by Analyst, got {status_put}: {body_put}")

        status_patch, body_patch = make_request(
            "PATCH",
            "/employees/CYB-1042",
            data={"department": "Analyst Tampering Test"},
            token=self.analyst_token,
        )
        self.assertEqual(status_patch, 403, f"Expected 403 on PATCH by Analyst, got {status_patch}: {body_patch}")

    def test_02_analyst_can_view_employees_and_reports(self):
        """Security Analyst can still view employee profiles and direct reports (read-only)."""
        status_get, body_get = make_request(
            "GET",
            "/employees/CYB-1042",
            token=self.analyst_token,
        )
        self.assertEqual(status_get, 200, f"Expected 200 on GET by Analyst, got {status_get}")

        status_reports, body_reports = make_request(
            "GET",
            "/employees/CYB-1042/direct-reports",
            token=self.analyst_token,
        )
        self.assertEqual(status_reports, 200, f"Expected 200 on GET direct reports by Analyst, got {status_reports}")
        self.assertIsInstance(body_reports, list)

    def test_03_admin_and_sec_mgr_can_update_employee(self):
        """Administrator and Security Manager can update employee records."""
        # Admin PATCH
        status_admin, body_admin = make_request(
            "PATCH",
            "/employees/CYB-1042",
            data={"designation": "Lead SecOps Architect"},
            token=self.admin_token,
        )
        self.assertEqual(status_admin, 200, f"Expected 200 on PATCH by Admin, got {status_admin}: {body_admin}")
        self.assertEqual(body_admin.get("designation"), "Lead SecOps Architect")

        # Security Manager PATCH
        status_mgr, body_mgr = make_request(
            "PATCH",
            "/employees/CYB-1042",
            data={"designation": "Principal SecOps Architect"},
            token=self.sec_mgr_token,
        )
        self.assertEqual(status_mgr, 200, f"Expected 200 on PATCH by Security Manager, got {status_mgr}: {body_mgr}")
        self.assertEqual(body_mgr.get("designation"), "Principal SecOps Architect")

    def test_04_patch_partial_update_preserves_omitted_fields(self):
        """PATCH updates only provided fields and preserves unmodified fields."""
        # First read CYB-1042 current state
        status_get, orig = make_request("GET", "/employees/CYB-1042", token=self.admin_token)
        orig_emp = orig.get("employee", {})
        orig_name = orig_emp.get("name")
        orig_email = orig_emp.get("email")

        # Update only department
        status_patch, res_patch = make_request(
            "PATCH",
            "/employees/CYB-1042",
            data={"department": "Threat Detection Unit"},
            token=self.admin_token,
        )
        self.assertEqual(status_patch, 200)
        self.assertEqual(res_patch.get("department"), "Threat Detection Unit")
        self.assertEqual(res_patch.get("name"), orig_name, "Name must not be wiped out by partial PATCH")
        self.assertEqual(res_patch.get("email"), orig_email, "Email must not be wiped out by partial PATCH")

    def test_05_manager_id_validation_on_create_and_update(self):
        """Supplying an invalid manager_id returns HTTP 400 Bad Request."""
        # Invalid manager on POST
        bad_create_data = {
            "employee_id": "TEST-BAD-MGR-01",
            "name": "Invalid Mgr Subordinate",
            "email": "invalid.mgr@threatintel.local",
            "department": "Engineering",
            "manager_id": 999999,  # Does not exist
        }
        status_post, body_post = make_request(
            "POST",
            "/employees",
            data=bad_create_data,
            token=self.admin_token,
        )
        self.assertEqual(status_post, 400, f"Expected 400 on invalid manager_id POST, got {status_post}: {body_post}")
        self.assertIn("does not exist", str(body_post.get("detail", "")).lower())

        # Invalid manager on PATCH
        status_patch, body_patch = make_request(
            "PATCH",
            "/employees/CYB-1042",
            data={"manager_id": 999999},
            token=self.admin_token,
        )
        self.assertEqual(status_patch, 400, f"Expected 400 on invalid manager_id PATCH, got {status_patch}: {body_patch}")
        self.assertIn("does not exist", str(body_patch.get("detail", "")).lower())

    def test_06_manager_subordinate_linking_and_direct_reports(self):
        """Creating a manager and subordinate, validating direct-reports hierarchy."""
        mgr_eid = "TEST-MGR-99"
        sub_eid = "TEST-SUB-99"

        # 1. Create Manager
        mgr_data = {
            "employee_id": mgr_eid,
            "name": "Dr. Sarah Conner",
            "email": "sconner@cyberops.local",
            "department": "SOC Management",
            "designation": "Director of Security",
        }
        status_m, body_m = make_request("POST", "/employees", data=mgr_data, token=self.admin_token)
        self.assertEqual(status_m, 201, f"Failed creating manager: {body_m}")
        mgr_db_id = body_m["id"]

        try:
            # 2. Create Subordinate with manager_id
            sub_data = {
                "employee_id": sub_eid,
                "name": "Kyle Reese",
                "email": "kreese@cyberops.local",
                "department": "SOC Management",
                "designation": "Security Specialist",
                "manager_id": mgr_db_id,
            }
            status_s, body_s = make_request("POST", "/employees", data=sub_data, token=self.admin_token)
            self.assertEqual(status_s, 201, f"Failed creating subordinate: {body_s}")
            self.assertEqual(body_s.get("manager_id"), mgr_db_id)
            self.assertEqual(body_s.get("manager_name"), "Dr. Sarah Conner")

            # 3. Verify GET direct reports on Manager
            status_dr, list_dr = make_request("GET", f"/employees/{mgr_eid}/direct-reports", token=self.admin_token)
            self.assertEqual(status_dr, 200)
            self.assertIsInstance(list_dr, list)
            sub_ids = [emp["employee_id"] for emp in list_dr]
            self.assertIn(sub_eid, sub_ids, f"Expected {sub_eid} in direct reports of {mgr_eid}: {list_dr}")

            # 4. Verify Subordinate has empty direct reports []
            status_sub_dr, sub_dr_list = make_request("GET", f"/employees/{sub_eid}/direct-reports", token=self.admin_token)
            self.assertEqual(status_sub_dr, 200)
            self.assertEqual(sub_dr_list, [], "Subordinate with no direct reports should return empty list []")

            # 5. Verify direct reports on non-existent employee returns 404
            status_404, body_404 = make_request("GET", "/employees/NONEXISTENT-EID-404/direct-reports", token=self.admin_token)
            self.assertEqual(status_404, 404, f"Expected 404 for non-existent employee, got {status_404}")

        finally:
            # Cleanup test employees
            make_request("DELETE", f"/employees/{sub_eid}", token=self.admin_token)
            make_request("DELETE", f"/employees/{mgr_eid}", token=self.admin_token)


if __name__ == "__main__":
    unittest.main(verbosity=2)
