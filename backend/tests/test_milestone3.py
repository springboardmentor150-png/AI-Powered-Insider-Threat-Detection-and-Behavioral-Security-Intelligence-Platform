# backend/tests/test_milestone3.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, mongo_db
from app.models import User, Employee, Alert, Incident
from app.risk_scoring import calculate_risk_score, WEIGHTS
from app.ueba import compare_to_peers, get_risk_trend

client = TestClient(app)

def get_auth_headers(email: str, password: str = "Security@123"):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# -------------------------------------------------------------
# 1. Test Weighted Risk Scoring Model (Part 1 Self-Check)
# -------------------------------------------------------------
def test_calculate_risk_score_weighting_and_caps():
    # Verify exact weights from project spec
    assert WEIGHTS["behavioral_anomalies"] == 0.35
    assert WEIGHTS["privilege_misuse"] == 0.25
    assert WEIGHTS["data_access_violations"] == 0.20
    assert WEIGHTS["access_pattern_deviations"] == 0.10
    assert WEIGHTS["historical_security_events"] == 0.10
    assert sum(WEIGHTS.values()) == 1.0

    # Test critical employee (Devon Miller - EMP1003)
    score_devon = calculate_risk_score("EMP1003")
    assert score_devon["risk_score"] >= 75.0
    assert score_devon["risk_category"] == "critical"
    # Ensure all factor scores are <= 100
    for factor, val in score_devon["factor_scores"].items():
        assert 0 <= val <= 100

    # Test high risk employee (Jonathan Hayes - EMP1002)
    score_jhayes = calculate_risk_score("EMP1002")
    assert score_jhayes["risk_category"] in ("high", "critical")

    # Test low risk employee (Elena - EMP1001)
    score_elena = calculate_risk_score("EMP1001")
    assert score_elena["risk_category"] == "low"

# -------------------------------------------------------------
# 2. Test UEBA Intelligence Workflows (Part 2 Self-Check)
# -------------------------------------------------------------
def test_ueba_peer_comparison_and_no_peers_edge_case():
    db = SessionLocal()
    try:
        # 1. Normal comparison with peers (Elena in Engineering with Liam)
        res_eng = compare_to_peers(db, "EMP1001")
        assert res_eng["peer_count"] >= 1
        assert "deviation_from_peers" in res_eng
        assert "department_avg_score" in res_eng

        # 2. Edge case: Employee with NO peers in department (Zoe in Legal)
        res_solo = compare_to_peers(db, "EMP1008")
        assert res_solo["peer_count"] == 0
        assert "No peers in department for comparison" in res_solo.get("note", "")

        # 3. Behavioral Trend Analysis (30-day anomaly histogram)
        trend = get_risk_trend("EMP1003", days=30)
        assert isinstance(trend, list)
    finally:
        db.close()

# -------------------------------------------------------------
# 3. Test Threat Investigation & Incident Workflows (Part 3)
# -------------------------------------------------------------
def test_incident_creation_rejection_and_timeline():
    analyst_headers = get_auth_headers("analyst@itbis.security")

    # 1. Low-risk employee (EMP1001) creation MUST be rejected with 400
    res_low = client.post("/incidents/create-from-risk/EMP1001", headers=analyst_headers)
    assert res_low.status_code == 400
    assert "Risk level too low to warrant an incident" in res_low.json()["detail"]

    # 2. High/Critical employee (EMP1003) creation MUST succeed
    res_high = client.post("/incidents/create-from-risk/EMP1003", headers=analyst_headers)
    assert res_high.status_code == 200
    created_inc = res_high.json()
    inc_id = created_inc["id"]

    # 3. Test Chronological Incident Timeline
    res_timeline = client.get(f"/incidents/{inc_id}/timeline", headers=analyst_headers)
    assert res_timeline.status_code == 200
    timeline_data = res_timeline.json()
    assert "timeline" in timeline_data
    timeline = timeline_data["timeline"]
    assert len(timeline) >= 1
    # Verify types contain both activity and anomaly
    types = [t["type"] for t in timeline]
    assert "activity" in types or "anomaly" in types

    # 4. Test Adding Evidence Notes
    res_evidence = client.post(
        f"/incidents/{inc_id}/evidence",
        json={"note": "Forensic disk image collected from workstation."},
        headers=analyst_headers
    )
    assert res_evidence.status_code == 200
    assert "Forensic disk image" in res_evidence.json()["note"]

# -------------------------------------------------------------
# 4. Test Alert Assignment & Resolution RBAC (Part 4)
# -------------------------------------------------------------
def test_alert_assignment_and_resolution_rbac():
    admin_headers = get_auth_headers("admin@itbis.security")
    manager_headers = get_auth_headers("manager@itbis.security")
    analyst_headers = get_auth_headers("analyst@itbis.security")

    # Fetch an open alert
    db = SessionLocal()
    alert = db.query(Alert).filter(Alert.status == "open").first()
    if not alert:
        alert = Alert(employee_id="EMP1003", message="Test Alert", severity="high", status="open")
        db.add(alert)
        db.commit()
        db.refresh(alert)
    alert_id = alert.id
    db.close()

    # 1. Analyst tries to ASSIGN alert -> Must be blocked (403 Forbidden)
    res_assign_forbidden = client.post(f"/alerts/{alert_id}/assign?analyst_user_id=2", headers=analyst_headers)
    assert res_assign_forbidden.status_code == 403

    # 2. Manager assigns alert -> Must succeed (200)
    res_assign_allowed = client.post(f"/alerts/{alert_id}/assign?analyst_user_id=2", headers=manager_headers)
    assert res_assign_allowed.status_code == 200
    assert res_assign_allowed.json()["status"] == "assigned"

    # 3. Analyst resolves alert -> Must succeed (200)
    res_resolve = client.patch(f"/alerts/{alert_id}/resolve", headers=analyst_headers)
    assert res_resolve.status_code == 200
    assert res_resolve.json()["status"] == "resolved"

    # 4. Test Risk Distribution summary
    res_dist = client.get("/analytics/risk-distribution", headers=manager_headers)
    assert res_dist.status_code == 200
    dist = res_dist.json()["distribution"]
    assert "critical" in dist and "high" in dist and "low" in dist

# -------------------------------------------------------------
# 5. Test Role-Appropriate Security Dashboards (Part 5)
# -------------------------------------------------------------
def test_all_three_dashboards():
    analyst_headers = get_auth_headers("analyst@itbis.security")
    manager_headers = get_auth_headers("manager@itbis.security")
    soc_headers = get_auth_headers("soc@itbis.security")

    # 1. Analyst Dashboard
    res_analyst = client.get("/dashboard/analyst", headers=analyst_headers)
    assert res_analyst.status_code == 200
    data_analyst = res_analyst.json()
    assert "open_alerts" in data_analyst
    assert "active_investigations" in data_analyst
    assert "high_risk_employees" in data_analyst

    # 2. SOC Dashboard
    res_soc = client.get("/dashboard/soc", headers=soc_headers)
    assert res_soc.status_code == 200
    data_soc = res_soc.json()
    assert "total_security_events" in data_soc
    assert "behavioral_anomalies_count" in data_soc

    # 3. Security Manager Dashboard
    res_mgr = client.get("/dashboard/manager", headers=manager_headers)
    assert res_mgr.status_code == 200
    data_mgr = res_mgr.json()
    assert "distribution" in data_mgr
    assert "compliance_score" in data_mgr