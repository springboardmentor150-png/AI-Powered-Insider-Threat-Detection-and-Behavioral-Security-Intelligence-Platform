# ITBIS Backend — FastAPI

## Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.11+ |
| PostgreSQL | 14+ |
| MongoDB | 6+ |

---

## Quick start

### 1 — Create the database

```sql
-- In psql or pgAdmin
CREATE USER itbis WITH PASSWORD 'changeme';
CREATE DATABASE itbis OWNER itbis;
```

### 2 — Configure environment

```bash
cd backend
copy .env.example .env      # Windows
# or: cp .env.example .env  # Mac/Linux
```

Edit `.env` and set real values if needed. For local dev the defaults work as-is if your PostgreSQL/MongoDB are on localhost with default ports.

### 3 — Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4 — Seed the databases

```bash
cd backend
python seed.py
```

This creates all PostgreSQL tables, inserts sample users/employees/alerts/incidents, and loads 24 activity logs into MongoDB. It is **safe to re-run** — existing records are skipped.

**Demo credentials after seeding:**

| Email | Password | Role |
|---|---|---|
| admin@northwind.co | Admin@1234 | Administrator |
| priya.raman@northwind.co | Manager@1234 | Security Manager |
| jonas.hale@northwind.co | Analyst@1234 | Security Analyst |
| mei.tanaka@northwind.co | Soc@12345678 | SOC Engineer |

### 5 — Start the API server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: http://localhost:8000/docs

---

## Connecting the frontend

1. Copy `.env.example` to `.env` in the **project root** (not backend/):
   ```
   VITE_API_URL=http://localhost:8000
   ```
2. Run `npm run dev` — the frontend will call the real backend.
3. Without `VITE_API_URL` set, the frontend runs in **mock/demo mode** with static data — no backend needed.

---

## API routes

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /auth/signup | — | Register first user (auto-Admin) |
| POST | /auth/login | — | Get JWT token |
| GET | /auth/me | Bearer | Current user profile |
| GET | /employees | Bearer | List employees (dept filter) |
| POST | /employees | Admin/Manager | Create employee |
| PATCH | /employees/{id} | Admin/Manager | Update employee |
| GET | /alerts | Bearer | List alerts (filters) |
| PATCH | /alerts/{id} | Bearer | Update alert status |
| GET | /activity-logs | Bearer | List logs (filters) |
| POST | /activity-logs | Admin/SOC | Ingest log event |
| GET | /users | Admin | List platform users |
| POST | /users | Admin | Create platform user |
| GET | /health | — | Liveness probe |

---

## Architecture

```
PostgreSQL (via SQLAlchemy async)
  ├── users         — console accounts + bcrypt passwords
  ├── employees     — monitored workforce identities
  ├── alerts        — threat detection records
  └── incidents     — investigation cases

MongoDB (via Motor async)
  └── activity_logs — behavioural telemetry events
```
