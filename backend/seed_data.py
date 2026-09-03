"""
Seeds the database with the test data described in the Day 5 and Day 7 guides:
- One test user per role (4 total)
- 5-6 realistic employees across 2-3 departments, including a manager/report pair

Run with:
    python seed_data.py

Safe to re-run: it skips anything that already exists.
"""

from app.database import Base, engine, SessionLocal
from app.models import User, Employee
from app.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

TEST_USERS = [
    {"email": "analyst1@company.com", "password": "SecurePass123", "role": "security_analyst"},
    {"email": "soc1@company.com", "password": "SecurePass123", "role": "soc_engineer"},
    {"email": "manager1@company.com", "password": "SecurePass123", "role": "security_manager"},
    {"email": "admin1@company.com", "password": "SecurePass123", "role": "admin"},
]

TEST_EMPLOYEES = [
    {
        "employee_id": "EMP1001",
        "name": "Rohit Sharma",
        "department": "Finance",
        "designation": "Finance Manager",
        "manager_id": None,
        "device_info": "laptop-fin-01",
        "access_privileges": "manager",
    },
    {
        "employee_id": "EMP1002",
        "name": "Ayesha Khan",
        "department": "Finance",
        "designation": "Financial Analyst",
        "manager_id": None,  # resolved below to EMP1001's internal id
        "device_info": "laptop-fin-02",
        "access_privileges": "standard",
    },
    {
        "employee_id": "EMP1003",
        "name": "Daniel Lee",
        "department": "IT",
        "designation": "System Administrator",
        "manager_id": None,
        "device_info": "laptop-it-01",
        "access_privileges": "admin",
    },
    {
        "employee_id": "EMP1004",
        "name": "Priya Nair",
        "department": "IT",
        "designation": "Support Engineer",
        "manager_id": None,  # resolved below to EMP1003's internal id
        "device_info": "laptop-it-02",
        "access_privileges": "standard",
    },
    {
        "employee_id": "EMP1005",
        "name": "Marcus Webb",
        "department": "Sales",
        "designation": "Sales Executive",
        "manager_id": None,
        "device_info": "laptop-sal-01",
        "access_privileges": "standard",
    },
    {
        "employee_id": "EMP1006",
        "name": "Sara Ibrahim",
        "department": "Sales",
        "designation": "Sales Manager",
        "manager_id": None,
        "device_info": "laptop-sal-02",
        "access_privileges": "manager",
    },
]

# manager relationships: employee_id -> manager's employee_id
MANAGER_LINKS = {
    "EMP1002": "EMP1001",
    "EMP1004": "EMP1003",
}


def seed_users():
    for u in TEST_USERS:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            print(f"  skip (exists): {u['email']}")
            continue
        user = User(
            email=u["email"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
        )
        db.add(user)
        print(f"  created: {u['email']} ({u['role']})")
    db.commit()


def seed_employees():
    created_by_employee_id = {}

    for e in TEST_EMPLOYEES:
        existing = db.query(Employee).filter(Employee.employee_id == e["employee_id"]).first()
        if existing:
            print(f"  skip (exists): {e['employee_id']}")
            created_by_employee_id[e["employee_id"]] = existing
            continue

        employee = Employee(
            employee_id=e["employee_id"],
            name=e["name"],
            department=e["department"],
            designation=e["designation"],
            manager_id=None,
            device_info=e["device_info"],
            access_privileges=e["access_privileges"],
        )
        db.add(employee)
        db.flush()  # get employee.id without a full commit yet
        created_by_employee_id[e["employee_id"]] = employee
        print(f"  created: {e['employee_id']} - {e['name']}")

    db.commit()

    # second pass: wire up manager_id now that every employee has a real internal id
    for report_emp_id, manager_emp_id in MANAGER_LINKS.items():
        report = created_by_employee_id.get(report_emp_id)
        manager = created_by_employee_id.get(manager_emp_id)
        if report and manager and report.manager_id != manager.id:
            report.manager_id = manager.id
            print(f"  linked: {report_emp_id} -> reports to -> {manager_emp_id}")
    db.commit()


if __name__ == "__main__":
    print("Seeding test users...")
    seed_users()
    print("\nSeeding test employees...")
    seed_employees()
    print("\nDone. Test user password for all accounts: SecurePass123")
    db.close()
