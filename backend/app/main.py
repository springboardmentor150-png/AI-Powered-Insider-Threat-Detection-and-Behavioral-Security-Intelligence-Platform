from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine, SessionLocal
from app.models import Employee, Alert
from app.routes.risk_routes import router as risk_router
from app.routes.ueba_routes import router as ueba_router
from app.routes.investigation_routes import router as investigation_router
from app.routes.alert_routes import router as alert_router
from app.routes.analytics_routes import router as analytics_router
from app.routes.dashboard_routes import router as dashboard_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ITBIS Milestone 3 API",
    version="3.0.0",
    description="Risk Scoring, UEBA, Threat Investigation, Alert Management and Security Dashboards"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(risk_router)
app.include_router(ueba_router)
app.include_router(investigation_router)
app.include_router(alert_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {"message": "ITBIS Milestone 3 backend is running"}

@app.get("/health")
def health():
    return {"status": "ok", "milestone": "M3"}

def seed_demo():
    db = SessionLocal()
    try:
        if db.query(Employee).count() == 0:
            employees = [
                Employee(employee_id="EMP-1001", name="Aarav Sharma", department="IT", email="aarav@itbis.local"),
                Employee(employee_id="EMP-1002", name="Neha Patil", department="IT", email="neha@itbis.local"),
                Employee(employee_id="EMP-1003", name="Rohan Deshmukh", department="HR", email="rohan@itbis.local"),
                Employee(employee_id="EMP-1004", name="Priya Kulkarni", department="IT", email="priya@itbis.local"),
                Employee(employee_id="EMP-1005", name="Vikram Joshi", department="Finance", email="vikram@itbis.local"),
            ]
            db.add_all(employees)
        if db.query(Alert).count() == 0:
            db.add_all([
                Alert(employee_id="EMP-1001", severity="critical", message="Multiple suspicious activities detected"),
                Alert(employee_id="EMP-1004", severity="high", message="Unusual privilege and download activity"),
                Alert(employee_id="EMP-1005", severity="high", message="Potential data exfiltration detected"),
            ])
        db.commit()
    finally:
        db.close()

seed_demo()
