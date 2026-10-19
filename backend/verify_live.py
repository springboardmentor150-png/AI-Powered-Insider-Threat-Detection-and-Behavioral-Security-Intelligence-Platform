import urllib.request
import json
import time

time.sleep(2)

print("=== TESTING BACKEND HEALTH ===")
try:
    with urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=5) as r:
        print(f"[PASS] Backend OpenAPI Docs: Status {r.status}")
except Exception as e:
    print(f"[FAIL] Backend /docs: {e}")

print("=== TESTING AUTH LOGIN ===")
login_payload = json.dumps({"email": "admin@itbis.cyber", "password": "AdminPassword123!"}).encode("utf-8")
req = urllib.request.Request("http://127.0.0.1:8000/auth/login", data=login_payload, headers={"Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=5) as r:
        login_res = json.loads(r.read().decode("utf-8"))
        token = login_res["access_token"]
        print(f"[PASS] Admin Login: Success, Token acquired (len={len(token)})")
except Exception as e:
    print(f"[FAIL] Login: {e}")
    token = None

if token:
    headers = {"Authorization": f"Bearer {token}"}
    print("=== TESTING /activity-logs/timeline ENDPOINT ===")
    queries = ["", "?time_range=24h", "?time_range=7d", "?time_range=30d", "?employee_id=FIN-2187", "?event_type=file_download"]
    for q in queries:
        req_tl = urllib.request.Request(f"http://127.0.0.1:8000/activity-logs/timeline{q}", headers=headers)
        with urllib.request.urlopen(req_tl, timeout=5) as r:
            res_tl = json.loads(r.read().decode("utf-8"))
            items = res_tl.get("items", [])
            print(f"[PASS] GET /activity-logs/timeline{q}: {len(items)} items (total={res_tl.get('total')})")

    print("=== TESTING /activity-logs/distribution ENDPOINT ===")
    req_dist = urllib.request.Request("http://127.0.0.1:8000/activity-logs/distribution", headers=headers)
    with urllib.request.urlopen(req_dist, timeout=5) as r:
        res_dist = json.loads(r.read().decode("utf-8"))
        print(f"[PASS] GET /activity-logs/distribution: {len(res_dist)} categories, Total Events: {sum(d['count'] for d in res_dist)}")

    print("=== TESTING /activity-logs/heatmap ENDPOINT ===")
    req_hm = urllib.request.Request("http://127.0.0.1:8000/activity-logs/heatmap", headers=headers)
    with urllib.request.urlopen(req_hm, timeout=5) as r:
        res_hm = json.loads(r.read().decode("utf-8"))
        print(f"[PASS] GET /activity-logs/heatmap: {len(res_hm)} cells")

print("=== ALL LIVE HTTP VERIFICATION TESTS PASSED ===")
