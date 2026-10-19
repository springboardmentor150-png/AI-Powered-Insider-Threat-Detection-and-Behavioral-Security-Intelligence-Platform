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
from app.models import Base, User
from app.main import app
from app.auth import verify_password, decode_token

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8001
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


def make_request(method, path, data=None, headers=None):
    url = f"{BASE_URL}{path}"
    req_headers = headers or {}
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
            return status_code, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        status_code = e.code
        body = e.read().decode("utf-8")
        return status_code, json.loads(body) if body else {}


class TestAuthLive(unittest.TestCase):
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
        from app.seed import seed_initial_data
        db = SessionLocal()
        seed_initial_data(db)
        db.close()

    def setUp(self):
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        db.query(User).delete()
        db.commit()
        db.close()

    def test_01_health_check(self):
        status, data = make_request("GET", "/")
        self.assertEqual(status, 200)
        self.assertEqual(data, {"status": "ITBIS backend is running"})

    def test_02_auth_test_route(self):
        status, data = make_request("GET", "/auth/test")
        self.assertEqual(status, 200)
        self.assertEqual(data, {"message": "Authentication route is working"})

    def test_03_valid_signup(self):
        payload = {
            "email": "analyst@itbis.com",
            "password": "StrongSecurityPassword123!",
            "role": "security_analyst"
        }
        status, data = make_request("POST", "/auth/signup", data=payload)
        self.assertEqual(status, 201)
        self.assertEqual(data["message"], "User created successfully")
        self.assertEqual(data["email"], "analyst@itbis.com")
        self.assertEqual(data["role"], "security_analyst")
        self.assertIn("id", data)

        # Ensure no sensitive fields exposed
        self.assertNotIn("password", data)
        self.assertNotIn("password_hash", data)

        # Verify DB directly
        db = SessionLocal()
        user = db.query(User).filter(User.email == "analyst@itbis.com").first()
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, "StrongSecurityPassword123!")
        self.assertTrue(user.password_hash.startswith("$2b$"))
        self.assertTrue(verify_password("StrongSecurityPassword123!", user.password_hash))
        db.close()

    def test_04_duplicate_signup_rejected(self):
        payload = {
            "email": "duplicate@itbis.com",
            "password": "Password123!",
            "role": "security_analyst"
        }
        status1, _ = make_request("POST", "/auth/signup", data=payload)
        self.assertEqual(status1, 201)

        status2, data2 = make_request("POST", "/auth/signup", data=payload)
        self.assertEqual(status2, 400)
        self.assertEqual(data2["detail"], "Email already registered")

    def test_05_missing_fields_rejected(self):
        status, _ = make_request("POST", "/auth/signup", data={"email": "bad@itbis.com"})
        self.assertEqual(status, 422)

        status2, _ = make_request("POST", "/auth/signup", data={"password": "Password123!"})
        self.assertEqual(status2, 422)

    def test_06_login_success_and_jwt(self):
        signup_payload = {
            "email": "soc@itbis.com",
            "password": "SocEngineerSecure789!",
            "role": "soc_engineer"
        }
        make_request("POST", "/auth/signup", data=signup_payload)

        login_payload = {
            "email": "soc@itbis.com",
            "password": "SocEngineerSecure789!"
        }
        status, data = make_request("POST", "/auth/login", data=login_payload)
        self.assertEqual(status, 200)
        self.assertEqual(data["token_type"], "bearer")
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["email"], "soc@itbis.com")
        self.assertEqual(data["user"]["role"], "soc_engineer")

        # Decode and verify JWT
        token = data["access_token"]
        payload = decode_token(token)
        self.assertEqual(payload["role"], "soc_engineer")
        self.assertEqual(payload["sub"], str(data["user"]["id"]))

    def test_07_login_invalid_credentials_rejected(self):
        signup_payload = {
            "email": "manager@itbis.com",
            "password": "ManagerPassword456!",
            "role": "security_manager"
        }
        make_request("POST", "/auth/signup", data=signup_payload)

        # Incorrect password
        status_wrong, data_wrong = make_request("POST", "/auth/login", data={
            "email": "manager@itbis.com",
            "password": "WrongPassword!"
        })
        self.assertEqual(status_wrong, 401)
        self.assertEqual(data_wrong["detail"], "Invalid email or password")

        # Nonexistent user
        status_ghost, data_ghost = make_request("POST", "/auth/login", data={
            "email": "nonexistent@itbis.com",
            "password": "AnyPassword!"
        })
        self.assertEqual(status_ghost, 401)
        self.assertEqual(data_ghost["detail"], "Invalid email or password")


if __name__ == "__main__":
    unittest.main()
