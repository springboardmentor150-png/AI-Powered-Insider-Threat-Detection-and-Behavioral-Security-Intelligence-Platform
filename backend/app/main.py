from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth_routes import router as auth_router
from app.routes.employee_routes import router as employee_router
from app.routes.log_routes import router as log_router
from app.routes.anomaly_routes import router as anomaly_router


app = FastAPI(
    title="ITBIS API",
    version="2.0.0"
)


app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(log_router)
app.include_router(anomaly_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "ITBIS backend is running"
    }
