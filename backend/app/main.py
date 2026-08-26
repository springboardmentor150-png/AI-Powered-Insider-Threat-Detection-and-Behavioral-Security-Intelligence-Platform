from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes.activity_logs import router as activity_logs_router
from app.database import engine
from app.models import Base
from app.routes.auth_routes import router as auth_router
from app.auth import require_role
from app.routes.employees import router as employee_router

app = FastAPI(title="ITBIS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(activity_logs_router)

@app.get("/")
def health_check():
    return {"status": "ITBIS backend is running"}


@app.get("/admin/dashboard")
def admin_dashboard(
    user=Depends(require_role("admin"))
):
    return {
        "message": "Welcome to the admin dashboard",
        "user_id": user["sub"],
        "role": user["role"]
    }