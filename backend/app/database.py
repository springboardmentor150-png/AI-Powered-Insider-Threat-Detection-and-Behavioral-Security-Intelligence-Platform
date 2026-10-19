import os
import logging
from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from pathlib import Path

logger = logging.getLogger("itbis.database")

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_FILE = BASE_DIR / "itbis.db"

raw_db_url = os.getenv("DATABASE_URL")
if not raw_db_url or not raw_db_url.strip():
    DATABASE_URL = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"
else:
    raw_db_url = raw_db_url.strip()
    if raw_db_url.startswith("postgres://"):
        DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
    else:
        DATABASE_URL = raw_db_url

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {"connect_timeout": 10}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database operational error encountered: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service temporarily unavailable"
        )
    finally:
        db.close()
