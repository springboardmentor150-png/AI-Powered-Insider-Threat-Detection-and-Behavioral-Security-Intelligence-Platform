from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Employee, Incident

db: Session = SessionLocal()

try:
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == "EMP001")
        .first()
    )

    if employee is None:
        raise SystemExit("EMP001 was not found. No incident created.")

    existing_test = (
        db.query(Incident)
        .filter(Incident.incident_type == "ITBIS_TEST_INVESTIGATION")
        .first()
    )

    if existing_test:
        print("A test incident already exists.")
        print("Incident ID:", existing_test.id)
        print("Status:", existing_test.status)
    else:
        incident = Incident(
            employee_id=employee.id,
            incident_type="ITBIS_TEST_INVESTIGATION",
            description=(
                "TEST DATA ONLY: Validate the incident investigation "
                "workflow. This is not a real security finding."
            ),
            severity="high",
            status="open",
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)

        print("Test incident created successfully.")
        print("Incident ID:", incident.id)
        print("Employee:", employee.employee_code)
        print("Severity:", incident.severity)
        print("Status:", incident.status)

finally:
    db.close()
