# backend/app/ml_engine/anomaly_detector.py
from datetime import datetime
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest

class BehavioralAnomalyDetector:
    """
    Evaluates employee activity logs using Isolation Forest and Statistical Baseline Deviation.
    """
    def __init__(self):
        # Initialize Isolation Forest with tuned hyperparameters for insider anomaly patterns
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.12,
            random_state=42,
            bootstrap=False
        )
        self._is_trained = False
        self._warmup_model()

    def _extract_features_from_logs(self, logs: List[Dict[str, Any]]) -> np.ndarray:
        """
        Transforms raw event dictionaries into a numerical feature vector:
        [
          0: total_events,
          1: off_hours_ratio,
          2: total_download_mb,
          3: usb_events_count,
          4: db_rows_accessed,
          5: priv_escalations_count,
          6: sensitive_access_count
        ]
        """
        if not logs:
            return np.zeros((1, 7))

        total_events = len(logs)
        off_hours_count = 0
        total_download_mb = 0.0
        usb_events = 0
        db_rows = 0
        priv_escalations = 0
        sensitive_access = 0

        for log in logs:
            event_type = (log.get("event_type") or "").lower()
            details = log.get("details") or {}
            
            # 1. Check time of event
            ts = log.get("timestamp")
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts)
                except Exception:
                    ts = datetime.utcnow()
            elif not isinstance(ts, datetime):
                ts = datetime.utcnow()

            hour = ts.hour
            weekday = ts.weekday() # 5=Sat, 6=Sun
            if hour < 7 or hour > 19 or weekday >= 5 or details.get("is_off_hours"):
                off_hours_count += 1

            # 2. File Download volume
            if "file_download" in event_type or "download" in event_type:
                size = float(details.get("size_mb", details.get("file_size_mb", 0)))
                total_download_mb += size
                if details.get("is_confidential") or details.get("sensitive"):
                    sensitive_access += 1

            # 3. USB Connection
            if "usb" in event_type:
                usb_events += 1

            # 4. Database Query
            if "database" in event_type or "db" in event_type:
                rows = int(details.get("rows_accessed", details.get("row_count", 0)))
                db_rows += rows
                if rows > 1000:
                    sensitive_access += 1

            # 5. Privilege Escalation / Sensitive Admin Action
            if "privilege" in event_type or "sudo" in event_type or "admin_override" in event_type:
                priv_escalations += 1

            # 6. Sensitive Flag in Details
            if details.get("confidential") or details.get("restricted_access"):
                sensitive_access += 1

        off_hours_ratio = off_hours_count / max(total_events, 1)
        
        vector = np.array([
            total_events,
            off_hours_ratio,
            total_download_mb,
            usb_events,
            float(db_rows),
            priv_escalations,
            sensitive_access
        ], dtype=np.float64)

        return vector.reshape(1, -1)

    def _warmup_model(self):
        """Pre-trains Isolation Forest on a synthetic baseline matrix of normal enterprise behaviors."""
        np.random.seed(42)
        # Normal profile: 10-40 events, <15% off hours, <50MB downloads, 0-1 USB, <500 DB rows, 0 priv escalations
        normal_samples = []
        for _ in range(300):
            events = np.random.uniform(5, 45)
            off_hours = np.random.uniform(0.0, 0.15)
            download_mb = np.random.exponential(scale=15.0)
            usb = 0 if np.random.rand() > 0.1 else 1
            db_rows = np.random.uniform(0, 300)
            priv = 0
            sensitive = 0 if np.random.rand() > 0.05 else 1
            normal_samples.append([events, off_hours, download_mb, usb, db_rows, priv, sensitive])

        # Rare anomalous samples for calibration
        anomalous_samples = [
            [80, 0.85, 450.0, 3, 15000, 2, 8],
            [120, 0.95, 800.0, 1, 50000, 4, 12],
            [25, 0.90, 5.0, 4, 0, 5, 2]
        ]
        X = np.vstack([normal_samples, anomalous_samples])
        self.model.fit(X)
        self._is_trained = True

    def detect_anomalies(self, logs: List[Dict[str, Any]], baseline: Dict[str, Any] = None) -> Tuple[bool, float, List[str]]:
        """
        Scores activity logs.
        Returns:
            is_anomaly (bool)
            anomaly_score (float, 0.0 to 1.0)
            indicators (List[str])
        """
        if not logs:
            return False, 0.0, ["No recent activity logs recorded"]

        features = self._extract_features_from_logs(logs)
        
        # Isolation Forest Decision Function (lower = more abnormal)
        raw_score = self.model.decision_function(features)[0]
        # Map raw score (-0.5 to 0.5) to probability-like 0.0 (normal) to 1.0 (highly anomalous)
        normalized_anomaly_score = float(np.clip(1.0 - (raw_score + 0.35) / 0.7, 0.0, 1.0))
        
        indicators = []
        feat = features[0]
        total_events, off_hours_ratio, dl_mb, usb_cnt, db_rows, priv_cnt, sens_cnt = feat

        if off_hours_ratio > 0.4:
            indicators.append(f"Unusual temporal activity: {int(off_hours_ratio*100)}% of actions performed during non-working hours")
        if dl_mb > 150.0:
            indicators.append(f"High-volume data download: {dl_mb:.1f} MB exfiltrated/transferred in monitoring window")
        if usb_cnt > 0:
            indicators.append(f"Physical media connection: {int(usb_cnt)} unauthorized USB mass storage events detected")
        if db_rows > 2500:
            indicators.append(f"Bulk database extraction: {int(db_rows)} database records dumped")
        if priv_cnt > 0:
            indicators.append(f"Privilege escalation attempts: {int(priv_cnt)} elevated permission / sudo overrides recorded")
        if sens_cnt > 3:
            indicators.append(f"Repeated access to sensitive/confidential company intellectual property")

        is_anomaly = normalized_anomaly_score > 0.55 or len(indicators) >= 2 or priv_cnt >= 2 or dl_mb > 300.0
        
        if is_anomaly and not indicators:
            indicators.append("Behavioral statistical deviation detected across multi-variable activity matrix")

        return is_anomaly, normalized_anomaly_score, indicators

anomaly_detector = BehavioralAnomalyDetector()
