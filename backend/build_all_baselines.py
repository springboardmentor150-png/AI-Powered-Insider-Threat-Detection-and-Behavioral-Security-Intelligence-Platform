from app.behavioral_profiling import build_all_baselines


employee_ids = [
    "EMP1001",
    "EMP1002",
    "EMP1003",
    "EMP1004",
    "EMP1005",
    "EMP1006",
]


results = build_all_baselines(employee_ids)

print("\n===== BASELINE DEBUG =====")
print("Type of results:", type(results))
print("Employees:", len(results))

total_baselines = 0

for employee_id, employee_baselines in results.items():

    print(f"\n{employee_id}")
    print("Type:", type(employee_baselines))
    print("Count:", len(employee_baselines))

    indicators = [
        baseline.get("indicator")
        for baseline in employee_baselines
    ]

    print("Indicators:", indicators)

    total_baselines += len(employee_baselines)


print("\n==========================")
print("Total baselines:", total_baselines)