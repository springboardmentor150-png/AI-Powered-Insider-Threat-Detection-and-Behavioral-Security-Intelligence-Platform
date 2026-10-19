import urllib.request
import json

BASE = "http://127.0.0.1:8000"

# 1. Login to get token
req = urllib.request.Request(
    f"{BASE}/auth/login",
    data=json.dumps({"email": "admin@itbis.cyber", "password": "AdminPassword123!"}).encode(),
    headers={"Content-Type": "application/json"}
)
token = json.loads(urllib.request.urlopen(req).read().decode())["access_token"]
auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("=== 1. EMPLOYEE BASELINE (CYB-1042) ===")
req1 = urllib.request.Request(f"{BASE}/behavior-analysis/CYB-1042", headers=auth_headers)
b_data = json.loads(urllib.request.urlopen(req1).read().decode())
emp_info = b_data.get("employee", {})
base_info = b_data.get("baseline", {})
print(f"Name: {emp_info.get('name')} | Dept: {emp_info.get('department')} | Role: {emp_info.get('designation')}")
print(f"Normal Hours: {base_info.get('normal_start_hour')}:00 - {base_info.get('normal_end_hour')}:00 UTC")
print(f"Usual Hardware: {base_info.get('usual_devices')}")
print(f"Baseline Status: {base_info.get('status_message')}")

print("\n=== 2. SUBMIT NORMAL LOGIN ===")
normal_event = {
    "employee_id": "CYB-1042",
    "event_type": "login",
    "action": "user_login",
    "timestamp": "2026-10-14T09:30:00Z",
    "device": "MacBook Pro M3 (SEC-D-991)",
    "ip_address": "10.0.1.45",
    "location": "Hyderabad Office",
    "is_test_event": True,
    "details": {"status": "SUCCESS", "mfa": True}
}
req2 = urllib.request.Request(f"{BASE}/activity-logs", data=json.dumps(normal_event).encode(), headers=auth_headers)
r2 = urllib.request.urlopen(req2)
res2 = json.loads(r2.read().decode())
print("Ingestion Status:", r2.status, "| Anomalies Detected:", res2.get("anomalies_detected", 0))

print("\n=== 3. SUBMIT UNUSUAL LOGIN (OFF-HOURS & UNKNOWN DEVICE) ===")
unusual_event = {
    "employee_id": "CYB-1042",
    "event_type": "login",
    "action": "user_login",
    "timestamp": "2026-10-14T03:15:00Z",
    "device": "Foreign-Hacker-Rig-09",
    "ip_address": "185.220.101.5",
    "location": "Unknown Foreign Geo",
    "is_test_event": True,
    "details": {"status": "SUCCESS"}
}
req3 = urllib.request.Request(f"{BASE}/activity-logs", data=json.dumps(unusual_event).encode(), headers=auth_headers)
r3 = urllib.request.urlopen(req3)
res3 = json.loads(r3.read().decode())
print("Ingestion Status:", r3.status, "| Anomalies Detected:", res3.get("anomalies_detected", 0))
for a in res3.get("anomalies", []):
    print(f"  Flagged: {a.get('anomaly_type')} | Severity: {a.get('severity')} | Observed: {a.get('observed_value')}")

print("\n=== 4. COMBINED REPORT (GET /anomalies/CYB-1042) ===")
req4 = urllib.request.Request(f"{BASE}/anomalies/CYB-1042", headers=auth_headers)
rep = json.loads(urllib.request.urlopen(req4).read().decode())
print("Employee:", rep.get("employee_id"), "| Name:", rep.get("employee_name"))
print("Total Flags:", rep.get("total_flags"), "| Rule Anomalies:", rep.get("total_rule_anomalies"), "| ML Anomalies:", rep.get("total_ml_anomalies"))
print("Severity Breakdown:", rep.get("severity_counts"))
for r in rep.get("rule_based_anomalies", []):
    print(f"  [Rule] {r.get('anomaly_type')} | Severity: {r.get('severity')} | Observed: {r.get('observed_value')}")
for m in rep.get("ml_anomalies", []):
    print(f"  [ML] {m.get('anomaly_type')} | Score: {m.get('anomaly_score')} | Date: {m.get('date')}")

print("\n=== 5. ANOMALY SUMMARY (GET /anomalies/summary) ===")
req5 = urllib.request.Request(f"{BASE}/anomalies/summary", headers=auth_headers)
sum_rep = json.loads(urllib.request.urlopen(req5).read().decode())
print("Total Platform Anomalies:", sum_rep.get("total_anomalies"), "| Unique Employees Affected:", sum_rep.get("unique_employees"))
print("Top Employees Ranked by Rule Anomaly Count:")
for te in sum_rep.get("top_employees", []):
    print(f"  - {te.get('employee_id')} ({te.get('employee_name')} - {te.get('department')}): Rule Flags: {te.get('rule_anomalies')}, ML: {te.get('ml_anomalies')}, Highest: {te.get('highest_severity')}")
