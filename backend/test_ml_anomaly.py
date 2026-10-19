"""
Unit Tests for Day 18: Isolation Forest Machine Learning Anomaly Detection
Tests model fitting, scoring, contamination configurations, insufficient data guards,
repeatability (random_state=42), model artifact persistence, invalid feature handling,
and persistent mongo_service abstraction.
"""

import os
import sys
import tempfile
import unittest
import numpy as np

# Ensure backend root on sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.ml_anomaly import (
    train_isolation_forest,
    score_samples,
    save_model,
    load_model,
    persist_ml_anomalies,
    run_ml_pipeline,
    InsufficientDataError,
    InvalidFeatureError,
    DEFAULT_CONTAMINATION,
    DEFAULT_RANDOM_STATE,
)
from app.ml_features import FEATURE_NAMES, prepare_feature_matrix


class TestMLAnomaly(unittest.TestCase):

    def setUp(self):
        """Generates 20 typical behavioral records plus 2 extreme outlier records."""
        self.synthetic_records = []
        for i in range(20):
            self.synthetic_records.append({
                "employee_id": f"EMP-{1000 + (i % 3)}",
                "date": f"2026-09-{i+1:02d}",
                "avg_login_hour": 9.0 + (i % 3) * 0.25,
                "download_count": 2 + (i % 2),
                "total_download_mb": 25.0 + (i % 4) * 5.0,
                "unique_devices": 1,
                "total_events": 5 + (i % 3),
            })

        # Outlier 1: Extreme off-hours midnight login with massive exfiltration
        self.synthetic_records.append({
            "employee_id": "EMP-ATTACKER-1",
            "date": "2026-09-25",
            "avg_login_hour": 1.5,
            "download_count": 45,
            "total_download_mb": 8500.0,
            "unique_devices": 6,
            "total_events": 120,
        })

        # Outlier 2: Extreme device surge and download spikes
        self.synthetic_records.append({
            "employee_id": "EMP-ATTACKER-2",
            "date": "2026-09-26",
            "avg_login_hour": 3.0,
            "download_count": 30,
            "total_download_mb": 6200.0,
            "unique_devices": 5,
            "total_events": 90,
        })

    def test_train_and_score_isolation_forest(self):
        """Verifies successful training and scoring with expected output structure."""
        X, valid_recs, _ = prepare_feature_matrix(self.synthetic_records)
        self.assertEqual(len(X), 22)

        model = train_isolation_forest(
            X,
            contamination=0.10,
            random_state=DEFAULT_RANDOM_STATE,
        )
        self.assertIsNotNone(model)

        scored = score_samples(model, X, valid_recs)
        self.assertEqual(len(scored), 22)

        for item in scored:
            self.assertIn("employee_id", item)
            self.assertIn("date", item)
            self.assertIn("anomaly_score", item)
            self.assertIn("anomaly_flag", item)
            self.assertIn("is_anomaly", item)
            self.assertIn("feature_values", item)
            self.assertIn(item["anomaly_flag"], (-1, 1))
            self.assertEqual(item["is_anomaly"], (item["anomaly_flag"] == -1))
            self.assertIsInstance(item["feature_values"], dict)

        # Confirm the extreme outlier was detected
        outliers = [s for s in scored if s["is_anomaly"]]
        outlier_ids = [s["employee_id"] for s in outliers]
        self.assertTrue("EMP-ATTACKER-1" in outlier_ids or "EMP-ATTACKER-2" in outlier_ids)

    def test_contamination_parameter_configurations(self):
        """
        Tests Isolation Forest behavior under different contamination rates:
        0.02, 0.05, and 0.10.
        Documents limitations: for small datasets (N=22), 0.02 yields 22 * 0.02 = 0.44 < 1
        outlier, whereas 0.10 flags ~2 outliers.
        """
        X, valid_recs, _ = prepare_feature_matrix(self.synthetic_records)

        # 1. Contamination = 0.02 (strict/conservative)
        model_02 = train_isolation_forest(X, contamination=0.02, random_state=42)
        scored_02 = score_samples(model_02, X, valid_recs)
        outliers_02 = [s for s in scored_02 if s["is_anomaly"]]

        # 2. Contamination = 0.05 (standard default)
        model_05 = train_isolation_forest(X, contamination=0.05, random_state=42)
        scored_05 = score_samples(model_05, X, valid_recs)
        outliers_05 = [s for s in scored_05 if s["is_anomaly"]]

        # 3. Contamination = 0.10 (sensitive)
        model_10 = train_isolation_forest(X, contamination=0.10, random_state=42)
        scored_10 = score_samples(model_10, X, valid_recs)
        outliers_10 = [s for s in scored_10 if s["is_anomaly"]]

        # Number of flagged outliers scales monotonically with contamination
        self.assertLessEqual(len(outliers_02), len(outliers_05))
        self.assertLessEqual(len(outliers_05), len(outliers_10))

        # Invalid contamination values must be rejected
        with self.assertRaises(ValueError):
            train_isolation_forest(X, contamination=0.0)

        with self.assertRaises(ValueError):
            train_isolation_forest(X, contamination=0.6)

    def test_insufficient_data_rejection(self):
        """Model training must reject empty datasets and sample counts below minimum threshold."""
        # 1. Empty dataset
        empty_X = np.empty((0, 5))
        with self.assertRaises(InsufficientDataError):
            train_isolation_forest(empty_X)

        # 2. Single row (N=1)
        single_X = np.array([[9.0, 2.0, 30.0, 1.0, 5.0]])
        with self.assertRaises(InsufficientDataError) as ctx:
            train_isolation_forest(single_X, min_samples=5)
        self.assertIn("requires at least 5", str(ctx.exception))

        # 3. Three rows (N=3, min_samples=5)
        small_X = np.array([
            [9.0, 2.0, 30.0, 1.0, 5.0],
            [9.5, 1.0, 15.0, 1.0, 4.0],
            [9.2, 3.0, 45.0, 1.0, 6.0],
        ])
        with self.assertRaises(InsufficientDataError):
            train_isolation_forest(small_X, min_samples=5)

    def test_repeatability_with_random_state_42(self):
        """
        Model training with random_state=42 must produce exactly reproducible
        scores and classifications across independent training runs.
        """
        X, valid_recs, _ = prepare_feature_matrix(self.synthetic_records)

        model_run_1 = train_isolation_forest(X, contamination=0.05, random_state=42)
        scored_run_1 = score_samples(model_run_1, X, valid_recs)

        model_run_2 = train_isolation_forest(X, contamination=0.05, random_state=42)
        scored_run_2 = score_samples(model_run_2, X, valid_recs)

        for s1, s2 in zip(scored_run_1, scored_run_2):
            self.assertEqual(s1["anomaly_flag"], s2["anomaly_flag"])
            self.assertAlmostEqual(s1["anomaly_score"], s2["anomaly_score"], places=4)

    def test_model_persistence_save_and_load(self):
        """Model can be saved to a .pkl file, reloaded, and reproduce identical predictions."""
        X, valid_recs, _ = prepare_feature_matrix(self.synthetic_records)
        model = train_isolation_forest(X, contamination=0.05, random_state=42)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_model_path = os.path.join(tmpdir, "test_anomaly_model.pkl")
            saved_path = save_model(model, filepath=tmp_model_path)
            self.assertTrue(os.path.exists(saved_path))

            loaded_model = load_model(saved_path)
            self.assertIsNotNone(loaded_model)

            # Verify predictions of loaded model match in-memory model
            preds_orig = model.predict(X)
            preds_loaded = loaded_model.predict(X)
            np.testing.assert_array_equal(preds_orig, preds_loaded)

    def test_invalid_features_handling(self):
        """Invalid feature matrices with NaNs, non-finite values, or wrong dimensions raise InvalidFeatureError."""
        # 1. Array with NaN
        nan_X = np.array([
            [9.0, 2.0, np.nan, 1.0, 5.0],
            [9.0, 2.0, 25.0, 1.0, 5.0],
            [9.0, 2.0, 25.0, 1.0, 5.0],
            [9.0, 2.0, 25.0, 1.0, 5.0],
            [9.0, 2.0, 25.0, 1.0, 5.0],
        ])
        with self.assertRaises(InvalidFeatureError):
            train_isolation_forest(nan_X)

        # 2. 1D array instead of 2D
        dim_1_X = np.array([9.0, 2.0, 25.0, 1.0, 5.0])
        with self.assertRaises(InvalidFeatureError):
            train_isolation_forest(dim_1_X)

    def test_mongo_service_storage_abstraction_persistence(self):
        """
        Persists detected ML anomalies through mongo_service abstraction,
        verifying persistent fallback when MongoDB is offline.
        """
        from app.mongodb import MongoDBService

        test_mongo = MongoDBService()
        self.assertIsInstance(test_mongo.is_connected, bool)

        X, valid_recs, _ = prepare_feature_matrix(self.synthetic_records)
        model = train_isolation_forest(X, contamination=0.10, random_state=42)
        scored = score_samples(model, X, valid_recs)

        # Clear prior test anomalies for isolation
        test_mongo.clear_anomalies("EMP-ATTACKER-1")

        persisted = persist_ml_anomalies(scored, mongo_service=test_mongo, only_anomalies=True)
        self.assertGreater(len(persisted), 0)

        for anom in persisted:
            self.assertEqual(anom["indicator"], "isolation_forest")
            self.assertEqual(anom["anomaly_type"], "ML_ISOLATION_FOREST")
            self.assertIn(anom["severity"], ("high", "critical"))
            self.assertIn("Score:", anom["observed_value"])

        # Retrieve from mongo_service and verify filter by indicator and anomaly_type
        retrieved = test_mongo.get_anomalies(indicator="isolation_forest", anomaly_type="ML_ISOLATION_FOREST")
        self.assertGreaterEqual(len(retrieved), len(persisted))

        # Clean up test anomalies
        test_mongo.clear_anomalies("EMP-ATTACKER-1")
        test_mongo.clear_anomalies("EMP-ATTACKER-2")


if __name__ == "__main__":
    unittest.main()
