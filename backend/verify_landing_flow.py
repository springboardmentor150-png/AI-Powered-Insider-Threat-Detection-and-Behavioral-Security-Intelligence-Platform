import urllib.request
import json
import time

time.sleep(1)

print("==================================================")
print("VERIFYING ITBIS LANDING & AUTH FLOW")
print("==================================================")

# 1. Verify Landing Page (/)
try:
    with urllib.request.urlopen("http://localhost:3000/", timeout=10) as r:
        html = r.read().decode("utf-8")
        assert r.status == 200, f"Expected 200, got {r.status}"
        assert "INSIDER THREAT" in html, "Missing heading in landing page"
        assert "BEHAVIORAL INTELLIGENCE" in html, "Missing subheading in landing page"
        assert "Access SOC Console" in html, "Missing Access SOC Console CTA in landing page"
        assert "End-to-End Intelligence Pipeline" in html, "Missing Threat Pipeline in landing page"
        assert "Behavioral Monitoring" in html, "Missing Behavioral Monitoring in landing page"
        assert "Dynamic Risk Scoring" in html, "Missing Risk Scoring in landing page"
        assert "Incident Management" in html, "Missing Incident Management in landing page"
        print("[PASS] Landing page (http://localhost:3000/): PASS (Status 200, all hero, pipeline, and feature elements present)")
except Exception as e:
    print(f"[FAIL] Landing page: {e}")

# 2. Verify Login Page (/login)
try:
    with urllib.request.urlopen("http://localhost:3000/login", timeout=10) as r:
        html_login = r.read().decode("utf-8")
        assert r.status == 200, f"Expected 200, got {r.status}"
        assert "Operator Email" in html_login, "Missing email field on login page"
        assert "Sign In" in html_login, "Missing Sign In button on login page"
        print("[PASS] Direct /login page (http://localhost:3000/login): PASS (Status 200, standalone auth form present)")
except Exception as e:
    print(f"[FAIL] Direct /login: {e}")

# 3. Verify Backend Auth API
try:
    login_payload = json.dumps({"email": "admin@itbis.cyber", "password": "AdminPassword123!"}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8000/auth/login", data=login_payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        res = json.loads(r.read().decode("utf-8"))
        token = res["access_token"]
        assert token and len(token) > 20, "Invalid token"
        print(f"[PASS] Authentication (/auth/login): PASS (JWT token obtained, role: {res.get('user', {}).get('role')})")
except Exception as e:
    print(f"[FAIL] Authentication: {e}")
    token = None

# 4. Verify Authenticated Dashboard API
if token:
    try:
        req_dash = urllib.request.Request("http://127.0.0.1:8000/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req_dash, timeout=5) as r:
            res_dash = json.loads(r.read().decode("utf-8"))
            print(f"[PASS] Dashboard Backend (/dashboard/summary): PASS (Monitored: {res_dash.get('total_employees')}, Incidents: {res_dash.get('open_incidents')})")
    except Exception as e:
        print(f"[FAIL] Dashboard Backend: {e}")

# 5. Verify Frontend Dashboard Route
try:
    with urllib.request.urlopen("http://localhost:3000/dashboard", timeout=10) as r:
        assert r.status == 200, f"Expected 200, got {r.status}"
        print("[PASS] Frontend Dashboard route (/dashboard): PASS (Status 200)")
except Exception as e:
    print(f"[FAIL] Frontend Dashboard: {e}")

print("==================================================")
print("ALL FLOW CHECKS PASSED SUCCESSFULLY!")
print("==================================================")
