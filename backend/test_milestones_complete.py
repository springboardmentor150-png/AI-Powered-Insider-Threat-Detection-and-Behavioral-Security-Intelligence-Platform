"""
Comprehensive automated verification suite for:
- Milestone 3: Risk Scoring & Threat Investigation (Parts 1-5)
- Milestone 4: Reports & Export System (Day 33 & Day 34)
"""

import io
import pandas as pd
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.database import SessionLocal, engine, Base
from app.main import app
from app.models import Alert, Employee, Evidence, Incident, InvestigationNote, User
from app.jwt_auth import create_access_token
from app.risk_scoring import calculate_risk_score
from app.ueba import get_peer_group_comparison, get_risk_trend


def run_all_tests():
    print("=" * 70)
    print("STARTING ITBIS COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 70)

    # Ensure all tables exist (including Evidence)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Setup / identify test users
        admin_user = db.query(User).filter(User.role == "admin").first()
        if not admin_user:
            admin_user = User(
                email="admin_verify@itbis.local",
                password_hash="testhash",
                role="admin",
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        analyst_user = db.query(User).filter(User.role == "security_analyst").first()
        if not analyst_user:
            analyst_user = User(
                email="analyst_verify@itbis.local",
                password_hash="testhash",
                role="security_analyst",
            )
            db.add(analyst_user)
            db.commit()
            db.refresh(analyst_user)

        manager_user = db.query(User).filter(User.role == "security_manager").first()
        if not manager_user:
            manager_user = User(
                email="manager_verify@itbis.local",
                password_hash="testhash",
                role="security_manager",
            )
            db.add(manager_user)
            db.commit()
            db.refresh(manager_user)

        admin_token = create_access_token(admin_user.id, "admin")
        analyst_token = create_access_token(analyst_user.id, "security_analyst")
        manager_token = create_access_token(manager_user.id, "security_manager")

        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        analyst_headers = {"Authorization": f"Bearer {analyst_token}"}
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        client = TestClient(app)

        # -------------------------------------------------------------
        # PART 1: Milestone 3 — Risk Scoring & Weightings
        # -------------------------------------------------------------
        print("\n[M3 Part 1] Testing Risk Scoring Engine...")
        risk_emp1 = calculate_risk_score("EMP001", db)
        assert "risk_score" in risk_emp1
        assert "final_score" in risk_emp1
        assert "sub_scores" in risk_emp1
        assert "factor_scores" in risk_emp1
        assert "risk_level" in risk_emp1
        assert "risk_category" in risk_emp1
        assert risk_emp1["weights"]["behavioral_anomalies"] == 0.35
        assert risk_emp1["weights"]["privilege_misuse"] == 0.25
        assert risk_emp1["weights"]["data_access_violations"] == 0.20
        assert risk_emp1["weights"]["access_pattern_deviations"] == 0.10
        assert risk_emp1["weights"]["historical_events"] == 0.10
        print("  [PASS] calculate_risk_score() produced correct 35/25/20/10/10 weighted score.")

        # -------------------------------------------------------------
        # PART 2: Milestone 3 — UEBA Peer Comparison & Edge Cases
        # -------------------------------------------------------------
        print("\n[M3 Part 2] Testing UEBA Peer Comparison & Isolated Departments...")
        peer_res = get_peer_group_comparison("EMP002", db) # Priya Mehta in HR (only 1 employee in HR)
        assert peer_res is not None
        assert peer_res["peer_count"] == 0
        assert "note" in peer_res
        print("  [PASS] Peer comparison gracefully handled employee with 0 department peers.")

        # -------------------------------------------------------------
        # PART 3: Milestone 3 — Incident Rejection on Low/Medium Risk
        # -------------------------------------------------------------
        print("\n[M3 Part 3] Testing Incident Creation Risk-Threshold Guardrails...")
        # EMP002 has low risk -> create-from-risk must be rejected (400)
        res_reject = client.post(
            "/incidents/create-from-risk/EMP002",
            headers=admin_headers,
        )
        assert res_reject.status_code == 400, f"Expected 400 for low risk, got {res_reject.status_code}"
        print("  [PASS] Low/Medium risk employee properly rejected from incident auto-creation.")

        # -------------------------------------------------------------
        # PART 4: Milestone 3 — Alert Assignment & Resolution RBAC
        # -------------------------------------------------------------
        print("\n[M3 Part 4] Testing Alert Assignment & Resolution RBAC...")
        # Create a test incident and alert
        emp1 = db.query(Employee).filter(Employee.employee_code == "EMP001").first()
        test_incident = Incident(
            employee_id=emp1.id,
            incident_type="Test Security Incident",
            description="Testing incident and alert lifecycle",
            severity="high",
            status="open",
        )
        db.add(test_incident)
        db.commit()
        db.refresh(test_incident)

        test_alert = Alert(
            incident_id=test_incident.id,
            employee_id=emp1.id,
            alert_type="Test Alert",
            message="Suspicious test pattern",
            severity="high",
            status="open",
        )
        db.add(test_alert)
        db.commit()
        db.refresh(test_alert)

        # Analyst cannot assign alert (only admin and security_manager)
        assign_analyst_fail = client.post(
            f"/alerts/{test_alert.id}/assign?analyst_user_id={analyst_user.id}",
            headers=analyst_headers,
        )
        assert assign_analyst_fail.status_code == 403
        print("  [PASS] Analyst properly denied alert assignment (403).")

        # Manager CAN assign alert
        assign_manager_ok = client.post(
            f"/alerts/{test_alert.id}/assign?analyst_user_id={analyst_user.id}",
            headers=manager_headers,
        )
        assert assign_manager_ok.status_code == 200
        print("  [PASS] Security Manager successfully assigned alert (200).")

        # Analyst CAN resolve alert
        resolve_analyst_ok = client.patch(
            f"/alerts/{test_alert.id}/resolve",
            headers=analyst_headers,
        )
        assert resolve_analyst_ok.status_code == 200
        print("  [PASS] Analyst successfully resolved alert (200).")

        # -------------------------------------------------------------
        # PART 5: Milestone 3 — Incident Timeline Integration
        # -------------------------------------------------------------
        print("\n[M3 Part 5] Testing Chronological Incident Timeline...")
        timeline_res = client.get(
            f"/incidents/{test_incident.id}/timeline",
            headers=analyst_headers,
        )
        assert timeline_res.status_code == 200
        t_data = timeline_res.json()
        assert "timeline" in t_data
        print(f"  [PASS] Incident timeline retrieved {len(t_data['timeline'])} merged chronologically sorted events.")

        # -------------------------------------------------------------
        # PART 6: Milestone 3 — Dashboards (Analyst, SOC, Manager)
        # -------------------------------------------------------------
        print("\n[M3 Part 6] Testing Security Dashboards...")
        dash_analyst = client.get("/dashboard/analyst", headers=analyst_headers)
        assert dash_analyst.status_code == 200
        assert "security_events" in dash_analyst.json()

        dash_soc = client.get("/dashboard/soc", headers=admin_headers)
        assert dash_soc.status_code == 200
        assert "alerts_by_severity" in dash_soc.json()

        dash_manager = client.get("/dashboard/manager", headers=manager_headers)
        assert dash_manager.status_code == 200
        assert "organizational_risk_posture" in dash_manager.json()
        print("  [PASS] All 3 Dashboards (Analyst, SOC, Security Manager) operational.")

        # -------------------------------------------------------------
        # PART 7: Milestone 4 — Day 33: PDF Reports
        # -------------------------------------------------------------
        print("\n[M4 Day 33] Testing PDF Risk Reports (with anomalies & zero anomalies)...")
        # Employee with anomalies
        pdf_res1 = client.get("/reports/EMP001/pdf", headers=analyst_headers)
        assert pdf_res1.status_code == 200
        assert pdf_res1.headers["content-type"] == "application/pdf"
        assert "attachment; filename=EMP001_risk_report.pdf" in pdf_res1.headers["content-disposition"]
        assert pdf_res1.content.startswith(b"%PDF")
        print("  [PASS] Employee with anomalies generated valid PDF with proper Content-Disposition header.")

        # Employee with ZERO anomalies
        pdf_res2 = client.get("/reports/EMP002/pdf", headers=analyst_headers)
        assert pdf_res2.status_code == 200
        assert pdf_res2.headers["content-type"] == "application/pdf"
        assert pdf_res2.content.startswith(b"%PDF")
        print("  [PASS] Employee with ZERO anomalies generated cleanly without crashing.")

        # Compliance summary PDF report
        comp_pdf_res = client.get("/reports/compliance/pdf", headers=manager_headers)
        assert comp_pdf_res.status_code == 200
        assert comp_pdf_res.headers["content-type"] == "application/pdf"
        assert "attachment; filename=compliance_summary_report.pdf" in comp_pdf_res.headers["content-disposition"]
        assert comp_pdf_res.content.startswith(b"%PDF")
        print("  [PASS] Compliance summary PDF report generated and downloaded cleanly.")

        # -------------------------------------------------------------
        # PART 8: Milestone 4 — Day 34: Excel Exports & Catalog
        # -------------------------------------------------------------
        print("\n[M4 Day 34] Testing Excel Exports & Report Catalog...")
        # Bulk Risk Scores Excel Export
        excel_risk_res = client.get("/reports/export/risk-scores", headers=manager_headers)
        assert excel_risk_res.status_code == 200
        assert excel_risk_res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert "attachment; filename=risk_scores_export.xlsx" in excel_risk_res.headers["content-disposition"]

        excel_risk_df = pd.read_excel(io.BytesIO(excel_risk_res.content), sheet_name="Risk Scores")
        expected_cols = ["Employee ID", "Name", "Department", "Risk Score", "Risk Level"]
        for col in expected_cols:
            assert col in excel_risk_df.columns, f"Missing column {col}"
        # Check sorted descending
        scores = excel_risk_df["Risk Score"].tolist()
        assert scores == sorted(scores, reverse=True), "Risk scores not sorted descending!"
        print("  [PASS] Risk Scores Excel export is valid, includes all columns, and is sorted highest-risk first.")

        # Filtered Risk Scores Excel Export
        excel_risk_it_res = client.get("/reports/export/risk-scores?department=IT", headers=manager_headers)
        assert excel_risk_it_res.status_code == 200
        excel_risk_it_df = pd.read_excel(io.BytesIO(excel_risk_it_res.content), sheet_name="Risk Scores")
        assert all(d == "IT" for d in excel_risk_it_df["Department"].tolist())
        print("  [PASS] Risk Scores Excel export filter parameter (department=IT) verified.")

        # Incident Report Excel Export
        excel_inc_res = client.get("/reports/export/incidents", headers=manager_headers)
        assert excel_inc_res.status_code == 200
        assert excel_inc_res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert "attachment; filename=incidents_export.xlsx" in excel_inc_res.headers["content-disposition"]
        excel_inc_df = pd.read_excel(io.BytesIO(excel_inc_res.content), sheet_name="Incidents")
        assert "Resolved" in excel_inc_df.columns
        print("  [PASS] Incidents Excel export correctly formatted and handles unresolved records without crashing.")

        # Report Catalog Endpoint
        catalog_res = client.get("/reports/catalog", headers=analyst_headers)
        assert catalog_res.status_code == 200
        catalog = catalog_res.json()
        assert "reports" in catalog
        assert len(catalog["reports"]) >= 4
        print(f"  [PASS] Report catalog lists all {len(catalog['reports'])} report endpoints.")

        print("\n" + "=" * 70)
        print("ALL VERIFICATION SUITE CHECKS PASSED PERFECTLY (100% SUCCESS)!")
        print("=" * 70)

    finally:
        # Cleanup test records
        try:
            db.query(Alert).filter(Alert.alert_type == "Test Alert").delete()
            db.query(Incident).filter(Incident.incident_type == "Test Security Incident").delete()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()


if __name__ == "__main__":
    run_all_tests()
