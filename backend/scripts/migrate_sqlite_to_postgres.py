"""
ITBIS SQLite to PostgreSQL Migration Utility
Transfers all existing SQLite data (users, employees, baselines, risk history, alerts, incidents, notes, audit logs)
into PostgreSQL with full table dependency ordering, conflict resolution, and sequence synchronization.
"""

import os
import sys
import logging
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from app.models import (
    Base,
    User,
    Employee,
    ActivityLog,
    BehavioralBaseline,
    RiskScoreHistory,
    Alert,
    Incident,
    InvestigationNote,
    AuditLog,
    Notification,
    SystemSetting,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("itbis.migrate")


def migrate_data(sqlite_url: str = None, postgres_url: str = None):
    if not sqlite_url:
        sqlite_db = backend_dir / "itbis.db"
        sqlite_url = f"sqlite:///{sqlite_db.as_posix()}"

    if not postgres_url:
        postgres_url = os.getenv("DATABASE_URL")
        if not postgres_url or "sqlite" in postgres_url:
            logger.error("No PostgreSQL DATABASE_URL found in environment. Please provide a PostgreSQL connection string.")
            return False

    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

    logger.info("Source SQLite: %s", sqlite_url)
    logger.info("Target PostgreSQL: %s", postgres_url.split("@")[-1] if "@" in postgres_url else postgres_url)

    # Setup source and target engines
    src_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    dst_engine = create_engine(postgres_url, pool_pre_ping=True)

    # Ensure all tables exist in target
    Base.metadata.create_all(bind=dst_engine)

    SrcSession = sessionmaker(bind=src_engine)
    DstSession = sessionmaker(bind=dst_engine)

    # Table migration order respecting Foreign Key constraints
    table_models = [
        ("users", User, "id"),
        ("employees", Employee, "id"),
        ("system_settings", SystemSetting, "id"),
        ("behavioral_baselines", BehavioralBaseline, "id"),
        ("risk_score_history", RiskScoreHistory, "id"),
        ("incidents", Incident, "id"),
        ("alerts", Alert, "id"),
        ("investigation_notes", InvestigationNote, "id"),
        ("notifications", Notification, "id"),
        ("audit_logs", AuditLog, "id"),
        ("activity_logs", ActivityLog, "id"),
    ]

    total_migrated = 0

    with SrcSession() as src_db, DstSession() as dst_db:
        for table_name, model, pk_col in table_models:
            try:
                src_records = src_db.query(model).all()
                if not src_records:
                    logger.info("Table '%s': 0 records in SQLite. Skipped.", table_name)
                    continue

                existing_pks = set(r[0] for r in dst_db.query(getattr(model, pk_col)).all())
                inserted_count = 0

                for record in src_records:
                    rec_pk = getattr(record, pk_col)
                    if rec_pk in existing_pks:
                        continue

                    # Detach from source session and merge into target
                    rec_dict = {c.name: getattr(record, c.name) for c in model.__table__.columns}
                    new_obj = model(**rec_dict)
                    dst_db.add(new_obj)
                    inserted_count += 1

                dst_db.commit()
                total_migrated += inserted_count
                logger.info("Table '%s': %d records migrated (%d already existed).", table_name, inserted_count, len(existing_pks))

                # Update PostgreSQL sequence to prevent PK collisions on future inserts
                if "postgresql" in postgres_url:
                    try:
                        seq_query = text(f"SELECT pg_get_serial_sequence('{table_name}', '{pk_col}');")
                        seq_res = dst_db.execute(seq_query).scalar()
                        if seq_res:
                            reset_query = text(f"SELECT setval('{seq_res}', COALESCE((SELECT MAX({pk_col}) FROM {table_name}), 1));")
                            dst_db.execute(reset_query)
                            dst_db.commit()
                    except Exception as seq_err:
                        logger.warning("Could not reset sequence for '%s': %s", table_name, seq_err)

            except Exception as e:
                dst_db.rollback()
                logger.error("Error migrating table '%s': %s", table_name, e)

    logger.info("Migration complete! Total new records migrated into PostgreSQL: %d", total_migrated)
    return True


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else None
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    migrate_data(src, dst)
