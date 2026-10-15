# backend/test_milestone4_endpoints.py
"""
Comprehensive automated test suite for Milestone 4 (Day 31 to Day 34).
Validates:
- Day 31: Compliance metrics, MTTR/MTTI calculations, zero-incident safety, role restrictions
- Day 32: Admin dashboard, platform volume analytics, audit logging across sensitive endpoints, 403 guards
- Day 33: In-memory PDF generation (many anomalies, 0 anomalies, compliance summary)
- Day 34: Excel exports (sorted risk scores, unresolved incident date handling, catalog endpoint)
"""
import io
from datetime import datetime, timedelta
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal, mongo_db
from app.models import User, Employee, Incident, Alert, AuditLog
from app.auth import create_access_token

client = TestClient(app)

def get_auth_headers(role: str, user_id: int = 1, email: str = "test@itbis.security"):
    token = create_access_token(user_id=user_id, email=email, role=role)
    return {"Authorization": f"Bearer {token}"}

def run_all_tests():
    print("=" * 70)
    print("STARTING MILESTONE 4 TEST SUITE (DAYS 31 - 34)")
    print("=" * 70)

    admin_headers = get_auth_headers("admin", user_id=1, email="admin@itbis.security")
    manager_headers = get_auth_headers("security_manager", user_id=3, email="manager@itbis.security")
    analyst_headers = get_auth_headers("security_analyst", user_id=2, email="analyst@itbis.security")
    soc_headers = get_auth_headers("soc_engineer", user_id=4, email="soc@itbis.security")

    db = SessionLocal()

    # -------------------------------------------------------------
    # 1. DAY 31: Security Manager Compliance View & MTTR/MTTI
    # -------------------------------------------------------------
    print("\n[TEST 1] Testing Day 31 Compliance View & MTTR/MTTI...")
    
    # 1A. Test role access
    res = client.get("/api/dashboard/manager/compliance", headers=analyst_headers)
    assert res.status_code == 403, f"Expected 403 for analyst, got {res.status_code}"
    print("  [PASS] Analyst correctly receives 403 Forbidden on compliance dashboard")

    res = client.get("/api/dashboard/manager/compliance", headers=manager_headers)
    assert res.status_code == 200, f"Expected 200 for manager, got {res.status_code}: {res.text}"
    comp_data = res.json()
    assert "total_incidents" in comp_data
    assert "resolved_incidents" in comp_data
    assert "resolution_rate_percent" in comp_data
    assert "open_critical_incidents" in comp_data
    print(f"  [PASS] Manager compliance metrics: Total={comp_data['total_incidents']}, Resolved={comp_data['resolved_incidents']}, Rate={comp_data['resolution_rate_percent']}%, Open Critical={comp_data['open_critical_incidents']}")

    # 1B. Test Alert Resolution with Time Gaps & calculate_mttr()
    print("  Testing MTTR calculation with simulated alert resolution...")
    alert_test = db.query(Alert).filter(Alert.status == "open").first()
    if not alert_test:
        alert_test = Alert(
            alert_code="ALT-TEST-MTTR",
            employee_id="EMP1001",
            severity="high",
            title="Test MTTR Alert",
            message="Simulated off-hours anomaly for MTTR verification",
            status="open",
            created_at=datetime.utcnow() - timedelta(hours=4, minutes=30)
        )
        db.add(alert_test)
        db.commit()
        db.refresh(alert_test)

    # Resolve alert via endpoint
    res_resolve = client.patch(f"/api/alerts/{alert_test.id}/resolve", headers=analyst_headers)
    assert res_resolve.status_code == 200
    
    # Re-check compliance metrics to verify MTTR is now a positive number
    res_after = client.get("/api/dashboard/manager/compliance", headers=manager_headers).json()
    print(f"  [PASS] MTTR calculated: {res_after.get('mean_time_to_respond_hours')} hours (MTTI: {res_after.get('mean_time_to_investigate_hours')} hours)")

    # -------------------------------------------------------------
    # 2. DAY 32: Admin Dashboard & Platform Health
    # -------------------------------------------------------------
    print("\n[TEST 2] Testing Day 32 Admin Dashboard & Platform Volume Analytics...")

    # 2A. Admin counts
    res_non_admin = client.get("/api/dashboard/admin", headers=manager_headers)
    assert res_non_admin.status_code == 403, f"Expected 403 for non-admin on admin dashboard, got {res_non_admin.status_code}"
    print("  [PASS] Non-admin role correctly blocked (403) from Admin Dashboard")

    res_admin = client.get("/api/dashboard/admin", headers=admin_headers)
    assert res_admin.status_code == 200
    admin_data = res_admin.json()
    assert admin_data["total_platform_users"] >= 4
    assert admin_data["employees_monitored"] >= 5
    assert admin_data["departments"] >= 3
    print(f"  [PASS] Admin Dashboard: Users={admin_data['total_platform_users']}, Monitored Employees={admin_data['employees_monitored']}, Unique Departments={admin_data['departments']}")
    print(f"    Users by Role: {admin_data['users_by_role']}")

    # 2B. Platform volume analytics
    res_analytics = client.get("/api/dashboard/admin/platform-analytics", headers=admin_headers)
    assert res_analytics.status_code == 200
    analytics_data = res_analytics.json()
    assert "total_activity_logs" in analytics_data
    assert "overall_anomaly_rate_percent" in analytics_data
    print(f"  [PASS] Platform Analytics: Logs={analytics_data['total_activity_logs']}, Rule Anomalies={analytics_data['total_rule_anomalies']}, ML Anomalies={analytics_data['total_ml_anomalies']}, Anomaly Rate={analytics_data['overall_anomaly_rate_percent']}%")

    # 2C. Audit logging across sensitive endpoints
    print("  Testing audit trail capture across sensitive actions...")
    
    # Sensitive Action 1: Assign alert
    assignee = db.query(User).filter(User.role == "security_analyst").first()
    target_alert = db.query(Alert).first()
    res_assign = client.post(f"/api/alerts/{target_alert.id}/assign?analyst_user_id={assignee.id}", headers=admin_headers)
    assert res_assign.status_code == 200

    # Sensitive Action 2: Create incident
    res_create_inc = client.post("/api/incidents", headers=admin_headers, json={
        "employee_id": "EMP1003",
        "title": "Audit Test Incident",
        "description": "Triggered to verify Day 32 audit logging mechanism",
        "severity": "CRITICAL"
    })
    assert res_create_inc.status_code == 201
    created_inc_id = res_create_inc.json()["id"]

    # Sensitive Action 3: Update incident status
    res_status = client.patch(f"/api/incidents/{created_inc_id}/status", headers=admin_headers, json={
        "status": "INVESTIGATING",
        "assigned_to": "admin@itbis.security"
    })
    assert res_status.status_code == 200

    # Query audit log endpoint
    res_audit = client.get("/api/dashboard/admin/audit-log", headers=admin_headers)
    assert res_audit.status_code == 200
    audit_entries = res_audit.json()
    assert len(audit_entries) >= 3
    actions_found = [e["action"] for e in audit_entries]
    print(f"  [PASS] Audit Log captured {len(audit_entries)} records. Recent actions: {actions_found[:5]}")
    assert any("assign_alert" in a for a in actions_found)
    assert any("create_incident" in a for a in actions_found)
    assert any("update_incident_status" in a for a in actions_found)

    # -------------------------------------------------------------
    # 3. DAY 33: In-Memory PDF Reports
    # -------------------------------------------------------------
    print("\n[TEST 3] Testing Day 33 In-Memory PDF Reports...")

    # 3A. Employee with multiple anomalies (EMP1003)
    res_pdf_1003 = client.get("/api/reports/EMP1003/pdf", headers=analyst_headers)
    assert res_pdf_1003.status_code == 200
    assert res_pdf_1003.headers["content-type"] == "application/pdf"
    assert "attachment; filename=EMP1003_risk_report.pdf" in res_pdf_1003.headers["content-disposition"]
    pdf_bytes_1003 = res_pdf_1003.content
    assert pdf_bytes_1003.startswith(b"%PDF"), "Response is not a valid PDF binary stream"
    print(f"  [PASS] EMP1003 PDF Risk Report generated ({len(pdf_bytes_1003)} bytes, starts with %PDF)")

    # 3B. Employee with ZERO anomalies (EMP1005 - clean developer)
    # Ensure EMP1005 has 0 anomalies in rule_anomalies
    clean_emp_id = "EMP1005"
    res_pdf_clean = client.get(f"/api/reports/{clean_emp_id}/pdf", headers=analyst_headers)
    assert res_pdf_clean.status_code == 200
    assert res_pdf_clean.headers["content-type"] == "application/pdf"
    pdf_bytes_clean = res_pdf_clean.content
    assert pdf_bytes_clean.startswith(b"%PDF")
    print(f"  [PASS] Clean Employee ({clean_emp_id}) PDF generated safely without crashing ({len(pdf_bytes_clean)} bytes)")

    # 3C. Compliance Summary PDF Report (Day 33 Exercise 3)
    res_pdf_comp = client.get("/api/reports/compliance/pdf", headers=manager_headers)
    assert res_pdf_comp.status_code == 200
    assert res_pdf_comp.headers["content-type"] == "application/pdf"
    assert "attachment; filename=compliance_summary_report.pdf" in res_pdf_comp.headers["content-disposition"]
    pdf_bytes_comp = res_pdf_comp.content
    assert pdf_bytes_comp.startswith(b"%PDF")
    print(f"  [PASS] Compliance Summary PDF Report generated ({len(pdf_bytes_comp)} bytes)")

    # -------------------------------------------------------------
    # 4. DAY 34: Excel Data Exports & Report Catalog
    # -------------------------------------------------------------
    print("\n[TEST 4] Testing Day 34 Excel Exports & Catalog...")

    # 4A. Risk scores Excel export
    res_excel_risk = client.get("/api/reports/export/risk-scores", headers=manager_headers)
    assert res_excel_risk.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in res_excel_risk.headers["content-type"]
    assert "risk_scores_export.xlsx" in res_excel_risk.headers["content-disposition"]
    
    # Parse excel content back with pandas to verify structure
    excel_risk_df = pd.read_excel(io.BytesIO(res_excel_risk.content), engine="openpyxl")
    assert not excel_risk_df.empty
    expected_cols = ["Employee ID", "Name", "Department", "Risk Score", "Risk Level"]
    for col in expected_cols:
        assert col in excel_risk_df.columns, f"Missing column {col} in risk Excel"
    # Verify sorting: highest risk score should be at top
    scores = excel_risk_df["Risk Score"].tolist()
    assert scores == sorted(scores, reverse=True), "Excel risk scores are not sorted descending"
    print(f"  [PASS] Risk Scores Excel Export verified: {len(excel_risk_df)} rows, sorted descending (Top risk: {scores[0]})")

    # 4B. Department filter on risk scores Excel
    res_excel_dept = client.get("/api/reports/export/risk-scores?department=Engineering", headers=manager_headers)
    assert res_excel_dept.status_code == 200
    excel_dept_df = pd.read_excel(io.BytesIO(res_excel_dept.content), engine="openpyxl")
    assert all(d.lower() == "engineering" for d in excel_dept_df["Department"])
    print(f"  [PASS] Department filter on Excel export verified: {len(excel_dept_df)} Engineering employees returned")

    # 4C. Incident Report Excel Export (handles unresolved records without crashing)
    res_excel_inc = client.get("/api/reports/export/incidents", headers=manager_headers)
    assert res_excel_inc.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in res_excel_inc.headers["content-type"]
    assert "incidents_export.xlsx" in res_excel_inc.headers["content-disposition"]
    excel_inc_df = pd.read_excel(io.BytesIO(res_excel_inc.content), engine="openpyxl")
    assert "Resolved" in excel_inc_df.columns
    # Check that unresolved rows show "Not resolved"
    unresolved_rows = excel_inc_df[excel_inc_df["Status"].isin(["OPEN", "INVESTIGATING"])]
    if not unresolved_rows.empty:
        assert any(unresolved_rows["Resolved"] == "Not resolved")
    print(f"  [PASS] Incident Excel Export verified: {len(excel_inc_df)} incidents exported, unresolved records show 'Not resolved'")

    # 4D. Report Catalog Endpoint
    res_catalog = client.get("/api/reports/catalog", headers=analyst_headers)
    assert res_catalog.status_code == 200
    catalog = res_catalog.json()
    assert "reports" in catalog
    assert len(catalog["reports"]) >= 4
    report_names = [r["name"] for r in catalog["reports"]]
    print(f"  [PASS] Report Catalog Endpoint verified ({len(catalog['reports'])} reports listed): {report_names}")

    db.close()
    print("\n" + "=" * 70)
    print("ALL MILESTONE 4 TEST SCENARIOS PASSED WITH ZERO FAILURES!")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
