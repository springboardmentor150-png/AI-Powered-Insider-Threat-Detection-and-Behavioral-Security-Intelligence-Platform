from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import models
from .database import engine, Base, get_db
from .schemas import (
    SignupRequest,
    LoginRequest,
    EmployeeCreate,
    LogIngestRequest
)
from .auth import (
    create_token,
    verify_password,
    decode_token,
    hash_password
)
from .log_ingestion import ingest_log, activity_logs


app = FastAPI(
    title="ITBIS Backend API",
    description="Insider Threat Behavioral Intelligence System",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


# Add Employee columns if the table already existed
with engine.begin() as conn:
    conn.execute(
        text(
            "ALTER TABLE employees "
            "ADD COLUMN IF NOT EXISTS device_info VARCHAR"
        )
    )
    conn.execute(
        text(
            "ALTER TABLE employees "
            "ADD COLUMN IF NOT EXISTS access_privileges VARCHAR"
        )
    )


security = HTTPBearer()


ALLOWED_ROLES = {
    "admin",
    "security_manager",
    "security_analyst",
    "soc_engineer"
}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        return decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


def require_roles(*roles):
    def checker(payload=Depends(get_current_user)):
        if payload.get("role") not in roles:
            raise HTTPException(
                status_code=403,
                detail="Not authorized for this action"
            )
        return payload

    return checker


@app.get("/")
def health_check():
    return {
        "message": "ITBIS Backend is running successfully"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/signup")
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db)
):
    if data.role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    existing_user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = models.User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User created successfully",
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }


@app.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_token(
        user.id,
        user.role
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role
    }


@app.get("/protected")
def protected(
    payload=Depends(get_current_user)
):
    return {
        "message": "Protected endpoint accessed successfully",
        "user_id": payload.get("sub"),
        "role": payload.get("role")
    }


@app.get("/admin")
def admin_only(
    payload=Depends(require_roles("admin"))
):
    return {
        "message": "Admin endpoint accessed successfully",
        "user_id": payload.get("sub"),
        "role": payload.get("role")
    }


@app.post("/employees")
def create_employee(
    data: EmployeeCreate,
    payload=Depends(
        require_roles(
            "admin",
            "security_manager"
        )
    ),
    db: Session = Depends(get_db)
):
    existing_employee = db.query(
        models.Employee
    ).filter(
        models.Employee.employee_id == data.employee_id
    ).first()

    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists"
        )

    employee = models.Employee(
        employee_id=data.employee_id,
        name=data.name,
        department=data.department,
        designation=data.designation,
        manager_id=data.manager_id,
        device_info=data.device_info,
        access_privileges=data.access_privileges
    )

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return {
        "message": "Employee onboarded successfully",
        "employee_id": employee.employee_id
    }


@app.get("/employees")
def list_employees(
    payload=Depends(
        require_roles(
            "admin",
            "security_analyst",
            "soc_engineer"
        )
    ),
    db: Session = Depends(get_db)
):
    return db.query(
        models.Employee
    ).all()


@app.get("/employees/{employee_id}")
def get_employee(
    employee_id: str,
    payload=Depends(
        require_roles(
            "admin",
            "security_analyst",
            "soc_engineer"
        )
    ),
    db: Session = Depends(get_db)
):
    employee = db.query(
        models.Employee
    ).filter(
        models.Employee.employee_id == employee_id
    ).first()

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee


@app.post("/logs/ingest")
def receive_log(
    data: LogIngestRequest,
    payload=Depends(
        require_roles(
            "admin",
            "security_manager",
            "security_analyst",
            "soc_engineer"
        )
    )
):
    try:
        entry = ingest_log(
            data.employee_id,
            data.event_type,
            data.details
        )

        return {
            "message": "Log ingested",
            "event_type": entry["event_type"],
            "employee_id": entry["employee_id"]
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"MongoDB unavailable: {exc}"
        )


@app.get("/logs")
def list_recent_logs(
    payload=Depends(
        require_roles(
            "admin",
            "security_manager",
            "security_analyst",
            "soc_engineer"
        )
    )
):
    try:
        docs = list(
            activity_logs
            .find()
            .sort("timestamp", -1)
            .limit(20)
        )

        for doc in docs:
            doc["_id"] = str(doc["_id"])

            if "timestamp" in doc:
                doc["timestamp"] = doc[
                    "timestamp"
                ].isoformat()

        return docs

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"MongoDB unavailable: {exc}"
        )