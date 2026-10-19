import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, SessionLocal
from app.models import Base
from app.seed import seed_initial_data
from app.routes.auth_routes import router as auth_router
from app.routes.employee_routes import router as employee_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.activity_routes import router as activity_router
from app.routes.behavior_routes import router as behavior_router
from app.routes.risk_routes import router as risk_router, singular_risk_router
from app.routes.alert_routes import router as alert_router, analytics_router
from app.routes.incident_routes import router as incident_router
from app.routes.report_routes import router as report_router
from app.routes.notification_routes import router as notification_router
from app.routes.settings_routes import router as settings_router
from app.routes.investigation_routes import router as investigation_router
from app.routes.search_routes import router as search_router
from app.routes.anomaly_routes import router as anomaly_router
from app.routes.ueba_routes import router as ueba_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("itbis.main")

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
    
    # Safe SQLite column migration for Milestone 3 extensions
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            if "sqlite" in str(engine.url):
                for table, col, col_type in [
                    ("incidents", "summary", "TEXT"),
                    ("incidents", "investigation_started_at", "DATETIME"),
                    ("investigation_notes", "author_user_id", "INTEGER"),
                    ("investigation_notes", "note", "TEXT"),
                    ("investigation_notes", "evidence_reference", "TEXT"),
                    ("alerts", "incident_id", "INTEGER"),
                    ("alerts", "escalated_at", "DATETIME"),
                    ("audit_logs", "user_id", "INTEGER"),
                ]:
                    try:
                        res = conn.execute(text(f"PRAGMA table_info({table});")).fetchall()
                        col_names = [r[1] for r in res]
                        if col not in col_names:
                            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type};"))
                            conn.commit()
                    except Exception:
                        pass
    except Exception as ex:
        logger.warning(f"Schema column check: {ex}")

    with SessionLocal() as db_session:
        seed_initial_data(db_session)

    # Automatic ML Model Regeneration on Startup if missing (Milestone 4: Day 37-38)
    try:
        from app.ml_anomaly import DEFAULT_MODEL_PATH, train_isolation_forest, save_model
        from app.ml_features import extract_daily_features, prepare_feature_matrix
        from app.mongodb import mongo_service
        import numpy as np

        if not os.path.exists(DEFAULT_MODEL_PATH):
            logger.info(f"Anomaly model file missing at {DEFAULT_MODEL_PATH}. Regenerating automatically...")
            activities = mongo_service.query_activity_logs(limit=5000).get("items", [])
            feature_records = extract_daily_features(activities) if activities else []
            if len(feature_records) >= 5:
                X, _ = prepare_feature_matrix(feature_records)
            else:
                rng = np.random.default_rng(42)
                X = rng.normal(loc=[0.5, 0.2, 0.05, 50.0, 1.2, 0.3], scale=[0.3, 0.1, 0.02, 15.0, 0.4, 0.2], size=(50, 6))
                X = np.clip(X, a_min=0.0, a_max=None)

            model = train_isolation_forest(X, contamination=0.05, random_state=42)
            save_model(model, DEFAULT_MODEL_PATH)
            logger.info(f"Anomaly model regenerated successfully at {DEFAULT_MODEL_PATH}.")
    except Exception as ml_err:
        logger.warning(f"ML model regeneration check: {ml_err}")
except Exception as e:
    logger.warning(f"Could not initialize database tables or seed at startup: {e}")

app = FastAPI(title="ITBIS API", version="1.0.0")

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(dashboard_router)
app.include_router(activity_router)
app.include_router(behavior_router)
app.include_router(risk_router)
app.include_router(singular_risk_router)
app.include_router(alert_router)
app.include_router(incident_router)
app.include_router(report_router)
app.include_router(notification_router)
app.include_router(settings_router)
app.include_router(investigation_router)
app.include_router(search_router)
app.include_router(anomaly_router)
app.include_router(ueba_router)
app.include_router(analytics_router)


# Configure CORS Origins
env_origins = os.getenv("ALLOWED_ORIGINS", os.getenv("CORS_ORIGINS", ""))
if env_origins.strip():
    allowed_origins = [orig.strip() for orig in env_origins.split(",") if orig.strip()]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$|^https?://.*\.onrender\.com$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)




@app.get("/")
@app.get("/health")
def health_check():
    return {"status": "ITBIS backend is running"}

