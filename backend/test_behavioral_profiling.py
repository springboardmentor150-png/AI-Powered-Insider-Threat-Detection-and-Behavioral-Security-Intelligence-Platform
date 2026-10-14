from app.behavioral_profiling import (
    build_employee_baselines,
)


employee_id = "EMP1001"

baselines = build_employee_baselines(
    employee_id
)

print("\nEmployee:", employee_id)
print("Baselines generated:", len(baselines))

for baseline in baselines:
    print("\n", baseline)