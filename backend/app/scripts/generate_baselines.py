"""
ITBIS Milestone 2 - Baseline Generation Script

Day 13-14:
    Generates behavioral baselines for every employee.

Numeric indicators:
    1. Login Time
    2. Resource Access Frequency
    3. Data Transfer Volume

Set-membership indicators:
    4. Device Usage
    5. Application Usage
"""

from app.database import SessionLocal
from app.models import Employee

from app.behavioral_profiling import (
    calculate_login_time_baseline,
    calculate_access_frequency_baseline,
    calculate_data_transfer_baseline,
    calculate_device_usage_baseline,
    calculate_application_usage_baseline,
)


def generate_baselines() -> None:
    db = SessionLocal()

    total_employees = 0
    total_possible_baselines = 0
    total_built_baselines = 0

    try:
        employees = (
            db.query(Employee)
            .order_by(Employee.employee_code)
            .all()
        )

        if not employees:
            print("No employees found in PostgreSQL.")
            return

        print("=" * 72)
        print("ITBIS Milestone 2 - Day 13-14 Baseline Generation")
        print("=" * 72)
        print()

        for employee in employees:
            employee_code = employee.employee_code

            results = {
                "login_time": calculate_login_time_baseline(employee_code),
                "resource_access_frequency": calculate_access_frequency_baseline(
                    employee_code
                ),
                "data_transfer_volume": calculate_data_transfer_baseline(
                    employee_code
                ),
                "device_usage": calculate_device_usage_baseline(
                    employee_code
                ),
                "application_usage": calculate_application_usage_baseline(
                    employee_code
                ),
            }

            built = [
                indicator
                for indicator, result in results.items()
                if result is not None
            ]

            skipped = [
                indicator
                for indicator, result in results.items()
                if result is None
            ]

            total_employees += 1
            total_possible_baselines += len(results)
            total_built_baselines += len(built)

            print(
                f"{employee_code}: "
                f"built={built}, "
                f"skipped={skipped}"
            )

        coverage_percentage = (
            (total_built_baselines / total_possible_baselines) * 100
            if total_possible_baselines
            else 0
        )

        print()
        print("=" * 72)
        print("Day 13-14 Baseline Summary")
        print("=" * 72)
        print(f"Employees processed: {total_employees}")
        print(
            f"Baselines built: "
            f"{total_built_baselines}/{total_possible_baselines}"
        )
        print(
            f"Baseline coverage: "
            f"{coverage_percentage:.2f}%"
        )
        print("=" * 72)

    finally:
        db.close()


if __name__ == "__main__":
    generate_baselines()