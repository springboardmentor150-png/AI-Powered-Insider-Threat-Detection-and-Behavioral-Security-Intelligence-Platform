from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo

from app.database import SessionLocal
from app.models import Employee, Incident, Alert
from app.mongo import (
    activity_logs,
    behavioral_baselines,
    rule_anomalies,
    ml_anomalies,
)
from app.ml_features import build_feature_table
from app.ml_anomaly import train_anomaly_model, score_anomalies
from app.risk_scoring import calculate_risk_score
from app.alert_service import generate_alerts
from app.anomaly_detection import (
    check_unusual_login_time,
    check_abnormal_data_transfer,
    check_excessive_resource_access,
    check_unknown_device,
    check_unknown_application,
)

INDIA_TZ = ZoneInfo("Asia/Kolkata")

def main():
    db = SessionLocal()
    print("--- 1. INSERTING 3 EMPLOYEES INTO POSTGRESQL ---")
    
    new_employees_data = [
        {
            "employee_code": "EMP005",
            "name": "Rajesh Kulkarni",
            "department": "IT",
            "role": "Cloud Security Architect",
            "email": "rajesh.kulkarni@threatintel.local",
        },
        {
            "employee_code": "EMP006",
            "name": "Ananya Iyer",
            "department": "Marketing",
            "role": "Digital Campaign Lead",
            "email": "ananya.iyer@threatintel.local",
        },
        {
            "employee_code": "EMP007",
            "name": "Kabir Singh",
            "department": "Finance",
            "role": "Senior Payroll Specialist",
            "email": "kabir.singh@threatintel.local",
        },
    ]
    
    created_employees = {}
    for data in new_employees_data:
        emp = db.query(Employee).filter(Employee.employee_code == data["employee_code"]).first()
        if not emp:
            emp = Employee(**data)
            db.add(emp)
            db.commit()
            db.refresh(emp)
            print(f"Created: {emp.employee_code} - {emp.name} (ID: {emp.id})")
        else:
            print(f"Existing: {emp.employee_code} - {emp.name} (ID: {emp.id})")
        created_employees[emp.employee_code] = emp

    print("\n--- 2. CREATING BEHAVIORAL BASELINES IN MONGODB ---")
    baselines_spec = {
        "EMP005": [
            {"indicator": "login_time", "typical_value": 9.25, "normal_range": 0.20, "sample_size": 15},
            {"indicator": "resource_access_frequency", "typical_value": 1, "normal_range": 0.0, "sample_size": 15},
            {"indicator": "data_transfer_volume", "typical_value": 14.50, "normal_range": 4.50, "sample_size": 15},
            {"indicator": "device_usage", "known_values": ["DEVICE-RAJESH-01", "DEVICE-RAJESH-02"], "sample_size": 2},
            {"indicator": "application_usage", "known_values": ["AWS Console", "Chrome", "Git", "Login Service", "VS Code"], "sample_size": 5},
        ],
        "EMP006": [
            {"indicator": "login_time", "typical_value": 9.75, "normal_range": 0.35, "sample_size": 15},
            {"indicator": "resource_access_frequency", "typical_value": 1, "normal_range": 0.0, "sample_size": 15},
            {"indicator": "data_transfer_volume", "typical_value": 32.00, "normal_range": 12.00, "sample_size": 15},
            {"indicator": "device_usage", "known_values": ["DEVICE-ANANYA-LAPTOP", "DEVICE-ANANYA-MOBILE"], "sample_size": 2},
            {"indicator": "application_usage", "known_values": ["Adobe Creative Cloud", "Chrome", "Figma", "Login Service", "Microsoft Teams"], "sample_size": 5},
        ],
        "EMP007": [
            {"indicator": "login_time", "typical_value": 8.90, "normal_range": 0.15, "sample_size": 15},
            {"indicator": "resource_access_frequency", "typical_value": 1, "normal_range": 0.0, "sample_size": 15},
            {"indicator": "data_transfer_volume", "typical_value": 16.00, "normal_range": 5.00, "sample_size": 15},
            {"indicator": "device_usage", "known_values": ["DEVICE-KABIR-WORKSTATION"], "sample_size": 1},
            {"indicator": "application_usage", "known_values": ["Chrome", "ERP Finance", "Login Service", "Microsoft Excel"], "sample_size": 4},
        ],
    }

    now_utc = datetime.now(timezone.utc)
    for code, bl_list in baselines_spec.items():
        for bl in bl_list:
            doc = {**bl, "employee_code": code, "last_updated": now_utc}
            behavioral_baselines.update_one(
                {"employee_code": code, "indicator": bl["indicator"]},
                {"$set": doc},
                upsert=True,
            )
        print(f"Baselines established for {code}")

    print("\n--- 3. GENERATING REALISTIC ACTIVITY TELEMETRY ---")
    for code in ["EMP005", "EMP006", "EMP007"]:
        activity_logs.delete_many({"employee_code": code})
        rule_anomalies.delete_many({"employee_code": code})

    base_date = date(2026, 9, 20)
    all_logs_to_insert = []
    
    # 3.1 EMP005: Rajesh Kulkarni (Normal / Low Risk)
    for day_offset in range(20):
        d = base_date + timedelta(days=day_offset)
        login_time = datetime(d.year, d.month, d.day, 9, 15 + (day_offset % 10), 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
        all_logs_to_insert.append({
            "employee_code": "EMP005",
            "event_type": "login",
            "source": "web",
            "ip_address": "192.168.10.45",
            "application": "Login Service",
            "device_id": "DEVICE-RAJESH-01",
            "risk_score": 5,
            "timestamp": login_time,
        })
        git_time = datetime(d.year, d.month, d.day, 11, 30, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
        all_logs_to_insert.append({
            "employee_code": "EMP005",
            "event_type": "resource_access",
            "source": "terminal",
            "resource": "repo/cloud-infra",
            "application": "Git",
            "device_id": "DEVICE-RAJESH-01",
            "risk_score": 5,
            "timestamp": git_time,
        })
        transfer_time = datetime(d.year, d.month, d.day, 16, 20, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
        all_logs_to_insert.append({
            "employee_code": "EMP005",
            "event_type": "data_transfer",
            "source": "cloud",
            "data_volume_mb": round(12.0 + (day_offset % 5), 2),
            "application": "AWS Console",
            "device_id": "DEVICE-RAJESH-01",
            "risk_score": 5,
            "timestamp": transfer_time,
        })

    # 3.2 EMP006: Ananya Iyer (Moderate / Marketing Campaign Lead)
    for day_offset in range(20):
        d = base_date + timedelta(days=day_offset)
        login_hour = 9 if day_offset % 4 != 0 else 10
        login_min = 40 + (day_offset % 15)
        login_time = datetime(d.year, d.month, d.day, login_hour, min(59, login_min), 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
        all_logs_to_insert.append({
            "employee_code": "EMP006",
            "event_type": "login",
            "source": "web",
            "ip_address": "192.168.20.12",
            "application": "Login Service",
            "device_id": "DEVICE-ANANYA-LAPTOP",
            "risk_score": 10,
            "timestamp": login_time,
        })
        vol = 85.0 if day_offset == 15 else round(30.0 + (day_offset % 15), 2)
        transfer_time = datetime(d.year, d.month, d.day, 14, 15, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
        all_logs_to_insert.append({
            "employee_code": "EMP006",
            "event_type": "data_transfer",
            "source": "web",
            "data_volume_mb": vol,
            "application": "Figma",
            "device_id": "DEVICE-ANANYA-LAPTOP",
            "risk_score": 15 if vol > 50 else 10,
            "timestamp": transfer_time,
        })

    # 3.3 EMP007: Kabir Singh (Insider Threat Actor - Severe Anomaly & Exfiltration)
    for day_offset in range(20):
        d = base_date + timedelta(days=day_offset)
        is_malicious_phase = (day_offset >= 16)

        if not is_malicious_phase:
            login_time = datetime(d.year, d.month, d.day, 8, 55, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs_to_insert.append({
                "employee_code": "EMP007",
                "event_type": "login",
                "source": "desktop",
                "ip_address": "192.168.30.5",
                "application": "Login Service",
                "device_id": "DEVICE-KABIR-WORKSTATION",
                "risk_score": 5,
                "timestamp": login_time,
            })
            transfer_time = datetime(d.year, d.month, d.day, 15, 30, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs_to_insert.append({
                "employee_code": "EMP007",
                "event_type": "data_transfer",
                "source": "desktop",
                "data_volume_mb": round(15.0 + (day_offset % 4), 2),
                "application": "Microsoft Excel",
                "device_id": "DEVICE-KABIR-WORKSTATION",
                "risk_score": 5,
                "timestamp": transfer_time,
            })
        else:
            night_login = datetime(d.year, d.month, d.day, 1, 45, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs_to_insert.append({
                "employee_code": "EMP007",
                "event_type": "login",
                "source": "vpn",
                "ip_address": "185.220.101.4",
                "application": "Login Service",
                "device_id": "DEVICE-UNREGISTERED-MAC",
                "risk_score": 90,
                "timestamp": night_login,
            })
            tool_time = datetime(d.year, d.month, d.day, 2, 10, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs_to_insert.append({
                "employee_code": "EMP007",
                "event_type": "resource_access",
                "source": "desktop",
                "resource": "db/payroll-ledger-2026.sql",
                "application": "Tor Browser",
                "device_id": "USB-SANDISK-SECURE",
                "risk_score": 95,
                "timestamp": tool_time,
            })
            exfil_vol = 850.0 + (day_offset - 16) * 150.0
            exfil_time = datetime(d.year, d.month, d.day, 2, 40, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs_to_insert.append({
                "employee_code": "EMP007",
                "event_type": "data_transfer",
                "source": "external_storage",
                "data_volume_mb": exfil_vol,
                "application": "7-Zip Encryptor",
                "device_id": "USB-SANDISK-SECURE",
                "risk_score": 98,
                "timestamp": exfil_time,
            })

    activity_logs.insert_many(all_logs_to_insert)
    print(f"Inserted {len(all_logs_to_insert)} activity logs across all 3 employees.")

    print("\n--- 4. RUNNING RULE-BASED ANOMALY DETECTION CHECKS ---")
    detected_rule_anomalies = []
    for log in all_logs_to_insert:
        emp_code = log["employee_code"]
        ts = log["timestamp"].astimezone(INDIA_TZ)
        hour_float = ts.hour + ts.minute / 60.0

        if log.get("event_type") == "login":
            anom = check_unusual_login_time(emp_code, hour_float)
            if anom: detected_rule_anomalies.append(anom)
            
        if log.get("device_id"):
            anom = check_unknown_device(emp_code, log["device_id"])
            if anom: detected_rule_anomalies.append(anom)

        if log.get("application"):
            anom = check_unknown_application(emp_code, log["application"])
            if anom: detected_rule_anomalies.append(anom)

        if log.get("data_volume_mb", 0) > 0:
            anom = check_abnormal_data_transfer(emp_code, log["data_volume_mb"])
            if anom: detected_rule_anomalies.append(anom)

    print(f"Generated {len(detected_rule_anomalies)} rule-based anomalies in MongoDB.")

    print("\n--- 5. TRAINING MACHINE LEARNING ISOLATION FOREST MODEL ---")
    features = build_feature_table()
    print(f"Feature table built: {len(features)} employee-per-day rows across all workforce personnel.")
    
    model = train_anomaly_model(features)
    scored = score_anomalies(model, features)
    print("Scored all feature vectors with Isolation Forest.")

    ml_anomalies.delete_many({})
    records = scored.to_dict(orient="records")
    for r in records:
        for k, v in list(r.items()):
            if isinstance(v, (date, datetime)):
                r[k] = v.isoformat()
    if records:
        ml_anomalies.insert_many(records)
    print(f"Persisted {len(records)} scored ML anomaly records into MongoDB.")

    print("\n--- 6. CALCULATING RISK SCORES FOR NEW EMPLOYEES ---")
    for code in ["EMP005", "EMP006", "EMP007"]:
        risk = calculate_risk_score(code, db)
        print(f"  {code} ({created_employees[code].name}): Final Score = {risk['final_score']} | Risk Level = {risk['risk_level']}")
        for factor, val in risk["factor_scores"].items():
            print(f"     * {factor}: {val}")

    print("\n--- 7. RUNNING AUTONOMOUS ALERT AND INCIDENT GENERATION SWEEP ---")
    alert_sweep_res = generate_alerts(db)
    print("Alert Sweep Output:", alert_sweep_res)

    for code in ["EMP005", "EMP006", "EMP007"]:
        emp = created_employees[code]
        inc_count = db.query(Incident).filter(Incident.employee_id == emp.id).count()
        al_count = db.query(Alert).filter(Alert.employee_id == emp.id).count()
        print(f"  {code} ({emp.name}): {inc_count} Incident(s), {al_count} Alert(s)")

    db.close()
    print("\nALL ENTRIES AND PIPELINES SUCCESSFULLY CREATED AND VERIFIED!")

if __name__ == "__main__":
    main()
