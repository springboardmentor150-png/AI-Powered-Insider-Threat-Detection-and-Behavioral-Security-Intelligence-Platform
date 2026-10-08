def calculate_z_score(actual_value, typical_value, std_deviation):
    if std_deviation == 0:
        std_deviation = 0.5

    return abs(actual_value - typical_value) / std_deviation


def check_behavioral_anomaly(actual_value, typical_value, std_deviation):
    z_score = calculate_z_score(
        actual_value,
        typical_value,
        std_deviation
    )

    return {
        "is_anomaly": z_score > 2.5,
        "z_score": round(z_score, 3),
        "threshold": 2.5
    }


def check_login_time_anomaly(actual_hour, typical_value, std_deviation):
    return check_behavioral_anomaly(
        actual_hour,
        typical_value,
        std_deviation
    )


def check_resource_access_anomaly(actual_value, typical_value, std_deviation):
    return check_behavioral_anomaly(
        actual_value,
        typical_value,
        std_deviation
    )


def check_device_usage_anomaly(actual_value, typical_value, std_deviation):
    return check_behavioral_anomaly(
        actual_value,
        typical_value,
        std_deviation
    )


def check_application_usage_anomaly(actual_value, typical_value, std_deviation):
    return check_behavioral_anomaly(
        actual_value,
        typical_value,
        std_deviation
    )


def check_data_transfer_anomaly(actual_value, typical_value, std_deviation):
    return check_behavioral_anomaly(
        actual_value,
        typical_value,
        std_deviation
    )


def check_communication_anomaly(actual_value, typical_value, std_deviation):
    return check_behavioral_anomaly(
        actual_value,
        typical_value,
        std_deviation
    )


# Rule-Based Detection


def check_access_anomaly(access_count, normal_access_count):
    if normal_access_count <= 0:
        return False

    return access_count > normal_access_count * 2


def check_data_exfiltration(transferred_mb, normal_transfer_mb):
    if normal_transfer_mb <= 0:
        return False

    return transferred_mb > normal_transfer_mb * 3


def check_privilege_abuse(user_role, action):
    privileged_actions = [
        "delete_user",
        "change_role",
        "grant_permission",
        "modify_security_settings"
    ]

    if user_role != "admin" and action in privileged_actions:
        return True

    return False


def check_abnormal_download(download_mb, normal_download_mb):
    if normal_download_mb <= 0:
        return False

    return download_mb > normal_download_mb * 3


def check_suspicious_device(device_id, known_devices):
    return device_id not in known_devices
