"""
ITBIS Behavioral Intelligence Platform - Isolation Forest ML Anomaly Detection
Milestone 2: Days 17-18

Implements unsupervised behavioral outlier detection using scikit-learn's IsolationForest.

Features & Capabilities:
- Reproducible random_state=42.
- Configurable contamination parameter (default: 0.05).
- Documented behavior and limitations for small datasets.
- Strict data adequacy guard: requires minimum valid samples (default: 5) to fit.
- Returns employee ID, date, anomaly score, anomaly flag (-1 / 1), and feature values.
- Persists trained model to backend/models/anomaly_model.pkl using joblib.
- Persists detected anomalies into mongo_service (with persistent JSON fallback when MongoDB is offline).

Contamination Documentation & Limitations:
- The `contamination` parameter defines the expected proportion of outliers in the
  dataset (values in (0.0, 0.5]).
- Default: 0.05 (top 5% most isolated points are labeled as anomalies).
- Common alternatives: 0.02 (strict/conservative for low false-positive tolerances)
  and 0.10 (sensitive for small datasets or higher-risk environments).
- Small Dataset Limitation:
  Isolation Forest determines its outlier decision threshold using the empirical
  quantile corresponding to `contamination`. When the sample size N is small (e.g. N < 20),
  a contamination of 0.05 results in N * 0.05 < 1 sample. In this scenario, the model
  may classify 0 or 1 sample as anomalous, and threshold estimates can exhibit higher
  variance. For small cohorts (N < 10), a contamination of 0.10 or direct analysis of
  the continuous decision_function score is recommended.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from app.ml_features import (
    FEATURE_NAMES,
    extract_daily_features,
    prepare_feature_matrix,
)

logger = logging.getLogger("itbis.ml_anomaly")

DEFAULT_CONTAMINATION = 0.05
DEFAULT_RANDOM_STATE = 42
DEFAULT_MIN_SAMPLES = 5

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODELS_DIR = os.path.join(_BACKEND_DIR, "models")
DEFAULT_MODEL_PATH = os.path.join(_MODELS_DIR, "anomaly_model.pkl")


class InsufficientDataError(ValueError):
    """Raised when the number of valid feature records is below the required threshold for training."""
    pass


class InvalidFeatureError(ValueError):
    """Raised when feature records contain invalid, non-finite, or empty values."""
    pass


def train_isolation_forest(
    X: np.ndarray,
    contamination: Union[float, str] = DEFAULT_CONTAMINATION,
    random_state: int = DEFAULT_RANDOM_STATE,
    n_estimators: int = 100,
    min_samples: int = DEFAULT_MIN_SAMPLES,
) -> IsolationForest:
    """
    Fits an IsolationForest estimator on the supplied 2D feature matrix.

    Args:
        X: 2D numpy array of shape (N, D) containing numeric feature rows.
        contamination: Proportion of outliers in the data set (default: 0.05).
        random_state: Seed for pseudo-random number generator (default: 42).
        n_estimators: Number of base estimators in the ensemble (default: 100).
        min_samples: Minimum number of samples required to train (default: 5).

    Returns:
        Fitted IsolationForest model.

    Raises:
        InsufficientDataError: If N < min_samples or X is empty.
        InvalidFeatureError: If X contains non-finite entries or wrong dimensions.
    """
    if X is None or len(X) == 0:
        raise InsufficientDataError(
            f"Insufficient data for Isolation Forest training: dataset is empty."
        )

    if not isinstance(X, np.ndarray):
        try:
            X = np.array(X, dtype=np.float64)
        except Exception as e:
            raise InvalidFeatureError(f"Cannot convert feature input to numpy array: {e}")

    if X.ndim != 2:
        raise InvalidFeatureError(
            f"Expected 2D feature matrix (N, D), received shape {X.shape}."
        )

    if not np.all(np.isfinite(X)):
        raise InvalidFeatureError(
            "Feature matrix contains non-finite values (NaN or Inf). Clean and impute features first."
        )

    n_samples, n_features = X.shape

    if n_samples < min_samples:
        raise InsufficientDataError(
            f"Insufficient data for Isolation Forest training: requires at least {min_samples} "
            f"valid daily feature rows, found {n_samples}."
        )

    # Validate contamination
    if isinstance(contamination, (int, float)):
        if not (0.0 < contamination <= 0.5):
            raise ValueError(
                f"Contamination must be in (0.0, 0.5], received {contamination}."
            )
    elif contamination != "auto":
        raise ValueError(
            f"Contamination must be a float in (0.0, 0.5] or 'auto', received {contamination}."
        )

    logger.info(
        "Fitting IsolationForest on %d samples x %d features (contamination=%s, random_state=%d)",
        n_samples,
        n_features,
        contamination,
        random_state,
    )

    clf = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    clf.fit(X)
    return clf


def score_samples(
    model: IsolationForest,
    X: np.ndarray,
    feature_records: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Scores daily feature records using a trained IsolationForest model.

    Args:
        model: Fitted IsolationForest estimator.
        X: 2D numpy array of shape (N, D) aligned with feature_records.
        feature_records: List of daily feature dicts corresponding to the rows of X.

    Returns:
        List of scored dictionaries containing:
          - employee_id: str
          - date: str (YYYY-MM-DD)
          - anomaly_score: float (decision_function score; negative indicates outlier)
          - anomaly_flag: int (-1 for anomaly, 1 for normal)
          - is_anomaly: bool (True if anomaly_flag == -1)
          - feature_values: Dict[str, Any]
    """
    if len(feature_records) == 0 or len(X) == 0:
        return []

    if len(X) != len(feature_records):
        raise ValueError(
            f"Feature matrix rows ({len(X)}) do not match feature_records count ({len(feature_records)})."
        )

    raw_scores = model.decision_function(X)
    predictions = model.predict(X)

    results: List[Dict[str, Any]] = []
    for i, rec in enumerate(feature_records):
        pred_val = int(predictions[i])
        score_val = round(float(raw_scores[i]), 4)
        is_anom = (pred_val == -1)

        results.append({
            "employee_id": rec["employee_id"],
            "date": rec["date"],
            "anomaly_score": score_val,
            "anomaly_flag": pred_val,
            "is_anomaly": is_anom,
            "feature_values": {
                "avg_login_hour": rec.get("avg_login_hour"),
                "download_count": rec.get("download_count"),
                "total_download_mb": rec.get("total_download_mb"),
                "unique_devices": rec.get("unique_devices"),
                "total_events": rec.get("total_events"),
            },
        })

    return results


def save_model(model: IsolationForest, filepath: Optional[str] = None) -> str:
    """
    Serializes and saves a trained IsolationForest model to disk using joblib.

    Args:
        model: Fitted IsolationForest estimator.
        filepath: Target .pkl file path (defaults to backend/models/anomaly_model.pkl).

    Returns:
        Canonical absolute path to the saved model file.
    """
    target_path = filepath or DEFAULT_MODEL_PATH
    target_dir = os.path.dirname(target_path)
    os.makedirs(target_dir, exist_ok=True)

    joblib.dump(model, target_path)
    logger.info("Saved trained IsolationForest model to %s", target_path)
    return target_path


def load_model(filepath: Optional[str] = None) -> IsolationForest:
    """
    Deserializes a trained IsolationForest model from disk using joblib.

    Args:
        filepath: Target .pkl file path (defaults to backend/models/anomaly_model.pkl).

    Returns:
        Loaded IsolationForest estimator.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    target_path = filepath or DEFAULT_MODEL_PATH
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Trained IsolationForest model not found at '{target_path}'.")

    model = joblib.load(target_path)
    logger.info("Loaded IsolationForest model from %s", target_path)
    return model


def persist_ml_anomalies(
    scored_results: List[Dict[str, Any]],
    mongo_service: Optional[Any] = None,
    only_anomalies: bool = True,
) -> List[Dict[str, Any]]:
    """
    Persists detected ML anomaly events through the mongo_service abstraction,
    using persistent JSON fallback when MongoDB is offline.

    Args:
        scored_results: Output from score_samples.
        mongo_service: MongoDBService instance (defaults to global singleton).
        only_anomalies: If True, only records with is_anomaly=True are persisted.

    Returns:
        List of saved anomaly records.
    """
    if mongo_service is None:
        from app.mongodb import mongo_service as default_service
        mongo_service = default_service

    persisted: List[Dict[str, Any]] = []

    for item in scored_results:
        if only_anomalies and not item.get("is_anomaly"):
            continue

        score = float(item.get("anomaly_score", 0.0))
        severity = "critical" if score < -0.15 else "high"

        doc = {
            "employee_id": item["employee_id"],
            "indicator": "isolation_forest",
            "anomaly_type": "ML_ISOLATION_FOREST",
            "severity": severity,
            "observed_value": f"Score: {score} (Flag: {item.get('anomaly_flag')})",
            "expected_baseline": "Normal operational behavior (score >= 0.0)",
            "description": f"Isolation Forest detected anomalous behavioral pattern on {item['date']}",
            "details": {
                "date": item["date"],
                "anomaly_score": score,
                "anomaly_flag": item.get("anomaly_flag"),
                "features": item.get("feature_values"),
            },
            "detection_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        save_fn = getattr(mongo_service, "record_anomaly", getattr(mongo_service, "save_anomaly", None))
        if save_fn:
            saved = save_fn(doc)
            persisted.append(saved)

    storage_mode = "MongoDB" if mongo_service.is_connected else "Persistent JSON Store"
    logger.info("Persisted %d ML anomalies to %s", len(persisted), storage_mode)
    return persisted


def run_ml_pipeline(
    activity_logs: Optional[List[Dict[str, Any]]] = None,
    contamination: Union[float, str] = DEFAULT_CONTAMINATION,
    random_state: int = DEFAULT_RANDOM_STATE,
    min_samples: int = DEFAULT_MIN_SAMPLES,
    save_artifact: bool = True,
    persist_anomalies: bool = True,
    model_path: Optional[str] = None,
    mongo_service: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    End-to-end execution of the Isolation Forest anomaly detection pipeline:
    1. Loads activity telemetry (from parameter or mongo_service storage).
    2. Builds daily feature records per employee per UTC day.
    3. Fits the Isolation Forest model on valid feature rows.
    4. Scores all rows.
    5. Optionally saves the model artifact to disk.
    6. Optionally persists detected anomalies through mongo_service.

    Returns:
        Dictionary with model, scored_records, anomalies_count, and storage metadata.
    """
    if mongo_service is None:
        from app.mongodb import mongo_service as default_service
        mongo_service = default_service

    if activity_logs is None:
        result = mongo_service.query_activity_logs(limit=5000)
        activity_logs = result.get("items", [])

    daily_records = extract_daily_features(activity_logs)
    X, valid_records, feature_names = prepare_feature_matrix(daily_records)

    model = train_isolation_forest(
        X,
        contamination=contamination,
        random_state=random_state,
        min_samples=min_samples,
    )

    scored = score_samples(model, X, valid_records)

    saved_path = None
    if save_artifact:
        saved_path = save_model(model, filepath=model_path)

    saved_anomalies = []
    if persist_anomalies:
        saved_anomalies = persist_ml_anomalies(scored, mongo_service=mongo_service)

    return {
        "model": model,
        "model_path": saved_path,
        "feature_names": feature_names,
        "total_records": len(valid_records),
        "scored_records": scored,
        "anomalies_detected": [r for r in scored if r["is_anomaly"]],
        "persisted_count": len(saved_anomalies),
        "storage_mode": "mongodb" if mongo_service.is_connected else "json_fallback",
    }
