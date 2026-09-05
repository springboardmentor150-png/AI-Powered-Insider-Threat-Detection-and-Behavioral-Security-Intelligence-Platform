# backend/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "ITBIS backend is running" in data["status"]

def test_login_and_rbac():
    # 1. Login as Admin
    admin_login = client.post("/api/auth/login", json={
        "email": "admin@itbis.security",
        "password": "Security@123"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Login as Security Analyst
    analyst_login = client.post("/api/auth/login", json={
        "email": "analyst@itbis.security",
        "password": "Security@123"
    })
    assert analyst_login.status_code == 200
    analyst_token = analyst_login.json()["access_token"]
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

    # 3. Test RBAC: Analyst tries to list users (Admin-only endpoint) -> Must return 403
    analyst_forbidden = client.get("/api/auth/users", headers=analyst_headers)
    assert analyst_forbidden.status_code == 403

    # 4. Admin accesses /api/auth/users -> Must return 200
    admin_allowed = client.get("/api/auth/users", headers=admin_headers)
    assert admin_allowed.status_code == 200
    assert len(admin_allowed.json()) >= 1

def test_employee_crud():
    # Login as Admin
    login_resp = client.post("/api/auth/login", json={
        "email": "admin@itbis.security",
        "password": "Security@123"
    })
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Create new employee
    emp_payload = {
        "employee_id": "EMP9999",
        "name": "Test Subject Agent",
        "department": "Security Research",
        "designation": "Penetration Tester",
        "device_info": "Kali Linux 2026.1",
        "access_privileges": "TEST_LAB_ADMIN"
    }
    create_resp = client.post("/api/employees", json=emp_payload, headers=headers)
    assert create_resp.status_code in [201, 400] # 201 if first time, 400 if already exists

    # Get employee
    get_resp = client.get("/api/employees/EMP9999", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Test Subject Agent"

def test_log_ingestion_and_ai_analysis():
    # Ingest suspicious log
    log_payload = {
        "employee_id": "EMP9999",
        "event_type": "usb_connect",
        "details": {"device": "Kingston_64G", "action": "WRITE_OPERATION"}
    }
    ingest_resp = client.post("/api/logs/ingest", json=log_payload)
    assert ingest_resp.status_code == 201

    # Login as Analyst
    login_resp = client.post("/api/auth/login", json={
        "email": "analyst@itbis.security",
        "password": "Security@123"
    })
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Trigger AI analysis
    ai_resp = client.post("/api/ai/analyze/EMP9999", headers=headers)
    assert ai_resp.status_code == 200
    data = ai_resp.json()
    assert "overall_risk_score" in data
    assert "threat_level" in data
    assert "mitre_mapping" in data

def test_threat_simulation():
    # Login as SOC Engineer
    login_resp = client.post("/api/auth/login", json={
        "email": "soc@itbis.security",
        "password": "Security@123"
    })
    headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    sim_payload = {
        "scenario": "mass_exfiltration",
        "employee_id": "EMP1001"
    }
    sim_resp = client.post("/api/simulation/run", json=sim_payload, headers=headers)
    assert sim_resp.status_code == 200
    assert sim_resp.json()["status"] == "simulation_completed"
