"""
ITBIS Milestone 4 - Automated API Tests Across The Whole Platform
(Matches Milestone 4 Day 35-36 Student Handout)
"""

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine, Base
from app.models import User
from app.auth import hash_password

client = TestClient(app)


def ensure_test_users():
    """Ensure standard test users exist with hashed passwords."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users_config = [
            ("admin@itbis.local", "admin123", "admin"),
            ("soc1@company.com", "testpass123", "soc_engineer"),
            ("analyst@itbis.local", "analyst123", "security_analyst"),
            ("manager@itbis.local", "manager123", "security_manager"),
        ]
        for email, pwd, role in users_config:
            u = db.query(User).filter(User.email == email).first()
            if not u:
                db.add(User(email=email, password_hash=hash_password(pwd), role=role))
            else:
                u.password_hash = hash_password(pwd)
                u.role = role
        db.commit()
    finally:
        db.close()


def get_auth_header(email: str, password: str) -> dict:
    """Reusable authentication header helper."""
    res = client.post(f"/auth/login?email={email}&password={password}")
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_end_to_end_flow():
    """Test the complete 3-milestone handoff: Ingestion -> Scoring -> Dashboards."""
    ensure_test_users()
    headers = get_auth_header("soc1@company.com", "testpass123")

    # 1. Ingest a log
    res = client.post(
        "/logs/ingest",
        json={
            "employee_id": "EMP001",
            "event_type": "login",
            "details": {"device": "laptop-01"},
        },
        headers=headers,
    )
    assert res.status_code == 200, f"Log ingestion failed: {res.text}"
    assert res.json().get("status") == "success"

    # 2. Check risk score responds
    res = client.get("/risk-score/EMP001", headers=headers)
    assert res.status_code == 200, f"Risk scoring failed: {res.text}"
    assert "risk_level" in res.json()
    assert "risk_score" in res.json()

    # 3. Check dashboard loads
    res = client.get("/dashboard/soc", headers=headers)
    assert res.status_code == 200, f"SOC dashboard failed: {res.text}"
    assert "alerts_by_severity" in res.json()


def test_all_four_dashboards():
    """Verify all 4 role dashboards: Analyst, SOC, Manager, and Admin."""
    ensure_test_users()
    admin_headers = get_auth_header("admin@itbis.local", "admin123")
    analyst_headers = get_auth_header("analyst@itbis.local", "analyst123")
    manager_headers = get_auth_header("manager@itbis.local", "manager123")
    soc_headers = get_auth_header("soc1@company.com", "testpass123")

    # 1. Analyst Dashboard
    res = client.get("/dashboard/analyst", headers=analyst_headers)
    assert res.status_code == 200

    # 2. SOC Dashboard
    res = client.get("/dashboard/soc", headers=soc_headers)
    assert res.status_code == 200

    # 3. Security Manager Dashboard
    res = client.get("/dashboard/manager", headers=manager_headers)
    assert res.status_code == 200

    # 4. Admin Dashboard (Milestone 4 Part 1)
    res = client.get("/dashboard/admin", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "user_count" in data
    assert "employee_count" in data
    assert "users_by_role" in data


def test_security_rbac_checklist():
    """Verify security checklist: endpoints require tokens and reject unauthorized roles."""
    ensure_test_users()
    # Unauthenticated call rejected
    res_no_auth = client.get("/dashboard/admin")
    assert res_no_auth.status_code == 401

    # Unauthorized role rejected
    analyst_headers = get_auth_header("analyst@itbis.local", "analyst123")
    res_wrong_role = client.get("/dashboard/admin", headers=analyst_headers)
    assert res_wrong_role.status_code == 403

    # Admin access granted
    admin_headers = get_auth_header("admin@itbis.local", "admin123")
    res_admin = client.get("/admin/users", headers=admin_headers)
    assert res_admin.status_code == 200
    assert "users" in res_admin.json()


if __name__ == "__main__":
    test_end_to_end_flow()
    test_all_four_dashboards()
    test_security_rbac_checklist()
    print("ALL TESTS IN test_full_pipeline.py PASSED (100% SUCCESS)!")
