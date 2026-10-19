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
from app.auth import create_token

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8011
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


def make_request(method, path, data=None, token=None, origin="http://localhost:3000"):
    url = f"{BASE_URL}{path}"
    headers = {"Origin": origin}
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
            resp_headers = dict(response.headers)
            body = response.read().decode("utf-8")
            return status_code, json.loads(body) if body else {}, resp_headers
    except urllib.error.HTTPError as e:
        status_code = e.code
        resp_headers = dict(e.headers)
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return status_code, parsed, resp_headers


class TestDashboardAndIntegration(unittest.TestCase):
    server_thread = None

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.server_thread = UvicornServerThread()
        cls.server_thread.start()

        for _ in range(30):
            try:
                code, _, _ = make_request("GET", "/health")
                if code == 200:
                    break
            except Exception:
                pass
            time.sleep(0.15)

        cls.token = create_token(user_id=1, role="Administrator")

    @classmethod
    def tearDownClass(cls):
        if cls.server_thread:
            cls.server_thread.stop()

    def test_01_cors_headers_on_localhost_origin(self):
        """CORS headers must be returned for http://localhost:3000."""
        status, data, headers = make_request("GET", "/health", origin="http://localhost:3000")
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("access-control-allow-origin"), "http://localhost:3000")

    def test_02_login_endpoint(self):
        """POST /auth/login verifies registered admin user and returns token."""
        status, res, _ = make_request("POST", "/auth/login", data={
            "email": "admin@itbis.cyber",
            "password": "AdminPassword123!"
        })
        self.assertEqual(status, 200)
        self.assertIn("access_token", res)
        self.assertEqual(res["user"]["email"], "admin@itbis.cyber")

    def test_03_dashboard_summary(self):
        """GET /dashboard/summary returns telemetry metrics and counts."""
        status, res, _ = make_request("GET", "/dashboard/summary", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("total_employees", res)
        self.assertIn("active_monitoring", res)
        self.assertIn("high_risk_employees", res)
        self.assertIn("open_alerts", res)
        self.assertIn("total_activities_ingested", res)
        self.assertEqual(res.get("system_status"), "OPERATIONAL")

    def test_04_alerts_endpoint(self):
        """GET /alerts?limit=5 returns paginated alerts."""
        status, res, _ = make_request("GET", "/alerts?limit=5", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("items", res)
        self.assertIsInstance(res["items"], list)
        self.assertLessEqual(len(res["items"]), 5)

    def test_05_threat_distribution(self):
        """GET /dashboard/threat-distribution returns categories breakdown."""
        status, res, _ = make_request("GET", "/dashboard/threat-distribution", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("categories", res)
        self.assertIsInstance(res["categories"], list)
        self.assertGreater(len(res["categories"]), 0)

    def test_06_activity_logs(self):
        """GET /activity-logs?limit=5 returns telemetry events."""
        status, res, _ = make_request("GET", "/activity-logs?limit=5", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("items", res)
        self.assertIsInstance(res["items"], list)
        self.assertLessEqual(len(res["items"]), 5)

    def test_07_employees_high_risk(self):
        """GET /employees?risk_level=HIGH&limit=4 returns filtered employees."""
        status, res, _ = make_request("GET", "/employees?risk_level=HIGH&limit=4", token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("items", res)
        self.assertIsInstance(res["items"], list)

    def test_08_dashboard_trends(self):
        """GET /dashboard/trend returns trend points for 24h, 7d, and 30d."""
        for tf in ["24h", "7d", "30d"]:
            status, res, _ = make_request("GET", f"/dashboard/trend?timeframe={tf}", token=self.token)
            self.assertEqual(status, 200)
            self.assertIn("points", res)
            self.assertIsInstance(res["points"], list)
            self.assertGreater(len(res["points"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
