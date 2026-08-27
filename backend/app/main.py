from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import hash_password, verify_password
from .database import get_db
from .dependencies import get_current_user, require_role
from .jwt_auth import create_access_token
from .models import Employee, User
from .mongo import activity_logs
from .schemas import ActivityLogCreate, EmployeeCreate


app = FastAPI(title="ITBIS API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ITBIS backend is running"}


@app.post("/activity")
def create_activity(activity: ActivityLogCreate):
    document = activity.model_dump()
    document["timestamp"] = datetime.now(timezone.utc)

    result = activity_logs.insert_one(document)

    return {
        "message": "Activity logged successfully",
        "id": str(result.inserted_id),
    }


@app.get("/activity/{employee_code}")
def get_employee_activity(employee_code: str):
    documents = list(
        activity_logs.find(
            {"employee_code": employee_code}
        ).sort("timestamp", -1)
    )

    for document in documents:
        document["id"] = str(document.pop("_id"))

    return {
        "employee_code": employee_code,
        "count": len(documents),
        "activities": documents,
    }


@app.post("/auth/signup")
def signup(
    email: str,
    password: str,
    role: str = "analyst",
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    password_hash = hash_password(password)

    user = User(
        email=email,
        password_hash=password_hash,
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    }


@app.post("/auth/login")
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    }


@app.get("/auth/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "message": "Authenticated user",
        "user_id": current_user["sub"],
        "role": current_user["role"],
    }


@app.get("/admin-test")
def admin_test(current_user=Depends(require_role("admin"))):
    return {
        "message": "Admin access granted",
        "user_id": current_user["sub"],
        "role": current_user["role"],
    }


@app.post("/employees")
def create_employee(
    employee: EmployeeCreate,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    existing_employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee.employee_code)
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail="Employee code already registered",
        )

    existing_email = (
        db.query(Employee)
        .filter(Employee.email == employee.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Employee email already registered",
        )

    new_employee = Employee(
        employee_code=employee.employee_code,
        name=employee.name,
        email=employee.email,
        department=employee.department,
        role=employee.role,
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {
        "message": "Employee created successfully",
        "id": new_employee.id,
        "employee_code": new_employee.employee_code,
        "name": new_employee.name,
        "email": new_employee.email,
        "department": new_employee.department,
        "role": new_employee.role,
    }


@app.get("/employees/{employee_code}")
def get_employee(
    employee_code: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    employee = (
        db.query(Employee)
        .filter(Employee.employee_code == employee_code)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    return {
        "id": employee.id,
        "employee_code": employee.employee_code,
        "name": employee.name,
        "email": employee.email,
        "department": employee.department,
        "role": employee.role,
        "created_at": employee.created_at,
    }


@app.get("/employees")
def list_employees(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    employees = (
        db.query(Employee)
        .order_by(Employee.id)
        .all()
    )

    return {
        "count": len(employees),
        "employees": [
            {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "name": employee.name,
                "email": employee.email,
                "department": employee.department,
                "role": employee.role,
                "created_at": employee.created_at,
            }
            for employee in employees
        ],
    }