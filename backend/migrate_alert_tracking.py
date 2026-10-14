from sqlalchemy import inspect, text
from app.database import engine

inspector = inspect(engine)
columns = {
    column["name"]
    for column in inspector.get_columns("alerts")
}

migration_statements = {
    "resolved_at": """
        ALTER TABLE alerts
        ADD COLUMN resolved_at TIMESTAMP WITH TIME ZONE NULL
    """,
    "escalated_at": """
        ALTER TABLE alerts
        ADD COLUMN escalated_at TIMESTAMP WITH TIME ZONE NULL
    """,
    "escalation_level": """
        ALTER TABLE alerts
        ADD COLUMN escalation_level INTEGER NOT NULL DEFAULT 0
    """,
}

with engine.begin() as connection:
    for column_name, statement in migration_statements.items():
        if column_name not in columns:
            connection.execute(text(statement))
            print(f"Added column: {column_name}")
        else:
            print(f"Column already exists: {column_name}")

print("Alert tracking migration completed.")
