# ITBIS — Milestone 4: Analytics, Testing & Deployment

Complete M4 demonstration package based on the student handout.

## Included
- Admin dashboard: platform counts, users by role, system health, recent users and audit trail
- Login + role-based access checks
- Users, Employees, Activity Logs, Anomalies, Risk Analysis, Incidents, Reports and Settings pages
- In-app notification endpoint
- Excel and PDF insider-threat exports
- Automated API tests for login, ingestion, risk score and admin role restriction
- Backend and frontend Dockerfiles
- Four-service docker-compose: backend, frontend, PostgreSQL, MongoDB
- README + MIT License

## Demo credentials
admin@itbis.com / Admin@123
manager@itbis.com / Manager@123
analyst@itbis.com / Analyst@123
soc@itbis.com / Soc@123

## Local run
Backend:
```powershell
cd backend
py -m venv venv
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Frontend in another terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:3000/login

## Tests
```powershell
cd backend
pytest
```

## Docker
```powershell
docker compose up --build
```

Frontend http://localhost:3000 and API docs http://localhost:8000/docs.

## Scope note
Notifications are represented as structured in-app data. This package uses in-memory demo data so it can run immediately; for production, persist data in PostgreSQL/MongoDB and inject DATABASE_URL, MONGO_URL and SECRET_KEY through environment variables.
