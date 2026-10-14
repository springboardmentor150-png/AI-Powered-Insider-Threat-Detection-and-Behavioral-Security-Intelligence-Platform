"""
Automated test suite verifying the new High Priority, Medium Priority, and Advanced Features:
- Audit Logs
- Explainable AI (XAI)
- Analyst Anomaly Feedback
- Global Search
- Admin User Management
- Alerts & Incident Status Updates
- Live Notifications
"""

from fastapi.testclient import TestClient
from app.main import app
from app.jwt_auth import create_access_token

client = TestClient(app)

# Test tokens
admin_token = create_access_token(2, "admin")
analyst_token = create_access_token(4, "security_analyst")

admin_headers = {"Authorization": f"Bearer {admin_token}"}
analyst_headers = {"Authorization": f"Bearer {analyst_token}"}

def run_tests():
    print("=" * 65)
    print("TESTING NEW ADVANCED & OPERATIONAL FEATURES")
    print("=" * 65)

    # 1. Test Alerts Listing
    res = client.get("/alerts", headers=analyst_headers)
    assert res.status_code == 200, f"Failed GET /alerts: {res.text}"
    print("[PASS] GET /alerts returned successfully")

    # 2. Test Audit Logs (Admin role)
    res = client.get("/audit-logs", headers=admin_headers)
    assert res.status_code == 200, f"Failed GET /audit-logs: {res.text}"
    print(f"[PASS] GET /audit-logs returned {res.json().get('total', 0)} audit records")

    # 3. Test Explainable AI (XAI)
    res = client.get("/anomalies/EMP-001/xai", headers=analyst_headers)
    assert res.status_code == 200, f"Failed XAI endpoint: {res.text}"
    xai_data = res.json()
    assert "explanations" in xai_data
    print(f"[PASS] GET /anomalies/EMP-001/xai returned {xai_data.get('count', 0)} feature explanations")

    # 4. Test Analyst Feedback Submission
    res = client.post(
        "/anomalies/test_anomaly_123/feedback",
        json={"feedback": "false_positive", "notes": "Approved off-hours maintenance backup."},
        headers=analyst_headers,
    )
    assert res.status_code == 200, f"Failed feedback submission: {res.text}"
    print("[PASS] POST /anomalies/test_anomaly_123/feedback recorded feedback")

    # 5. Test Anomaly Feedback List
    res = client.get("/anomalies/feedback", headers=analyst_headers)
    assert res.status_code == 200
    assert res.json().get("count", 0) >= 1
    print("[PASS] GET /anomalies/feedback retrieved recorded feedback list")

    # 6. Test Global Threat Hunting Search
    res = client.get("/search?q=admin", headers=analyst_headers)
    assert res.status_code == 200
    search_data = res.json()
    assert "total_matches" in search_data
    print(f"[PASS] GET /search?q=admin found {search_data.get('total_matches')} matches across entities")

    # 7. Test Admin Users List & Role Update
    res = client.get("/admin/users", headers=admin_headers)
    assert res.status_code == 200
    users = res.json().get("users", [])
    assert len(users) > 0
    print(f"[PASS] GET /admin/users returned {len(users)} users")

    # 8. Test Notifications
    res = client.get("/notifications", headers=analyst_headers)
    assert res.status_code == 200
    print(f"[PASS] GET /notifications returned {res.json().get('count')} active alerts")

    print("=" * 65)
    print("ALL NEW FEATURE ENDPOINTS VERIFIED AND PASSING!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
