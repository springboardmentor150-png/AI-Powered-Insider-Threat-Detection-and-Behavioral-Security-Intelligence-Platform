
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .models import Employee, Incident
from .mongo import ml_anomalies, behavioral_baselines, rule_anomalies


# Milestone 3 risk-factor weights. The weights sum to 1.0.
WEIGHTS = {
    "behavioral_anomalies": 0.35,
    "privilege_misuse": 0.25,
    "data_access_violations": 0.20,
    "access_pattern_deviations": 0.10,
    "historical_events": 0.10,
}

# Risk-level thresholds from the Milestone 3 design.
RISK_THRESHOLDS = {
    "Critical": 75,
    "High": 50,
    "Medium": 25,
}


def _bounded_score(value: float) -> float:
    """Keep every factor score between 0 and 100."""
    return round(max(0.0, min(100.0, float(value))), 2)


def _count_score(count: int, points_per_event: int = 10) -> float:
    """
    Normalize an event count to a 0–100 score.

    This is an initial, configurable scoring rule—not a learned probability.
    """
    return _bounded_score(max(0, count) * points_per_event)


def score_behavioral_anomalies(employee_code: str) -> float:
    """Score stored rule-based and ML anomaly evidence."""
    rule_count = rule_anomalies.count_documents(
        {"employee_code": employee_code}
    )
    ml_count = ml_anomalies.count_documents(
        {"employee_code": employee_code, "is_anomaly": True}
    )

    # Count both evidence sources, then cap the factor at 100.
    return _count_score(rule_count + ml_count)


def score_privilege_misuse(employee_code: str) -> float:
    """
    Return zero until a reliable privilege-misuse signal is available.

    Current verified schemas do not establish a privilege-change event
    collection or a privilege-misuse indicator. Do not infer this signal
    from unrelated anomaly records.
    """
    return 0.0


def score_data_access_violations(employee_code: str) -> float:
    """Score stored anomalies related to transfers and resource access."""
    relevant_indicators = {
        "data_transfer_volume",
        "resource_access_frequency",
    }

    rule_count = rule_anomalies.count_documents(
        {
            "employee_code": employee_code,
            "indicator": {"$in": list(relevant_indicators)},
        }
    )

    # ML records do not identify a specific violation type, so they are
    # deliberately not counted again in this factor.
    return _count_score(rule_count)


def score_access_pattern_deviations(employee_code: str) -> float:
    """Score stored anomalies involving unfamiliar devices or applications."""
    relevant_indicators = {
        "device_usage",
        "application_usage",
        "login_time",
    }

    rule_count = rule_anomalies.count_documents(
        {
            "employee_code": employee_code,
            "indicator": {"$in": list(relevant_indicators)},
        }
    )

    # The ML model's aggregate score does not identify a specific access
    # pattern, so it is not counted again here.
    return _count_score(rule_count)


def score_historical_events(
    employee_code: str,
    db: Session,
) -> float:
    """Score the employee's historical incidents stored in PostgreSQL."""
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .first()
    )

    if employee is None:
        return 0.0

    incident_count = (
        db.query(Incident)
        .filter(Incident.employee_id == employee.id)
        .count()
    )

    return _count_score(incident_count)


def get_risk_level(final_score: float) -> str:
    """Convert a 0–100 score into a risk category."""
    if final_score >= RISK_THRESHOLDS["Critical"]:
        return "Critical"
    if final_score >= RISK_THRESHOLDS["High"]:
        return "High"
    if final_score >= RISK_THRESHOLDS["Medium"]:
        return "Medium"
    return "Low"


from .database import SessionLocal


def calculate_risk_score(
    employee_code: str,
    db: Session | None = None,
) -> dict:
    """
    Calculate the employee's weighted risk score.

    Returns the overall score, risk level, factor scores, and calculation
    timestamp. Raises ValueError if the employee does not exist.
    """
    should_close_db = False
    if db is None:
        db = SessionLocal()
        should_close_db = True

    try:
        is_numeric_id = False
        int_id = None
        try:
            int_id = int(employee_code)
            is_numeric_id = True
        except (ValueError, TypeError):
            pass

        employee = (
            db.query(Employee)
            .filter(
                (Employee.employee_code == str(employee_code))
                | ((Employee.id == int_id) if is_numeric_id else False)
            )
            .first()
        )

        if employee is None:
            raise ValueError(f"Employee '{employee_code}' was not found")

        resolved_code = employee.employee_code

        factor_scores = {
            "behavioral_anomalies": score_behavioral_anomalies(resolved_code),
            "privilege_misuse": score_privilege_misuse(resolved_code),
            "data_access_violations": score_data_access_violations(resolved_code),
            "access_pattern_deviations": score_access_pattern_deviations(
                resolved_code
            ),
            "historical_events": score_historical_events(resolved_code, db),
        }

        weighted_score = sum(
            factor_scores[factor] * weight
            for factor, weight in WEIGHTS.items()
        )
        final_score = _bounded_score(weighted_score)

        peer_comparison = compare_employee_with_peers(resolved_code)
        risk_level = get_risk_level(final_score)

        return {
            "employee_id": resolved_code,
            "employee_code": resolved_code,
            "employee_name": employee.name,
            "risk_score": final_score,
            "final_score": final_score,
            "risk_level": risk_level,
            "risk_category": risk_level.lower(),
            "factor_scores": factor_scores,
            "sub_scores": factor_scores,
            "weights": WEIGHTS.copy(),
            "privilege_misuse_signal_available": False,
            "peer_comparison": peer_comparison,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        if should_close_db:
            db.close()


def compare_employee_with_peers(employee_code: str) -> dict:
    """
    Compare an employee's numeric behavioral baselines with other employees
    for the same indicator.

    This is a descriptive peer comparison, not a threat verdict.
    Categorical device/application indicators are excluded from numeric
    comparisons and are reported separately.
    """
    numeric_indicators = {
        "login_time",
        "data_transfer_volume",
        "resource_access_frequency",
    }

    employee_baselines = {
        item["indicator"]: item
        for item in behavioral_baselines.find(
            {"employee_code": employee_code},
            {"_id": 0},
        )
    }

    if not employee_baselines:
        return {
            "employee_code": employee_code,
            "peer_count": 0,
            "comparisons": [],
            "message": "No behavioral baselines are available for this employee.",
        }

    comparisons = []

    for indicator in sorted(numeric_indicators):
        own_baseline = employee_baselines.get(indicator)

        if own_baseline is None:
            continue

        own_value = own_baseline.get("typical_value")

        if not isinstance(own_value, (int, float)):
            continue

        peer_documents = list(
            behavioral_baselines.find(
                {
                    "indicator": indicator,
                    "employee_code": {"$ne": employee_code},
                    "typical_value": {"$type": "number"},
                },
                {"_id": 0},
            )
        )

        peer_values = [
            float(document["typical_value"])
            for document in peer_documents
        ]

        if not peer_values:
            comparisons.append(
                {
                    "indicator": indicator,
                    "employee_value": float(own_value),
                    "peer_count": 0,
                    "peer_average": None,
                    "difference_from_peer_average": None,
                    "comparison_available": False,
                }
            )
            continue

        peer_average = sum(peer_values) / len(peer_values)
        difference = float(own_value) - peer_average

        comparisons.append(
            {
                "indicator": indicator,
                "employee_value": round(float(own_value), 2),
                "peer_count": len(peer_values),
                "peer_average": round(peer_average, 2),
                "difference_from_peer_average": round(difference, 2),
                "comparison_available": True,
            }
        )

    return {
        "employee_code": employee_code,
        "peer_count": max(
            (item["peer_count"] for item in comparisons),
            default=0,
        ),
        "comparisons": comparisons,
        "interpretation": (
            "Differences are descriptive and do not independently establish "
            "suspicious behavior."
        ),
    }
