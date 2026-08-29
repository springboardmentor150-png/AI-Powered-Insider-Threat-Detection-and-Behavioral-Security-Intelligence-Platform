from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    department: str
    designation: str
    manager_id: int | None = None
    device_info: str | None = None
    access_privileges: str | None = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int

    class Config:
        from_attributes = True

class ActivityLogCreate(BaseModel):
    employee_id: str
    event_type: str
    details: dict
