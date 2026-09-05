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
    ai_routes,
    simulation_routes
)

# Initialize tables and seed records immediately on load
seed_database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] ITBIS API Gateway operational.")
    yield
    print("[SHUTDOWN] ITBIS API Gateway shutting down.")

app = FastAPI(
    title="AI Insider Threat Behavioral Intelligence System (ITBIS)",
    description="Enterprise-grade platform for AI-powered behavioral profiling, anomaly detection, risk scoring, and SOC incident investigation.",
    version="1.0.0",
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

# Mount routes
app.include_router(auth_routes.router, prefix=settings.API_V1_STR)
app.include_router(employee_routes.router, prefix=settings.API_V1_STR)
app.include_router(log_routes.router, prefix=settings.API_V1_STR)
app.include_router(alert_routes.router, prefix=settings.API_V1_STR)
app.include_router(incident_routes.router, prefix=settings.API_V1_STR)
app.include_router(ai_routes.router, prefix=settings.API_V1_STR)
app.include_router(simulation_routes.router, prefix=settings.API_V1_STR)

@app.get("/")
def health_check():
    return {
        "status": "ITBIS backend is running",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
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
