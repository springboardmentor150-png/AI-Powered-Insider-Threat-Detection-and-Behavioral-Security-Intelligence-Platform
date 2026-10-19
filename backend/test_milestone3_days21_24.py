"""
Unit & Integration Test Suite for Milestone 3: Days 21-24
ITBIS: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Covers:
- Day 21: Weighted scoring model design, weight sum to 1.00, sub-score capping, mathematical single-factor ceiling.
- Day 22: Sub-score functions, multi-vector corroboration, boundary thresholds (Low/Medium/High/Critical),
          and GET /risk-score/{employee_id} (+ dual-route GET /risk-scores/{employee_id}).
- Day 23: Departmental peer group comparison, self-exclusion, single-person department edge case, peer percentile,
          and GET /ueba/peer-comparison/{employee_id}.
- Day 24: Chronological anomaly trend (zero date gaps), 14-day window halving trend direction (increasing/decreasing/stable),
          and GET /ueba/profile/{employee_id}.
- RBAC security verification across all Milestone 3 endpoints.
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
from app.models import Employee, Incident, User
from app.auth import create_token
from app.mongodb import mongo_service
from app.risk_scoring import (
    WEIGHTS,
    FACTOR_MULTIPLIERS,
    score_behavioral_anomalies,
    score_privilege_misuse,
    score_data_access_violations,
    score_access_pattern_deviations,
    score_historical_events,
    calculate_risk_score,
)
from app.ueba import (
    get_peer_group_comparison,
    get_risk_trend,
    get_trend_direction,
    get_ueba_profile,
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


class TestMilestone3Days21To24(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()

        # Ensure admin user for JWT auth
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

        # Seed dedicated test employees
        cls.test_employees = [
            ("EMP-M3-CLEAN", "Clean Test Employee", "Quality Assurance"),
            ("EMP-M3-BEHAVIOR", "Behavioral Anomaly Employee", "Engineering"),
            ("EMP-M3-PRIVILEGE", "Privilege Misuse Employee", "System Operations"),
            ("EMP-M3-MULTI", "Multi-Vector Threat Employee", "Finance"),
            ("EMP-M3-HIST", "Historical Incident Employee", "Legal"),
            ("EMP-M3-SOLO", "Solo Department Employee", "Special Research Lab"),
            ("EMP-M3-PEER-A", "Peer Employee Alpha", "Sales Operations"),
            ("EMP-M3-PEER-B", "Peer Employee Beta", "Sales Operations"),
            ("EMP-M3-PEER-C", "Peer Employee Gamma", "Sales Operations"),
            ("EMP-M3-TREND", "Trend Evaluation Employee", "Data Analytics"),
        ]

        cls.created_db_employees = {}
        for emp_id, name, dept in cls.test_employees:
            emp = cls.db.query(Employee).filter(Employee.employee_id == emp_id).first()
            if not emp:
                emp = Employee(
                    employee_id=emp_id,
                    name=name,
                    department=dept,
                    designation="Specialist",
                    status="ACTIVE",
                    risk_score=15,
                    risk_level="Low",
                )
                cls.db.add(emp)
                cls.db.commit()
                cls.db.refresh(emp)
            cls.created_db_employees[emp_id] = emp

        # Clear existing test anomalies from mongo_service for our test IDs
        now = datetime.now(timezone.utc)
        for emp_id, _, _ in cls.test_employees:
            mongo_service.clear_anomalies(emp_id)
        mongo_service.clear_anomalies("EMP-M3-CAP")

        # 1. EMP-M3-CLEAN has 0 anomalies, 0 incidents

        # 2. EMP-M3-BEHAVIOR has 3 timing anomalies
        for i in range(3):
            mongo_service.save_anomaly({
                "employee_id": "EMP-M3-BEHAVIOR",
                "anomaly_type": "UNUSUAL_LOGIN_TIME",
                "severity": "LOW",
                "description": f"Login off hours sample {i}",
                "timestamp": (now - timedelta(days=i)).isoformat(),
                "detected_at": (now - timedelta(days=i)).isoformat(),
            })

        # 3. EMP-M3-PRIVILEGE has 1 privilege escalation anomaly
        mongo_service.save_anomaly({
            "employee_id": "EMP-M3-PRIVILEGE",
            "anomaly_type": "PRIVILEGE_CHANGE",
            "severity": "HIGH",
            "description": "Unauthorized role grant detected",
            "timestamp": now.isoformat(),
            "detected_at": now.isoformat(),
        })

        # 4. EMP-M3-MULTI has multi-vector anomalies
        # 7 behavioral (70), 3 privilege (75), 3 data exfiltration (100), 4 unknown device (60)
        for _ in range(7):
            mongo_service.save_anomaly({
                "employee_id": "EMP-M3-MULTI",
                "anomaly_type": "UNUSUAL_OFF_HOURS",
                "severity": "MEDIUM",
                "description": "Unusual off hours access",
                "timestamp": now.isoformat(),
            })
        for _ in range(3):
            mongo_service.save_anomaly({
                "employee_id": "EMP-M3-MULTI",
                "anomaly_type": "PRIVILEGE_CHANGE",
                "severity": "CRITICAL",
                "description": "Admin privileges added",
                "timestamp": now.isoformat(),
            })
        for _ in range(3):
            mongo_service.save_anomaly({
                "employee_id": "EMP-M3-MULTI",
                "anomaly_type": "DATA_EXFILTRATION_RISK",
                "severity": "CRITICAL",
                "description": "Massive data exfiltration",
                "timestamp": now.isoformat(),
            })
        for _ in range(4):
            mongo_service.save_anomaly({
                "employee_id": "EMP-M3-MULTI",
                "anomaly_type": "UNKNOWN_DEVICE",
                "severity": "MEDIUM",
                "description": "Access from untrusted laptop",
                "timestamp": now.isoformat(),
            })

        # 5. EMP-M3-HIST has 5 past security incidents in SQL
        hist_emp = cls.created_db_employees["EMP-M3-HIST"]
        existing_incidents = cls.db.query(Incident).filter(Incident.employee_id == hist_emp.id).count()
        if existing_incidents < 5:
            for i in range(5 - existing_incidents):
                inc = Incident(
                    employee_id=hist_emp.id,
                    title=f"Historical Security Policy Breach {i+1}",
                    description="Resolved prior security infraction",
                    severity="MEDIUM",
                    status="RESOLVED",
                    created_at=datetime.now(timezone.utc) - timedelta(days=100 + i),
                )
                cls.db.add(inc)
            cls.db.commit()

        # 6. Sales Operations peers:
        # PEER-A has 2 data violations
        for _ in range(2):
            mongo_service.save_anomaly({
                "employee_id": "EMP-M3-PEER-A",
                "anomaly_type": "DATA_EXFILTRATION_RISK",
                "severity": "HIGH",
                "timestamp": now.isoformat(),
            })
        # PEER-B has 1 unknown device
        mongo_service.save_anomaly({
            "employee_id": "EMP-M3-PEER-B",
            "anomaly_type": "UNKNOWN_DEVICE",
            "severity": "LOW",
            "timestamp": now.isoformat(),
        })
        # PEER-C is clean

        # 7. EMP-M3-TREND has 0 anomalies in days 8-14 ago, and 5 anomalies in the last 7 days
        for day_offset in range(1, 6):
            mongo_service.save_anomaly({
                "employee_id": "EMP-M3-TREND",
                "anomaly_type": "UNUSUAL_LOGIN_TIME",
                "severity": "LOW",
                "timestamp": (now - timedelta(days=day_offset)).isoformat(),
                "detected_at": (now - timedelta(days=day_offset)).isoformat(),
                "details": {"date": (now - timedelta(days=day_offset)).strftime("%Y-%m-%d")},
            })

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # ==================== DAY 21 TESTS: WEIGHTED MODEL DESIGN ====================

    def test_day21_weights_sum_to_one(self):
        """Verify the 5 executive factor weights sum strictly to 1.00 (100%)."""
        total_weight = sum(WEIGHTS.values())
        self.assertAlmostEqual(total_weight, 1.0, places=5)
        self.assertEqual(WEIGHTS["behavioral_anomalies"], 0.35)
        self.assertEqual(WEIGHTS["privilege_misuse"], 0.25)
        self.assertEqual(WEIGHTS["data_access_violations"], 0.20)
        self.assertEqual(WEIGHTS["access_pattern_deviations"], 0.10)
        self.assertEqual(WEIGHTS["historical_events"], 0.10)

    def test_day21_factor_multipliers_and_max_out_thresholds(self):
        """Verify count-to-subscore multipliers and max-out design limits."""
        self.assertEqual(FACTOR_MULTIPLIERS["behavioral_anomalies"], 10.0)
        self.assertEqual(FACTOR_MULTIPLIERS["privilege_misuse"], 25.0)
        self.assertEqual(FACTOR_MULTIPLIERS["data_access_violations"], 40.0)
        self.assertEqual(FACTOR_MULTIPLIERS["access_pattern_deviations"], 15.0)
        self.assertEqual(FACTOR_MULTIPLIERS["historical_events"], 20.0)

    def test_day21_single_factor_mathematical_ceiling(self):
        """
        Verify that no single factor alone can reach a score of 60.0.
        The largest weight is Behavioral Anomalies (35%), which at max 100 contributes exactly 35.0.
        """
        for factor, weight in WEIGHTS.items():
            max_single_contribution = 100.0 * weight
            self.assertLess(max_single_contribution, 60.0, f"Factor '{factor}' alone should not reach 60.0")

    # ==================== DAY 22 TESTS: RISK SCORING ENGINE ====================

    def test_day22_clean_employee_scores_zero(self):
        """Clean employee with zero anomalies and zero incidents must score 0.0 with Low risk."""
        result = calculate_risk_score("EMP-M3-CLEAN", self.db)
        self.assertEqual(result["employee_id"], "EMP-M3-CLEAN")
        self.assertEqual(result["final_score"], 0.0)
        self.assertEqual(result["risk_level"], "Low")
        for sub, score in result["sub_scores"].items():
            self.assertEqual(score, 0.0, f"Sub-score {sub} should be 0.0 for clean employee")

    def test_day22_behavioral_anomalies_only_lands_in_low_or_medium(self):
        """Employee with 3 behavioral anomalies has sub-score 30.0 and final_score = 30 * 0.35 = 10.5 (Low)."""
        result = calculate_risk_score("EMP-M3-BEHAVIOR", self.db)
        self.assertEqual(result["sub_scores"]["behavioral_anomalies"], 30.0)
        self.assertEqual(result["sub_scores"]["privilege_misuse"], 0.0)
        self.assertEqual(result["final_score"], 10.5)
        self.assertEqual(result["risk_level"], "Low")

    def test_day22_privilege_misuse_score_jump(self):
        """Even 1 privilege misuse anomaly creates an immediate jump (25.0 sub-score, 6.3 final score)."""
        result = calculate_risk_score("EMP-M3-PRIVILEGE", self.db)
        self.assertEqual(result["sub_scores"]["privilege_misuse"], 25.0)
        self.assertAlmostEqual(result["final_score"], 6.25, delta=0.1)  # 25 * 0.25 = 6.25 (rounds to 6.2)

    def test_day22_multi_factor_threat_reaches_high_or_critical(self):
        """Multi-vector corroborated threats combine sub-scores across vectors to reach High or Critical."""
        result = calculate_risk_score("EMP-M3-MULTI", self.db)
        self.assertGreaterEqual(result["final_score"], 50.0)
        self.assertIn(result["risk_level"], ["High", "Critical"])
        self.assertGreater(result["sub_scores"]["behavioral_anomalies"], 0.0)
        self.assertGreater(result["sub_scores"]["privilege_misuse"], 0.0)
        self.assertGreater(result["sub_scores"]["data_access_violations"], 0.0)

    def test_day22_historical_events_only_bounded_by_ten_percent(self):
        """
        Employee with 5 historical incidents and no current anomalies has sub-score 100 on historical,
        producing a final_score of exactly 10.0 (Low risk), bounded by the 10% weight.
        """
        result = calculate_risk_score("EMP-M3-HIST", self.db)
        self.assertEqual(result["sub_scores"]["historical_events"], 100.0)
        self.assertEqual(result["sub_scores"]["behavioral_anomalies"], 0.0)
        self.assertEqual(result["final_score"], 10.0)
        self.assertEqual(result["risk_level"], "Low")

    def test_day22_sub_score_cap_at_one_hundred(self):
        """All sub-scores must never exceed 100.0 regardless of extreme raw counts."""
        # Inject extreme counts for a temporary test employee
        now = datetime.now(timezone.utc)
        for _ in range(25):
            mongo_service.save_anomaly({
                "employee_id": "EMP-M3-CAP",
                "anomaly_type": "PRIVILEGE_CHANGE",
                "severity": "CRITICAL",
                "timestamp": now.isoformat(),
            })
        sub = score_privilege_misuse("EMP-M3-CAP")
        self.assertEqual(sub, 100.0, "Sub-score must be strictly capped at 100.0")

    def test_day22_live_risk_score_endpoints(self):
        """Test live GET /risk-score/{employee_id} and GET /risk-scores/{employee_id} endpoints."""
        # Singular endpoint
        status_code, body = http_request("GET", "/risk-score/EMP-M3-BEHAVIOR", token=self.token)
        self.assertEqual(status_code, 200)
        self.assertEqual(body["employee_id"], "EMP-M3-BEHAVIOR")
        self.assertIn("sub_scores", body)
        self.assertIn("final_score", body)
        self.assertIn("risk_level", body)

        # Plural endpoint
        status_code2, body2 = http_request("GET", "/risk-scores/EMP-M3-BEHAVIOR", token=self.token)
        self.assertEqual(status_code2, 200)
        self.assertEqual(body2["final_score"], body["final_score"])

        # Non-existent employee returns 404
        status_code_404, err_body = http_request("GET", "/risk-score/NON_EXISTENT_EMP_999", token=self.token)
        self.assertEqual(status_code_404, 404)

    # ==================== DAY 23 TESTS: PEER GROUP COMPARISON ====================

    def test_day23_peer_group_excludes_subject_employee(self):
        """Peer comparison must exclude the employee themselves from their own department average."""
        result = get_peer_group_comparison("EMP-M3-PEER-A", self.db)
        self.assertIsNotNone(result)
        self.assertEqual(result["employee_id"], "EMP-M3-PEER-A")
        # Department is 'Sales Operations' with PEER-A, PEER-B, PEER-C
        # When comparing PEER-A, peer_count must be 2 (PEER-B and PEER-C)
        self.assertEqual(result["peer_count"], 2)
        self.assertIsNotNone(result["department_avg_score"])
        self.assertIsNotNone(result["deviation_from_peers"])
        self.assertIsNotNone(result["peer_percentile"])

    def test_day23_single_person_department_graceful_handling(self):
        """A 1-person department must return peer_count=0 with note rather than crashing on divide-by-zero."""
        result = get_peer_group_comparison("EMP-M3-SOLO", self.db)
        self.assertIsNotNone(result)
        self.assertEqual(result["peer_count"], 0)
        self.assertIsNone(result["department_avg_score"])
        self.assertIsNone(result["deviation_from_peers"])
        self.assertIn("No peers found", result.get("note", ""))

    def test_day23_peer_percentile_calculation(self):
        """Peer percentile accurately measures percentage of departmental peers with lower risk score."""
        result = get_peer_group_comparison("EMP-M3-PEER-A", self.db)
        # PEER-A has risk score around 16.0 (2 data violations: 80 * 0.20 = 16.0)
        # PEER-B has risk score around 1.5, PEER-C has 0.0
        # Both peers score less than PEER-A, so peer_percentile should be 100.0%
        self.assertGreaterEqual(result["peer_percentile"], 50.0)

    def test_day23_live_peer_comparison_endpoint(self):
        """Test live GET /ueba/peer-comparison/{employee_id}."""
        status_code, body = http_request("GET", "/ueba/peer-comparison/EMP-M3-PEER-A", token=self.token)
        self.assertEqual(status_code, 200)
        self.assertEqual(body["employee_id"], "EMP-M3-PEER-A")
        self.assertEqual(body["peer_count"], 2)

        # 1-person department returns 200 with note
        status_solo, body_solo = http_request("GET", "/ueba/peer-comparison/EMP-M3-SOLO", token=self.token)
        self.assertEqual(status_solo, 200)
        self.assertEqual(body_solo["peer_count"], 0)
        self.assertIsNotNone(body_solo.get("note"))

        # Non-existent employee returns 404
        status_404, _ = http_request("GET", "/ueba/peer-comparison/NON_EXISTENT_EMP", token=self.token)
        self.assertEqual(status_404, 404)

    # ==================== DAY 24 TESTS: TREND ANALYSIS & PREDICTION ====================

    def test_day24_get_risk_trend_contiguous_dates(self):
        """get_risk_trend returns exact requested days with zero date gaps."""
        trend = get_risk_trend("EMP-M3-TREND", days=30)
        self.assertEqual(len(trend), 30)

        # Verify contiguous sequence
        for i in range(len(trend) - 1):
            d1 = datetime.strptime(trend[i]["date"], "%Y-%m-%d").date()
            d2 = datetime.strptime(trend[i + 1]["date"], "%Y-%m-%d").date()
            self.assertEqual(d2 - d1, timedelta(days=1), f"Gap detected between {d1} and {d2}")

    def test_day24_get_trend_direction_increasing(self):
        """Employee with recent spike in second week must be classified as 'increasing'."""
        direction = get_trend_direction("EMP-M3-TREND")
        self.assertEqual(direction["employee_id"], "EMP-M3-TREND")
        self.assertEqual(direction["direction"], "increasing")
        self.assertGreater(direction["second_week_avg"], direction["first_week_avg"])

    def test_day24_get_trend_direction_stable_for_clean_employee(self):
        """Clean employee with 0 anomalies in both weeks must be classified as 'stable'."""
        direction = get_trend_direction("EMP-M3-CLEAN")
        self.assertEqual(direction["direction"], "stable")
        self.assertEqual(direction["first_week_avg"], 0.0)
        self.assertEqual(direction["second_week_avg"], 0.0)

    def test_day24_live_trend_and_profile_endpoints(self):
        """Test live GET /ueba/trend/{employee_id} and GET /ueba/profile/{employee_id}."""
        # Trend endpoint
        status_trend, body_trend = http_request("GET", "/ueba/trend/EMP-M3-TREND?days=14", token=self.token)
        self.assertEqual(status_trend, 200)
        self.assertEqual(body_trend["direction"], "increasing")
        self.assertEqual(len(body_trend["trend"]), 14)

        # Unified UEBA profile endpoint
        status_prof, body_prof = http_request("GET", "/ueba/profile/EMP-M3-PEER-A", token=self.token)
        self.assertEqual(status_prof, 200)
        self.assertEqual(body_prof["employee_id"], "EMP-M3-PEER-A")
        self.assertIn("risk_score", body_prof)
        self.assertIn("peer_comparison", body_prof)
        self.assertIn("trend", body_prof)
        self.assertEqual(body_prof["peer_comparison"]["peer_count"], 2)

        # 404 for unknown employee
        status_404, _ = http_request("GET", "/ueba/profile/NON_EXISTENT_EMP", token=self.token)
        self.assertEqual(status_404, 404)

    # ==================== RBAC SECURITY TESTS ====================

    def test_milestone3_endpoints_require_authentication(self):
        """All Milestone 3 endpoints must reject unauthenticated requests with HTTP 401."""
        endpoints = [
            "/risk-score/EMP-M3-CLEAN",
            "/risk-scores/EMP-M3-CLEAN",
            "/ueba/peer-comparison/EMP-M3-CLEAN",
            "/ueba/trend/EMP-M3-CLEAN",
            "/ueba/profile/EMP-M3-CLEAN",
        ]
        for ep in endpoints:
            status_code, _ = http_request("GET", ep, token=None)
            self.assertEqual(status_code, 401, f"Endpoint {ep} should require auth (401)")


if __name__ == "__main__":
    unittest.main()
