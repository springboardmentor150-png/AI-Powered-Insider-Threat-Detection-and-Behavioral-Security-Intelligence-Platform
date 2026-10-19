"""
Unit & Integration Test Suite for Milestone 2: Days 19-20 Combined Anomaly Reports
ITBIS: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Tests:
1. Employee with rule-based anomalies only
2. Employee with ML anomalies only
3. Employee with both types (distinct detector evidence preserved)
4. Employee with no anomalies (graceful 200 OK)
5. Unknown employee (HTTP 404 Not Found)
6. Severity and ML score sorting (critical->high->medium->low; ML lowest/most negative score first)
7. Summary counts and top employees (deterministic ordering and unique employee distinction)
8. Empty storage response
9. Authentication and RBAC (401 on missing/invalid token, 200 on valid token)
10. Persistent JSON fallback resilience when MongoDB is offline
"""

import json
import os
import sys
import unittest
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Ensure backend root on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database import SessionLocal
from app.models import Employee, User
from app.auth import create_token
from app.mongodb import mongo_service, MongoDBService

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


class TestCombinedAnomalyReports(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()

        # Create or verify test admin user for JWT auth
        admin_user = cls.db.query(User).filter(User.email == "admin@itbis.cyber").first()
        if not admin_user:
            admin_user = User(
                email="admin@itbis.cyber",
                name="Security Administrator",
                role="ADMIN",
                is_active=True,
            )
            admin_user.set_password("AdminPassword123!")
            cls.db.add(admin_user)
            cls.db.commit()
            cls.db.refresh(admin_user)

        cls.token = create_token(user_id=admin_user.id, role=admin_user.role)


        # Seed test employees in SQL registry
        cls.test_employees = [
            ("EMP-RULE-ONLY", "Rule Only Employee", "IT"),
            ("EMP-ML-ONLY", "ML Only Employee", "Finance"),
            ("EMP-BOTH", "Hybrid Threat Employee", "Security"),
            ("EMP-CLEAN", "Clean Baseline Employee", "HR"),
            ("EMP-SORT-TEST", "Sorting Test Employee", "Engineering"),
        ]

        for code, name, dept in cls.test_employees:
            emp = cls.db.query(Employee).filter(Employee.employee_id == code).first()
            if not emp:
                emp = Employee(
                    employee_id=code,
                    name=name,
                    email=f"{code.lower()}@itbis.cyber",
                    department=dept,
                    designation="Test Subject",
                    risk_score=10,
                    risk_level="LOW",
                    status="ACTIVE",
                )
                cls.db.add(emp)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        for code, _, _ in cls.test_employees:
            mongo_service.clear_anomalies(code)
        cls.db.close()

    def setUp(self):
        for code, _, _ in self.test_employees:
            mongo_service.clear_anomalies(code)

    def tearDown(self):
        for code, _, _ in self.test_employees:
            mongo_service.clear_anomalies(code)

    def test_01_employee_with_rule_based_anomalies_only(self):
        """1. Employee with rule-based anomalies only returns correct counts and zero ML anomalies."""
        emp_id = "EMP-RULE-ONLY"

        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "UNUSUAL_LOGIN_TIME",
            "indicator": "avg_login_hour",
            "severity": "high",
            "observed_value": 3.5,
            "typical_value": 9.0,
            "detection_timestamp": "2026-09-10T03:30:00Z",
        })
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "ABNORMAL_DATA_TRANSFER",
            "indicator": "data_transfer_volume",
            "severity": "critical",
            "observed_value": 150.0,
            "typical_value": 20.0,
            "detection_timestamp": "2026-09-10T11:00:00Z",
        })

        status_code, data = http_request("GET", f"/anomalies/{emp_id}", token=self.token)
        self.assertEqual(status_code, 200)

        self.assertEqual(data["employee_id"], emp_id)
        self.assertEqual(data["total_anomalies"], 2)
        self.assertEqual(data["total_rule_anomalies"], 2)
        self.assertEqual(data["total_ml_anomalies"], 0)
        self.assertEqual(len(data["rule_based_anomalies"]), 2)
        self.assertEqual(len(data["ml_anomalies"]), 0)
        self.assertEqual(data["severity_counts"]["critical"], 1)
        self.assertEqual(data["severity_counts"]["high"], 1)

    def test_02_employee_with_ml_anomalies_only(self):
        """2. Employee with ML anomalies only returns correct score, flag, and zero rule anomalies."""
        emp_id = "EMP-ML-ONLY"

        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "ML_ISOLATION_FOREST",
            "indicator": "isolation_forest",
            "severity": "critical",
            "observed_value": "Score: -0.2150 (Flag: -1)",
            "expected_baseline": "Normal operational behavior (score >= 0.0)",
            "details": {
                "date": "2026-09-15",
                "anomaly_score": -0.2150,
                "anomaly_flag": -1,
                "features": {
                    "avg_login_hour": 2.0,
                    "download_count": 35,
                    "total_download_mb": 4200.0,
                    "unique_devices": 4,
                    "total_events": 80,
                },
            },
            "detection_timestamp": "2026-09-15T18:00:00Z",
        })

        status_code, data = http_request("GET", f"/anomalies/{emp_id}", token=self.token)
        self.assertEqual(status_code, 200)

        self.assertEqual(data["employee_id"], emp_id)
        self.assertEqual(data["total_anomalies"], 1)
        self.assertEqual(data["total_rule_anomalies"], 0)
        self.assertEqual(data["total_ml_anomalies"], 1)
        self.assertEqual(len(data["rule_based_anomalies"]), 0)
        self.assertEqual(len(data["ml_anomalies"]), 1)

        ml_item = data["ml_anomalies"][0]
        self.assertEqual(ml_item["anomaly_type"], "ML_ISOLATION_FOREST")
        self.assertAlmostEqual(ml_item["anomaly_score"], -0.2150, places=4)
        self.assertEqual(ml_item["anomaly_flag"], -1)
        self.assertEqual(ml_item["date"], "2026-09-15")
        self.assertIsNotNone(ml_item["feature_values"])
        self.assertEqual(ml_item["feature_values"]["download_count"], 35)

    def test_03_employee_with_both_types(self):
        """3. Employee with both types preserves distinct detector evidence without duplication."""
        emp_id = "EMP-BOTH"

        # 1. Rule anomaly: suspicious device
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "SUSPICIOUS_DEVICE",
            "indicator": "device_usage",
            "severity": "high",
            "observed_value": "Unauthorized-External-Node",
            "expected_baseline": "Corporate-Laptop-01",
            "detection_timestamp": "2026-09-20T10:00:00Z",
        })

        # 2. ML anomaly on same date
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "ML_ISOLATION_FOREST",
            "indicator": "isolation_forest",
            "severity": "critical",
            "observed_value": "Score: -0.1800 (Flag: -1)",
            "expected_baseline": "Normal operational behavior (score >= 0.0)",
            "details": {
                "date": "2026-09-20",
                "anomaly_score": -0.1800,
                "anomaly_flag": -1,
                "features": {
                    "avg_login_hour": 10.0,
                    "download_count": 5,
                    "total_download_mb": 1500.0,
                    "unique_devices": 3,
                    "total_events": 25,
                },
            },
            "detection_timestamp": "2026-09-20T18:00:00Z",
        })

        status_code, data = http_request("GET", f"/anomalies/{emp_id}", token=self.token)
        self.assertEqual(status_code, 200)

        self.assertEqual(data["employee_id"], emp_id)
        self.assertEqual(data["total_anomalies"], 2)
        self.assertEqual(data["total_rule_anomalies"], 1)
        self.assertEqual(data["total_ml_anomalies"], 1)
        self.assertEqual(len(data["rule_based_anomalies"]), 1)
        self.assertEqual(len(data["ml_anomalies"]), 1)

        # Confirm distinct detector evidence preserved
        self.assertEqual(data["rule_based_anomalies"][0]["anomaly_type"], "SUSPICIOUS_DEVICE")
        self.assertEqual(data["ml_anomalies"][0]["anomaly_type"], "ML_ISOLATION_FOREST")

    def test_04_employee_with_no_anomalies(self):
        """4. Known employee with zero anomalies returns graceful 200 OK with empty lists."""
        emp_id = "EMP-CLEAN"

        status_code, data = http_request("GET", f"/anomalies/{emp_id}", token=self.token)
        self.assertEqual(status_code, 200)

        self.assertEqual(data["employee_id"], emp_id)
        self.assertEqual(data["total_anomalies"], 0)
        self.assertEqual(data["total_rule_anomalies"], 0)
        self.assertEqual(data["total_ml_anomalies"], 0)
        self.assertEqual(data["rule_based_anomalies"], [])
        self.assertEqual(data["ml_anomalies"], [])
        self.assertEqual(data["severity_counts"]["critical"], 0)

    def test_05_unknown_employee(self):
        """5. Non-existent employee returns HTTP 404 Not Found."""
        status_code, data = http_request("GET", "/anomalies/NON-EXISTENT-EMP-XYZ", token=self.token)
        self.assertEqual(status_code, 404)
        self.assertIn("not found in registry", data.get("detail", ""))

    def test_06_severity_and_ml_score_sorting(self):
        """6. Verifies rule anomalies sorted critical->high->medium->low and ML anomalies sorted most anomalous first."""
        emp_id = "EMP-SORT-TEST"

        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "A1_LOW",
            "indicator": "ind1",
            "severity": "low",
            "observed_value": 1,
            "detection_timestamp": "2026-09-01T10:00:00Z",
        })
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "A2_CRITICAL",
            "indicator": "ind2",
            "severity": "critical",
            "observed_value": 2,
            "detection_timestamp": "2026-09-01T11:00:00Z",
        })
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "A3_MEDIUM",
            "indicator": "ind3",
            "severity": "medium",
            "observed_value": 3,
            "detection_timestamp": "2026-09-01T12:00:00Z",
        })
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "A4_HIGH",
            "indicator": "ind4",
            "severity": "high",
            "observed_value": 4,
            "detection_timestamp": "2026-09-01T13:00:00Z",
        })

        # Seed ML anomalies with varying scores: -0.05, -0.32, -0.15
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "ML_ISOLATION_FOREST",
            "indicator": "isolation_forest",
            "details": {"date": "2026-09-02", "anomaly_score": -0.05, "anomaly_flag": -1},
            "detection_timestamp": "2026-09-02T10:00:00Z",
        })
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "ML_ISOLATION_FOREST",
            "indicator": "isolation_forest",
            "details": {"date": "2026-09-03", "anomaly_score": -0.32, "anomaly_flag": -1},
            "detection_timestamp": "2026-09-03T10:00:00Z",
        })
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "ML_ISOLATION_FOREST",
            "indicator": "isolation_forest",
            "details": {"date": "2026-09-04", "anomaly_score": -0.15, "anomaly_flag": -1},
            "detection_timestamp": "2026-09-04T10:00:00Z",
        })

        status_code, data = http_request("GET", f"/anomalies/{emp_id}", token=self.token)
        self.assertEqual(status_code, 200)

        # Rule sorting check: critical -> high -> medium -> low
        rule_sevs = [r["severity"] for r in data["rule_based_anomalies"]]
        self.assertEqual(rule_sevs, ["critical", "high", "medium", "low"])

        # ML score sorting check: most anomalous (lowest / most negative) first: -0.32 -> -0.15 -> -0.05
        ml_scores = [m["anomaly_score"] for m in data["ml_anomalies"]]
        self.assertEqual(ml_scores, [-0.32, -0.15, -0.05])

    def test_07_summary_counts_and_top_employees(self):
        """7. Verifies summary endpoint aggregations, deterministic ranking, and distinct employee counts."""
        mongo_service.record_anomaly({
            "employee_id": "EMP-RULE-ONLY",
            "anomaly_type": "UNUSUAL_LOGIN_TIME",
            "indicator": "avg_login_hour",
            "severity": "critical",
            "observed_value": 3.0,
            "detection_timestamp": "2026-09-22T04:00:00Z",
            "details": {"date": "2026-09-22"},
        })
        mongo_service.record_anomaly({
            "employee_id": "EMP-RULE-ONLY",
            "anomaly_type": "ABNORMAL_DATA_TRANSFER",
            "indicator": "data_transfer_volume",
            "severity": "high",
            "observed_value": 120.0,
            "detection_timestamp": "2026-09-22T05:00:00Z",
            "details": {"date": "2026-09-22"},
        })
        mongo_service.record_anomaly({
            "employee_id": "EMP-ML-ONLY",
            "anomaly_type": "ML_ISOLATION_FOREST",
            "indicator": "isolation_forest",
            "severity": "high",
            "observed_value": "Score: -0.1200",
            "detection_timestamp": "2026-09-23T12:00:00Z",
            "details": {"date": "2026-09-23", "anomaly_score": -0.1200},
        })

        status_code, data = http_request("GET", "/anomalies/summary", token=self.token)
        self.assertEqual(status_code, 200)

        self.assertGreaterEqual(data["total_anomalies"], 3)
        self.assertGreaterEqual(data["total_rule_anomalies"], 2)
        self.assertGreaterEqual(data["total_ml_anomalies"], 1)
        self.assertEqual(data["total_anomalies"], data["total_rule_anomalies"] + data["total_ml_anomalies"])
        self.assertGreaterEqual(data["unique_employees"], 2)

        top_emps = data["top_employees"]
        self.assertGreaterEqual(len(top_emps), 2)
        self.assertGreaterEqual(top_emps[0]["total_anomalies"], top_emps[1]["total_anomalies"])

        self.assertIsInstance(data["anomalies_over_time"], list)
        self.assertGreaterEqual(len(data["anomalies_over_time"]), 1)

    def test_08_empty_storage_handling(self):
        """8. Anomaly summary handles empty storage gracefully with 0 counts."""
        from unittest.mock import patch
        import app.routes.anomaly_routes as anom_routes

        with patch.object(anom_routes.mongo_service, "get_anomalies", return_value=[]):
            resp = anom_routes.get_anomaly_summary(db=self.db, current_user={"sub": "1", "role": "ADMIN"})
            data = resp.model_dump() if hasattr(resp, "model_dump") else resp.dict()

            self.assertEqual(data["total_anomalies"], 0)
            self.assertEqual(data["total_rule_anomalies"], 0)
            self.assertEqual(data["total_ml_anomalies"], 0)
            for s in ["critical", "high", "medium", "low"]:
                self.assertEqual(data["counts_by_severity"].get(s, 0), 0)
            self.assertEqual(data["top_employees"], [])
            self.assertEqual(data["anomalies_over_time"], [])

    def test_09_authentication_and_rbac(self):
        """9. Unauthenticated requests are rejected with 401; valid token is accepted."""
        # 1. No Authorization header -> 401
        status_code1, _ = http_request("GET", "/anomalies/summary")
        self.assertEqual(status_code1, 401)

        status_code2, _ = http_request("GET", "/anomalies/EMP-CLEAN")
        self.assertEqual(status_code2, 401)

        # 2. Invalid Bearer token -> 401
        status_code3, _ = http_request("GET", "/anomalies/summary", token="invalid.token.signature")
        self.assertEqual(status_code3, 401)

        # 3. Valid Bearer token -> 200
        status_code4, _ = http_request("GET", "/anomalies/summary", token=self.token)
        self.assertEqual(status_code4, 200)

    def test_10_persistent_json_fallback(self):
        """10. Persistent storage reloads anomalies across fresh service instances while MongoDB is offline."""
        emp_id = "EMP-RULE-ONLY"
        mongo_service.record_anomaly({
            "employee_id": emp_id,
            "anomaly_type": "PERSISTENCE_TEST_ANOMALY",
            "indicator": "persistence_indicator",
            "severity": "high",
            "observed_value": "Telemetry-Probe",
            "detection_timestamp": "2026-09-30T10:00:00Z",
        })

        fresh_service = MongoDBService()
        self.assertFalse(fresh_service.is_connected)

        records = fresh_service.get_anomalies(employee_id=emp_id)
        found = any(r.get("anomaly_type") == "PERSISTENCE_TEST_ANOMALY" for r in records)
        self.assertTrue(found, "Anomaly was not found in reloaded persistent storage.")


if __name__ == "__main__":
    unittest.main()
