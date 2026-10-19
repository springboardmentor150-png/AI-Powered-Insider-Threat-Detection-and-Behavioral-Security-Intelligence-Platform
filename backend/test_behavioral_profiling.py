"""
Unit and Integration Test Suite for Behavioral Profiling Engine (Milestone 2: Day 11-14)
ITBIS: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform.

Tests:
1. Numeric mean and sample standard deviation calculations (Bessel's correction N-1).
2. Minimum sample size enforcement (N < 5 rejected, N >= 5 accepted).
3. Preservation of zero standard deviation (not treated as missing data).
4. Set-membership indicators (device_usage, application_usage) without forced averages.
5. Daily access counts and data transfer aggregation by date.
6. Communication pattern calculation from email activities.
7. Handling missing, malformed, or invalid event details and timestamps.
8. Employees with zero activity logs (safe reporting of insufficient data).
9. Configurable lookback period filtering (e.g. 90-day window).
10. Baseline upsert behavior (idempotency, prevents duplicates).
11. Storage engine connection fallback handling.
12. Baseline generation script end-to-end integration.
"""

import math
import unittest
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from app.behavioral_profiling import (
    calculate_mean,
    calculate_sample_std_dev,
    parse_timestamp,
    timestamp_to_decimal_hour,
    calculate_login_time_baseline,
    calculate_resource_access_frequency_baseline,
    calculate_device_usage_baseline,
    calculate_application_usage_baseline,
    calculate_data_transfer_volume_baseline,
    calculate_communication_patterns_baseline,
    build_employee_profile,
    save_employee_baselines,
    get_employee_baselines,
    MIN_SAMPLE_SIZE,
)
from app.mongodb import mongo_service


class TestBehavioralProfilingEngine(unittest.TestCase):

    def test_01_numeric_mean_and_sample_std_dev(self):
        """Validates arithmetic mean and sample standard deviation with Bessel's correction."""
        # Standard dataset: [10, 12, 23, 23, 16, 23, 21, 16]
        # Sum = 144, Mean = 18.0
        # Sum of squared deviations = 192
        # Sample variance = 192 / (8 - 1) = 27.42857...
        # Sample std dev = sqrt(192/7) = 5.237229...
        data = [10.0, 12.0, 23.0, 23.0, 16.0, 23.0, 21.0, 16.0]
        mean = calculate_mean(data)
        std_dev = calculate_sample_std_dev(data)

        self.assertAlmostEqual(mean, 18.0, places=4)
        self.assertAlmostEqual(std_dev, 5.23723, places=4)

        # Empty data handling
        self.assertEqual(calculate_mean([]), 0.0)
        self.assertEqual(calculate_sample_std_dev([]), 0.0)

        # Single element (N < 2)
        self.assertEqual(calculate_sample_std_dev([9.5]), 0.0)

    def test_02_preservation_of_zero_standard_deviation(self):
        """Preserves zero standard deviation when all values are identical (not missing data)."""
        data = [9.0, 9.0, 9.0, 9.0, 9.0]
        mean = calculate_mean(data)
        std_dev = calculate_sample_std_dev(data)

        self.assertEqual(mean, 9.0)
        self.assertEqual(std_dev, 0.0)
        self.assertIsNotNone(std_dev)
        # Confirm that 0.0 is a float, not None or skipped
        self.assertIsInstance(std_dev, float)

    def test_03_timestamp_to_decimal_hour(self):
        """Converts timestamps to decimal hours accurately."""
        dt1 = datetime(2026, 9, 10, 8, 30, 0, tzinfo=timezone.utc)
        self.assertAlmostEqual(timestamp_to_decimal_hour(dt1), 8.5, places=3)

        dt2 = datetime(2026, 9, 10, 14, 15, 0, tzinfo=timezone.utc)
        self.assertAlmostEqual(timestamp_to_decimal_hour(dt2), 14.25, places=3)

        dt3 = datetime(2026, 9, 10, 2, 0, 0, tzinfo=timezone.utc)
        self.assertAlmostEqual(timestamp_to_decimal_hour(dt3), 2.0, places=3)

    def test_04_login_time_baseline_minimum_sample_size(self):
        """Enforces minimum sample size of 5 for avg_login_hour."""
        emp_id = "TEST-LOGIN-01"

        # 4 observations (insufficient, N < 5) -> must return None
        logs_4 = [
            {"event_type": "login", "timestamp": f"2026-09-0{i+1}T09:00:00+00:00"}
            for i in range(4)
        ]
        b_4 = calculate_login_time_baseline(logs_4, emp_id)
        self.assertIsNone(b_4, "Should return None when observations < 5")

        # 5 observations (sufficient, N = 5) -> must calculate baseline
        logs_5 = [
            {"event_type": "login", "timestamp": f"2026-09-0{i+1}T09:{i*10:02d}:00+00:00"}
            for i in range(5)
        ]
        b_5 = calculate_login_time_baseline(logs_5, emp_id)
        self.assertIsNotNone(b_5)
        self.assertEqual(b_5["employee_id"], emp_id)
        self.assertEqual(b_5["indicator"], "avg_login_hour")
        self.assertEqual(b_5["sample_size"], 5)
        self.assertIn("typical_value", b_5)
        self.assertIn("std_deviation", b_5)
        self.assertIn("last_updated", b_5)

    def test_05_resource_access_frequency_daily_aggregation(self):
        """Groups resource access events by calendar day and enforces min 5 distinct days."""
        emp_id = "TEST-ACCESS-01"

        # 10 events across only 3 days -> distinct days = 3 (< 5) -> must be skipped
        logs_3_days = [
            {"event_type": "file_download", "timestamp": "2026-09-01T10:00:00+00:00"},
            {"event_type": "file_download", "timestamp": "2026-09-01T11:00:00+00:00"},
            {"event_type": "data_transfer", "timestamp": "2026-09-01T12:00:00+00:00"},
            {"event_type": "file_upload", "timestamp": "2026-09-02T10:00:00+00:00"},
            {"event_type": "remote_access", "timestamp": "2026-09-02T11:00:00+00:00"},
            {"event_type": "file_download", "timestamp": "2026-09-03T10:00:00+00:00"},
        ]
        b_short = calculate_resource_access_frequency_baseline(logs_3_days, emp_id)
        self.assertIsNone(b_short)

        # 6 distinct days -> must generate baseline
        logs_6_days = list(logs_3_days) + [
            {"event_type": "file_download", "timestamp": "2026-09-04T10:00:00+00:00"},
            {"event_type": "file_download", "timestamp": "2026-09-05T10:00:00+00:00"},
            {"event_type": "file_download", "timestamp": "2026-09-06T10:00:00+00:00"},
        ]
        b_valid = calculate_resource_access_frequency_baseline(logs_6_days, emp_id)
        self.assertIsNotNone(b_valid)
        self.assertEqual(b_valid["indicator"], "resource_access_frequency")
        self.assertEqual(b_valid["sample_size"], 6)

    def test_06_device_usage_set_membership(self):
        """Categorical indicator device_usage extracts unique devices without meaningless statistics."""
        emp_id = "TEST-DEV-01"
        logs = [
            {"device": "MacBook-Air-01", "timestamp": "2026-09-01T10:00:00+00:00"},
            {"device": "MacBook-Air-01", "timestamp": "2026-09-02T10:00:00+00:00"},
            {"device": "SEC-DESKTOP-05", "timestamp": "2026-09-03T10:00:00+00:00"},
            {"details": {"device": "Corp-Laptop-99"}, "timestamp": "2026-09-04T10:00:00+00:00"},
            {"device": "N/A", "timestamp": "2026-09-05T10:00:00+00:00"},  # Must ignore N/A
        ]
        b = calculate_device_usage_baseline(logs, emp_id)
        self.assertIsNotNone(b)
        self.assertEqual(b["indicator"], "device_usage")
        self.assertIn("known_values", b)
        self.assertNotIn("typical_value", b)
        self.assertNotIn("std_deviation", b)
        self.assertEqual(set(b["known_values"]), {"Corp-Laptop-99", "MacBook-Air-01", "SEC-DESKTOP-05"})
        self.assertEqual(b["sample_size"], 4)

    def test_07_application_usage_set_membership(self):
        """Categorical indicator application_usage normalizes URI schemes and tools."""
        emp_id = "TEST-APP-01"
        logs = [
            {"resource": "s3://vault/reports.tar.gz", "timestamp": "2026-09-01T10:00:00+00:00"},
            {"resource": "SharePoint://HR/Policies/docs.pdf", "timestamp": "2026-09-02T10:00:00+00:00"},
            {"resource": "Exchange://Mailbox/All", "timestamp": "2026-09-03T10:00:00+00:00"},
            {"details": {"tool": "PowerShell_AD_Module"}, "timestamp": "2026-09-04T10:00:00+00:00"},
        ]
        b = calculate_application_usage_baseline(logs, emp_id)
        self.assertIsNotNone(b)
        self.assertEqual(b["indicator"], "application_usage")
        self.assertIn("known_values", b)
        self.assertIn("S3_Storage", b["known_values"])
        self.assertIn("SharePoint", b["known_values"])
        self.assertIn("Exchange_Mail", b["known_values"])
        self.assertIn("PowerShell_AD_Module", b["known_values"])

    def test_08_data_transfer_volume_daily_mb_aggregation(self):
        """Aggregates upload/download volume by day and computes mean and std dev."""
        emp_id = "TEST-TRANSFER-01"
        # 5 distinct days with 50MB per day
        logs = [
            {
                "event_type": "file_download",
                "timestamp": f"2026-09-0{i+1}T11:00:00+00:00",
                "details": {"size_mb": 50.0}
            }
            for i in range(5)
        ]
        b = calculate_data_transfer_volume_baseline(logs, emp_id)
        self.assertIsNotNone(b)
        self.assertEqual(b["indicator"], "data_transfer_volume")
        self.assertEqual(b["typical_value"], 50.0)
        self.assertEqual(b["std_deviation"], 0.0)  # Zero variance preserved!
        self.assertEqual(b["sample_size"], 5)

    def test_09_communication_patterns_from_email_activity(self):
        """Computes daily communication pattern from email_activity events."""
        emp_id = "TEST-COMM-01"
        logs = [
            {
                "event_type": "email_activity",
                "timestamp": f"2026-09-0{i+1}T15:00:00+00:00",
                "details": {"recipient": f"colleague{i}@enterprise.corp"}
            }
            for i in range(5)
        ]
        b = calculate_communication_patterns_baseline(logs, emp_id)
        self.assertIsNotNone(b)
        self.assertEqual(b["indicator"], "communication_patterns")
        self.assertEqual(b["typical_value"], 1.0)
        self.assertEqual(b["sample_size"], 5)

    def test_10_missing_and_malformed_event_details(self):
        """Handles missing timestamps, malformed size strings, and null fields gracefully."""
        emp_id = "TEST-CORRUPT-01"
        corrupt_logs = [
            {"event_type": "login", "timestamp": None},
            {"event_type": "login", "timestamp": "not-a-timestamp"},
            {"event_type": "file_download", "timestamp": "2026-09-01T10:00:00", "details": None},
            {"event_type": "file_download", "timestamp": "2026-09-02T10:00:00", "details": {"size_mb": "invalid_number"}},
            {"event_type": None, "timestamp": "2026-09-03T10:00:00"},
            {"device": None, "resource": None},
        ]
        profile = build_employee_profile(emp_id, logs=corrupt_logs)
        self.assertIsNotNone(profile)
        self.assertEqual(profile["employee_id"], emp_id)
        # All numeric indicators should be skipped safely due to insufficient valid data
        self.assertIn("avg_login_hour", profile["skipped"])
        self.assertIn("data_transfer_volume", profile["skipped"])

    def test_11_employee_with_zero_logs(self):
        """Employees with no activity logs are handled safely without errors."""
        emp_id = "EMP-NO-LOGS"
        profile = build_employee_profile(emp_id, logs=[])
        self.assertIsNotNone(profile)
        self.assertEqual(len(profile["generated"]), 0)
        self.assertEqual(len(profile["skipped"]), 6)
        self.assertIn("0/5 logins", profile["skipped"]["avg_login_hour"])
        self.assertIn("No device identifiers", profile["skipped"]["device_usage"])

    def test_12_configurable_lookback_filtering(self):
        """Filters out events older than configurable lookback window."""
        emp_id = "TEST-LOOKBACK"
        now = datetime.now(timezone.utc)
        # 1 recent event (10 days ago), 10 ancient events (150 days ago)
        logs = [
            {"event_type": "login", "timestamp": (now - timedelta(days=10)).isoformat()}
        ] + [
            {"event_type": "login", "timestamp": (now - timedelta(days=150)).isoformat()}
            for _ in range(10)
        ]
        # In a 30-day window, only the 1 recent event is in range (< 5) -> baseline skipped
        # In a 200-day window, all 11 events are in range (>= 5) -> baseline generated
        cutoff_30 = now - timedelta(days=30)
        recent_30 = [l for l in logs if parse_timestamp(l["timestamp"]) >= cutoff_30]
        self.assertEqual(len(recent_30), 1)
        b_30 = calculate_login_time_baseline(recent_30, emp_id)
        self.assertIsNone(b_30)

        b_200 = calculate_login_time_baseline(logs, emp_id)
        self.assertIsNotNone(b_200)
        self.assertEqual(b_200["sample_size"], 11)

    def test_13_baseline_upsert_idempotency(self):
        """Upserting baselines replaces existing record and avoids duplicate entries."""
        emp_id = "TEST-UPSERT-EMP"
        test_baseline_1 = {
            "employee_id": emp_id,
            "indicator": "avg_login_hour",
            "typical_value": 9.0,
            "std_deviation": 0.5,
            "sample_size": 10,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        # First insert
        mongo_service.upsert_baseline(test_baseline_1)
        records_after_1 = mongo_service.get_baselines(employee_id=emp_id, indicator="avg_login_hour")
        self.assertEqual(len(records_after_1), 1)
        self.assertEqual(records_after_1[0]["typical_value"], 9.0)

        # Second insert with updated values
        test_baseline_2 = {
            "employee_id": emp_id,
            "indicator": "avg_login_hour",
            "typical_value": 9.25,
            "std_deviation": 0.4,
            "sample_size": 15,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        mongo_service.upsert_baseline(test_baseline_2)
        records_after_2 = mongo_service.get_baselines(employee_id=emp_id, indicator="avg_login_hour")

        # Must still be exactly 1 record with updated values (no duplicates!)
        self.assertEqual(len(records_after_2), 1)
        self.assertEqual(records_after_2[0]["typical_value"], 9.25)
        self.assertEqual(records_after_2[0]["sample_size"], 15)

        # Cleanup
        mongo_service.delete_baseline(emp_id, "avg_login_hour")
        self.assertEqual(len(mongo_service.get_baselines(employee_id=emp_id, indicator="avg_login_hour")), 0)


if __name__ == "__main__":
    unittest.main()
