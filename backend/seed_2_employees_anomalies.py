"""
seed_2_employees_anomalies.py
Inserts 2 employees:
1. EMP008 (Rohan Patel) - Medium anomalies (elevated off-hours access, second home device, moderate data spikes)
2. EMP009 (Deepika Sen) - High anomalies (critical off-hours logins, rogue tools, massive exfiltration transfers)
Retrains Isolation Forest, scores feature vectors, calculates risk scores, and generates alerts/incidents.
"""

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
    check_unknown_device,
    check_unknown_application,
)

INDIA_TZ = ZoneInfo("Asia/Kolkata")

def main():
    db = SessionLocal()
    print("--- 1. INSERTING EMPLOYEES EMP008 & EMP009 INTO POSTGRESQL ---")
    
    new_employees = [
        {
            "employee_code": "EMP008",
            "name": "Rohan Patel",
            "department": "Sales",
            "role": "Enterprise Account Executive",
            "email": "rohan.patel@threatintel.local",
        },
        {
            "employee_code": "EMP009",
            "name": "Deepika Sen",
            "department": "Engineering",
            "role": "Principal DevOps Engineer",
            "email": "deepika.sen@threatintel.local",
        },
    ]

    created = {}
    for data in new_employees:
        emp = db.query(Employee).filter(Employee.employee_code == data["employee_code"]).first()
        if not emp:
            emp = Employee(**data)
            db.add(emp)
            db.commit()
            db.refresh(emp)
            print(f"Created: {emp.employee_code} - {emp.name} (ID: {emp.id})")
        else:
            print(f"Existing: {emp.employee_code} - {emp.name} (ID: {emp.id})")
        created[emp.employee_code] = emp

    print("\n--- 2. CONFIGURING BEHAVIORAL BASELINES IN MONGODB ---")
    baselines_spec = {
        "EMP008": [
            {"indicator": "login_time", "typical_value": 9.10, "normal_range": 0.25, "sample_size": 15},
            {"indicator": "resource_access_frequency", "typical_value": 1, "normal_range": 0.0, "sample_size": 15},
            {"indicator": "data_transfer_volume", "typical_value": 20.00, "normal_range": 8.00, "sample_size": 15},
            {"indicator": "device_usage", "known_values": ["DEVICE-ROHAN-WORK-LAPTOP"], "sample_size": 1},
            {"indicator": "application_usage", "known_values": ["Salesforce CRM", "Chrome", "Microsoft Outlook", "Login Service"], "sample_size": 4},
        ],
        "EMP009": [
            {"indicator": "login_time", "typical_value": 9.40, "normal_range": 0.20, "sample_size": 15},
            {"indicator": "resource_access_frequency", "typical_value": 1, "normal_range": 0.0, "sample_size": 15},
            {"indicator": "data_transfer_volume", "typical_value": 25.00, "normal_range": 10.00, "sample_size": 15},
            {"indicator": "device_usage", "known_values": ["DEVICE-DEEPIKA-UBUNTU"], "sample_size": 1},
            {"indicator": "application_usage", "known_values": ["Kubernetes CLI", "Chrome", "GitLab", "VS Code", "Login Service"], "sample_size": 5},
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
    for code in ["EMP008", "EMP009"]:
        emp = created[code]
        db.query(Alert).filter(Alert.employee_id == emp.id).delete()
        db.query(Incident).filter(Incident.employee_id == emp.id).delete()
        db.commit()
        activity_logs.delete_many({"employee_code": code})
        rule_anomalies.delete_many({"employee_code": code})

    base_date = date(2026, 9, 20)
    all_logs = []

    # 3.1 EMP008: Rohan Patel - MEDIUM ANOMALIES
    # Standard sales workflow, but has 2 days with evening work on personal device & moderate data download spikes
    for day_offset in range(20):
        d = base_date + timedelta(days=day_offset)
        has_evening_shift = (day_offset in [10, 15])

        if not has_evening_shift:
            # Normal business day
            login_time = datetime(d.year, d.month, d.day, 9, 10 + (day_offset % 10), 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs.append({
                "employee_code": "EMP008",
                "event_type": "login",
                "source": "web",
                "ip_address": "192.168.40.15",
                "application": "Login Service",
                "device_id": "DEVICE-ROHAN-WORK-LAPTOP",
                "risk_score": 5,
                "timestamp": login_time,
            })
            transfer_time = datetime(d.year, d.month, d.day, 14, 30, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs.append({
                "employee_code": "EMP008",
                "event_type": "data_transfer",
                "source": "crm",
                "data_volume_mb": round(18.0 + (day_offset % 6), 2),
                "application": "Salesforce CRM",
                "device_id": "DEVICE-ROHAN-WORK-LAPTOP",
                "risk_score": 5,
                "timestamp": transfer_time,
            })
        else:
            # Moderate anomaly day: Late evening login at 21:45 PM + second device + elevated download (78 - 85 MB)
            evening_login = datetime(d.year, d.month, d.day, 21, 45, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs.append({
                "employee_code": "EMP008",
                "event_type": "login",
                "source": "vpn",
                "ip_address": "103.21.244.18",
                "application": "Login Service",
                "device_id": "DEVICE-ROHAN-HOME-PC", # Unfamiliar secondary device
                "risk_score": 35,
                "timestamp": evening_login,
            })
            elevated_vol = 78.5 + (day_offset % 6)
            transfer_time = datetime(d.year, d.month, d.day, 22, 15, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs.append({
                "employee_code": "EMP008",
                "event_type": "data_transfer",
                "source": "crm",
                "data_volume_mb": elevated_vol,
                "application": "Salesforce CRM",
                "device_id": "DEVICE-ROHAN-WORK-LAPTOP",
                "risk_score": 35,
                "timestamp": transfer_time,
            })

    # 3.2 EMP009: Deepika Sen - HIGH ANOMALIES (Severe Threat Exfiltration)
    for day_offset in range(20):
        d = base_date + timedelta(days=day_offset)
        is_high_threat = (day_offset >= 15) # Last 5 days are critical threat activities

        if not is_high_threat:
            # Normal DevOps work
            login_time = datetime(d.year, d.month, d.day, 9, 35, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs.append({
                "employee_code": "EMP009",
                "event_type": "login",
                "source": "desktop",
                "ip_address": "192.168.50.8",
                "application": "Login Service",
                "device_id": "DEVICE-DEEPIKA-UBUNTU",
                "risk_score": 5,
                "timestamp": login_time,
            })
            transfer_time = datetime(d.year, d.month, d.day, 15, 0, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs.append({
                "employee_code": "EMP009",
                "event_type": "data_transfer",
                "source": "repo",
                "data_volume_mb": round(22.0 + (day_offset % 8), 2),
                "application": "GitLab",
                "device_id": "DEVICE-DEEPIKA-UBUNTU",
                "risk_score": 5,
                "timestamp": transfer_time,
            })
        else:
            # High threat days:
            # 1. Midnight/off-hours login at 02:40 AM
            night_login = datetime(d.year, d.month, d.day, 2, 40, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs.append({
                "employee_code": "EMP009",
                "event_type": "login",
                "source": "vpn",
                "ip_address": "185.191.171.12",
                "application": "Login Service",
                "device_id": "DEVICE-ANONYMOUS-DROPBOX", # Rogue device
                "risk_score": 95,
                "timestamp": night_login,
            })
            # 2. Unauthorized tool usage and critical vault resource access
            tool_time = datetime(d.year, d.month, d.day, 3, 5, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs.append({
                "employee_code": "EMP009",
                "event_type": "resource_access",
                "source": "terminal",
                "resource": "vault/master-credentials.enc",
                "application": "MegaSync Uploader", # Rogue app
                "device_id": "DEVICE-ANONYMOUS-DROPBOX",
                "risk_score": 98,
                "timestamp": tool_time,
            })
            # 3. Massive exfiltration transfers (950 MB up to 1800 MB!)
            exfil_vol = 950.0 + (day_offset - 15) * 220.0
            exfil_time = datetime(d.year, d.month, d.day, 3, 30, 0, tzinfo=INDIA_TZ).astimezone(timezone.utc)
            all_logs.append({
                "employee_code": "EMP009",
                "event_type": "data_transfer",
                "source": "cloud_storage",
                "data_volume_mb": exfil_vol,
                "application": "MegaSync Uploader",
                "device_id": "DEVICE-ANONYMOUS-DROPBOX",
                "risk_score": 99,
                "timestamp": exfil_time,
            })

    activity_logs.insert_many(all_logs)
    print(f"Inserted {len(all_logs)} activity logs for EMP008 and EMP009.")

    print("\n--- 4. RUNNING RULE ANOMALY DETECTIONS ---")
    detected = []
    for log in all_logs:
        code = log["employee_code"]
        ts = log["timestamp"].astimezone(INDIA_TZ)
        hour_float = ts.hour + ts.minute / 60.0

        if log.get("event_type") == "login":
            a = check_unusual_login_time(code, hour_float)
            if a: detected.append(a)

        if log.get("device_id"):
            a = check_unknown_device(code, log["device_id"])
            if a: detected.append(a)

        if log.get("application"):
            a = check_unknown_application(code, log["application"])
            if a: detected.append(a)

        if log.get("data_volume_mb", 0) > 0:
            a = check_abnormal_data_transfer(code, log["data_volume_mb"])
            if a: detected.append(a)

    print(f"Detected {len(detected)} rule anomalies in MongoDB.")

    print("\n--- 5. RETRAINING ISOLATION FOREST ML MODEL ---")
    features = build_feature_table()
    print(f"Features built: {len(features)} employee-per-day rows across all employees.")

    model = train_anomaly_model(features)
    scored = score_anomalies(model, features)
    print("Scored all feature vectors.")

    ml_anomalies.delete_many({})
    records = scored.to_dict(orient="records")
    for r in records:
        for k, v in list(r.items()):
            if isinstance(v, (date, datetime)):
                r[k] = v.isoformat()
    if records:
        ml_anomalies.insert_many(records)
    print(f"Persisted {len(records)} scored ML anomaly records to MongoDB.")

    print("\n--- 6. CALCULATING RISK SCORES ---")
    for code in ["EMP008", "EMP009"]:
        risk = calculate_risk_score(code, db)
        print(f"  {code} ({created[code].name}): Final Score = {risk['final_score']} | Risk Level = {risk['risk_level']}")
        for f, val in risk["factor_scores"].items():
            print(f"     * {f}: {val}")

    print("\n--- 7. RUNNING ALERT & INCIDENT GENERATION SWEEP ---")
    sweep = generate_alerts(db)
    print("Alert Sweep Output:", sweep)

    for code in ["EMP008", "EMP009"]:
        emp = created[code]
        inc_count = db.query(Incident).filter(Incident.employee_id == emp.id).count()
        al_count = db.query(Alert).filter(Alert.employee_id == emp.id).count()
        print(f"  {code} ({emp.name}): {inc_count} Incident(s), {al_count} Alert(s)")

    db.close()
    print("\nALL 2 EMPLOYEES AND ASSOCIATED WORKFLOWS SUCCESSFULLY CONFIGURED!")

if __name__ == "__main__":
    main()
