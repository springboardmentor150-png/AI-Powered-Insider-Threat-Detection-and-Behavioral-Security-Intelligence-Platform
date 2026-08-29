from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models import User, hash_password, verify_password
from app.models import Employee
from app.auth import create_token, decode_token
from app.log_ingestion import ingest_log

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ITBIS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_check():
    return {"status": "ITBIS backend is running"}

class SignupRequest(BaseModel):
    email: str
    password: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), role=data.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created", "user_id": user.id, "role": user.role}

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.id, user.role)
    return {"access_token": token, "token_type": "bearer", "role": user.role}

def require_role(*allowed_roles):
    def checker(authorization: str = Header(...)):
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        if payload["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not authorized for this action")
        return payload
    return checker

@app.get("/admin/users")
def list_users(user=Depends(require_role("admin"))):
    return {"message": "Only admins see this"}

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    department: str
    designation: str
    manager_id: int | None = None

@app.post("/employees")
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db), user=Depends(require_role("admin", "security_manager"))):
    employee = Employee(**data.dict())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return {"message": "Employee onboarded", "employee_id": employee.employee_id}

@app.get("/employees/{employee_id}")
def get_employee(employee_id: str, db: Session = Depends(get_db), user=Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager"))):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.get("/employees")
def list_employees(db: Session = Depends(get_db), user=Depends(require_role("admin", "security_analyst", "soc_engineer", "security_manager"))):
    return db.query(Employee).all()

@app.post("/logs/ingest")
def receive_log(employee_id: str, event_type: str, details: dict):
    entry = ingest_log(employee_id, event_type, details)
    return {"message": "Log ingested", "event_type": event_type}