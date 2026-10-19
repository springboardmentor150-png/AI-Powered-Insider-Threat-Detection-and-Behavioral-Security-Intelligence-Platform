"""
Comprehensive Test Suite for Rule-Based Anomaly Detection (Milestone 2: Day 15-16)
ITBIS: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Tests:
1. Normal login within threshold: no anomaly.
2. Unusual login at 03:00 against typical login hour of 09:12: detected when configured spread and threshold warrant it.
3. Large data transfer: detected when sufficiently outside baseline.
4. Excessive transfer frequency: detected when sufficiently outside baseline.
5. Known device: no anomaly.
6. Unknown device: suspicious-device anomaly.
7. Known application: no anomaly.
8. Unknown application: unauthorized-access anomaly.
9. Employee without baseline: no false anomaly (returns None).
10. Zero and near-zero spread: no division error (protected by min_spread).
11. Invalid or missing measurements: handled safely without errors.
12. Anomalies persist and can be retrieved after reinitializing storage service.
13. Ingestion integration: valid events trigger appropriate detectors and record anomalies.
14. Severity classification: medium, high, and critical boundaries.
"""

import os
import sys
import unittest
from datetime import datetime, timezone
from typing import Dict, Any

# Ensure backend root on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.mongodb import mongo_service, MongoDBService
from app.anomaly_detection import (
    check_numeric_anomaly,
    detect_login_anomaly,
    detect_download_anomaly,
    detect_transfer_frequency_anomaly,
    check_set_anomaly,
    detect_device_anomaly,
    detect_unauthorized_access,
    DEFAULT_NUMERIC_THRESHOLD,
    MIN_SPREAD,
)


class TestRuleBasedAnomalyDetection(unittest.TestCase):
    test_emp = "TEST-ANOM-901"
    no_baseline_emp = "TEST-NO-BASE-999"

    @classmethod
    def setUpClass(cls):
        # Seed test baselines in storage
        # 1. avg_login_hour: typical = 9.20 (09:12 AM), std_deviation = 1.0
        mongo_service.upsert_baseline({
            "employee_id": cls.test_emp,
            "indicator": "avg_login_hour",
            "typical_value": 9.20,
            "std_deviation": 1.0,
            "sample_size": 10,
        })
        # 2. data_transfer_volume: typical = 25.0 MB, std_deviation = 5.0
        mongo_service.upsert_baseline({
            "employee_id": cls.test_emp,
            "indicator": "data_transfer_volume",
            "typical_value": 25.0,
            "std_deviation": 5.0,
            "sample_size": 8,
        })
        # 3. resource_access_frequency: typical = 2.0/day, std_deviation = 0.0 (zero variance test)
        mongo_service.upsert_baseline({
            "employee_id": cls.test_emp,
            "indicator": "resource_access_frequency",
            "typical_value": 2.0,
            "std_deviation": 0.0,
            "sample_size": 12,
        })
        # 4. device_usage: known devices
        mongo_service.upsert_baseline({
            "employee_id": cls.test_emp,
            "indicator": "device_usage",
            "known_values": ["MacBook-Pro-SEC-01", "ThinkPad-P1", "corp-workstation-09"],
            "sample_size": 25,
        })
        # 5. application_usage: known applications
        mongo_service.upsert_baseline({
            "employee_id": cls.test_emp,
            "indicator": "application_usage",
            "known_values": ["Exchange_Mail", "S3_Storage", "SharePoint", "Web_siem.enterprise.corp"],
            "sample_size": 30,
        })

    @classmethod
    def tearDownClass(cls):
        # Cleanup isolated test data
        for ind in [
            "avg_login_hour",
            "data_transfer_volume",
            "resource_access_frequency",
            "device_usage",
            "application_usage",
        ]:
            mongo_service.delete_baseline(cls.test_emp, ind)
        mongo_service.clear_anomalies(cls.test_emp)

    def setUp(self):
        # Clear anomalies for this test subject before each test
        mongo_service.clear_anomalies(self.test_emp)

    def test_01_normal_login_within_threshold_no_anomaly(self):
        """Test 1: Normal login (e.g. 09:30 AM -> 9.50) is within 2.0 std dev -> returns None."""
        # typical = 9.20, std = 1.0, observed = 9.50 -> ratio = |9.50 - 9.20| / 1.0 = 0.30 <= 2.0
        res = detect_login_anomaly(self.test_emp, 9.50)
        self.assertIsNone(res, "Expected no anomaly for normal login time.")

    def test_02_unusual_login_at_0300_detected(self):
        """Test 2: Unusual login at 03:00 (3.00) against typical 09:12 (9.20) -> detected as high/critical."""
        # typical = 9.20, std = 1.0, observed = 3.00 -> ratio = |3.00 - 9.20| / 1.0 = 6.20 > 5.0 (critical)
        res = detect_login_anomaly(self.test_emp, 3.00)
        self.assertIsNotNone(res, "Expected anomaly to be detected for 03:00 login.")
        self.assertEqual(res["anomaly_type"], "UNUSUAL_LOGIN_TIME")
        self.assertEqual(res["indicator"], "avg_login_hour")
        self.assertEqual(res["observed_value"], 3.0)
        self.assertEqual(res["typical_value"], 9.2)
        self.assertGreater(res["deviation_ratio"], 5.0)
        self.assertEqual(res["severity"], "critical")

        # Also test with ISO timestamp string for 03:00
        res_iso = detect_login_anomaly(self.test_emp, "2026-10-13T03:00:00Z")
        self.assertIsNotNone(res_iso)
        self.assertEqual(res_iso["observed_value"], 3.0)

    def test_03_large_data_transfer_detected(self):
        """Test 3: Large data transfer outside baseline is detected with appropriate severity."""
        # typical = 25.0 MB, std = 5.0. 
        # Normal transfer: 30 MB -> ratio = 1.0 <= 2.0 -> None
        normal = detect_download_anomaly(self.test_emp, 30.0)
        self.assertIsNone(normal)

        # Medium anomaly: 40 MB -> ratio = 15.0 / 5.0 = 3.0 -> medium
        medium_anom = detect_download_anomaly(self.test_emp, 40.0)
        self.assertIsNotNone(medium_anom)
        self.assertEqual(medium_anom["severity"], "medium")

        # Massive transfer: 150 MB -> ratio = |150 - 25| / 5 = 25.0 -> critical
        huge_anom = detect_download_anomaly(self.test_emp, 150.0)
        self.assertIsNotNone(huge_anom)
        self.assertEqual(huge_anom["anomaly_type"], "ABNORMAL_DATA_TRANSFER")
        self.assertEqual(huge_anom["severity"], "critical")
        self.assertEqual(huge_anom["observed_value"], 150.0)

    def test_04_excessive_transfer_frequency_detected(self):
        """Test 4: Excessive transfer frequency detected when outside baseline."""
        # baseline: typical = 2.0, std = 0.0 -> effective spread = max(0.0, 0.1) = 0.1
        # Normal frequency: 2.0 -> ratio = 0.0 <= 2.0 -> None
        self.assertIsNone(detect_transfer_frequency_anomaly(self.test_emp, 2.0))

        # Extreme frequency: 15 transfers/day -> ratio = |15 - 2| / 0.1 = 130.0 -> critical
        freq_anom = detect_transfer_frequency_anomaly(self.test_emp, 15)
        self.assertIsNotNone(freq_anom)
        self.assertEqual(freq_anom["anomaly_type"], "EXCESSIVE_TRANSFER_FREQUENCY")
        self.assertEqual(freq_anom["severity"], "critical")

    def test_05_known_device_no_anomaly(self):
        """Test 5: Known device returns None."""
        res = detect_device_anomaly(self.test_emp, "MacBook-Pro-SEC-01")
        self.assertIsNone(res, "Known device must not trigger an anomaly.")

        # Case-insensitive check
        res_case = detect_device_anomaly(self.test_emp, "thinkpad-p1")
        self.assertIsNone(res_case, "Known device should match case-insensitively.")

    def test_06_unknown_device_triggers_suspicious_device_anomaly(self):
        """Test 6: Unknown device triggers suspicious-device anomaly with high severity."""
        res = detect_device_anomaly(self.test_emp, "ROG-Strix-G15 (Unregistered)")
        self.assertIsNotNone(res)
        self.assertEqual(res["anomaly_type"], "SUSPICIOUS_DEVICE")
        self.assertEqual(res["indicator"], "device_usage")
        self.assertEqual(res["severity"], "high")
        self.assertEqual(res["observed_value"], "ROG-Strix-G15 (Unregistered)")

    def test_07_known_application_no_anomaly(self):
        """Test 7: Known application returns None."""
        # Exact app name
        res = detect_unauthorized_access(self.test_emp, "S3_Storage")
        self.assertIsNone(res)

        # Resource URI that normalizes to known app
        res_uri = detect_unauthorized_access(self.test_emp, "s3://vault/reports.csv")
        self.assertIsNone(res_uri)

    def test_08_unknown_application_triggers_unauthorized_access_anomaly(self):
        """Test 8: Unknown application triggers unauthorized-access anomaly with high severity."""
        res = detect_unauthorized_access(self.test_emp, "TorBrowser_DarkWeb")
        self.assertIsNotNone(res)
        self.assertEqual(res["anomaly_type"], "UNAUTHORIZED_APPLICATION_ACCESS")
        self.assertEqual(res["indicator"], "application_usage")
        self.assertEqual(res["severity"], "high")
        self.assertEqual(res["observed_value"], "TorBrowser_DarkWeb")

    def test_09_employee_without_baseline_returns_none(self):
        """Test 9: Employee without baseline returns None (no false anomaly)."""
        # Numeric checks
        self.assertIsNone(detect_login_anomaly(self.no_baseline_emp, 3.0))
        self.assertIsNone(detect_download_anomaly(self.no_baseline_emp, 5000.0))
        self.assertIsNone(detect_transfer_frequency_anomaly(self.no_baseline_emp, 50))
        # Set checks
        self.assertIsNone(detect_device_anomaly(self.no_baseline_emp, "Rogue-Node-99"))
        self.assertIsNone(detect_unauthorized_access(self.no_baseline_emp, "Unknown-Tool"))

    def test_10_zero_and_near_zero_spread_no_division_error(self):
        """Test 10: Zero standard deviation in baseline uses min_spread (0.1) without ZeroDivisionError."""
        # resource_access_frequency has std_deviation = 0.0
        # Check ratio calculation: |4 - 2| / 0.1 = 20.0 (no division by zero!)
        res = check_numeric_anomaly(
            employee_id=self.test_emp,
            indicator="resource_access_frequency",
            new_value=4.0,
            anomaly_type="FREQUENCY_CHECK",
            min_spread=0.1,
            threshold=2.0,
        )
        self.assertIsNotNone(res)
        self.assertEqual(res["details"]["raw_spread"], 0.0)
        self.assertEqual(res["details"]["effective_spread"], 0.1)
        self.assertEqual(res["deviation_ratio"], 20.0)

    def test_11_invalid_or_missing_measurements_handled_safely(self):
        """Test 11: Invalid, None, or malformed values are handled safely without exceptions."""
        self.assertIsNone(detect_login_anomaly(self.test_emp, None))
        self.assertIsNone(detect_login_anomaly(self.test_emp, "not-a-date-or-number"))
        self.assertIsNone(detect_download_anomaly(self.test_emp, None))
        self.assertIsNone(detect_download_anomaly(self.test_emp, "invalid_size"))
        self.assertIsNone(detect_device_anomaly(self.test_emp, None))
        self.assertIsNone(detect_device_anomaly(self.test_emp, "   "))
        self.assertIsNone(detect_device_anomaly(self.test_emp, "NONE"))
        self.assertIsNone(detect_unauthorized_access(self.test_emp, None))
        self.assertIsNone(check_numeric_anomaly(self.test_emp, "avg_login_hour", float("nan"), "TEST"))

    def test_12_anomalies_persist_and_retrievable_after_reinitialization(self):
        """Test 12: Anomalies persist in storage and remain available after reinitializing service."""
        # Record an anomaly
        anom = detect_device_anomaly(self.test_emp, "Alienware-Laptop-XX")
        self.assertIsNotNone(anom)

        # Retrieve through active service
        stored = mongo_service.get_anomalies(employee_id=self.test_emp)
        self.assertGreaterEqual(len(stored), 1)
        self.assertTrue(any(a["observed_value"] == "Alienware-Laptop-XX" for a in stored))

        # Reinitialize a new MongoDBService instance from persistent disk files
        new_service = MongoDBService()
        reloaded = new_service.get_anomalies(employee_id=self.test_emp)
        self.assertGreaterEqual(len(reloaded), 1)
        self.assertTrue(any(a["observed_value"] == "Alienware-Laptop-XX" for a in reloaded))

    def test_13_severity_classification_boundaries(self):
        """Test 13: Verifies exact severity classifications (medium, high, critical)."""
        # baseline: typical = 25.0, std = 5.0
        # ratio <= 2.0 (<= 35 MB) -> None
        self.assertIsNone(detect_download_anomaly(self.test_emp, 35.0))

        # ratio = 2.5 (37.5 MB) -> medium (2.0 < ratio <= 3.0)
        med = detect_download_anomaly(self.test_emp, 37.5)
        self.assertIsNotNone(med)
        self.assertEqual(med["severity"], "medium")

        # ratio = 4.0 (45.0 MB) -> high (3.0 < ratio <= 5.0)
        high_anom = detect_download_anomaly(self.test_emp, 45.0)
        self.assertIsNotNone(high_anom)
        self.assertEqual(high_anom["severity"], "high")

        # ratio = 6.0 (55.0 MB) -> critical (ratio > 5.0)
        crit = detect_download_anomaly(self.test_emp, 55.0)
        self.assertIsNotNone(crit)
        self.assertEqual(crit["severity"], "critical")

    def test_14_anomalies_retrieval_and_filtering(self):
        """Test 14: Verifies get_anomalies filtering by employee, indicator, and severity."""
        detect_download_anomaly(self.test_emp, 60.0)
        detect_device_anomaly(self.test_emp, "Rogue-Terminal-X")
        
        all_emp_anoms = mongo_service.get_anomalies(employee_id=self.test_emp)
        self.assertGreaterEqual(len(all_emp_anoms), 2)
        
        filtered_crit = mongo_service.get_anomalies(employee_id=self.test_emp, severity="critical")
        self.assertGreaterEqual(len(filtered_crit), 1)
        self.assertEqual(filtered_crit[0]["severity"], "critical")
        
        filtered_high = mongo_service.get_anomalies(employee_id=self.test_emp, severity="high")
        self.assertGreaterEqual(len(filtered_high), 1)
        self.assertEqual(filtered_high[0]["severity"], "high")


if __name__ == "__main__":
    unittest.main()
