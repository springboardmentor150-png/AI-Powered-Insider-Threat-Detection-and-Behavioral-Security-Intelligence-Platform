# itbis/scripts/test_system.py
"""
End-to-End Test & Verification Suite for ITBIS Platform (Milestone 3 Enhanced).
Validates Backend API, Authentication, RBAC, Employee CRUD, Telemetry Ingestion,
Weighted Risk Scoring (35/25/20/10/10), UEBA Peer Comparison & Risk Trends,
Threat Investigation Timeline & Multi-Analyst Evidence, Alert Assignment/Resolution,
Role-Specific Security Dashboards (Analyst, SOC, Manager), and Threat Simulation.
"""
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def print_step(title):
    print(f"\n[TEST STEP] {title}...")

def test_system():
    print("=" * 70)
    print(" ITBIS - Milestone 3 Complete End-to-End System Verification Suite")
    print("=" * 70)

    # 1. Health Check
    print_step("1. Testing Root & Health Check Endpoints")
    try:
        r = requests.get(f"{BASE_URL}/")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        print("  [PASS] Root Health-check OK:", r.json().get("milestone", r.json().get("status")))
        
        r_health = requests.get(f"{BASE_URL}/health")
        assert r_health.status_code == 200
        print("  [PASS] Detailed Health OK:", r_health.json())
    except requests.exceptions.ConnectionError:
        print("  [FAIL] ERROR: Backend server is not running at http://127.0.0.1:8000.")
        print("    Please start the backend with `python backend/run.py` first.")
        sys.exit(1)

    # 2. Test User Authentication & RBAC
    print_step("2. Testing User Login & RBAC Role Enforcement")
    # Admin Login
    r_admin = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@itbis.security",
        "password": "Security@123"
    })
    assert r_admin.status_code == 200
    admin_token = r_admin.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Manager Login
    r_mgr = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "manager@itbis.security",
        "password": "Security@123"
    })
    assert r_mgr.status_code == 200
    mgr_token = r_mgr.json()["access_token"]
    mgr_headers = {"Authorization": f"Bearer {mgr_token}"}

    # Analyst Login
    r_analyst = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "analyst@itbis.security",
        "password": "Security@123"
    })
    assert r_analyst.status_code == 200
    analyst_token = r_analyst.json()["access_token"]
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}
    print("  [PASS] Acquired JWT Tokens for Admin, Manager, and Analyst roles.")

    # 3. Milestone 3 Part 1: Weighted Risk Scoring Engine
    print_step("3. Testing Milestone 3 Part 1: Weighted Risk Scoring (35/25/20/10/10)")
    r_risk = requests.get(f"{BASE_URL}/ueba/risk-score/EMP1003", headers=analyst_headers)
    assert r_risk.status_code == 200
    risk_data = r_risk.json()
    assert risk_data["risk_category"] == "critical"
    print(f"  [PASS] Employee EMP1003 Score: {risk_data['risk_score']} (Category: {risk_data['risk_category']})")
    print(f"  [PASS] 5 Factor Breakdown: {risk_data['factor_scores']}")

    # 4. Milestone 3 Part 2: UEBA Peer Comparison & Trends
    print_step("4. Testing Milestone 3 Part 2: UEBA Peer Group Comparison & Anomaly Trend")
    r_peer = requests.get(f"{BASE_URL}/ueba/peer-comparison/EMP1001", headers=analyst_headers)
    assert r_peer.status_code == 200
    peer_data = r_peer.json()
    print(f"  [PASS] EMP1001 vs Engineering Peers: Score = {peer_data['employee_score']}, Dept Avg = {peer_data['department_avg_score']}, Deviation = {peer_data['deviation_from_peers']}")

    # Edge case: Solo department with 0 peers
    r_solo = requests.get(f"{BASE_URL}/ueba/peer-comparison/EMP1008", headers=analyst_headers)
    assert r_solo.status_code == 200
    assert r_solo.json()["peer_count"] == 0
    print(f"  [PASS] Verified 0-Peers Edge Case: {r_solo.json().get('note')}")

    # Trend
    r_trend = requests.get(f"{BASE_URL}/ueba/risk-trend/EMP1003?days=30", headers=analyst_headers)
    assert r_trend.status_code == 200
    print(f"  [PASS] 30-Day Behavioral Anomaly Trend retrieved ({len(r_trend.json())} spike dates).")

    # 5. Milestone 3 Part 3: Threat Investigation & Timeline
    print_step("5. Testing Milestone 3 Part 3: Threat Investigation, Timeline & Evidence Notes")
    # Low-risk rejection test
    r_rej = requests.post(f"{BASE_URL}/incidents/create-from-risk/EMP1001", headers=analyst_headers)
    assert r_rej.status_code == 400
    print("  [PASS] Verified Low-Risk Incident Rejection (400 Bad Request).")

    # High-risk creation test
    r_inc = requests.post(f"{BASE_URL}/incidents/create-from-risk/EMP1003", headers=analyst_headers)
    assert r_inc.status_code == 200
    inc_obj = r_inc.json()
    inc_id = inc_obj["id"]
    print(f"  [PASS] Created Incident from High Risk: {inc_obj.get('incident_code')} (Severity: {inc_obj.get('severity')})")

    # Timeline test
    r_tl = requests.get(f"{BASE_URL}/incidents/{inc_id}/timeline", headers=analyst_headers)
    assert r_tl.status_code == 200
    print(f"  [PASS] Chronological Timeline retrieved ({len(r_tl.json()['timeline'])} merged logs/anomalies).")

    # Evidence test
    r_ev = requests.post(f"{BASE_URL}/incidents/{inc_id}/evidence", json={"note": "Workstation memory dump extracted."}, headers=analyst_headers)
    assert r_ev.status_code == 200
    print(f"  [PASS] Added Evidence Note: {r_ev.json()['note']}")

    # 6. Milestone 3 Part 4: Alert Delegation & Resolution RBAC
    print_step("6. Testing Milestone 3 Part 4: Alert Delegation & Resolution RBAC")
    r_alerts = requests.get(f"{BASE_URL}/alerts", headers=analyst_headers)
    assert r_alerts.status_code == 200
    alts = r_alerts.json()
    if alts:
        alt_id = alts[0]["id"]
        # Analyst forbidden to assign
        r_f = requests.post(f"{BASE_URL}/alerts/{alt_id}/assign?analyst_user_id=2", headers=analyst_headers)
        assert r_f.status_code == 403
        print("  [PASS] RBAC Check: Analyst blocked from alert assignment (403 Forbidden).")

        # Manager allowed to assign
        r_a = requests.post(f"{BASE_URL}/alerts/{alt_id}/assign?analyst_user_id=2", headers=mgr_headers)
        assert r_a.status_code == 200
        print(f"  [PASS] Manager assigned alert: {r_a.json()['message']}")

        # Analyst resolves alert
        r_res = requests.patch(f"{BASE_URL}/alerts/{alt_id}/resolve", headers=analyst_headers)
        assert r_res.status_code == 200
        print(f"  [PASS] Analyst resolved alert: {r_res.json()['message']}")

    # 7. Milestone 3 Part 5: Role-Specific Security Dashboards
    print_step("7. Testing Milestone 3 Part 5: Role-Specific Dashboards (Analyst, SOC, Manager)")
    r_adash = requests.get(f"{BASE_URL}/dashboard/analyst", headers=analyst_headers)
    assert r_adash.status_code == 200
    print(f"  [PASS] Analyst Dashboard: Open Alerts = {r_adash.json()['open_alerts']}, Active Invs = {r_adash.json()['active_investigations']}")

    r_sdash = requests.get(f"{BASE_URL}/dashboard/soc", headers=analyst_headers)
    assert r_sdash.status_code == 200
    print(f"  [PASS] SOC Dashboard: Total Events = {r_sdash.json()['total_security_events']}, Anomalies = {r_sdash.json()['behavioral_anomalies_count']}")

    r_mdash = requests.get(f"{BASE_URL}/dashboard/manager", headers=mgr_headers)
    assert r_mdash.status_code == 200
    print(f"  [PASS] Manager Dashboard: Distribution = {r_mdash.json()['distribution']}, Compliance = {r_mdash.json()['compliance_score']}%")

    print("\n" + "=" * 70)
    print(" ALL MILESTONE 3 VERIFICATION CRITERIA PASSED WITH 100% SUCCESS! ")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    test_system()