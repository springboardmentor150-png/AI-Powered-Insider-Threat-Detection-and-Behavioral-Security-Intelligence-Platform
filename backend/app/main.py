"""
ITBIS FastAPI entrypoint.

Run with:
uvicorn app.main:app --reload

Then visit:
http://127.0.0.1:8000/         -> health check
http://127.0.0.1:8000/docs     -> interactive API docs
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import (
    auth_routes,
    employee_routes,
    admin_routes,
    activity_routes,
    anomaly_routes,
    risk_routes,
    ueba_routes,  
    investigation_routes,   
    day28_routes,
    dashboard_routes,      
)

load_dotenv()

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:3000"
)

# Creates all tables defined in models.py if they don't already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ITBIS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing routes
app.include_router(auth_routes.router)
app.include_router(employee_routes.router)
app.include_router(admin_routes.router)
app.include_router(activity_routes.router)
app.include_router(anomaly_routes.router)

# Day 21: Insider Risk Scoring
app.include_router(risk_routes.router)
app.include_router(ueba_routes.router)
app.include_router(investigation_routes.router)
app.include_router(day28_routes.router)
app.include_router(dashboard_routes.router)


@app.get("/")
def health_check():
    return {"status": "ITBIS backend is running"}