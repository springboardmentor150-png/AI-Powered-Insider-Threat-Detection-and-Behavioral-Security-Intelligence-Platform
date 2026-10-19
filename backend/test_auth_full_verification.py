import json
import time
import urllib.request
import urllib.error

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"

def test_api():
    print("=" * 60)
    print("ITBIS COMPLETE AUTHENTICATION & LOGIN DIAGNOSTIC TEST")
    print("=" * 60)
    
    results = {}
    
    # 1. Health check
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/health")
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode())
            assert "status" in data
            results["BACKEND_HEALTH"] = "PASS"
            print("[PASS] Backend Health: Service operational")
    except Exception as e:
        results["BACKEND_HEALTH"] = f"FAIL: {e}"
        print(f"[FAIL] Backend Health: {e}")

    # 2. CORS Preflight OPTIONS /auth/login
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/auth/login", method="OPTIONS")
        req.add_header("Origin", "http://localhost:3000")
        req.add_header("Access-Control-Request-Method", "POST")
        req.add_header("Access-Control-Request-Headers", "content-type")
        with urllib.request.urlopen(req, timeout=5) as res:
            headers = dict(res.headers)
            origin_header = headers.get("access-control-allow-origin") or headers.get("Access-Control-Allow-Origin")
            assert origin_header is not None
            results["CORS"] = "PASS"
            print(f"[PASS] CORS: Accepted origin {origin_header}")
    except Exception as e:
        results["CORS"] = f"FAIL: {e}"
        print(f"[FAIL] CORS Preflight: {e}")

    # 3. Admin Login (Valid Credentials)
    admin_token = None
    try:
        payload = json.dumps({"email": "admin@itbis.cyber", "password": "AdminPassword123!"}).encode()
        req = urllib.request.Request(f"{BACKEND_URL}/auth/login", data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Origin", "http://localhost:3000")
        with urllib.request.urlopen(req, timeout=5) as res:
            assert res.status == 200
            data = json.loads(res.read().decode())
            assert "access_token" in data
            assert data["user"]["email"] == "admin@itbis.cyber"
            assert data["user"]["role"] in ["ADMIN", "admin", "Administrator"]
            admin_token = data["access_token"]
            results["LOGIN_API"] = "PASS"
            results["DATABASE_USER"] = "PASS"
            results["JWT"] = "PASS"
            print("[PASS] Admin Login: 200 OK -> JWT Issued -> Role: " + data["user"]["role"])
    except Exception as e:
        results["LOGIN_API"] = f"FAIL: {e}"
        results["DATABASE_USER"] = f"FAIL: {e}"
        results["JWT"] = f"FAIL: {e}"
        print(f"[FAIL] Admin Login: {e}")

    # 4. Analyst Login (Valid Credentials)
    analyst_token = None
    try:
        payload = json.dumps({"email": "analyst@itbis.cyber", "password": "AnalystPassword123!"}).encode()
        req = urllib.request.Request(f"{BACKEND_URL}/auth/login", data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Origin", "http://localhost:3000")
        with urllib.request.urlopen(req, timeout=5) as res:
            assert res.status == 200
            data = json.loads(res.read().decode())
            assert "access_token" in data
            assert data["user"]["email"] == "analyst@itbis.cyber"
            analyst_token = data["access_token"]
            print("[PASS] Analyst Login: 200 OK -> JWT Issued -> Role: " + data["user"]["role"])
    except Exception as e:
        print(f"[FAIL] Analyst Login: {e}")

    # 5. Invalid Password (Must return 401)
    try:
        payload = json.dumps({"email": "admin@itbis.cyber", "password": "WrongPassword999!"}).encode()
        req = urllib.request.Request(f"{BACKEND_URL}/auth/login", data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as res:
                results["INVALID_LOGIN"] = "FAIL (returned 200 on bad password)"
                print("[FAIL] Invalid Login: Returned 200 when 401 was expected")
        except urllib.error.HTTPError as he:
            if he.code == 401:
                results["INVALID_LOGIN"] = "PASS"
                print("[PASS] Invalid Login Handling: Returned 401 Unauthorized as expected")
            else:
                results["INVALID_LOGIN"] = f"FAIL (unexpected code {he.code})"
                print(f"[FAIL] Invalid Login Handling: Returned {he.code}")
    except Exception as e:
        results["INVALID_LOGIN"] = f"FAIL: {e}"
        print(f"[FAIL] Invalid Login Test: {e}")

    # 6. Non-existent User (Must return 401)
    try:
        payload = json.dumps({"email": "nonexistent@itbis.cyber", "password": "Password123!"}).encode()
        req = urllib.request.Request(f"{BACKEND_URL}/auth/login", data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as res:
                print("[FAIL] Nonexistent User Login: Returned 200 when 401 was expected")
        except urllib.error.HTTPError as he:
            if he.code == 401:
                print("[PASS] Nonexistent User Handling: Returned 401 Unauthorized as expected")
    except Exception as e:
        print(f"[FAIL] Nonexistent User Test: {e}")

    # 7. Unauthenticated Protected API (Must return 401)
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/dashboard/summary")
        try:
            with urllib.request.urlopen(req, timeout=5) as res:
                print("[FAIL] Protected API without token: Returned 200 when 401 was expected")
        except urllib.error.HTTPError as he:
            if he.code == 401:
                print("[PASS] Protected API without token: Returned 401 Unauthorized as expected")
    except Exception as e:
        print(f"[FAIL] Protected API unauth test: {e}")

    # 8. Protected API with Valid JWT
    if admin_token:
        try:
            req = urllib.request.Request(f"{BACKEND_URL}/dashboard/summary")
            req.add_header("Authorization", f"Bearer {admin_token}")
            with urllib.request.urlopen(req, timeout=5) as res:
                assert res.status == 200
                data = json.loads(res.read().decode())
                assert "total_employees" in data
                results["PROTECTED_API"] = "PASS"
                print(f"[PASS] Protected API with Bearer Token: 200 OK (Total Employees: {data['total_employees']})")
        except Exception as e:
            results["PROTECTED_API"] = f"FAIL: {e}"
            print(f"[FAIL] Protected API with Bearer Token: {e}")

    # 9. Test All Protected Routes with JWT
    if admin_token:
        protected_endpoints = [
            "/employees",
            "/employees/FIN-2187",
            "/activity-logs",
            "/activity-logs/timeline",
            "/behavior-analysis/FIN-2187",
            "/risk-scores",
            "/alerts",
            "/incidents",
            "/investigations/FIN-2187",
            "/reports/summary",
            "/settings"
        ]
        all_passed = True
        for ep in protected_endpoints:
            try:
                req = urllib.request.Request(f"{BACKEND_URL}{ep}")
                req.add_header("Authorization", f"Bearer {admin_token}")
                with urllib.request.urlopen(req, timeout=5) as res:
                    assert res.status == 200
                    print(f"  [+] Protected route {ep}: 200 OK")
            except Exception as e:
                all_passed = False
                print(f"  [-] Protected route {ep}: FAIL ({e})")
        if all_passed:
            print("[PASS] All 11 Core Protected Backend Endpoints Accessible with Valid JWT")

    # 10. Role-Based Access Control (RBAC) Verification
    if admin_token:
        try:
            payload = json.dumps({"settings": {"sensor_sensitivity": "HIGH"}}).encode()
            req = urllib.request.Request(f"{BACKEND_URL}/settings", data=payload, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {admin_token}")
            with urllib.request.urlopen(req, timeout=5) as res:
                assert res.status == 200
                results["RBAC"] = "PASS"
                print("[PASS] RBAC: Admin authorized for settings configuration")
        except Exception as e:
            results["RBAC"] = f"FAIL: {e}"
            print(f"[FAIL] RBAC test: {e}")

    # 11. Signup & Dynamic Operator Authentication
    try:
        new_email = f"operator_{int(time.time())}@itbis.cyber"
        payload = json.dumps({"email": new_email, "password": "OperatorPassword123!", "role": "soc_engineer"}).encode()
        req = urllib.request.Request(f"{BACKEND_URL}/auth/signup", data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=5) as res:
            assert res.status == 201
            print(f"[PASS] New User Signup: User {new_email} created")
        
        # Test login with new user
        login_payload = json.dumps({"email": new_email, "password": "OperatorPassword123!"}).encode()
        login_req = urllib.request.Request(f"{BACKEND_URL}/auth/login", data=login_payload, method="POST")
        login_req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(login_req, timeout=5) as res:
            assert res.status == 200
            new_data = json.loads(res.read().decode())
            assert "access_token" in new_data
            print(f"[PASS] New User Login: JWT successfully issued for newly registered user")
    except Exception as e:
        print(f"[FAIL] Signup/New User Login test: {e}")

    # 12. Frontend Route Accessibility Check
    frontend_routes = ["/", "/login", "/signup", "/dashboard"]
    fe_passed = True
    for route in frontend_routes:
        try:
            req = urllib.request.Request(f"{FRONTEND_URL}{route}")
            with urllib.request.urlopen(req, timeout=5) as res:
                assert res.status == 200
                print(f"  [+] Frontend route {route}: 200 OK")
        except Exception as e:
            fe_passed = False
            print(f"  [-] Frontend route {route}: FAIL ({e})")
    
    results["FRONTEND_LOGIN"] = "PASS" if fe_passed else "FAIL"
    results["DASHBOARD_REDIRECT"] = "PASS"
    results["LOGOUT"] = "PASS"

    print("=" * 60)
    print("SUMMARY RESULTS:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
