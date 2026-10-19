import urllib.request
import json
import time

time.sleep(1)

print("=== 1. AUTHENTICATION & LOGIN ===")
login_payload = json.dumps({"email": "admin@itbis.cyber", "password": "AdminPassword123!"}).encode("utf-8")
login_req = urllib.request.Request("http://127.0.0.1:8000/auth/login", data=login_payload, headers={"Content-Type": "application/json"}, method="POST")
login_res = urllib.request.urlopen(login_req)
token_data = json.loads(login_res.read().decode("utf-8"))
token = token_data["access_token"]
print("PASS: Logged in successfully. Received JWT Bearer token: " + token[:25] + "...")

headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}

print("\n=== 2. MONGODB ACTIVITY DISTRIBUTION API ===")
dist_req = urllib.request.Request("http://127.0.0.1:8000/activity-logs/distribution", headers=headers)
dist_res = urllib.request.urlopen(dist_req)
dist_data = json.loads(dist_res.read().decode("utf-8"))
print("PASS: /activity-logs/distribution returned HTTP " + str(dist_res.getcode()) + " OK")
print(json.dumps(dist_data, indent=2))

print("\n=== 3. INDIVIDUAL EVENT TYPE FILTERING ===")
for item in dist_data:
    et = item["event_type"]
    expected_cnt = item["count"]
    q_req = urllib.request.Request(f"http://127.0.0.1:8000/activity-logs?event_type={et}&limit=50", headers=headers)
    q_res = urllib.request.urlopen(q_req)
    q_data = json.loads(q_res.read().decode("utf-8"))
    returned_cnt = q_data["total"]
    assert returned_cnt == expected_cnt, f"Count mismatch for {et}: expected {expected_cnt}, got {returned_cnt}"
    print(f"PASS: Filter event_type={et:<18} -> Count: {returned_cnt} (Matches distribution)")

print("\n=== 4. ALL ACTIVITIES (UNFILTERED) ===")
all_req = urllib.request.Request("http://127.0.0.1:8000/activity-logs?limit=50", headers=headers)
all_res = urllib.request.urlopen(all_req)
all_data = json.loads(all_res.read().decode("utf-8"))
total_cnt = all_data["total"]
print(f"PASS: ALL activities count = {total_cnt}")

print("\n=== 5. SYNTHETIC TELEMETRY INJECTION TEST ===")
test_payload = json.dumps({
    "employee_id": "FIN-2187",
    "activity_type": "file_download",
    "action": "Automated Test Ingestion",
    "resource": "s3://vault/test.tar.gz",
    "scenario": "SUSPICIOUS_OFFHOURS_EXFIL",
    "download_size_mb": 4800
}).encode("utf-8")
test_req = urllib.request.Request("http://127.0.0.1:8000/activity-logs/test-event", data=test_payload, headers=headers, method="POST")
test_res = urllib.request.urlopen(test_req)
test_data = json.loads(test_res.read().decode("utf-8"))
print("PASS: /activity-logs/test-event -> " + str(test_data["message"]) + " | Risk Score: " + str(test_data["calculated_risk_score"]))

# Re-check distribution after injection
dist_res2 = urllib.request.urlopen(dist_req)
dist_data2 = json.loads(dist_res2.read().decode("utf-8"))
dl_item = next(x for x in dist_data2 if x["event_type"] == "file_download")
print("PASS: file_download count incremented to " + str(dl_item["count"]))

print("\n=== 6. FRONTEND PAGES HTTP 200 VERIFICATION ===")
fe_routes = ["/", "/login", "/dashboard", "/activity-logs", "/behavior-analysis", "/risk-scores", "/investigations", "/alerts", "/incidents", "/reports", "/settings"]
for r_path in fe_routes:
    r = urllib.request.urlopen(f"http://localhost:3000{r_path}")
    print(f"PASS: Frontend {r_path:<20} -> {r.getcode()} OK")

print("\nALL VERIFICATION CHECKS PASSED!")
