from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes.auth_routes import router as auth_router
from app.routes.employee_routes import router as employee_router
from app.routes.log_routes import router as log_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(title="ITBIS API")


# Routes
app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(log_router)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {
        "status": "ITBIS backend is running"
    }