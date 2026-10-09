import requests
import time

BASE_URL = "http://localhost:8000"

def run_tests():
    print("STARTING E2E TEST WORKFLOW...")
    
    # 1. Admin Login (Requires an admin user or signup first)
    # Seed Admin User directly via DB to bypass public signup constraints
    import sqlite3
    import psycopg2
    try:
        conn = psycopg2.connect("postgresql://postgres:Itibis15@localhost:5432/itbis")
        cur = conn.cursor()
        # Ensure canonical roles
        cur.execute("UPDATE users SET role = 'ADMIN' WHERE email = 'admin@itbis.com'")
        cur.execute("UPDATE users SET role = 'SECURITY_ANALYST' WHERE email = 'analyst@itbis.com'")
        conn.commit()
    except Exception as e:
        print("Could not seed DB via SQL:", e)
        pass
        
    # Login Admin
    print("\n[AUTH] Logging in Admin...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@itbis.com", "password": "secure123"})
    admin_token = res.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("Admin logged in successfully.")
    
    # Login Analyst
    print("\n[AUTH] Logging in Security Analyst...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"email": "analyst@itbis.com", "password": "secure123"})
    analyst_token = res.json().get("access_token")
    analyst_headers = {"Authorization": f"Bearer {analyst_token}"}
    print("Analyst logged in successfully.")
    
    # User CRUD (Admin)
    print("\n[USERS] Admin Listing Users...")
    res = requests.get(f"{BASE_URL}/users", headers=admin_headers)
    print(res.status_code, len(res.json()), "users found.")
    
    # Employee Management (Admin)
    print("\n[EMPLOYEES] Creating Employee...")
    emp_data = {"employee_id": "EMP-TEST-999", "name": "Test Employee", "department": "IT", "designation": "Staff", "device_info": "Macbook", "access_privileges": "Standard"}
    res = requests.post(f"{BASE_URL}/employees", json=emp_data, headers=admin_headers)
    print("Create Employee:", res.status_code, res.text)
    
    print("[EMPLOYEES] Analyst Listing Employees...")
    res = requests.get(f"{BASE_URL}/employees", headers=analyst_headers)
    print("Analyst Employee List Status:", res.status_code)
    
    # Log Ingestion
    print("\n[LOGS] Ingesting Activity Logs...")
    requests.post(f"{BASE_URL}/logs/ingest", json={"employee_id": "EMP-TEST-999", "event_type": "login", "details": {"device": "Macbook", "ip": "1.1.1.1"}})
    requests.post(f"{BASE_URL}/logs/ingest", json={"employee_id": "EMP-TEST-999", "event_type": "file_download", "details": {"device": "Macbook", "count": 15}})
    requests.post(f"{BASE_URL}/logs/ingest", json={"employee_id": "EMP-TEST-999", "event_type": "usb_activity", "details": {"device": "Unknown-USB"}})
    for _ in range(3):
         requests.post(f"{BASE_URL}/logs/ingest", json={"employee_id": "EMP-TEST-999", "event_type": "login", "details": {"device": "Macbook", "ip": "1.1.1.1"}})
    time.sleep(1)
    
    # Analytics / Baselines
    print("\n[ANALYTICS] Generating Baseline...")
    res = requests.post(f"{BASE_URL}/analytics/baseline/EMP-TEST-999", headers=admin_headers)
    print("Baseline:", res.status_code, res.json())
    
    print("\n[ANALYTICS] Running Anomaly Detection...")
    res = requests.post(f"{BASE_URL}/analytics/anomalies/EMP-TEST-999", headers=admin_headers)
    print("Anomalies:", res.status_code, res.json())
    
    print("\n[ANALYTICS] Scoring Risk...")
    res = requests.post(f"{BASE_URL}/analytics/risk-score/EMP-TEST-999", headers=admin_headers)
    print("Risk Score:", res.status_code, res.json())
    
    # Alerts
    print("\n[WARNINGS] Listing Alerts...")
    res = requests.get(f"{BASE_URL}/alerts", headers=admin_headers)
    alerts = res.json()
    print("Alerts found:", len(alerts))
    
    if len(alerts) > 0:
        alert_id = alerts[0]["id"]
        # Incidents
        print("\n[INCIDENTS] Creating Incident from Alert...")
        res = requests.post(f"{BASE_URL}/incidents", json={"alert_id": alert_id}, headers=admin_headers)
        print("Incident Created:", res.status_code, res.json())
        incident_id = res.json()["id"]
        
        print(f"[INCIDENTS] Updating Incident {incident_id}...")
        res = requests.put(f"{BASE_URL}/incidents/{incident_id}?status=investigating&notes=Checking", headers=admin_headers)
        print("Incident Updated:", res.status_code)
    
    print("\n[DASHBOARD] Fetching Stats...")
    res = requests.get(f"{BASE_URL}/analytics/dashboard-stats", headers=admin_headers)
    print("Dashboard Stats:", res.status_code, res.json())

    # Delete test employee
    print("\n[CLEANUP] Deleting test employee...")
    res = requests.delete(f"{BASE_URL}/employees/EMP-TEST-999", headers=admin_headers)
    print("Delete Employee:", res.status_code)

if __name__ == "__main__":
    run_tests()
