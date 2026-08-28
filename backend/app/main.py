from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from .routes.auth_routes import router as auth_router
from .routes.role_routes import router as role_router
from .routes.employee_routes import router as employee_router
from .routes.log_routes import router as log_router

app = FastAPI(title="ITBIS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(role_router)
app.include_router(employee_router)
app.include_router(log_router)


@app.get("/")
def health_check():
    return {"status": "ITBIS backend is running"}
