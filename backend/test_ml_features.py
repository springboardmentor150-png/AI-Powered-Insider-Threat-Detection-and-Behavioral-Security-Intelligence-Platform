"""
Unit Tests for Day 17: Machine Learning Feature Engineering
Tests feature extraction, UTC day boundaries, missing fields, duplicate events,
empty input, and missing measurement policy.
"""

import os
import sys
import unittest
from datetime import datetime, timezone

# Ensure backend root on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.ml_features import (
    FEATURE_NAMES,
    extract_daily_features,
    prepare_feature_matrix,
    parse_utc_timestamp,
)


class TestMLFeatures(unittest.TestCase):

    def test_empty_activity_logs(self):
        """Empty activity log list returns empty list without raising exceptions."""
        self.assertEqual(extract_daily_features([]), [])
        self.assertEqual(extract_daily_features(None), [])

    def test_malformed_and_missing_timestamps(self):
        """Malformed, unparseable, or missing timestamps are skipped safely without crashing."""
        logs = [
            {"employee_id": "CYB-101", "event_type": "login", "timestamp": "invalid-timestamp"},
            {"employee_id": "CYB-101", "event_type": "login", "timestamp": None},
            {"employee_id": "CYB-101", "event_type": "login", "timestamp": ""},
            {"employee_id": "CYB-101", "event_type": "login", "timestamp": "not-a-date"},
            {
                "employee_id": "CYB-101",
                "event_type": "login",
                "timestamp": "2026-09-08T09:00:00Z",
                "device": "MacBook-Air",
            },
        ]
        features = extract_daily_features(logs)
        self.assertEqual(len(features), 1)
        rec = features[0]
        self.assertEqual(rec["employee_id"], "CYB-101")
        self.assertEqual(rec["date"], "2026-09-08")
        self.assertEqual(rec["total_events"], 1)
        self.assertEqual(rec["avg_login_hour"], 9.0)

    def test_utc_day_boundary_conversion(self):
        """
        Events with non-UTC timezone offsets are mapped to their correct UTC date.
        Example: 2026-09-08T02:00:00+05:30 corresponds to 2026-09-07T20:30:00 UTC.
        """
        logs = [
            # 02:00 AM IST on Sept 8 is 20:30 UTC on Sept 7
            {
                "employee_id": "EMP-UTC-01",
                "event_type": "login",
                "timestamp": "2026-09-08T02:00:00+05:30",
                "device": "Laptop-A",
            },
            # 11:00 AM IST on Sept 8 is 05:30 UTC on Sept 8
            {
                "employee_id": "EMP-UTC-01",
                "event_type": "login",
                "timestamp": "2026-09-08T11:00:00+05:30",
                "device": "Laptop-A",
            },
        ]
        features = extract_daily_features(logs)
        self.assertEqual(len(features), 2)

        # First record belongs to Sept 7 UTC
        self.assertEqual(features[0]["date"], "2026-09-07")
        self.assertEqual(features[0]["avg_login_hour"], 20.5)

        # Second record belongs to Sept 8 UTC
        self.assertEqual(features[1]["date"], "2026-09-08")
        self.assertEqual(features[1]["avg_login_hour"], 5.5)

    def test_feature_aggregation_calculations(self):
        """
        Verifies calculation of all 5 daily features:
        - avg_login_hour
        - download_count
        - total_download_mb
        - unique_devices
        - total_events
        """
        logs = [
            {
                "employee_id": "DEV-100",
                "event_type": "login",
                "timestamp": "2026-09-10T08:00:00Z",
                "device": "Dev-Workstation-1",
            },
            {
                "employee_id": "DEV-100",
                "event_type": "login",
                "timestamp": "2026-09-10T10:00:00Z",
                "device": "Dev-Workstation-1",
            },
            {
                "employee_id": "DEV-100",
                "event_type": "file_download",
                "action": "Downloaded source code repo",
                "timestamp": "2026-09-10T11:30:00Z",
                "device": "Dev-Workstation-2",
                "details": {"size_mb": 45.5},
            },
            {
                "employee_id": "DEV-100",
                "event_type": "file_download",
                "action": "Downloaded docker image",
                "timestamp": "2026-09-10T14:00:00Z",
                "device": "Dev-Workstation-1",
                "details": {"size_mb": 154.5},
            },
            {
                "employee_id": "DEV-100",
                "event_type": "usb_connect",
                "timestamp": "2026-09-10T15:00:00Z",
                "device": "Dev-Workstation-3",
            },
        ]

        features = extract_daily_features(logs)
        self.assertEqual(len(features), 1)
        rec = features[0]

        self.assertEqual(rec["employee_id"], "DEV-100")
        self.assertEqual(rec["date"], "2026-09-10")
        # avg login: (8.0 + 10.0) / 2 = 9.0
        self.assertEqual(rec["avg_login_hour"], 9.0)
        # download count: 2
        self.assertEqual(rec["download_count"], 2)
        # total download MB: 45.5 + 154.5 = 200.0
        self.assertEqual(rec["total_download_mb"], 200.0)
        # unique devices: Dev-Workstation-1, Dev-Workstation-2, Dev-Workstation-3 = 3
        self.assertEqual(rec["unique_devices"], 3)
        # total events: 5
        self.assertEqual(rec["total_events"], 5)

    def test_missing_login_policy_not_zero(self):
        """
        Crucial policy test: When an employee records activity on a day with NO login events,
        avg_login_hour must be None (missing measurement), NOT 0.0 (midnight).
        """
        logs = [
            {
                "employee_id": "FIN-200",
                "event_type": "file_download",
                "timestamp": "2026-09-12T14:00:00Z",
                "device": "Finance-PC",
                "details": {"size_mb": 10.0},
            },
            {
                "employee_id": "FIN-200",
                "event_type": "usb_connect",
                "timestamp": "2026-09-12T15:00:00Z",
                "device": "Finance-PC",
            },
        ]
        features = extract_daily_features(logs)
        self.assertEqual(len(features), 1)
        rec = features[0]

        # Must be None, not 0.0!
        self.assertIsNone(rec["avg_login_hour"])
        self.assertEqual(rec["download_count"], 1)
        self.assertEqual(rec["total_download_mb"], 10.0)
        self.assertEqual(rec["unique_devices"], 1)
        self.assertEqual(rec["total_events"], 2)

    def test_prepare_feature_matrix_imputation(self):
        """
        Tests conversion to dense numpy matrix for ML models.
        Confirms missing avg_login_hour (None) is imputed with default 12.0 (midday),
        NOT 0.0 (midnight).
        """
        records = [
            {
                "employee_id": "A",
                "date": "2026-09-01",
                "avg_login_hour": 9.0,
                "download_count": 2,
                "total_download_mb": 50.0,
                "unique_devices": 1,
                "total_events": 4,
            },
            {
                "employee_id": "B",
                "date": "2026-09-01",
                "avg_login_hour": None,  # No login recorded
                "download_count": 0,
                "total_download_mb": 0.0,
                "unique_devices": 1,
                "total_events": 2,
            },
        ]

        X, valid_recs, names = prepare_feature_matrix(records, default_login_hour=12.0)
        self.assertEqual(X.shape, (2, 5))
        self.assertEqual(len(valid_recs), 2)
        self.assertEqual(names, FEATURE_NAMES)

        # Row 0: login hour was 9.0
        self.assertEqual(X[0, 0], 9.0)
        # Row 1: login hour was None -> imputed with 12.0
        self.assertEqual(X[1, 0], 12.0)

    def test_deduplication_of_duplicate_events(self):
        """Duplicate activity logs are safely deduplicated without skewing counts."""
        duplicate_log = {
            "id": "event-12345",
            "employee_id": "CYB-999",
            "event_type": "file_download",
            "timestamp": "2026-09-15T12:00:00Z",
            "device": "Laptop-1",
            "details": {"size_mb": 50.0},
        }

        logs = [duplicate_log, duplicate_log, duplicate_log]
        features = extract_daily_features(logs, deduplicate=True)

        self.assertEqual(len(features), 1)
        self.assertEqual(features[0]["total_events"], 1)
        self.assertEqual(features[0]["download_count"], 1)
        self.assertEqual(features[0]["total_download_mb"], 50.0)

    def test_missing_details_and_device_fields(self):
        """Logs with missing details dict or missing device fields are parsed safely."""
        logs = [
            {
                "employee_id": "HR-555",
                "event_type": "login",
                "timestamp": "2026-09-16T09:30:00Z",
            },
            {
                "employee_id": "HR-555",
                "event_type": "file_download",
                "timestamp": "2026-09-16T11:00:00Z",
                "device": None,
                "details": None,
            },
        ]

        features = extract_daily_features(logs)
        self.assertEqual(len(features), 1)
        rec = features[0]
        self.assertEqual(rec["avg_login_hour"], 9.5)
        self.assertEqual(rec["download_count"], 1)
        self.assertEqual(rec["total_download_mb"], 0.0)
        self.assertEqual(rec["unique_devices"], 0)
        self.assertEqual(rec["total_events"], 2)


if __name__ == "__main__":
    unittest.main()
