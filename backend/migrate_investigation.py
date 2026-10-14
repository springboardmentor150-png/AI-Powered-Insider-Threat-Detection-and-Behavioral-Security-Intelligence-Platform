from sqlalchemy import text
from app.database import engine

migration_sql = """
ALTER TABLE incidents
    ADD COLUMN IF NOT EXISTS summary TEXT NULL;

ALTER TABLE incidents
    ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP NULL;

CREATE TABLE IF NOT EXISTS investigation_notes (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL
        REFERENCES incidents(id) ON DELETE CASCADE,
    author_user_id INTEGER NOT NULL
        REFERENCES users(id),
    note TEXT NOT NULL,
    evidence_reference VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_investigation_notes_incident_id
    ON investigation_notes (incident_id);

CREATE INDEX IF NOT EXISTS ix_investigation_notes_author_user_id
    ON investigation_notes (author_user_id);
"""

with engine.begin() as connection:
    for statement in migration_sql.split(";"):
        if statement.strip():
            connection.execute(text(statement))

print("Migration applied successfully.")
