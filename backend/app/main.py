from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes.auth_routes import router as auth_router
from app.routes.employee_routes import router as employee_router
from app.routes.log_routes import router as log_router
from app.auth import require_role

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ITBIS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(log_router)

@app.get("/")
def read_root():
    return {"status": "ITBIS backend is running"}

@app.get("/admin/users")
def get_admin_users(token_payload: dict = Depends(require_role("admin"))):
    return {"message": "Only admins see this"}
