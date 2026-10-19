import json
import urllib.request
import urllib.error
import unittest
import sys
import os

BASE_URL = "http://127.0.0.1:8000"

def request(method, path, data=None, token=None):
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


class TestMilestone1Day9And10(unittest.TestCase):
    admin_token = None
    analyst_token = None
    test_user_id = None
    test_employee_db_id = None

    @classmethod
    def setUpClass(cls):
        # Ensure default seed accounts exist even if an isolated test wiped users
        from app.database import SessionLocal
        from app.seed import seed_initial_data
        db = SessionLocal()
        try:
            seed_initial_data(db)
        finally:
            db.close()

        # 1. Login as Admin
        status, res = request("POST", "/auth/login", {
            "email": "admin@itbis.cyber",
            "password": "AdminPassword123!"
        })
        assert status == 200, f"Admin login failed: {res}"
        cls.admin_token = res["access_token"]

    def test_01_signup_and_password_hashing_security(self):
        """Signup verifies password hashing without exposing password or hash in response."""
        test_email = "audit_analyst_temp@itbis.cyber"
        # Cleanup if leftover
        status, res = request("POST", "/auth/signup", {
            "email": test_email,
            "password": "SecurePassword123!",
            "role": "Security Analyst"
        })
        if status == 400 and "already registered" in str(res):
            # Already exists, login
            status_login, res_login = request("POST", "/auth/login", {
                "email": test_email,
                "password": "SecurePassword123!"
            })
            self.assertEqual(status_login, 200)
            self.__class__.analyst_token = res_login["access_token"]
            return

        self.assertEqual(status, 201)
        self.assertIn("id", res)
        self.assertEqual(res["email"], test_email)
        # Ensure password and hash are NOT exposed
        self.assertNotIn("password", res)
        self.assertNotIn("password_hash", res)
        self.__class__.test_user_id = res["id"]

        # Check DB directly to verify bcrypt hash
        from app.database import SessionLocal
        from app.models import User
        db = SessionLocal()
        try:
            u = db.query(User).filter(User.id == res["id"]).first()
            self.assertIsNotNone(u)
            self.assertTrue(u.password_hash.startswith("$2b$") or u.password_hash.startswith("$2a$"))
            self.assertNotEqual(u.password_hash, "SecurePassword123!")
        finally:
            db.close()

    def test_02_login_and_jwt_authentication(self):
        """Login verifies credentials and returns a valid JWT token."""
        test_email = "audit_analyst_temp@itbis.cyber"
        status, res = request("POST", "/auth/login", {
            "email": test_email,
            "password": "SecurePassword123!"
        })
        self.assertEqual(status, 200)
        self.assertIn("access_token", res)
        self.assertEqual(res["token_type"], "bearer")
        self.assertEqual(res["user"]["email"], test_email)
        self.__class__.analyst_token = res["access_token"]

        # Wrong password must fail
        status_bad, _ = request("POST", "/auth/login", {
            "email": test_email,
            "password": "WrongPassword!"
        })
        self.assertEqual(status_bad, 401)

    def test_03_role_based_permissions_permitted_vs_forbidden(self):
        """Permitted vs Forbidden endpoints by role (Analyst is forbidden from ingest/employee create, Admin is permitted)."""
        # 1. Analyst attempts to ingest activity log -> 403 Forbidden
        status_forbid, res_forbid = request("POST", "/activity-logs", {
            "employee_id": "CYB-1042",
            "event_type": "login",
            "action": "Unauthorized Analyst Ingestion"
        }, token=self.analyst_token)
        self.assertEqual(status_forbid, 403)
        self.assertIn("Not authorized", str(res_forbid))

        # 2. Analyst attempts to create employee -> 403 Forbidden
        status_emp_forbid, _ = request("POST", "/employees", {
            "employee_id": "EMP-FORBIDDEN",
            "name": "Forbidden Test",
            "email": "forbid@enterprise.corp",
            "department": "IT",
            "designation": "Analyst"
        }, token=self.analyst_token)
        self.assertEqual(status_emp_forbid, 403)

        # 3. Admin is permitted to access these endpoints
        status_admin_ok, _ = request("GET", "/employees", token=self.admin_token)
        self.assertEqual(status_admin_ok, 200)

    def test_04_employee_creation_duplicate_validation_and_patch(self):
        """Create employee, verify duplicate rejection, and PATCH a single field."""
        emp_id = "AUD-9901"
        payload = {
            "employee_id": emp_id,
            "name": "Audit Test Subject",
            "email": "audit.subject@enterprise.corp",
            "department": "Information Security",
            "designation": "Staff Auditor",
            "work_location": "Hyderabad",
            "risk_score": 25
        }

        # Clean existing if needed
        from app.database import SessionLocal
        from app.models import Employee
        db = SessionLocal()
        try:
            existing = db.query(Employee).filter(Employee.employee_id == emp_id).first()
            if existing:
                db.delete(existing)
                db.commit()
        finally:
            db.close()

        # 1. Create employee with Admin token
        status_create, res_create = request("POST", "/employees", payload, token=self.admin_token)
        self.assertEqual(status_create, 201)
        self.assertEqual(res_create["employee_id"], emp_id)
        self.assertEqual(res_create["designation"], "Staff Auditor")
        self.__class__.test_employee_db_id = res_create["id"]

        # 2. Verify duplicate employee ID is rejected with 400 Bad Request
        status_dup, res_dup = request("POST", "/employees", payload, token=self.admin_token)
        self.assertEqual(status_dup, 400)
        self.assertIn("already registered", str(res_dup))

        # 3. Retrieve employee
        status_get, res_get = request("GET", f"/employees/{emp_id}", token=self.admin_token)
        self.assertEqual(status_get, 200)
        self.assertEqual(res_get["employee"]["employee_id"], emp_id)

        # 4. PATCH one field (designation)
        status_patch, res_patch = request("PATCH", f"/employees/{emp_id}", {
            "designation": "Senior Audit Specialist"
        }, token=self.admin_token)
        self.assertEqual(status_patch, 200)
        self.assertEqual(res_patch["designation"], "Senior Audit Specialist")
        # Ensure unrelated fields did not change
        self.assertEqual(res_patch["department"], "Information Security")
        self.assertEqual(res_patch["email"], "audit.subject@enterprise.corp")
        self.assertEqual(res_patch["work_location"], "Hyderabad")

    def test_05_activity_log_ingestion_validations(self):
        """Verify event_type list, reject unknown event_type (400), unknown employee (404), unauthenticated (401)."""
        emp_id = "AUD-9901"

        # 1. Reject unauthenticated request with 401
        status_unauth, _ = request("POST", "/activity-logs", {
            "employee_id": emp_id,
            "event_type": "login"
        })
        self.assertEqual(status_unauth, 401)

        # 2. Reject unknown event type with 400
        status_bad_event, res_bad_event = request("POST", "/activity-logs", {
            "employee_id": emp_id,
            "event_type": "crypto_mining_daemon"
        }, token=self.admin_token)
        self.assertEqual(status_bad_event, 400)
        self.assertIn("Unknown event_type", str(res_bad_event))

        # 3. Reject non-existent employee with 404
        status_no_emp, res_no_emp = request("POST", "/activity-logs", {
            "employee_id": "NONEXISTENT-EMP-99999",
            "event_type": "login"
        }, token=self.admin_token)
        self.assertEqual(status_no_emp, 404)
        self.assertIn("not found in employee registry", str(res_no_emp))

    def test_06_ingest_two_valid_events_and_objectid_conversion(self):
        """Ingest at least two valid event types, verify ObjectId converted to string."""
        emp_id = "AUD-9901"

        # Event 1: login
        status_ev1, res_ev1 = request("POST", "/activity-logs", {
            "employee_id": emp_id,
            "event_type": "login",
            "action": "Audit Subject Authenticated to Secure Vault",
            "resource": "https://vault.enterprise.corp",
            "device": "SEC-AUD-LAPTOP-01",
            "ip_address": "10.0.15.42",
            "location": "Hyderabad",
            "risk_weight": 10,
            "is_suspicious": False,
            "details": {"auth_factor": "MFA_TOTP"}
        }, token=self.admin_token)
        self.assertEqual(status_ev1, 201)
        self.assertIn("id", res_ev1)
        self.assertIsInstance(res_ev1["id"], str)
        self.assertNotIn("_id", res_ev1)

        # Event 2: usb_connect
        status_ev2, res_ev2 = request("POST", "/activity-logs", {
            "employee_id": emp_id,
            "event_type": "usb_connect",
            "action": "Hardware Security Token Inserted",
            "resource": "USB://YubiKey-5C-NFC",
            "device": "SEC-AUD-LAPTOP-01",
            "ip_address": "10.0.15.42",
            "location": "Hyderabad",
            "risk_weight": 5,
            "is_suspicious": False,
            "details": {"serial_number": "YK-982341"}
        }, token=self.admin_token)
        self.assertEqual(status_ev2, 201)
        self.assertIn("id", res_ev2)
        self.assertIsInstance(res_ev2["id"], str)
        self.assertNotIn("_id", res_ev2)

    def test_07_retrieve_logs_filtering_and_newest_first_sorting(self):
        """Retrieve logs with employee filtering, event_type filtering, validated limit, and newest-first order."""
        emp_id = "AUD-9901"

        # 1. Retrieve all logs for this employee
        status_all, res_all = request("GET", f"/activity-logs?employee_id={emp_id}", token=self.admin_token)
        self.assertEqual(status_all, 200)
        self.assertGreaterEqual(res_all["total"], 2)
        items = res_all["items"]
        self.assertTrue(all(item["employee_id"] == emp_id for item in items))

        # Verify newest-first ordering: timestamp[0] >= timestamp[1]
        t0 = items[0]["timestamp"]
        t1 = items[1]["timestamp"]
        self.assertGreaterEqual(t0, t1)

        # 2. Filter by event_type=usb_connect
        status_usb, res_usb = request("GET", f"/activity-logs?employee_id={emp_id}&event_type=usb_connect", token=self.admin_token)
        self.assertEqual(status_usb, 200)
        self.assertGreaterEqual(res_usb["total"], 1)
        self.assertTrue(all(item["event_type"] == "usb_connect" for item in res_usb["items"]))

        # 3. Validated result limit check
        # limit=0 is invalid (< 1) -> 422
        status_zero, _ = request("GET", "/activity-logs?limit=0", token=self.admin_token)
        self.assertEqual(status_zero, 422)

        # limit=101 is invalid (> 100) -> 422
        status_over, _ = request("GET", "/activity-logs?limit=101", token=self.admin_token)
        self.assertEqual(status_over, 422)

    def test_08_dashboard_activity_feed_operational(self):
        """Dashboard telemetry feed and summary continue to work without regression."""
        status_act, res_act = request("GET", "/activity-logs?limit=5", token=self.admin_token)
        self.assertEqual(status_act, 200)
        self.assertLessEqual(len(res_act["items"]), 5)

        status_sum, res_sum = request("GET", "/dashboard/summary", token=self.admin_token)
        self.assertEqual(status_sum, 200)
        self.assertIn("total_employees", res_sum)
        self.assertIn("critical_risk_employees", res_sum)

    @classmethod
    def tearDownClass(cls):
        # Safe cleanup of isolated test data
        from app.database import SessionLocal
        from app.models import Employee, User
        db = SessionLocal()
        try:
            db.query(Employee).filter(Employee.employee_id == "AUD-9901").delete()
            db.query(User).filter(User.email == "audit_analyst_temp@itbis.cyber").delete()
            db.commit()
        finally:
            db.close()

        # Clean from json store
        import json
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "activity_logs.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    docs = json.load(f)
                cleaned = [d for d in docs if d.get("employee_id") != "AUD-9901"]
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(cleaned, f, indent=2)
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
