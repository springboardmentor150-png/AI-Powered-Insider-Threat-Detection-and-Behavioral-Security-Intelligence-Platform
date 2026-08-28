# AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform

## Project Description

This platform monitors employee activity within an organization to detect unusual or risky behavior from people who already have legitimate access to systems and data. Unlike traditional security tools that focus on external attackers, this system focuses on **insider threats** — employees, contractors, or administrators who may misuse their access.

The system collects activity logs, establishes behavioral baselines, and eventually identifies deviations that could indicate security risks such as:

- An employee downloading confidential files unusually
- An administrator escalating privileges
- An employee accessing systems outside normal working hours
- Unusual file downloads, USB device activity, or login behavior

## Problem Being Solved

Organizations spend heavily on perimeter security but often overlook threats from within. Insider threats — whether malicious, negligent, or compromised — can cause significant data breaches and financial loss. This platform provides behavioral intelligence to detect and respond to such risks early.

## Architecture

```
┌─────────────────────┐
│      USERS          │
│  (Platform Users)   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│   NEXT.JS FRONTEND  │
│   (Port 3000)       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  FASTAPI BACKEND    │
│  (Port 8000)        │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌────────────┐  ┌──────────┐
│ PostgreSQL │  │  MongoDB  │
│(Structured)│  │(Flexible) │
└────────────┘  └──────────┘
```

## Technology Stack

| Layer          | Technology                          |
|----------------|-------------------------------------|
| Frontend       | Next.js, React, Axios               |
| Backend        | FastAPI, Python, Uvicorn            |
| Authentication | JWT, bcrypt, Passlib                |
| ORM            | SQLAlchemy                          |
| Database (SQL) | PostgreSQL                          |
| Database (NoSQL)| MongoDB                           |
| Dev Tools      | VS Code, Git, GitHub, Postman       |

## Folder Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── security.py
│   │   ├── log_ingestion.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth_routes.py
│   │       ├── employee_routes.py
│   │       └── log_routes.py
│   ├── requirements.txt
│   └── .env
├── frontend/
├── .gitignore
└── README.md
```

## Database Design

### PostgreSQL Tables

**users** — Platform users who log into the application
| Field          | Type    | Notes                     |
|----------------|---------|---------------------------|
| id             | Integer | Primary Key               |
| email          | String  | Unique, Required          |
| password_hash  | String  | Required                  |
| role           | String  | Required (see roles below)|

**employees** — People being monitored by the platform
| Field             | Type    | Notes                          |
|-------------------|---------|--------------------------------|
| id                | Integer | Primary Key                    |
| employee_id       | String  | Unique, e.g. EMP1001           |
| name              | String  | Required                       |
| department        | String  | Optional                       |
| designation       | String  | Optional                       |
| manager_id        | Integer | FK → employees.id (self-ref)   |
| device_info       | String  | Optional                       |
| access_privileges | String  | Optional                       |

**incidents** — Security incidents (foundation for future use)
| Field        | Type     | Notes                     |
|--------------|----------|---------------------------|
| id           | Integer  | Primary Key               |
| employee_id  | Integer  | FK → employees.id         |
| status       | String   | open / investigating / resolved |
| severity     | String   | informational / low / medium / high / critical |
| created_at   | DateTime | Auto-generated            |

**alerts** — Security alerts (foundation for future use)
| Field        | Type     | Notes                     |
|--------------|----------|---------------------------|
| id           | Integer  | Primary Key               |
| employee_id  | Integer  | FK → employees.id         |
| severity     | String   | Required                  |
| message      | String   | Required                  |
| assigned_to  | Integer  | FK → users.id (nullable)  |
| created_at   | DateTime | Auto-generated            |

### MongoDB Collections

**activity_logs** — Flexible employee activity records
```json
{
  "employee_id": "EMP1001",
  "event_type": "login",
  "timestamp": "2026-08-28T10:00:00Z",
  "details": {
    "ip_address": "192.168.1.10",
    "device": "laptop-01",
    "location": "Bengaluru Office"
  }
}
```

## Platform User Roles

| Role              | Description                                    |
|-------------------|------------------------------------------------|
| security_analyst  | Reviews alerts, investigates suspicious behavior |
| soc_engineer      | Monitors security events and anomalies          |
| security_manager  | Views organization-wide risk and trends         |
| admin             | Manages platform users and system settings      |

## How to Set Up

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- MongoDB

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/itbis_db
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=your-secret-key-here
```

Run the backend:
```bash
cd app
uvicorn main:app --reload
```

Access Swagger docs: http://127.0.0.1:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Access frontend: http://localhost:3000

## API Endpoints

| Method | Endpoint                    | Description              | Auth Required |
|--------|-----------------------------|--------------------------|---------------|
| GET    | /                           | Health check             | No            |
| POST   | /auth/signup                | Register a new user      | No            |
| POST   | /auth/login                 | Login and get JWT        | No            |
| GET    | /admin/users                | List all users           | Admin only    |
| GET    | /reports/risk-posture       | Risk posture report      | Admin, Manager|
| GET    | /alerts/my                  | View my alerts           | All roles     |
| POST   | /employees                  | Create employee          | Admin, Manager|
| GET    | /employees                  | List all employees       | Admin, Analyst, SOC|
| GET    | /employees/{employee_id}    | Get employee by ID       | Admin, Analyst, SOC|
| PUT    | /employees/{employee_id}    | Update employee          | Admin, Manager|
| DELETE | /employees/{employee_id}    | Delete employee          | Admin, Manager|
| POST   | /logs/ingest                | Ingest activity log      | All roles     |

## Authentication Flow

1. User signs up with email, password, and role
2. Password is hashed with bcrypt before storage
3. User logs in with email and password
4. Server verifies credentials and returns a JWT
5. Client stores the JWT and sends it in the `Authorization: Bearer <token>` header
6. Server validates the token for each protected request

## Milestone 1 Features — Completed

- Project architecture and database schema
- FastAPI backend setup with CORS
- Next.js frontend setup
- PostgreSQL integration with SQLAlchemy
- MongoDB integration with PyMongo
- User signup and login
- Bcrypt password hashing
- JWT authentication
- Role-based access control (4 roles)
- Employee profile management (CRUD)
- Activity log ingestion pipeline
- Sample/mock activity log testing

## Future Work (Later Milestones)

- Behavioral profiling engine
- Anomaly detection with ML
- Insider risk scoring
- Threat investigation module
- UEBA intelligence engine
- Alert and incident management workflow
- Dashboard and analytics
- Notification and escalation system
- Reports and export
- Docker deployment
