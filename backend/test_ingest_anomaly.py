from datetime import datetime

from app.rule_anomaly_detection import ingest_log_and_check


employee_id = "EMP1001"


# ---------------------------------------------------------
# Test 1: Normal login
# ---------------------------------------------------------

normal_login = {
    "employee_id": employee_id,
    "event_type": "login",
    "timestamp": datetime.now().replace(
        hour=9,
        minute=0,
        second=0,
        microsecond=0,
    ),
    "details": {
        "device": "Laptop-01",
    },
}

print("\n========== NORMAL LOGIN ==========")

result = ingest_log_and_check(normal_login)

print(result)


# ---------------------------------------------------------
# Test 2: Abnormal login
# ---------------------------------------------------------

abnormal_login = {
    "employee_id": employee_id,
    "event_type": "login",
    "timestamp": datetime.now().replace(
        hour=15,
        minute=0,
        second=0,
        microsecond=0,
    ),
    "details": {
        "device": "Laptop-01",
    },
}

print("\n========== ABNORMAL LOGIN ==========")

result = ingest_log_and_check(abnormal_login)

print(result)


# ---------------------------------------------------------
# Test 3: Unknown device
# ---------------------------------------------------------

unknown_device = {
    "employee_id": employee_id,
    "event_type": "application_usage",
    "timestamp": datetime.now(),
    "details": {
        "device": "Unknown-Laptop",
        "application": "VS Code",
    },
}

print("\n========== UNKNOWN DEVICE ==========")

result = ingest_log_and_check(unknown_device)

print(result)