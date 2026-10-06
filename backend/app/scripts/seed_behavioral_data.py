"""
ITBIS Milestone 2 - Behavioral Dataset Seeder

Purpose:
    Generate controlled and realistic behavioral activity history
    for the four employees currently registered in ITBIS.

Dataset design:
    - 40 records per employee
    - 160 Milestone 2 records total
    - Existing Milestone 1 records are preserved
    - Synthetic device IDs are used
    - Login behavior is generated in IST and stored in UTC
    - Activity fields are populated according to event meaning
    - Role-specific applications and resources are used

The generated records are development/training data.
They do not represent real employee activity.
"""

from datetime import datetime, timedelta, timezone
import random

from pymongo import MongoClient


# ============================================================
# CONFIGURATION
# ============================================================

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "itbis"
COLLECTION_NAME = "activity_logs"

DATASET_SOURCE = "milestone_2_seed"

RECORDS_PER_EMPLOYEE = 40

RANDOM_SEED = 42

# India Standard Time = UTC + 5 hours 30 minutes.
IST = timezone(timedelta(hours=5, minutes=30))

random.seed(RANDOM_SEED)


# ============================================================
# EMPLOYEE DEFINITIONS
# ============================================================

EMPLOYEES = {
    "EMP001": {
        "name": "Rahul Sharma",
        "department": "IT",
        "role": "Software Engineer",

        "devices": [
            "DEVICE-RAHUL-01",
            "DEVICE-RAHUL-02",
        ],

        "primary_device": "DEVICE-RAHUL-01",

        "ip_addresses": [
            "192.168.10.101",
            "192.168.10.111",
        ],

        "login_hour": 9,
        "login_minute_range": (0, 25),

        "applications": [
            "VS Code",
            "Chrome",
            "Git",
        ],

        "resources": [
            "project_repository",
            "source_code",
            "technical_documentation",
            "development_files",
        ],

        "communication_types": [
            "team_chat",
            "email",
        ],

        "file_transfer_range": (1.0, 25.0),
        "network_transfer_range": (10.0, 40.0),
    },

    "EMP002": {
        "name": "Priya Mehta",
        "department": "HR",
        "role": "HR Executive",

        "devices": [
            "DEVICE-PRIYA-01",
            "DEVICE-PRIYA-02",
        ],

        "primary_device": "DEVICE-PRIYA-01",

        "ip_addresses": [
            "192.168.10.102",
            "192.168.10.112",
        ],

        "login_hour": 9,
        "login_minute_range": (20, 50),

        "applications": [
            "Chrome",
            "Microsoft Word",
            "Microsoft Excel",
        ],

        "resources": [
            "employee_records",
            "hr_documents",
            "leave_records",
            "employee_reports",
        ],

        "communication_types": [
            "email",
            "team_chat",
        ],

        "file_transfer_range": (0.5, 15.0),
        "network_transfer_range": (5.0, 25.0),
    },

    "EMP003": {
        "name": "Arjun Kapoor",
        "department": "Finance",
        "role": "Financial Analyst",

        "devices": [
            "DEVICE-ARJUN-01",
            "DEVICE-ARJUN-02",
        ],

        "primary_device": "DEVICE-ARJUN-01",

        "ip_addresses": [
            "192.168.10.103",
            "192.168.10.113",
        ],

        "login_hour": 8,
        "login_minute_range": (35, 55),

        "applications": [
            "Microsoft Excel",
            "Chrome",
            "Finance Portal",
        ],

        "resources": [
            "financial_reports",
            "budget_files",
            "financial_spreadsheets",
            "monthly_reports",
        ],

        "communication_types": [
            "email",
            "team_chat",
        ],

        "file_transfer_range": (5.0, 40.0),
        "network_transfer_range": (15.0, 60.0),
    },

    "EMP004": {
        "name": "Neha Verma",
        "department": "IT",
        "role": "System Administrator",

        "devices": [
            "DEVICE-NEHA-01",
            "DEVICE-NEHA-02",
            "DEVICE-NEHA-03",
        ],

        "primary_device": "DEVICE-NEHA-01",

        "ip_addresses": [
            "192.168.10.104",
            "192.168.10.114",
            "192.168.10.124",
        ],

        "login_hour": 8,
        "login_minute_range": (0, 30),

        "applications": [
            "PowerShell",
            "Chrome",
            "Windows Terminal",
            "Admin Portal",
        ],

        "resources": [
            "server_logs",
            "system_configuration",
            "infrastructure_files",
            "deployment_resources",
        ],

        "communication_types": [
            "team_chat",
            "email",
        ],

        "file_transfer_range": (5.0, 60.0),
        "network_transfer_range": (20.0, 100.0),
    },
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_collection():
    """
    Connect to MongoDB and return:

        client
        activity_logs collection
    """

    client = MongoClient(MONGO_URI)

    database = client[DATABASE_NAME]

    collection = database[COLLECTION_NAME]

    return client, collection


# ============================================================
# DEVICE SELECTION
# ============================================================

def choose_device(employee: dict):
    """
    Select a normal device for an employee.

    The primary device is used most frequently.
    Secondary devices appear occasionally.

    This creates a realistic device pattern without
    introducing an anomalous device yet.
    """

    if random.random() < 0.85:
        device_index = 0
    else:
        device_index = random.randint(
            1,
            len(employee["devices"]) - 1,
        )

    ip_index = device_index

    return (
        employee["devices"][device_index],
        employee["ip_addresses"][ip_index],
    )


# ============================================================
# TIMESTAMP GENERATION
# ============================================================

def generate_timestamp(
    employee: dict,
    activity_type: str,
    day_offset: int,
):
    """
    Generate timestamps in IST and convert them to UTC.

    This prevents the login baseline from being accidentally
    shifted by the timezone.

    Example:

        09:10 IST
            ↓
        03:40 UTC
    """

    base_date = datetime(
        2026,
        8,
        1,
        tzinfo=IST,
    )

    activity_date = base_date + timedelta(
        days=day_offset
    )

    if activity_type == "login":

        hour = employee["login_hour"]

        minimum_minute, maximum_minute = (
            employee["login_minute_range"]
        )

        minute = random.randint(
            minimum_minute,
            maximum_minute,
        )

    elif activity_type == "device_usage":

        hour = random.randint(8, 17)

        minute = random.randint(0, 59)

    else:

        hour = random.randint(9, 17)

        minute = random.randint(0, 59)

    second = random.randint(0, 59)

    local_timestamp = activity_date.replace(
        hour=hour,
        minute=minute,
        second=second,
        microsecond=0,
    )

    return local_timestamp.astimezone(timezone.utc)


# ============================================================
# COMMON EVENT INFORMATION
# ============================================================

def get_device_information(employee: dict):
    """
    Return a normal device ID and corresponding IP address.
    """

    device_id, ip_address = choose_device(employee)

    return device_id, ip_address


# ============================================================
# LOGIN EVENT
# ============================================================

def create_login_activity(
    employee_code: str,
    employee: dict,
    day_offset: int,
):
    """
    Create a login event.

    Login events are mainly used for:
        - Login Times
        - Device Usage
    """

    device_id, ip_address = get_device_information(
        employee
    )

    return {
        "employee_code": employee_code,
        "event_type": "login",
        "source": "workstation",
        "ip_address": ip_address,
        "device_id": device_id,
        "application": "Login Service",
        "resource": None,
        "data_volume_mb": None,
        "communication_type": None,
        "risk_score": 0,
        "timestamp": generate_timestamp(
            employee,
            "login",
            day_offset,
        ),
        "dataset_source": DATASET_SOURCE,
    }


# ============================================================
# FILE ACCESS EVENT
# ============================================================

def create_file_access_activity(
    employee_code: str,
    employee: dict,
    day_offset: int,
):
    """
    Create a resource/file access event.

    Used mainly for:
        - Resource Access Frequency
        - Application Usage
        - Device Usage
        - Data Transfer Volume
    """

    device_id, ip_address = get_device_information(
        employee
    )

    return {
        "employee_code": employee_code,
        "event_type": "file_access",
        "source": "filesystem",
        "ip_address": ip_address,
        "device_id": device_id,
        "application": random.choice(
            employee["applications"]
        ),
        "resource": random.choice(
            employee["resources"]
        ),
        "data_volume_mb": round(
            random.uniform(
                *employee["file_transfer_range"]
            ),
            2,
        ),
        "communication_type": None,
        "risk_score": 0,
        "timestamp": generate_timestamp(
            employee,
            "file_access",
            day_offset,
        ),
        "dataset_source": DATASET_SOURCE,
    }


# ============================================================
# APPLICATION USAGE EVENT
# ============================================================

def create_app_usage_activity(
    employee_code: str,
    employee: dict,
    day_offset: int,
):
    """
    Create an application usage event.

    Used mainly for:
        - Application Usage
        - Device Usage
    """

    device_id, ip_address = get_device_information(
        employee
    )

    return {
        "employee_code": employee_code,
        "event_type": "app_usage",
        "source": "workstation",
        "ip_address": ip_address,
        "device_id": device_id,
        "application": random.choice(
            employee["applications"]
        ),
        "resource": None,
        "data_volume_mb": None,
        "communication_type": None,
        "risk_score": 0,
        "timestamp": generate_timestamp(
            employee,
            "app_usage",
            day_offset,
        ),
        "dataset_source": DATASET_SOURCE,
    }


# ============================================================
# DATA TRANSFER EVENT
# ============================================================

def create_data_transfer_activity(
    employee_code: str,
    employee: dict,
    day_offset: int,
):
    """
    Create a network/data transfer event.

    Used mainly for:
        - Data Transfer Volume
        - Application Usage
        - Resource Access Frequency
        - Device Usage
    """

    device_id, ip_address = get_device_information(
        employee
    )

    return {
        "employee_code": employee_code,
        "event_type": "data_transfer",
        "source": "network",
        "ip_address": ip_address,
        "device_id": device_id,
        "application": random.choice(
            employee["applications"]
        ),
        "resource": random.choice(
            employee["resources"]
        ),
        "data_volume_mb": round(
            random.uniform(
                *employee["network_transfer_range"]
            ),
            2,
        ),
        "communication_type": None,
        "risk_score": 0,
        "timestamp": generate_timestamp(
            employee,
            "data_transfer",
            day_offset,
        ),
        "dataset_source": DATASET_SOURCE,
    }


# ============================================================
# COMMUNICATION EVENT
# ============================================================

def create_communication_activity(
    employee_code: str,
    employee: dict,
    day_offset: int,
):
    """
    Create a communication event.

    Used mainly for:
        - Communication Patterns
        - Application Usage
        - Device Usage
    """

    device_id, ip_address = get_device_information(
        employee
    )

    return {
        "employee_code": employee_code,
        "event_type": "communication",
        "source": "communication_platform",
        "ip_address": ip_address,
        "device_id": device_id,
        "application": random.choice(
            employee["applications"]
        ),
        "resource": None,
        "data_volume_mb": None,
        "communication_type": random.choice(
            employee["communication_types"]
        ),
        "risk_score": 0,
        "timestamp": generate_timestamp(
            employee,
            "communication",
            day_offset,
        ),
        "dataset_source": DATASET_SOURCE,
    }


# ============================================================
# DEVICE USAGE EVENT
# ============================================================

def create_device_usage_activity(
    employee_code: str,
    employee: dict,
    day_offset: int,
):
    """
    Create a device usage event.

    Used mainly for:
        - Device Usage
        - Application Usage
    """

    device_id, ip_address = get_device_information(
        employee
    )

    return {
        "employee_code": employee_code,
        "event_type": "device_usage",
        "source": "endpoint",
        "ip_address": ip_address,
        "device_id": device_id,
        "application": random.choice(
            employee["applications"]
        ),
        "resource": None,
        "data_volume_mb": None,
        "communication_type": None,
        "risk_score": 0,
        "timestamp": generate_timestamp(
            employee,
            "device_usage",
            day_offset,
        ),
        "dataset_source": DATASET_SOURCE,
    }


# ============================================================
# GENERIC ACTIVITY CREATOR
# ============================================================

def create_activity(
    employee_code: str,
    employee: dict,
    activity_type: str,
    day_offset: int,
):
    """Create one activity according to its event type."""

    if activity_type == "login":
        return create_login_activity(
            employee_code,
            employee,
            day_offset,
        )

    if activity_type == "file_access":
        return create_file_access_activity(
            employee_code,
            employee,
            day_offset,
        )

    if activity_type == "app_usage":
        return create_app_usage_activity(
            employee_code,
            employee,
            day_offset,
        )

    if activity_type == "data_transfer":
        return create_data_transfer_activity(
            employee_code,
            employee,
            day_offset,
        )

    if activity_type == "communication":
        return create_communication_activity(
            employee_code,
            employee,
            day_offset,
        )

    if activity_type == "device_usage":
        return create_device_usage_activity(
            employee_code,
            employee,
            day_offset,
        )

    raise ValueError(
        f"Unknown activity type: {activity_type}"
    )


# ============================================================
# EMPLOYEE DATASET GENERATION
# ============================================================

def generate_employee_dataset(
    employee_code: str,
    employee: dict,
):
    """
    Generate exactly 40 records for one employee.

    Distribution:

        login           = 8
        file_access     = 8
        app_usage       = 7
        data_transfer   = 6
        communication   = 6
        device_usage    = 5

        Total            = 40
    """

    activity_distribution = (
        ["login"] * 8
        + ["file_access"] * 8
        + ["app_usage"] * 7
        + ["data_transfer"] * 6
        + ["communication"] * 6
        + ["device_usage"] * 5
    )

    random.shuffle(activity_distribution)

    # Spread activities over six weeks.
    day_offsets = random.sample(
        range(0, 42),
        RECORDS_PER_EMPLOYEE,
    )

    records = []

    for activity_type, day_offset in zip(
        activity_distribution,
        day_offsets,
    ):

        record = create_activity(
            employee_code,
            employee,
            activity_type,
            day_offset,
        )

        records.append(record)

    records.sort(
        key=lambda record: record["timestamp"]
    )

    return records


# ============================================================
# DATASET RESET
# ============================================================

def remove_existing_seed_data(collection):
    """
    Remove ONLY records generated by this Milestone 2
    seed generator.

    Existing Milestone 1 records do not contain the
    dataset_source marker and therefore remain untouched.
    """

    result = collection.delete_many(
        {
            "dataset_source": DATASET_SOURCE
        }
    )

    return result.deleted_count


# ============================================================
# DATASET VALIDATION
# ============================================================

def validate_records(records):
    """
    Validate the generated dataset before insertion.
    """

    expected_records = (
        len(EMPLOYEES)
        * RECORDS_PER_EMPLOYEE
    )

    if len(records) != expected_records:
        raise RuntimeError(
            "Dataset size validation failed. "
            f"Expected {expected_records}, "
            f"generated {len(records)}."
        )

    for record in records:

        required_fields = [
            "employee_code",
            "event_type",
            "source",
            "device_id",
            "application",
            "timestamp",
            "dataset_source",
        ]

        for field in required_fields:

            if field not in record:
                raise RuntimeError(
                    f"Required field missing: {field}"
                )

        if record["dataset_source"] != DATASET_SOURCE:
            raise RuntimeError(
                "Invalid dataset source marker."
            )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(collection):
    """Print database and employee-wise statistics."""

    total_records = collection.count_documents({})

    seeded_records = collection.count_documents(
        {
            "dataset_source": DATASET_SOURCE
        }
    )

    print()
    print("=" * 65)
    print("ITBIS Milestone 2 Dataset Summary")
    print("=" * 65)

    print(
        f"Total activity_logs records: {total_records}"
    )

    print(
        f"Milestone 2 seeded records: {seeded_records}"
    )

    print(
        f"Milestone 1 preserved records: "
        f"{total_records - seeded_records}"
    )

    print()
    print("Employee-wise records:")

    for employee_code, employee in EMPLOYEES.items():

        count = collection.count_documents(
            {
                "employee_code": employee_code,
                "dataset_source": DATASET_SOURCE,
            }
        )

        print(
            f"  {employee_code} - "
            f"{employee['name']}: "
            f"{count}"
        )

    print()
    print("Event-type distribution:")

    pipeline = [
        {
            "$match": {
                "dataset_source": DATASET_SOURCE
            }
        },
        {
            "$group": {
                "_id": "$event_type",
                "count": {"$sum": 1},
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        },
    ]

    for item in collection.aggregate(pipeline):

        print(
            f"  {item['_id']}: "
            f"{item['count']}"
        )

    print("=" * 65)
    print()


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("ITBIS Milestone 2 - Behavioral Dataset Seeder")
    print("=" * 65)
    print()

    client, collection = get_collection()

    try:

        # ----------------------------------------------------
        # Remove old Milestone 2 seed data
        # ----------------------------------------------------

        deleted_count = remove_existing_seed_data(
            collection
        )

        print(
            f"Previous Milestone 2 seed records removed: "
            f"{deleted_count}"
        )

        print(
            "Original Milestone 1 records were preserved."
        )

        print()

        # ----------------------------------------------------
        # Generate new dataset
        # ----------------------------------------------------

        print(
            "Generating corrected behavioral dataset..."
        )

        all_records = []

        for employee_code, employee in EMPLOYEES.items():

            employee_records = (
                generate_employee_dataset(
                    employee_code,
                    employee,
                )
            )

            all_records.extend(
                employee_records
            )

            print(
                f"{employee_code} - "
                f"{employee['name']}: "
                f"{len(employee_records)} records"
            )

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        validate_records(all_records)

        print()
        print(
            f"Generated records: "
            f"{len(all_records)}"
        )

        # ----------------------------------------------------
        # Insert
        # ----------------------------------------------------

        print()
        print(
            "Inserting corrected dataset into MongoDB..."
        )

        result = collection.insert_many(
            all_records
        )

        print(
            f"Inserted records: "
            f"{len(result.inserted_ids)}"
        )

        # ----------------------------------------------------
        # Final verification
        # ----------------------------------------------------

        print_summary(collection)

    finally:

        client.close()


# ============================================================
# SCRIPT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()