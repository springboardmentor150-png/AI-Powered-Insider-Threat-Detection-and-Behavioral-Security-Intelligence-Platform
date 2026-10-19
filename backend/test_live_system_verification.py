import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:3000"

def request(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
            try:
                parsed = json.loads(content.decode("utf-8"))
            except Exception:
                parsed = content # binary or non-json
            return resp.getcode(), parsed
    except urllib.error.HTTPError as e:
        err_body = e.read()
        try:
            parsed = json.loads(err_body.decode("utf-8"))
        except Exception:
            parsed = err_body.decode("utf-8")
        return e.code, parsed
    except Exception as exc:
        return 0, str(exc)

def test_frontend_routes():
    print("\n--- Testing Frontend Routes (Next.js) ---")
    routes = [
        "/",
        "/login",
        "/signup",
        "/dashboard",
        "/employees",
        "/activity-logs",
        "/alerts",
        "/incidents",
        "/investigations",
        "/risk-scores",
        "/behavior-analysis",
        "/reports",
        "/settings",
    ]
    results = {}
    for r in routes:
        try:
            req = urllib.request.Request(f"{FRONTEND_URL}{r}", method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                code = resp.getcode()
                results[r] = (code, "OK")
                print(f"  [PASS] Frontend {r}: {code}")
        except urllib.error.HTTPError as e:
            results[r] = (e.code, "HTTPError")
            print(f"  [FAIL] Frontend {r}: {e.code}")
        except Exception as ex:
            results[r] = (0, str(ex))
            print(f"  [ERROR] Frontend {r}: {ex}")
    return results

def main():
    print("==================================================")
    print("   ITBIS Live System & Feature Verification Test  ")
    print("==================================================")
    
    report = {"passed": [], "failed": []}

    def check(name, success, detail=""):
        if success:
            report["passed"].append(name)
            print(f" [PASS] {name} {detail}")
        else:
            report["failed"].append((name, detail))
            print(f" [FAIL] {name}: {detail}")

    # 1. Health
    code, data = request("GET", "/health")
    check("Backend Health Check", code == 200, str(data))

    # 2. Authentication - Login
    code, data = request("POST", "/auth/login", {"email": "admin@itbis.cyber", "password": "AdminPassword123!"})
    admin_token = data.get("access_token") if isinstance(data, dict) else None
    check("Admin Login", code == 200 and admin_token is not None, f"Token present: {bool(admin_token)}")

    code, data = request("POST", "/auth/login", {"email": "analyst@itbis.cyber", "password": "AnalystPassword123!"})
    analyst_token = data.get("access_token") if isinstance(data, dict) else None
    check("Analyst Login", code == 200 and analyst_token is not None, f"Token present: {bool(analyst_token)}")

    # 3. Authentication - Signup
    import random
    rand_email = f"test_soc_{random.randint(1000, 9999)}@itbis.cyber"
    code, data = request("POST", "/auth/signup", {"email": rand_email, "password": "TestPassword123!", "role": "security_analyst"})
    check("User Signup", code == 201, str(data.get("message") if isinstance(data, dict) else data))

    # 4. Dashboard Routes
    code, data = request("GET", "/dashboard/summary", token=analyst_token)
    check("Dashboard Summary", code == 200 and "total_employees" in data, f"Total Employees: {data.get('total_employees') if isinstance(data, dict) else 0}")

    code, data = request("GET", "/dashboard/threat-distribution", token=analyst_token)
    check("Dashboard Threat Distribution", code == 200 and "categories" in data)

    code, data = request("GET", "/dashboard/trend?timeframe=7d", token=analyst_token)
    check("Dashboard Trend", code == 200 and "points" in data)

    code, data = request("GET", "/dashboard/manager/compliance", token=admin_token)
    check("Compliance Dashboard", code == 200 and "mttr_hours" in data, f"MTTR: {data.get('mttr_hours') if isinstance(data, dict) else 0} hrs")

    code, data = request("GET", "/dashboard/admin", token=admin_token)
    check("Admin Dashboard Overview", code == 200)

    # 5. Employees Management
    code, data = request("GET", "/employees", token=analyst_token)
    emp_list = data.get("items", []) if isinstance(data, dict) else []
    check("List Employees", code == 200 and len(emp_list) > 0, f"Count: {len(emp_list)}")

    sample_emp = emp_list[0] if emp_list else {"employee_id": "CYB-1042", "id": 1}
    sample_emp_id = sample_emp["employee_id"]
    sample_numeric_id = sample_emp.get("id", 1)

    code, data = request("GET", f"/employees/{sample_emp_id}", token=analyst_token)
    check("Get Single Employee Detail", code == 200 and "employee" in data and data["employee"]["employee_id"] == sample_emp_id)

    # 6. Activity Logs (MongoDB / JSON fallback)
    code, data = request("GET", "/activity-logs?limit=10", token=analyst_token)
    check("Query Activity Logs", code == 200 and "items" in data, f"Total: {data.get('total') if isinstance(data, dict) else 0}")

    code, data = request("POST", "/activity-logs", {
        "employee_id": sample_emp_id,
        "event_type": "login",
        "action": "Live Verification Login",
        "resource": "SOC Portal",
        "device": "SOC-Workstation-01",
        "ip_address": "192.168.1.99"
    }, token=admin_token)
    check("Ingest Activity Log (Admin)", code in [200, 201])

    code, data = request("POST", "/activity-logs/test-event", {
        "employee_id": sample_emp_id,
        "activity_type": "file_download",
        "action": "Test Download Telemetry",
        "resource": "Confidential Vault",
        "scenario": "SUSPICIOUS_OFFHOURS_EXFIL"
    }, token=analyst_token)
    check("Trigger Synthetic Test Event", code in [200, 201])

    code, data = request("GET", f"/activity-logs/timeline?employee_id={sample_emp_id}", token=analyst_token)
    check("Activity Timeline", code == 200 and "items" in data)

    code, data = request("GET", "/activity-logs/heatmap", token=analyst_token)
    check("Activity Heatmap", code == 200 and isinstance(data, list))

    code, data = request("GET", "/activity-logs/distribution", token=analyst_token)
    check("Activity Distribution", code == 200 and isinstance(data, list))

    # 7. Anomalies & Risk Scoring
    code, data = request("GET", f"/anomalies/{sample_emp_id}", token=analyst_token)
    check("Combined Anomalies for Employee", code == 200 and "employee_id" in data)

    code, data = request("GET", "/anomalies/summary", token=analyst_token)
    check("Anomalies Summary", code == 200 and ("top_employees" in data or "top_10_employees" in data or isinstance(data, list)))

    code, data = request("GET", "/risk-scores", token=analyst_token)
    check("Risk Scores List", code == 200 and "items" in data)

    code, data = request("GET", f"/risk-scores/{sample_emp_id}/history", token=analyst_token)
    check("Employee Risk History", code == 200 and isinstance(data, list))

    code, data = request("GET", f"/risk-score/{sample_emp_id}", token=analyst_token)
    check("Single Employee Risk Score", code == 200 and ("final_score" in data or "risk_score" in data))

    # 8. Behavior Analysis
    code, data = request("GET", f"/behavior-analysis/{sample_emp_id}", token=analyst_token)
    check("Behavioral Baseline & Anomaly Inspector", code == 200 and "baseline" in data)

    # 9. Alerts
    code, data = request("GET", "/alerts", token=analyst_token)
    alerts_list = data.get("items", []) if isinstance(data, dict) else data
    check("List Alerts", code == 200, f"Count: {len(alerts_list)}")

    created_alert_id = None
    code, data = request("POST", "/alerts", {
        "employee_id": sample_numeric_id,
        "title": "Suspicious Off-Hours Data Access",
        "message": "Employee accessed database outside normal business hours.",
        "category": "UNAUTHORIZED_ACCESS",
        "severity": "HIGH",
        "risk_score": 75
    }, token=analyst_token)
    if code in [200, 201] and isinstance(data, dict):
        created_alert_id = data.get("id")
    check("Create Alert", code in [200, 201] and created_alert_id is not None, f"Alert ID: {created_alert_id}")

    if created_alert_id:
        code, data = request("PATCH", f"/alerts/{created_alert_id}/acknowledge", token=analyst_token)
        check("Acknowledge Alert", code == 200 and data.get("status") in ["ACKNOWLEDGED", "acknowledged"])

        code, data = request("POST", f"/alerts/{created_alert_id}/create-incident", token=analyst_token)
        check("Escalate Alert to Incident", code in [200, 201])

        code, data = request("PATCH", f"/alerts/{created_alert_id}/resolve", token=analyst_token)
        check("Resolve Alert", code == 200 and data.get("status") in ["RESOLVED", "resolved"])

    # 10. Incidents
    code, data = request("GET", "/incidents", token=analyst_token)
    incidents_list = data.get("items", []) if isinstance(data, dict) else data
    check("List Incidents", code == 200, f"Count: {len(incidents_list)}")

    sample_incident_id = incidents_list[0]["id"] if incidents_list else 1
    code, data = request("GET", f"/incidents/{sample_incident_id}", token=analyst_token)
    check("Get Single Incident", code == 200 and "id" in data)

    code, data = request("PATCH", f"/incidents/{sample_incident_id}/status", {
        "status": "INVESTIGATING",
        "resolution_notes": "Forensic triage commenced by SOC analyst."
    }, token=analyst_token)
    check("Update Incident Status", code == 200)

    # 11. Investigations
    code, data = request("GET", f"/investigations/{sample_emp_id}", token=analyst_token)
    check("Get Employee Investigation Dossier", code == 200 and "employee" in data and "timeline" in data)

    code, data = request("POST", f"/investigations/{sample_emp_id}/notes", {
        "note_text": "Analyst verified benign network event. Test completed successfully."
    }, token=analyst_token)
    check("Add Investigation Case Note", code in [200, 201])

    # 12. Reports
    code, data = request("GET", "/reports/summary", token=analyst_token)
    check("Reports Executive Summary", code == 200 and "total_monitored_employees" in data)

    code, data = request("GET", "/reports/export-csv", token=analyst_token)
    check("Export Reports CSV", code == 200 and len(data) > 0)

    code, data = request("GET", "/reports/export-excel", token=analyst_token)
    check("Export Reports Excel (.xlsx)", code == 200 and len(data) > 0)

    code, data = request("GET", f"/reports/{sample_emp_id}/pdf", token=analyst_token)
    check("Employee PDF Report", code == 200 and isinstance(data, bytes) and len(data) > 100, f"PDF bytes: {len(data) if isinstance(data, bytes) else 0}")

    code, data = request("GET", "/reports/compliance/pdf", token=admin_token)
    check("Compliance PDF Report (Admin)", code == 200 and isinstance(data, bytes) and len(data) > 100, f"PDF bytes: {len(data) if isinstance(data, bytes) else 0}")

    # 13. Settings & Diagnostics
    code, data = request("GET", "/settings", token=analyst_token)
    check("Get System Settings", code == 200 and isinstance(data, dict))

    code, data = request("POST", "/settings", {
        "settings": {
            "anomaly_threshold": "60",
            "critical_threshold": "80",
            "sensor_sensitivity": "HIGH"
        }
    }, token=admin_token)
    check("Update System Settings", code == 200)

    code, data = request("GET", "/settings/db-diagnostics", token=analyst_token)
    check("Database Diagnostics", code == 200 and "database_engine" in data, f"Engine: {data.get('database_engine')}")

    code, data = request("GET", "/settings/telemetry-diagnostics", token=analyst_token)
    check("Telemetry Diagnostics", code == 200 and "telemetry_backend" in data, f"Backend: {data.get('telemetry_backend')}")

    # 14. Frontend routes
    fe_results = test_frontend_routes()
    fe_all_ok = all(c == 200 for c, _ in fe_results.values())
    check("All Frontend Pages Rendered", fe_all_ok, f"{sum(1 for c, _ in fe_results.values() if c == 200)}/{len(fe_results)} routes 200 OK")

    print("\n==================================================")
    print(f"SUMMARY: {len(report['passed'])} PASSED, {len(report['failed'])} FAILED")
    print("==================================================")
    if report["failed"]:
        for name, err in report["failed"]:
            print(f"FAILED: {name} -> {err}")
        sys.exit(1)
    else:
        print(">>> ALL ITBIS END-TO-END FEATURES VERIFIED OPERATIONAL! <<<")
        sys.exit(0)

if __name__ == "__main__":
    main()
