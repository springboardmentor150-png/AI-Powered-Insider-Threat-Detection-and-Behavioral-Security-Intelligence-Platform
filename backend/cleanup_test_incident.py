from app.database import SessionLocal
from app.models import Incident, InvestigationNote

db = SessionLocal()

try:
    incident = (
        db.query(Incident)
        .filter(
            Incident.id == 1,
            Incident.incident_type == "ITBIS_TEST_INVESTIGATION",
        )
        .first()
    )

    if incident is None:
        print("Test incident not found. Nothing deleted.")
    else:
        note_count = (
            db.query(InvestigationNote)
            .filter(InvestigationNote.incident_id == incident.id)
            .count()
        )

        db.delete(incident)
        db.commit()

        print("Test incident deleted:", incident.id)
        print("Associated test notes deleted:", note_count)

finally:
    db.close()
