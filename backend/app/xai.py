"""
ITBIS - Explainable AI (XAI) Engine for Behavioral Anomaly Detection
Provides feature attribution, baseline deviation analysis, and natural language explanations
for unsupervised machine learning (Isolation Forest) anomalies.
"""

from __future__ import annotations
from typing import Any
import numpy as np
import pandas as pd

from .ml_features import FEATURE_COLUMNS
from .mongo import behavioral_baselines, ml_anomalies


FEATURE_METADATA = {
    "avg_login_hour": {
        "label": "Login Timing Anomaly",
        "unit": "Hour of Day (24h)",
        "format": lambda v: f"{int(v):02d}:{int((v % 1) * 60):02d}",
        "description": "Deviations from standard organizational operating hours.",
    },
    "total_download_mb": {
        "label": "Data Exfiltration Volume",
        "unit": "MB",
        "format": lambda v: f"{v:.1f} MB",
        "description": "Significant spike in outbound or local download data volume.",
    },
    "download_count": {
        "label": "File Download Frequency",
        "unit": "Files",
        "format": lambda v: f"{int(v)} files",
        "description": "Excessive file exports or download actions.",
    },
    "unique_devices": {
        "label": "Multi-Device Endpoint Usage",
        "unit": "Endpoints",
        "format": lambda v: f"{int(v)} device(s)",
        "description": "Activity detected across multiple unfamiliar devices or MAC addresses.",
    },
    "total_events": {
        "label": "Activity Event Velocity",
        "unit": "Events",
        "format": lambda v: f"{int(v)} events",
        "description": "High-velocity event bursts indicative of automated scripts or scraping.",
    },
}

# Empirical baseline defaults across organization when employee baseline is sparse
DEFAULT_BASELINE_STATS = {
    "avg_login_hour": {"mean": 10.5, "std": 1.8},
    "total_download_mb": {"mean": 22.0, "std": 15.0},
    "download_count": {"mean": 4.0, "std": 3.0},
    "unique_devices": {"mean": 1.1, "std": 0.4},
    "total_events": {"mean": 45.0, "std": 20.0},
}


def explain_anomaly_record(
    record: dict[str, Any],
    employee_code: str | None = None,
) -> dict[str, Any]:
    """
    Generate Explainable AI (XAI) feature attribution breakdown for a single anomaly record.
    """
    emp_code = employee_code or record.get("employee_code") or "UNKNOWN"
    
    # Attempt to retrieve personalized baseline from MongoDB
    emp_baseline = None
    if emp_code != "UNKNOWN":
        emp_baseline = behavioral_baselines.find_one({"employee_code": emp_code})

    factor_details = []
    z_scores = []

    for feat in FEATURE_COLUMNS:
        meta = FEATURE_METADATA.get(feat, {"label": feat, "unit": "", "format": str, "description": ""})
        actual_val = float(record.get(feat, 0.0))

        # Determine reference mean and std
        if emp_baseline and feat in emp_baseline:
            base_mean = float(emp_baseline[feat].get("mean", DEFAULT_BASELINE_STATS[feat]["mean"]))
            base_std = float(emp_baseline[feat].get("std", DEFAULT_BASELINE_STATS[feat]["std"]))
        else:
            base_mean = DEFAULT_BASELINE_STATS[feat]["mean"]
            base_std = DEFAULT_BASELINE_STATS[feat]["std"]

        std_safe = max(base_std, 0.5)
        z_score = abs(actual_val - base_mean) / std_safe
        z_scores.append(z_score)

        direction = "normal"
        if actual_val > base_mean + (1.2 * std_safe):
            direction = "elevated"
        elif actual_val < base_mean - (1.2 * std_safe):
            direction = "suppressed"

        factor_details.append({
            "feature": feat,
            "label": meta["label"],
            "unit": meta["unit"],
            "actual_value": actual_val,
            "formatted_actual": meta["format"](actual_val),
            "baseline_mean": round(base_mean, 2),
            "formatted_baseline": meta["format"](base_mean),
            "z_score": round(z_score, 2),
            "direction": direction,
            "description": meta["description"],
        })

    # Compute relative contribution percentage
    total_z = sum(z_scores) if sum(z_scores) > 0 else 1.0
    for i, factor in enumerate(factor_details):
        contrib_pct = round((z_scores[i] / total_z) * 100.0, 1)
        factor["contribution_percentage"] = contrib_pct
        
        if contrib_pct >= 35.0 or z_scores[i] >= 2.5:
            factor["impact"] = "critical"
        elif contrib_pct >= 20.0 or z_scores[i] >= 1.5:
            factor["impact"] = "high"
        elif contrib_pct >= 10.0:
            factor["impact"] = "moderate"
        else:
            factor["impact"] = "low"

    # Sort descending by contribution percentage
    factor_details.sort(key=lambda x: x["contribution_percentage"], reverse=True)

    top_factor = factor_details[0] if factor_details else None
    second_factor = factor_details[1] if len(factor_details) > 1 else None

    # Construct narrative synthesis
    narrative = f"Isolation Forest flagged this observation primarily due to {top_factor['label'].lower()} ({top_factor['contribution_percentage']}% attribution, {top_factor['formatted_actual']} vs expected {top_factor['formatted_baseline']})."
    if second_factor and second_factor["contribution_percentage"] >= 18.0:
        narrative += f" Secondary driver was {second_factor['label'].lower()} ({second_factor['contribution_percentage']}% attribution)."

    return {
        "employee_code": emp_code,
        "date": record.get("date"),
        "anomaly_score": round(float(record.get("anomaly_score", -0.5)), 4),
        "is_anomaly": bool(record.get("is_anomaly", True)),
        "summary": narrative,
        "top_contributor": top_factor["label"] if top_factor else "Unknown",
        "contributing_factors": factor_details,
    }
