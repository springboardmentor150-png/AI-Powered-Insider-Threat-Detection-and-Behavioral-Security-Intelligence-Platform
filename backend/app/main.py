
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from collections import Counter

from app.database import engine, Base, get_db
from app.models import User, Employee
from app.auth import get_current_user
from app.routes.auth_routes import router as auth_router
from app.routes.employee_routes import router as employee_router
from app.routes.log_routes import router as log_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ITBIS API", version="1.0.0")

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

app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(log_router)


@app.get("/")
def health_check():
    return {"status": "ITBIS backend is running"}


def check_report_access(user):
    if user.role not in ("admin", "security_manager"):
        raise HTTPException(
            status_code=403,
            detail="Admin or security manager access required",
        )


@app.get("/dashboard/admin")
def admin_dashboard(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    users = db.query(User).all()
    role_counts = dict(Counter(u.role for u in users))

    return {
        "user_count": len(users),
        "employee_count": db.query(Employee).count(),
        "total_incidents": None,
        "open_incidents": None,
        "users_by_role": role_counts,
        "note": "Incident counts unavailable: Incident model is not configured.",
    }


@app.get("/reports/insider-threat/excel")
def export_excel(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    check_report_access(user)

    from openpyxl import Workbook

    employees = db.query(Employee).all()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Employee Report"

    sheet.append([
        "Employee ID", "Name", "Email",
        "Department", "Role", "Status",
    ])

    for employee in employees:
        sheet.append([
            employee.employee_id,
            employee.name,
            employee.email,
            employee.department or "",
            employee.role or "",
            employee.status or "",
        ])

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="itbis_employee_report.xlsx"'
        },
    )


@app.get("/reports/insider-threat/pdf")
def export_pdf(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    check_report_access(user)

    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    )
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet

    employees = db.query(Employee).all()
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    data = [[
        "Employee ID", "Name", "Email",
        "Department", "Role", "Status",
    ]]

    for employee in employees:
        data.append([
            str(employee.employee_id),
            str(employee.name),
            str(employee.email),
            str(employee.department or ""),
            str(employee.role or ""),
            str(employee.status or ""),
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    document.build([
        Paragraph("ITBIS Employee Report", styles["Title"]),
        Spacer(1, 16),
        table,
    ])

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                'attachment; filename="itbis_employee_report.pdf"'
        },
    )
