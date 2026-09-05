# backend/app/ml_engine/risk_scorer.py
from typing import List, Dict, Any, Tuple

class BehavioralRiskScorer:
    """
    Computes a composite 0-100 insider threat risk score based on anomaly signals,
    data sensitivity, temporal irregularities, and baseline variance.
    """
    def compute_risk(
        self,
        base_employee_risk: float,
        anomaly_detected: bool,
        anomaly_score: float,
        indicators: List[str],
        logs: List[Dict[str, Any]]
    ) -> Tuple[float, str, List[str]]:
        """
        Returns:
            final_risk_score (float, 0-100),
            threat_level (str: "LOW", "MEDIUM", "HIGH", "CRITICAL"),
            top_factors (List[str])
        """
        score = base_employee_risk or 15.0
        factors = []

        # 1. Anomaly Model Contribution (up to 35 points)
        if anomaly_detected:
            model_points = anomaly_score * 35.0
            score += model_points
            factors.append(f"AI Anomaly Model: +{model_points:.1f} pts (Anomaly Confidence: {anomaly_score*100:.1f}%)")

        # 2. Heuristic Specific Threat Boosts
        for log in logs:
            event_type = (log.get("event_type") or "").lower()
            details = log.get("details") or {}

            # USB mass exfiltration
            if "usb" in event_type:
                score += 25.0
                factors.append("Removable USB media exfiltration risk (+25.0 pts)")
                break

        for log in logs:
            event_type = (log.get("event_type") or "").lower()
            details = log.get("details") or {}
            
            # Massive DB dump
            rows = int(details.get("rows_accessed", details.get("row_count", 0)))
            if rows > 5000:
                score += 30.0
                factors.append(f"Mass database query scraping detected ({rows} rows) (+30.0 pts)")
                break

        for log in logs:
            event_type = (log.get("event_type") or "").lower()
            details = log.get("details") or {}
            
            # Privilege escalation
            if "privilege" in event_type or "sudo" in event_type or details.get("admin_override"):
                score += 20.0
                factors.append("Unauthorized administrative privilege escalation (+20.0 pts)")
                break

        # 3. Indicator Contributions
        for ind in indicators:
            if "temporal" in ind.lower():
                score += 15.0
                factors.append("High ratio of off-hours operations (+15.0 pts)")
            if "download" in ind.lower():
                score += 20.0
                factors.append("Excessive data egress volume (+20.0 pts)")

        # Deduplicate factors
        unique_factors = list(dict.fromkeys(factors))

        # Clamp score between 0 and 100
        final_score = float(min(100.0, max(0.0, score)))

        # Determine Threat Level
        if final_score >= 80.0:
            threat_level = "CRITICAL"
        elif final_score >= 60.0:
            threat_level = "HIGH"
        elif final_score >= 35.0:
            threat_level = "MEDIUM"
        else:
            threat_level = "LOW"

        return round(final_score, 1), threat_level, unique_factors

risk_scorer = BehavioralRiskScorer()
