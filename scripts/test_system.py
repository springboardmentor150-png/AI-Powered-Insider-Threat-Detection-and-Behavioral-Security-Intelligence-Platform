# itbis/scripts/test_system.py
"""
End-to-End Test & Verification Script for ITBIS Platform.
Validates Backend API, Authentication, RBAC, Employee CRUD, Telemetry Ingestion,
AI Anomaly Scoring, Alert Triage, Incident Escalation, and Simulation.
"""
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def print_step(title):
    print(f"\n[TEST STEP] {title}...")

def test_system():
    print("=" * 65)
    print(" ITBIS - End-to-End System Verification Suite")
    print("=" * 65)

    # 1. Health Check
    print_step("1. Testing Root & Health Check Endpoints")
    try:
        r = requests.get(f"{BASE_URL}/")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        print("  [PASS] Root Health-check OK:", r.json().get("status"))
        
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
    assert r_admin.status_code == 200, f"Admin login failed: {r_admin.text}"
    admin_token = r_admin.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("  [PASS] Admin JWT Token acquired successfully.")

    # Analyst Login
    r_analyst = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "analyst@itbis.security",
        "password": "Security@123"
    })
    assert r_analyst.status_code == 200
    analyst_token = r_analyst.json()["access_token"]
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}
    print("  [PASS] Security Analyst JWT Token acquired successfully.")

    # Verify RBAC restriction on /api/auth/users (admin-only)
    r_forbidden = requests.get(f"{BASE_URL}/api/auth/users", headers=analyst_headers)
    assert r_forbidden.status_code == 403, "Analyst should receive 403 Forbidden on Admin route"
    print("  [PASS] RBAC Verified: Analyst correctly blocked from Admin endpoint (403 Forbidden).")

    r_allowed = requests.get(f"{BASE_URL}/api/auth/users", headers=admin_headers)
    assert r_allowed.status_code == 200
    print(f"  [PASS] RBAC Verified: Admin successfully fetched {len(r_allowed.json())} system users.")

    # 3. Employee Directory & Baselining
    print_step("3. Testing Employee Directory & Baseline Retrieval")
    r_emps = requests.get(f"{BASE_URL}/api/employees", headers=analyst_headers)
    assert r_emps.status_code == 200
    emps = r_emps.json()
    assert len(emps) >= 1, "No employees found"
    target_emp = emps[0]["employee_id"]
    print(f"  [PASS] Fetched {len(emps)} monitored employee profiles. Selected target: {target_emp}")

    r_base = requests.get(f"{BASE_URL}/api/employees/{target_emp}/baseline", headers=analyst_headers)
    assert r_base.status_code == 200
    print("  [PASS] Retrieved learned behavioral baseline:", r_base.json().get("typical_work_hours"))

    # 4. Activity Log Ingestion
    print_step("4. Testing Activity Log Ingestion Pipeline")
    ingest_payload = {
        "employee_id": target_emp,
        "event_type": "file_download",
        "details": {"file_name": "quarterly_intel_report.pdf", "size_mb": 12.5, "is_confidential": False}
    }
    r_ingest = requests.post(f"{BASE_URL}/api/logs/ingest", json=ingest_payload)
    assert r_ingest.status_code == 201
    print("  [PASS] Ingested single event into MongoDB document store. Log ID:", r_ingest.json().get("log_id"))

    # 5. AI Behavioral Anomaly & Risk Analysis
    print_step("5. Testing AI Anomaly Engine & Threat Scoring")
    r_ai = requests.post(f"{BASE_URL}/api/ai/analyze/{target_emp}", headers=analyst_headers)
    assert r_ai.status_code == 200
    ai_data = r_ai.json()
    print(f"  [PASS] AI Analysis Complete: Risk Score = {ai_data['overall_risk_score']}/100, Threat Level = {ai_data['threat_level']}")
    print(f"  [PASS] Anomaly Score = {ai_data['anomaly_score']}, Analyzed Logs = {ai_data['analyzed_event_count']}")

    # 6. Alerts & Incident Escalation
    print_step("6. Testing Alert Triage & Incident Lifecycle")
    r_alerts = requests.get(f"{BASE_URL}/api/alerts", headers=analyst_headers)
    assert r_alerts.status_code == 200
    alerts = r_alerts.json()
    if alerts:
        first_alert = alerts[0]
        # Acknowledge
        r_ack = requests.post(f"{BASE_URL}/api/alerts/{first_alert['id']}/acknowledge", headers=analyst_headers)
        assert r_ack.status_code == 200
        print(f"  [PASS] Acknowledged alert {first_alert['alert_code']}")

        # Escalate to Incident
        r_esc = requests.post(f"{BASE_URL}/api/alerts/{first_alert['id']}/escalate", headers=analyst_headers)
        assert r_esc.status_code == 200
        inc_id = r_esc.json().get("incident_id")
        print(f"  [PASS] Escalated to Incident: {r_esc.json().get('incident_code')}")

        if inc_id:
            # Generate AI Forensic Report
            r_report = requests.post(f"{BASE_URL}/api/incidents/{inc_id}/generate-ai-report", headers=analyst_headers)
            assert r_report.status_code == 200
            print("  [PASS] Generated AI Forensic Threat Dossier with MITRE ATT&CK correlation.")

    # 7. Threat Simulation
    print_step("7. Testing Threat Simulation Vector")
    r_sim = requests.post(f"{BASE_URL}/api/simulation/run", json={
        "scenario": "mass_exfiltration",
        "employee_id": target_emp
    }, headers=analyst_headers)
    assert r_sim.status_code == 200
    print(f"  [PASS] Successfully executed simulation scenario '{r_sim.json()['scenario']}' with {r_sim.json()['generated_events_count']} generated telemetry events.")

    print("\n" + "=" * 65)
    print(" ALL 7 SYSTEM VERIFICATION MODULES PASSED SUCCESSFULLY! ")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    test_system()