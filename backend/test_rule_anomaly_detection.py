from app.rule_anomaly_detection import (
    check_login_time,
    check_data_transfer_volume,
    check_device_usage,
    check_application_usage,
)


employee_id = "EMP1001"


print("\n========== LOGIN TIME ==========")

print("\nNormal login:")
print(check_login_time(employee_id, 9.0))

print("\nAbnormal login:")
print(check_login_time(employee_id, 15.0))


print("\n========== DATA TRANSFER ==========")

print("\nNormal transfer:")
print(check_data_transfer_volume(employee_id, 250))

print("\nAbnormal transfer:")
print(check_data_transfer_volume(employee_id, 1000))


print("\n========== DEVICE ==========")

print("\nKnown device:")
print(check_device_usage(employee_id, "Laptop-01"))

print("\nUnknown device:")
print(check_device_usage(employee_id, "Unknown-Laptop"))


print("\n========== APPLICATION ==========")

print("\nKnown application:")
print(check_application_usage(employee_id, "VS Code"))

print("\nUnknown application:")
print(check_application_usage(employee_id, "Unknown-App"))