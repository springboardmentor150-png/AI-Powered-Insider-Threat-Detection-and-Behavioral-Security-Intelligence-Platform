"""
ITBIS FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, close_mongo, engine
from app.routers import activity_logs, alerts, auth, employees, users

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    # Create all PostgreSQL tables if they don't exist yet.
    # For production use Alembic migrations instead.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    await engine.dispose()
    await close_mongo()


app = FastAPI(
    title="ITBIS — Insider Threat Behavioral Intelligence",
    description=(
        "Backend API for the ITBIS security operations console. "
        "Milestone 1: auth, employee management, alerts, activity logs."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(users.router)
app.include_router(alerts.router)
app.include_router(activity_logs.router)


@app.get("/health", tags=["health"])
async def health():
    """Simple liveness probe."""
    return {"status": "ok", "service": "itbis-api"}
