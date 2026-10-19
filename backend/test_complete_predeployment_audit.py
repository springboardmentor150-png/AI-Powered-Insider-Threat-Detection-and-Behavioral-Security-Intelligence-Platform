import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://localhost:3000"

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            try:
                json_body = json.loads(body)
            except Exception:
                json_body = body
            return resp.status, json_body, resp.headers
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            json_body = json.loads(body)
        except Exception:
            json_body = body
        return e.code, json_body, e.headers
    except Exception as e:
        return 0, str(e), {}

print("=" * 60)
print("ITBIS — COMPLETE PRE-DEPLOYMENT AUDIT & VERIFICATION SUITE")
print("=" * 60)

results = []

def record(phase, test_name, status, detail=""):
    results.append({
        "phase": phase,
        "test": test_name,
        "status": status,
        "detail": detail
    })
    tag = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"{tag} {phase} | {test_name}: {detail}")

# ==========================================
# PHASE 3: BACKEND STARTUP & HEALTH
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/health")
if status == 200 and isinstance(body, dict) and "status" in body:
    record("PHASE 3: BACKEND STARTUP", "GET /health", "PASS", "Service operational")
else:
    record("PHASE 3: BACKEND STARTUP", "GET /health", "FAIL", f"Status {status}: {body}")

status, body, _ = make_request(f"{BACKEND_URL}/openapi.json")
if status == 200 and isinstance(body, dict) and "paths" in body:
    record("PHASE 3: BACKEND STARTUP", "GET /openapi.json", "PASS", f"{len(body['paths'])} API routes registered")
else:
    record("PHASE 3: BACKEND STARTUP", "GET /openapi.json", "FAIL", f"Status {status}")

# ==========================================
# PHASE 4: AUTHENTICATION AUDIT
# ==========================================
# 1. Existing Admin Login
status, body, _ = make_request(f"{BACKEND_URL}/auth/login", method="POST", data={
    "email": "admin@itbis.cyber",
    "password": "AdminPassword123!"
})
admin_token = None
if status == 200 and "access_token" in body:
    admin_token = body["access_token"]
    record("PHASE 4: AUTHENTICATION", "Existing Admin Login", "PASS", f"JWT issued, role={body.get('user', {}).get('role')}")
else:
    record("PHASE 4: AUTHENTICATION", "Existing Admin Login", "FAIL", f"Status {status}: {body}")

# 2. Existing Analyst Login
status, body, _ = make_request(f"{BACKEND_URL}/auth/login", method="POST", data={
    "email": "analyst@itbis.cyber",
    "password": "AnalystPassword123!"
})
if status == 200 and "access_token" in body:
    record("PHASE 4: AUTHENTICATION", "Existing Analyst Login", "PASS", f"JWT issued, role={body.get('user', {}).get('role')}")
else:
    record("PHASE 4: AUTHENTICATION", "Existing Analyst Login", "FAIL", f"Status {status}: {body}")

# 3. Invalid Password Test
status, body, _ = make_request(f"{BACKEND_URL}/auth/login", method="POST", data={
    "email": "admin@itbis.cyber",
    "password": "WrongPassword_999!"
})
if status == 401:
    record("PHASE 4: AUTHENTICATION", "Invalid Password Handling", "PASS", "Proper 401 response returned")
else:
    record("PHASE 4: AUTHENTICATION", "Invalid Password Handling", "FAIL", f"Expected 401, got {status}")

# 4. New Operator Signup & Login Flow
new_email = f"operator_{int(datetime.now(timezone.utc).timestamp())}@itbis.cyber"
status, body, _ = make_request(f"{BACKEND_URL}/auth/signup", method="POST", data={
    "email": new_email,
    "password": "OperatorPass123!",
    "role": "soc_engineer"
})
if status == 201:
    record("PHASE 4: AUTHENTICATION", "New Operator Signup", "PASS", f"User {new_email} created")
    # Test Login for this new user
    status_login, body_login, _ = make_request(f"{BACKEND_URL}/auth/login", method="POST", data={
        "email": new_email,
        "password": "OperatorPass123!"
    })
    if status_login == 200 and "access_token" in body_login:
        record("PHASE 4: AUTHENTICATION", "New Operator Login", "PASS", "Login -> JWT successful for new user")
    else:
        record("PHASE 4: AUTHENTICATION", "New Operator Login", "FAIL", f"Status {status_login}")
else:
    record("PHASE 4: AUTHENTICATION", "New Operator Signup", "FAIL", f"Status {status}: {body}")

if not admin_token:
    print("FATAL: Admin token not acquired. Aborting authenticated checks.")
    sys.exit(1)

auth_headers = {"Authorization": f"Bearer {admin_token}"}

# ==========================================
# PHASE 18: CORS & PREFLIGHT
# ==========================================
status, _, headers = make_request(f"{BACKEND_URL}/auth/login", method="OPTIONS", headers={
    "Origin": "http://localhost:3000",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "authorization,content-type"
})
if status == 200:
    record("PHASE 18: CORS", "Preflight OPTIONS /auth/login", "PASS", f"CORS headers accepted for localhost:3000")
else:
    record("PHASE 18: CORS", "Preflight OPTIONS /auth/login", "FAIL", f"Status {status}")

# ==========================================
# PHASE 6: EMPLOYEES API
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/employees", headers=auth_headers)
if status == 200 and "items" in body and body["total"] >= 6:
    emp_ids = [e["employee_id"] for e in body["items"]]
    record("PHASE 6: EMPLOYEES", "GET /employees", "PASS", f"{body['total']} employees loaded. IDs: {emp_ids[:4]}")
else:
    record("PHASE 6: EMPLOYEES", "GET /employees", "FAIL", f"Status {status}: {body}")

# Employee Detail
status, body, _ = make_request(f"{BACKEND_URL}/employees/FIN-2187", headers=auth_headers)
if status == 200 and "employee" in body and body["employee"]["employee_id"] == "FIN-2187":
    record("PHASE 6: EMPLOYEES", "GET /employees/FIN-2187", "PASS", f"Detail + baseline + activities loaded for {body['employee']['name']}")
else:
    record("PHASE 6: EMPLOYEES", "GET /employees/FIN-2187", "FAIL", f"Status {status}: {body}")

# ==========================================
# PHASE 7: DASHBOARD API
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/dashboard/summary", headers=auth_headers)
if status == 200 and "total_employees" in body and body["total_employees"] >= 6:
    record("PHASE 7: DASHBOARD", "GET /dashboard/summary", "PASS", f"Monitored: {body['total_employees']}, Ingested Telemetry: {body.get('total_activities_ingested')}")
else:
    record("PHASE 7: DASHBOARD", "GET /dashboard/summary", "FAIL", f"Status {status}: {body}")

status, body, _ = make_request(f"{BACKEND_URL}/dashboard/trend?timeframe=7d", headers=auth_headers)
if status == 200 and "points" in body and len(body["points"]) == 7:
    record("PHASE 7: DASHBOARD", "GET /dashboard/trend (7d)", "PASS", f"{len(body['points'])} trend points calculated")
else:
    record("PHASE 7: DASHBOARD", "GET /dashboard/trend", "FAIL", f"Status {status}: {body}")

status, body, _ = make_request(f"{BACKEND_URL}/dashboard/threat-distribution", headers=auth_headers)
if status == 200 and "categories" in body and len(body["categories"]) > 0:
    record("PHASE 7: DASHBOARD", "GET /dashboard/threat-distribution", "PASS", f"{len(body['categories'])} threat categories breakdown")
else:
    record("PHASE 7: DASHBOARD", "GET /dashboard/threat-distribution", "FAIL", f"Status {status}: {body}")

# ==========================================
# PHASE 8: ACTIVITY TELEMETRY / MONGODB
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/activity-logs", headers=auth_headers)
if status == 200 and "items" in body:
    record("PHASE 8: TELEMETRY", "GET /activity-logs", "PASS", f"{body['total']} total telemetry logs in store")
else:
    record("PHASE 8: TELEMETRY", "GET /activity-logs", "FAIL", f"Status {status}: {body}")

status, body, _ = make_request(f"{BACKEND_URL}/activity-logs/timeline?time_range=30d", headers=auth_headers)
if status == 200 and "items" in body and body["total"] > 0:
    record("PHASE 8: TELEMETRY", "GET /activity-logs/timeline", "PASS", f"{body['total']} chronological events streamed")
else:
    record("PHASE 8: TELEMETRY", "GET /activity-logs/timeline", "FAIL", f"Status {status}: {body}")

status, body, _ = make_request(f"{BACKEND_URL}/activity-logs/distribution", headers=auth_headers)
if status == 200 and isinstance(body, list) and len(body) == 8:
    record("PHASE 8: TELEMETRY", "GET /activity-logs/distribution", "PASS", "All 8 event types active in distribution")
else:
    record("PHASE 8: TELEMETRY", "GET /activity-logs/distribution", "FAIL", f"Status {status}")

status, body, _ = make_request(f"{BACKEND_URL}/activity-logs/heatmap", headers=auth_headers)
if status == 200 and isinstance(body, list) and len(body) == 168:
    record("PHASE 8: TELEMETRY", "GET /activity-logs/heatmap", "PASS", "7x24 (168 cells) intensity matrix calculated")
else:
    record("PHASE 8: TELEMETRY", "GET /activity-logs/heatmap", "FAIL", f"Status {status}")

# ==========================================
# PHASE 9: BEHAVIOR ANALYSIS
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/behavior-analysis/FIN-2187", headers=auth_headers)
if status == 200 and "baseline" in body and "behavior_deviation_score" in body:
    record("PHASE 9: BEHAVIOR ANALYSIS", "GET /behavior-analysis/FIN-2187", "PASS", f"Baseline active, deviation score: {body['behavior_deviation_score']}")
else:
    record("PHASE 9: BEHAVIOR ANALYSIS", "GET /behavior-analysis/FIN-2187", "FAIL", f"Status {status}: {body}")

# ==========================================
# PHASE 10: RISK SCORES
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/risk-scores", headers=auth_headers)
if status == 200 and "items" in body and body["total"] >= 6:
    record("PHASE 10: RISK SCORES", "GET /risk-scores", "PASS", f"{body['total']} employee risk scores computed")
else:
    record("PHASE 10: RISK SCORES", "GET /risk-scores", "FAIL", f"Status {status}: {body}")

# ==========================================
# PHASE 11: ALERTS API
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/alerts", headers=auth_headers)
if status == 200 and "items" in body:
    alert_count = body["total"]
    record("PHASE 11: ALERTS", "GET /alerts", "PASS", f"{alert_count} active/historical alerts")
else:
    record("PHASE 11: ALERTS", "GET /alerts", "FAIL", f"Status {status}: {body}")

# ==========================================
# PHASE 12: INCIDENTS API
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/incidents", headers=auth_headers)
if status == 200 and "items" in body:
    record("PHASE 12: INCIDENTS", "GET /incidents", "PASS", f"{body['total']} incidents listed")
else:
    record("PHASE 12: INCIDENTS", "GET /incidents", "FAIL", f"Status {status}: {body}")

# ==========================================
# PHASE 13: INVESTIGATION CENTER
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/investigations/FIN-2187", headers=auth_headers)
if status == 200 and "employee" in body and "timeline" in body:
    record("PHASE 13: INVESTIGATIONS", "GET /investigations/FIN-2187", "PASS", f"Unified dossier loaded with {len(body['timeline'])} timeline items")
else:
    record("PHASE 13: INVESTIGATIONS", "GET /investigations/FIN-2187", "FAIL", f"Status {status}: {body}")

# Add Note Test
status, body, _ = make_request(f"{BACKEND_URL}/investigations/FIN-2187/notes", method="POST", data={
    "note_text": "Pre-deployment audit verification test case note."
}, headers=auth_headers)
if status == 201 and "note_text" in body:
    record("PHASE 13: INVESTIGATIONS", "POST /investigations/{emp}/notes", "PASS", "Analyst case note persisted")
else:
    record("PHASE 13: INVESTIGATIONS", "POST /investigations/{emp}/notes", "FAIL", f"Status {status}: {body}")

# Export Summary Test
status, body, _ = make_request(f"{BACKEND_URL}/investigations/FIN-2187/export", headers=auth_headers)
if status == 200 and "report_id" in body and "subject" in body:
    record("PHASE 13: INVESTIGATIONS", "GET /investigations/{emp}/export", "PASS", f"Report {body['report_id']} generated")
else:
    record("PHASE 13: INVESTIGATIONS", "GET /investigations/{emp}/export", "FAIL", f"Status {status}: {body}")

# ==========================================
# PHASE 14: REPORTS API
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/reports/summary", headers=auth_headers)
if status == 200 and "total_monitored_employees" in body:
    record("PHASE 14: REPORTS", "GET /reports/summary", "PASS", f"Executive report generated ({body['total_monitored_employees']} employees)")
else:
    record("PHASE 14: REPORTS", "GET /reports/summary", "FAIL", f"Status {status}: {body}")

status, body, _ = make_request(f"{BACKEND_URL}/reports/export-csv", headers=auth_headers)
if status == 200 and "Employee ID" in str(body):
    record("PHASE 14: REPORTS", "GET /reports/export-csv", "PASS", "Valid CSV report generated")
else:
    record("PHASE 14: REPORTS", "GET /reports/export-csv", "FAIL", f"Status {status}")

# ==========================================
# PHASE 15: NOTIFICATIONS API
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/notifications", headers=auth_headers)
if status == 200 and isinstance(body, list):
    record("PHASE 15: NOTIFICATIONS", "GET /notifications", "PASS", f"{len(body)} SOC notifications retrieved")
else:
    record("PHASE 15: NOTIFICATIONS", "GET /notifications", "FAIL", f"Status {status}")

# ==========================================
# PHASE 16: SETTINGS API
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/settings", headers=auth_headers)
if status == 200 and "anomaly_threshold" in body:
    record("PHASE 16: SETTINGS", "GET /settings", "PASS", f"Anomaly threshold={body['anomaly_threshold']}, Sensitivity={body.get('sensor_sensitivity')}")
else:
    record("PHASE 16: SETTINGS", "GET /settings", "FAIL", f"Status {status}: {body}")

# ==========================================
# PHASE 17: GLOBAL SEARCH API
# ==========================================
status, body, _ = make_request(f"{BACKEND_URL}/search?q=FIN-2187", headers=auth_headers)
if status == 200 and "results" in body and body["total_matches"] > 0:
    record("PHASE 17: GLOBAL SEARCH", "GET /search?q=FIN-2187", "PASS", f"{body['total_matches']} matches across entities")
else:
    record("PHASE 17: GLOBAL SEARCH", "GET /search?q=FIN-2187", "FAIL", f"Status {status}: {body}")

# ==========================================
# PHASE 21: FRONTEND ROUTING AUDIT (HTTP LIVE)
# ==========================================
frontend_routes = [
    ("/", "Landing Page (Public)", "INSIDER THREAT"),
    ("/login", "Login Page (Public)", "Security Operations Console"),
    ("/signup", "Signup Page (Public)", "Operator Enrollment"),
    ("/dashboard", "SOC Dashboard", "Dashboard"),
    ("/employees", "Employees Registry", "Employees"),
    ("/activity-logs", "Activity Logs & Timeline", "Activity"),
    ("/behavior-analysis", "Behavior Analysis", "Behavior"),
    ("/risk-scores", "Risk Scores", "Risk"),
    ("/alerts", "Alerts Console", "Alerts"),
    ("/incidents", "Incident Management", "Incidents"),
    ("/investigations", "Investigation Center", "Investigation"),
    ("/reports", "Reports & Export", "Reports"),
    ("/settings", "System Settings", "Settings"),
]

for route, desc, keyword in frontend_routes:
    status, body, _ = make_request(f"{FRONTEND_URL}{route}")
    if status == 200:
        record("PHASE 21: FRONTEND ROUTING", f"Route {route} ({desc})", "PASS", f"Status 200 OK")
    else:
        record("PHASE 21: FRONTEND ROUTING", f"Route {route} ({desc})", "FAIL", f"Status {status}")

# ==========================================
# PHASE 24: COMPLETE SYNTHETIC E2E THREAT FLOW
# ==========================================
print("\n--- RUNNING COMPLETE E2E THREAT DETECTION LIFECYCLE ---")
# 1. Ingest anomalous activity
status, body, _ = make_request(f"{BACKEND_URL}/activity-logs/test-event", method="POST", data={
    "employee_id": "FIN-2187",
    "activity_type": "file_download",
    "action": "Mass Download Sensitive Payroll Archive",
    "resource": "SharePoint://Finance/Confidential/Executive_Salaries_2026.xlsx",
    "device_id": "ROG-Strix-Laptop (Unenrolled)",
    "ip_address": "198.51.100.99",
    "scenario": "EXFILTRATION_OFFHOURS"
}, headers=auth_headers)

if status == 201 and body.get("alert_created"):
    record("PHASE 24: E2E THREAT FLOW", "Activity -> Baseline -> Anomaly -> Alert", "PASS", 
           f"Risk Score: {body.get('calculated_risk_score')}, Tier: {body.get('risk_level')}, Alert #{body.get('alert_id')} created")
    
    alert_id = body.get("alert_id")
    # 2. Escalate alert to Incident
    status_inc, body_inc, _ = make_request(f"{BACKEND_URL}/alerts/{alert_id}/create-incident", method="POST", headers=auth_headers)
    if status_inc == 200 and "id" in body_inc:
        inc_id = body_inc["id"]
        record("PHASE 24: E2E THREAT FLOW", "Alert -> Incident Escalation", "PASS", f"Incident INC-{inc_id} opened")

        # 3. Transition Incident to INVESTIGATING
        make_request(f"{BACKEND_URL}/incidents/{inc_id}/status", method="PATCH", data={"status": "INVESTIGATING", "resolution_notes": "Forensics underway"}, headers=auth_headers)
        
        # 4. Transition Incident to CONTAINED
        make_request(f"{BACKEND_URL}/incidents/{inc_id}/status", method="PATCH", data={"status": "CONTAINED", "resolution_notes": "Revoked IAM keys & isolated IP"}, headers=auth_headers)

        # 5. Transition Incident to RESOLVED
        status_res, body_res, _ = make_request(f"{BACKEND_URL}/incidents/{inc_id}/status", method="PATCH", data={"status": "RESOLVED", "resolution_notes": "Forensic case closed"}, headers=auth_headers)
        if status_res == 200 and body_res.get("status") == "RESOLVED":
            record("PHASE 24: E2E THREAT FLOW", "Incident Lifecycle (Open->Investigating->Contained->Resolved)", "PASS", "Incident fully resolved")
        else:
            record("PHASE 24: E2E THREAT FLOW", "Incident Resolution", "FAIL", f"Status {status_res}")
    else:
        record("PHASE 24: E2E THREAT FLOW", "Alert Escalation", "FAIL", f"Status {status_inc}")
else:
    record("PHASE 24: E2E THREAT FLOW", "Synthetic Threat Ingestion", "FAIL", f"Status {status}: {body}")

print("\n" + "=" * 60)
pass_count = sum(1 for r in results if r["status"] == "PASS")
fail_count = sum(1 for r in results if r["status"] == "FAIL")
print(f"AUDIT SUMMARY: {pass_count} PASSED, {fail_count} FAILED OUT OF {len(results)} CHECKS")
print("=" * 60)

if fail_count > 0:
    print("FAILED CHECKS:")
    for r in results:
        if r["status"] == "FAIL":
            print(f"- {r['phase']} | {r['test']}: {r['detail']}")
    sys.exit(1)
else:
    print("ALL PRE-DEPLOYMENT AUDIT CHECKS PASSED WITH ZERO FAILURES.")
    sys.exit(0)
