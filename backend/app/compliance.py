"""
ITBIS Compliance & MTTR/MTTI Metrics Engine (Milestone 4: Day 31-32)
Provides enterprise operational metrics, Mean Time to Resolve (MTTR),
Mean Time to Investigate (MTTI), and compliance indicators.
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import Incident, Alert, InvestigationNote

logger = logging.getLogger("itbis.compliance")


def calculate_mttr(db: Session) -> float:
    """
    Calculates Mean Time to Resolve (MTTR) in hours across resolved incidents and alerts.
    Safely handles zero divisions and missing timestamps.
    """
    durations: List[float] = []

    resolved_incidents = db.query(Incident).filter(
        Incident.status.in_(["resolved", "RESOLVED", "closed", "CLOSED"]),
        Incident.resolved_at.isnot(None),
        Incident.created_at.isnot(None),
    ).all()

    for inc in resolved_incidents:
        if inc.resolved_at and inc.created_at:
            diff_hours = (inc.resolved_at - inc.created_at).total_seconds() / 3600.0
            if diff_hours >= 0:
                durations.append(diff_hours)

    # Supplement with resolved alerts if incident sample size is small
    resolved_alerts = db.query(Alert).filter(
        Alert.status.in_(["resolved", "RESOLVED"]),
        Alert.resolved_at.isnot(None),
        Alert.created_at.isnot(None),
    ).all()

    for al in resolved_alerts:
        if al.resolved_at and al.created_at:
            diff_hours = (al.resolved_at - al.created_at).total_seconds() / 3600.0
            if diff_hours >= 0:
                durations.append(diff_hours)

    if not durations:
        return 0.0

    return round(sum(durations) / len(durations), 2)


def calculate_mtti(db: Session) -> float:
    """
    Calculates Mean Time to Investigate (MTTI) in hours from incident creation
    until investigation commences (recorded in investigation_started_at or first note).
    Safely handles zero divisions.
    """
    durations: List[float] = []

    incidents = db.query(Incident).filter(
        Incident.created_at.isnot(None)
    ).all()

    for inc in incidents:
        start_time = inc.investigation_started_at
        if not start_time:
            # Fallback to earliest investigation note timestamp if available
            first_note = db.query(InvestigationNote).filter(
                InvestigationNote.incident_id == inc.id
            ).order_by(InvestigationNote.created_at.asc()).first()
            if first_note and first_note.created_at:
                start_time = first_note.created_at

        if start_time and inc.created_at:
            diff_hours = (start_time - inc.created_at).total_seconds() / 3600.0
            if diff_hours >= 0:
                durations.append(diff_hours)

    if not durations:
        return 0.0

    return round(sum(durations) / len(durations), 2)


def get_compliance_metrics(db: Session) -> Dict[str, Any]:
    """
    Assembles overall compliance and SLA performance indicators:
    - total_incidents
    - resolved (status resolved/closed)
    - resolution_rate_percent (zero-guarded)
    - open_critical_incidents (open/investigating with severity critical)
    - mttr_hours & mtti_hours
    """
    total_incidents = db.query(Incident).count()
    resolved = db.query(Incident).filter(
        Incident.status.in_(["resolved", "RESOLVED", "closed", "CLOSED"])
    ).count()

    resolution_rate = round((resolved / total_incidents) * 100.0, 1) if total_incidents > 0 else 100.0

    open_critical = db.query(Incident).filter(
        Incident.status.in_(["open", "OPEN", "investigating", "INVESTIGATING"]),
        Incident.severity.in_(["critical", "CRITICAL"]),
    ).count()

    mttr = calculate_mttr(db)
    mtti = calculate_mtti(db)

    return {
        "total_incidents": total_incidents,
        "resolved_incidents": resolved,
        "resolution_rate_percent": resolution_rate,
        "open_critical_incidents": open_critical,
        "mttr_hours": mttr,
        "mtti_hours": mtti,
        "compliance_status": "COMPLIANT" if resolution_rate >= 75.0 and open_critical == 0 else "ATTENTION_REQUIRED",
    }
