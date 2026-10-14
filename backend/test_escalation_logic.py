
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models import Alert, Employee, Incident
from app.alert_escalation import escalate_overdue_alerts


IST = timezone(timedelta(hours=5, minutes=30))
TEST_PREFIX = "TEMP_ESCALATION_TEST"


def main():
    db = SessionLocal()
    incident_id = None

    try:
        employee = db.query(Employee).filter(
            Employee.employee_code == "EMP001"
        ).first()

        if employee is None:
            raise RuntimeError("EMP001 not found; no test records created.")

        incident = Incident(
            employee_id=employee.id,
            incident_type=TEST_PREFIX,
            description="Temporary automated escalation test",
            severity="high",
            status="open",
        )
        db.add(incident)
        db.flush()
        incident_id = incident.id

        now = datetime.now(IST).replace(tzinfo=None)

        recent_alert = Alert(
            incident_id=incident.id,
            employee_id=employee.id,
            alert_type=TEST_PREFIX,
            message="Temporary recent alert",
            severity="high",
            status="open",
            created_at=now - timedelta(minutes=2),
            escalation_level=0,
        )

        overdue_alert = Alert(
            incident_id=incident.id,
            employee_id=employee.id,
            alert_type=TEST_PREFIX,
            message="Temporary overdue alert",
            severity="high",
            status="open",
            created_at=now - timedelta(minutes=45),
            escalation_level=0,
        )

        db.add_all([recent_alert, overdue_alert])
        db.commit()

        recent_id = recent_alert.id
        overdue_id = overdue_alert.id

        print("\nTEST 1: Recent alert must not escalate")
        result = escalate_overdue_alerts(db)
        db.refresh(recent_alert)
        assert recent_alert.escalation_level == 0, (
            "FAIL: recent alert was escalated too early"
        )
        print("PASS: recent alert was not escalated")
        print("Escalation summary:", result)

        print("\nTEST 2: Overdue alert must escalate")
        db.refresh(overdue_alert)
        assert overdue_alert.escalation_level == 1, (
            "FAIL: overdue alert was not escalated"
        )
        assert overdue_alert.status == "escalated", (
            "FAIL: overdue alert status is incorrect"
        )
        print("PASS: overdue alert escalated")

        print("\nTEST 3: Repeated execution must not escalate twice")
        original_escalated_at = overdue_alert.escalated_at
        result_again = escalate_overdue_alerts(db)
        db.refresh(overdue_alert)

        assert overdue_alert.escalation_level == 1, (
            "FAIL: escalation level changed on repeated execution"
        )
        assert overdue_alert.escalated_at == original_escalated_at, (
            "FAIL: escalation timestamp was reset"
        )
        print("PASS: repeated execution did not escalate twice")
        print("Second-run summary:", result_again)

    finally:
        try:
            if incident_id is not None:
                db.query(Alert).filter(
                    Alert.incident_id == incident_id,
                    Alert.alert_type == TEST_PREFIX,
                ).delete(synchronize_session=False)

                db.query(Incident).filter(
                    Incident.id == incident_id,
                    Incident.incident_type == TEST_PREFIX,
                ).delete(synchronize_session=False)

                db.commit()
                print("\nCleanup: temporary test records removed.")
        except Exception:
            db.rollback()
            print(
                "\nWARNING: cleanup failed. "
                "Inspect temporary test records before continuing."
            )
        finally:
            db.close()


if __name__ == "__main__":
    main()
