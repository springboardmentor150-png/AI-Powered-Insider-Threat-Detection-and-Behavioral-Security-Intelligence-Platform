# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import doc_db
from app.seed_data import seed_database
from app.routes import (
    auth_routes,
    employee_routes,
    log_routes,
    alert_routes,
    incident_routes,
    investigation_routes,
    ueba_routes,
    dashboard_routes,
    ai_routes,
    simulation_routes
)

# Initialize tables and seed records immediately on load
seed_database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] ITBIS Milestone 3 Operational.")
    yield
    print("[SHUTDOWN] ITBIS Gateway shutting down.")

app = FastAPI(
    title="AI Insider Threat Behavioral Intelligence System (ITBIS) - Milestone 3",
    description="Risk Scoring, UEBA Intelligence, Threat Investigation & Security Dashboards (Milestone 3).",
    version="3.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers under both /api and root prefix for full compatibility
routers = [
    auth_routes.router,
    employee_routes.router,
    log_routes.router,
    alert_routes.router,
    incident_routes.router,
    investigation_routes.router,
    ueba_routes.router,
    dashboard_routes.router,
    ai_routes.router,
    simulation_routes.router
]

for r in routers:
    app.include_router(r, prefix=settings.API_V1_STR)
    app.include_router(r)

@app.get("/")
def health_check():
    return {
        "status": "ITBIS backend is running",
        "system": settings.PROJECT_NAME,
        "milestone": "Milestone 3: Risk Scoring & Threat Investigation",
        "version": "3.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
def detailed_health():
    return {
        "status": "healthy",
        "database": "relational_active",
        "document_store": "mongodb_live" if doc_db.is_connected_to_mongo else "embedded_store_active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)