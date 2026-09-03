# ITBIS — Insider Threat Behavioral Intelligence System

Milestone 1 implementation (Days 1–8): project setup, authentication & RBAC,
and employee identity/profile management, generated from the ITBIS deep-dive
student guides.

## Project layout

```
itbis/
├── backend/     FastAPI + PostgreSQL + MongoDB
└── frontend/    Next.js (App Router) + Tailwind + axios
```

## Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit .env with your real DB credentials
```

You need PostgreSQL and MongoDB running locally (or update `DATABASE_URL` /
`MONGO_URL` in `.env`). If you don't have them installed yet, you can point
`DATABASE_URL` at `sqlite:///./itbis.db` temporarily to keep moving.

Create the tables and seed test data:

```bash
python seed_data.py
```

This creates one test user per role (password `SecurePass123` for all):
- analyst1@company.com (security_analyst)
- soc1@company.com (soc_engineer)
- manager1@company.com (security_manager)
- admin1@company.com (admin)

...and 6 sample employees across Finance, IT, and Sales, including two
manager/report relationships.

Run the API:

```bash
uvicorn app.main:app --reload
```

- http://127.0.0.1:8000/ → health check
- http://127.0.0.1:8000/docs → interactive Swagger docs

## Frontend setup

```bash
cd frontend
npm install
cp .env.local.example .env.local   # defaults to http://127.0.0.1:8000
npm run dev
```

Visit http://localhost:3000. You should see the backend's health-check
message, then be able to log in at `/login` with a seeded account and view
the employee list at `/employees`.

## What's implemented

**Day 1–2** — Architecture and PostgreSQL/MongoDB schema (see `app/models.py`
for the relational tables; `app/database.py` exposes the Mongo collections
for `activity_logs` and `behavioral_baselines`, ready for later milestones).

**Day 3–4** — FastAPI health check, CORS configured for the Next.js frontend,
Next.js app connecting to it live.

**Day 5–6** — `/auth/signup`, `/auth/login` with bcrypt password hashing and
JWT tokens; `require_role()` dependency enforcing the 4-role RBAC model on
every protected endpoint.

**Day 7–8** — Full employee CRUD (`onboard`, `get`, `list` with department
filter, `PATCH` with `exclude_unset` partial updates), manager/report lookups
(`/employees/{id}/reports`), and department mapping
(`/departments/{department}/employees`).

**Not included**: Day 9–10 (activity log ingestion, Milestone 1 demo) — that
guide wasn't provided when this project was generated. The MongoDB
connection and collections it will need are already wired up in
`app/database.py`.

## Testing the RBAC boundaries (Day 6 self-check)

| Endpoint | Should work for | Should be blocked for |
|---|---|---|
| `GET /admin/users` | admin | everyone else |
| `GET /employees/{id}` | admin, security_analyst, soc_engineer, security_manager | — |
| `PATCH /employees/{id}` | admin, security_manager | security_analyst, soc_engineer |
| `GET /reports/risk-posture` | admin, security_manager | security_analyst, soc_engineer |
| `GET /alerts/my` | all 4 roles | — |

Log in as each seeded user in `/docs`, copy the `access_token`, and call each
endpoint with `Authorization: Bearer <token>` to confirm the expected
200/403 responses.
