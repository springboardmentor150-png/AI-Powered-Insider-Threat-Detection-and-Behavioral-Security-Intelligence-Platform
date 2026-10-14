"""
ITBIS - Milestone 2
Historical Activity Log Generator

Generates realistic employee activity data for:
- Day 10: Activity Log Ingestion
- Day 11-14: Behavioral Baselines
- Day 15-16: Rule-Based Anomaly Detection
- Day 17-18: Isolation Forest ML

Run from the backend directory:

python seed_activity_data.py
"""

import random
from datetime import datetime, timedelta

from dotenv import load_dotenv

from app.database import activity_logs_collection


load_dotenv()


# ============================================================
# Configuration
# ============================================================

EMPLOYEE_IDS = [
    "EMP1001",
    "EMP1002",
    "EMP1003",
    "EMP1004",
    "EMP1005",
    "EMP1006",
]

DAYS_OF_HISTORY = 45

GENERATED_BY = "seed_activity_data_v1"


# ============================================================
# Employee behavioral profiles
# ============================================================
#
# These profiles create different normal routines for each
# employee instead of making everyone behave identically.
#
# This is important because our project uses per-employee
# behavioral baselines.
# ============================================================

EMPLOYEE_PROFILES = {
    "EMP1001": {
        "login_hour": 9.0,
        "login_variation": 0.35,
        "devices": ["Laptop-01"],
        "applications": ["Chrome", "VS Code", "PostgreSQL"],
        "daily_activity": (5, 9),
        "transfer_mb": (20, 120),
    },

    "EMP1002": {
        "login_hour": 9.4,
        "login_variation": 0.30,
        "devices": ["Laptop-02"],
        "applications": ["Chrome", "Excel", "SAP"],
        "daily_activity": (6, 10),
        "transfer_mb": (30, 150),
    },

    "EMP1003": {
        "login_hour": 8.7,
        "login_variation": 0.25,
        "devices": ["Laptop-03", "Desktop-03"],
        "applications": ["Chrome", "VS Code", "Git"],
        "daily_activity": (7, 12),
        "transfer_mb": (40, 180),
    },

    "EMP1004": {
        "login_hour": 9.8,
        "login_variation": 0.40,
        "devices": ["Laptop-04"],
        "applications": ["Chrome", "Teams", "Excel"],
        "daily_activity": (4, 8),
        "transfer_mb": (15, 100),
    },

    "EMP1005": {
        "login_hour": 8.9,
        "login_variation": 0.30,
        "devices": ["Laptop-05"],
        "applications": ["Chrome", "Python", "VS Code"],
        "daily_activity": (8, 13),
        "transfer_mb": (50, 220),
    },

    "EMP1006": {
        "login_hour": 10.1,
        "login_variation": 0.45,
        "devices": ["Laptop-06", "Desktop-06"],
        "applications": ["Chrome", "Salesforce", "Teams"],
        "daily_activity": (5, 9),
        "transfer_mb": (20, 130),
    },
}


# ============================================================
# Helper functions
# ============================================================

def random_timestamp_for_login(base_date, profile):
    """
    Generate a login timestamp around the employee's
    normal login hour.
    """

    login_hour = random.gauss(
        profile["login_hour"],
        profile["login_variation"]
    )

    # Keep generated login time inside a realistic range.
    login_hour = max(7.0, min(12.0, login_hour))

    hour = int(login_hour)
    minute = int((login_hour - hour) * 60)

    minute = max(0, min(59, minute))

    return datetime(
        base_date.year,
        base_date.month,
        base_date.day,
        hour,
        minute,
    )


def random_device(profile):
    return random.choice(profile["devices"])


def random_application(profile):
    return random.choice(profile["applications"])


def random_transfer_size(profile):
    low, high = profile["transfer_mb"]

    return round(
        random.uniform(low, high),
        2
    )


def create_log(employee_id, event_type, timestamp, details):
    """
    Create one MongoDB activity-log document.
    """

    return {
        "employee_id": employee_id,
        "event_type": event_type,
        "timestamp": timestamp,
        "details": details,
        "generated_by": GENERATED_BY,
    }


# ============================================================
# Generate one employee's activity
# ============================================================

def generate_employee_logs(employee_id, start_date):
    """
    Generate historical activity for one employee.
    """

    profile = EMPLOYEE_PROFILES[employee_id]

    logs = []

    for day_offset in range(DAYS_OF_HISTORY):

        current_date = start_date + timedelta(days=day_offset)

        # ----------------------------------------------------
        # Skip some weekend activity
        # ----------------------------------------------------

        is_weekend = current_date.weekday() >= 5

        if is_weekend:
            # Employees occasionally work on weekends,
            # but much less frequently.
            if random.random() > 0.20:
                continue

        # ----------------------------------------------------
        # 1. LOGIN EVENT
        # ----------------------------------------------------

        login_time = random_timestamp_for_login(
            current_date,
            profile
        )

        device = random_device(profile)

        logs.append(
            create_log(
                employee_id=employee_id,
                event_type="login",
                timestamp=login_time,
                details={
                    "device": device
                },
            )
        )

        # ----------------------------------------------------
        # Number of normal daily activities
        # ----------------------------------------------------

        min_activity, max_activity = profile["daily_activity"]

        if is_weekend:
            min_activity = max(1, min_activity // 3)
            max_activity = max(2, max_activity // 3)

        activity_count = random.randint(
            min_activity,
            max_activity
        )

        # ----------------------------------------------------
        # 2. APPLICATION USAGE
        # ----------------------------------------------------

        for _ in range(activity_count // 3):

            activity_time = login_time + timedelta(
                minutes=random.randint(20, 120)
            )

            logs.append(
                create_log(
                    employee_id=employee_id,
                    event_type="application_usage",
                    timestamp=activity_time,
                    details={
                        "device": random_device(profile),
                        "application": random_application(profile),
                    },
                )
            )

        # ----------------------------------------------------
        # 3. FILE DOWNLOADS
        # ----------------------------------------------------

        download_count = random.randint(1, 3)

        for _ in range(download_count):

            activity_time = login_time + timedelta(
                minutes=random.randint(30, 240)
            )

            logs.append(
                create_log(
                    employee_id=employee_id,
                    event_type="file_download",
                    timestamp=activity_time,
                    details={
                        "device": random_device(profile),
                        "size_mb": random_transfer_size(profile),
                    },
                )
            )

        # ----------------------------------------------------
        # 4. FILE UPLOADS
        # ----------------------------------------------------

        upload_count = random.randint(0, 2)

        for _ in range(upload_count):

            activity_time = login_time + timedelta(
                minutes=random.randint(45, 300)
            )

            logs.append(
                create_log(
                    employee_id=employee_id,
                    event_type="file_upload",
                    timestamp=activity_time,
                    details={
                        "device": random_device(profile),
                        "size_mb": round(
                            random_transfer_size(profile) * 0.5,
                            2,
                        ),
                    },
                )
            )

        # ----------------------------------------------------
        # 5. DATA TRANSFER
        # ----------------------------------------------------

        transfer_count = random.randint(0, 2)

        for _ in range(transfer_count):

            activity_time = login_time + timedelta(
                minutes=random.randint(60, 360)
            )

            logs.append(
                create_log(
                    employee_id=employee_id,
                    event_type="data_transfer",
                    timestamp=activity_time,
                    details={
                        "device": random_device(profile),
                        "size_mb": random_transfer_size(profile),
                    },
                )
            )

    return logs


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("ITBIS - Historical Activity Data Generator")
    print("=" * 60)

    # --------------------------------------------------------
    # Make the script safe to run multiple times.
    #
    # Only remove documents generated by THIS script.
    # Your manually inserted activity logs are preserved.
    # --------------------------------------------------------

    deleted = activity_logs_collection.delete_many(
        {
            "generated_by": GENERATED_BY
        }
    )

    print(
        f"Removed {deleted.deleted_count} previous generated logs."
    )

    # --------------------------------------------------------
    # Fixed seed makes the generated dataset reproducible.
    # --------------------------------------------------------

    random.seed(42)

    # --------------------------------------------------------
    # Start history 45 days before today.
    # --------------------------------------------------------

    today = datetime.utcnow().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    start_date = today - timedelta(
        days=DAYS_OF_HISTORY - 1
    )

    all_logs = []

    # --------------------------------------------------------
    # Generate logs for every seeded employee.
    # --------------------------------------------------------

    for employee_id in EMPLOYEE_IDS:

        employee_logs = generate_employee_logs(
            employee_id,
            start_date
        )

        all_logs.extend(employee_logs)

        print(
            f"{employee_id}: "
            f"{len(employee_logs)} activity logs generated"
        )

    # --------------------------------------------------------
    # Insert into MongoDB.
    # --------------------------------------------------------

    if all_logs:

        result = activity_logs_collection.insert_many(
            all_logs
        )

        print()
        print(
            f"Inserted {len(result.inserted_ids)} "
            "activity logs into MongoDB."
        )

    print()
    print("=" * 60)
    print("Activity data generation complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()