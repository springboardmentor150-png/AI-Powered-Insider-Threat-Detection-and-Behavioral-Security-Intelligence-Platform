from sqlalchemy import text
from app.database import engine

with engine.begin() as conn:
    conn.execute(
        text(
            "ALTER TABLE alerts "
            "ADD COLUMN IF NOT EXISTS incident_id INTEGER "
            "REFERENCES incidents(id)"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE alerts "
            "ADD COLUMN IF NOT EXISTS status VARCHAR "
            "DEFAULT 'open' NOT NULL"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE alerts "
            "ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP"
        )
    )

    conn.execute(
        text(
            "ALTER TABLE alerts "
            "ADD COLUMN IF NOT EXISTS escalated_at TIMESTAMP"
        )
    )

print("Alert table updated successfully.")