from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Employee, Activity, User
from .schemas import EmployeeCreate, ActivityCreate, UserCreate
from .mongodb import activity_logs


app = FastAPI()


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# AUTHENTICATION SETTINGS
# ============================================================

SECRET_KEY = "itbis-secret-key-change-this-later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# PASSWORD FUNCTIONS
# ============================================================

def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
    password: str,
    hashed_password: str
):
    return pwd_context.verify(
        password,
        hashed_password
    )


# ============================================================
# JWT FUNCTIONS
# ============================================================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise credentials_exception

    return user


# ============================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================

def require_role(*allowed_roles):

    def checker(
        current_user: User = Depends(
            get_current_user
        )
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="Not authorized for this action"
            )

        return current_user

    return checker


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "status": "ITBIS backend is running"
    }


# ============================================================
# HELLO
# ============================================================

@app.get("/hello")
def hello():

    return {
        "message": "Hello Subramanya!"
    }


# ============================================================
# SIGNUP
# ============================================================

@app.post("/signup")
def signup(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    if user.role not in [
        "admin",
        "analyst",
        "employee"
    ]:

        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    hashed_password = hash_password(
        user.password
    )

    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "username": new_user.username,
        "role": new_user.role
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not existing_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    password_valid = verify_password(
        form_data.password,
        existing_user.hashed_password
    )

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token({
        "sub": existing_user.username,
        "role": existing_user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": existing_user.username,
        "role": existing_user.role
    }


# ============================================================
# CURRENT USER
# ============================================================

@app.get("/me")
def get_me(
    current_user: User = Depends(
        get_current_user
    )
):

    return {
        "username": current_user.username,
        "role": current_user.role
    }


# ============================================================
# EMPLOYEES - GET ALL
# ============================================================

@app.get("/employees")
def get_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    employees = db.query(Employee).all()

    return employees


# ============================================================
# EMPLOYEES - CREATE
# ============================================================

@app.post("/employees")
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    )
):

    existing_employee = db.query(Employee).filter(
        Employee.employee_id == employee.employee_id
    ).first()

    if existing_employee:

        raise HTTPException(
            status_code=400,
            detail="Employee ID already exists"
        )

    new_employee = Employee(
        employee_id=employee.employee_id,
        name=employee.name,
        department=employee.department,
        designation=employee.designation,
        manager_id=employee.manager_id,
        device_info=employee.device_info,
        access_privileges=employee.access_privileges
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {
        "message": "Employee created successfully",
        "employee_id": new_employee.employee_id
    }


# ============================================================
# EMPLOYEES - UPDATE
# ============================================================

@app.put("/employees/{employee_id}")
def update_employee(
    employee_id: str,
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    )
):

    existing_employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()

    if existing_employee is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    # Check if the new employee ID belongs
    # to another employee
    if employee.employee_id != employee_id:

        duplicate_employee = db.query(Employee).filter(
            Employee.employee_id == employee.employee_id
        ).first()

        if duplicate_employee:

            raise HTTPException(
                status_code=400,
                detail="New employee ID already exists"
            )

    existing_employee.employee_id = employee.employee_id
    existing_employee.name = employee.name
    existing_employee.department = employee.department
    existing_employee.designation = employee.designation
    existing_employee.manager_id = employee.manager_id
    existing_employee.device_info = employee.device_info
    existing_employee.access_privileges = employee.access_privileges

    db.commit()
    db.refresh(existing_employee)

    return {
        "message": "Employee updated successfully",
        "employee_id": existing_employee.employee_id
    }


# ============================================================
# EMPLOYEES - DELETE
# ============================================================

@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin")
    )
):

    existing_employee = db.query(Employee).filter(
        Employee.employee_id == employee_id
    ).first()

    if existing_employee is None:

        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    db.delete(existing_employee)
    db.commit()

    return {
        "message": "Employee deleted successfully",
        "employee_id": employee_id
    }


# ============================================================
# ACTIVITIES - GET
# ============================================================

@app.get("/activities")
def get_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    activities = db.query(Activity).all()

    return activities


# ============================================================
# ACTIVITIES - CREATE
# ============================================================

@app.post("/activities")
def create_activity(
    activity: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    new_activity = Activity(
        employee_id=activity.employee_id,
        activity_type=activity.activity_type,
        resource=activity.resource,
        timestamp=activity.timestamp,
        ip_address=activity.ip_address,
        device=activity.device
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return {
        "message": "Activity created successfully",
        "activity_id": new_activity.id
    }


# ============================================================
# ADMIN - GET USERS
# ============================================================

@app.get("/admin/users")
def admin_users(
    current_user: User = Depends(
        require_role("admin")
    ),
    db: Session = Depends(get_db)
):

    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
        for user in users
    ]


# ============================================================
# SECURITY OVERVIEW
# ============================================================

@app.get("/security/overview")
def security_overview(
    current_user: User = Depends(
        require_role("admin", "analyst")
    )
):

    return {
        "message": "Security overview accessible",
        "username": current_user.username,
        "role": current_user.role
    }


# ============================================================
# MONGODB - INGEST ACTIVITY LOG
# ============================================================

@app.post("/logs/ingest")
def ingest_log(
    log: dict,
    current_user: User = Depends(
        get_current_user
    )
):

    log_document = {
        "employee_id": log.get(
            "employee_id"
        ),

        "activity_type": log.get(
            "activity_type"
        ),

        "resource": log.get(
            "resource"
        ),

        "timestamp": log.get(
            "timestamp"
        ),

        "ip_address": log.get(
            "ip_address"
        ),

        "device": log.get(
            "device"
        ),

        "ingested_by": current_user.username,

        "ingested_at": datetime.utcnow()
    }

    result = activity_logs.insert_one(
        log_document
    )

    return {
        "message": "Activity log stored successfully",
        "log_id": str(
            result.inserted_id
        )
    }


# ============================================================
# MONGODB - GET ACTIVITY LOGS
# ============================================================

@app.get("/logs")
def get_logs(
    current_user: User = Depends(
        get_current_user
    )
):

    logs = list(
        activity_logs.find(
            {},
            {
                "_id": 1,
                "employee_id": 1,
                "activity_type": 1,
                "resource": 1,
                "timestamp": 1,
                "ip_address": 1,
                "device": 1,
                "ingested_by": 1,
                "ingested_at": 1
            }
        ).sort(
            "ingested_at",
            -1
        )
    )

    for log in logs:

        log["_id"] = str(
            log["_id"]
        )

    return logs