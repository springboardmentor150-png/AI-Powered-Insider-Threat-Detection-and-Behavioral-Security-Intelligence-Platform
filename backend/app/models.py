from sqlalchemy import Column, Integer, String
from passlib.context import CryptContext
from app.database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    role = Column(String)  # "security_analyst", "soc_engineer", "security_manager", "admin"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True)
    name = Column(String)
    department = Column(String)
    designation = Column(String)
    manager_id = Column(Integer, nullable=True)
    device_info = Column(String, nullable=True)
    access_privileges = Column(String, nullable=True)