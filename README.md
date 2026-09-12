# Insider Threat Behavioral Intelligence System (ITBIS)

**Insider Threat Behavioral Intelligence System (ITBIS)** is an enterprise-grade cybersecurity platform engineered to monitor, analyze, and investigate risky insider behavior performed by employees with authorized system access.

---

## 🏛️ System Architecture

```
                                 +-------------------------+
                                 |  Next.js Frontend Client |
                                 |   (http://localhost:3000)|
                                 +------------+------------+
                                              |
                                              v  REST APIs / JWT Bearer
                                 +------------+------------+
                                 |  FastAPI Backend Server |
                                 |   (http://localhost:8000)|
                                 +-----+-------------+-----+
                                       |             |
                        +--------------+             +--------------+
                        v                                           v
         +--------------+--------------+             +--------------+--------------+
         |     PostgreSQL Relational   |             |      MongoDB Document Store |
         | (Users, Employees, Alerts,  |             | (Activity Logs, Behavioral  |
         |           Incidents)        |             |          Baselines)         |
         +-----------------------------+             +-----------------------------+
```

### Why Dual Databases?
* **PostgreSQL**: Used for structured relational data requiring strict schema integrity (User accounts, employee identities, security alerts, and incident dockets).
* **MongoDB**: Used for high-speed flexible JSON document telemetry ingestion (Device logins, off-hours file downloads, USB insertions, VPN logins, and privilege escalations).

---

## ⚡ Technology Stack

### Backend
* **Language**: Python 3.10+
* **Framework**: FastAPI (Uvicorn ASGI Web Server)
* **Relational DB**: PostgreSQL / SQLite fallback (SQLAlchemy ORM)
* **Document DB**: MongoDB (PyMongo Client with Fallback Engine)
* **Authentication**: JWT Tokens (8-Hour Expiration)
* **Password Hashing**: Passlib + Bcrypt
* **Validation**: Pydantic v2
* **CORS**: Configured for `http://localhost:3000`

### Frontend
* **Framework**: Next.js 14 (App Router)
* **Library**: React 18 + TypeScript
* **Styling**: Vanilla Tailwind CSS (Custom Dark SOC Theme)
* **HTTP Client**: Axios (Centralized Bearer Token Interceptor)
* **Icons**: Lucide React

---

## 🔑 Role-Based Access Control (RBAC) Matrix

| Feature / Page | Security Analyst | SOC Engineer | Security Manager | Admin |
| :--- | :---: | :---: | :---: | :---: |
| **View Dashboard** | ✅ | ✅ | ✅ | ✅ |
| **View Employee Profiles** | ✅ | ✅ | ✅ | ✅ |
| **Create / Edit Employees** | ❌ | ❌ | ✅ | ✅ |
| **Delete Employee** | ❌ | ❌ | ❌ | ✅ |
| **View Activity Logs** | ✅ | ✅ | ✅ | ✅ |
| **Test Log Ingestion** | ✅ | ✅ | ✅ | ✅ |
| **View & Update Alerts** | ✅ | ✅ | ✅ | ✅ |
| **View & Update Incidents** | ✅ | ✅ | ✅ | ✅ |
| **Admin User Management** | ❌ | ❌ | ❌ | ✅ |
| **System Settings** | ❌ | ❌ | ❌ | ✅ |

*Note: Unauthorized role access attempts trigger backend HTTP 403 Forbidden responses and render a high-tech UI Access Denied screen.*

---

## 🚀 Easy Windows Setup & Quickstart

### Prerequisites
* Python 3.10 or higher
* Node.js v18 or higher
* PostgreSQL & MongoDB (Optional: The application includes automatic fallback engines if database servers are not active during local testing).

---

### Step 1: Clone & Configure Environment Variables

```bash
# Clone or navigate to ITBIS workspace
cd ITBIS

# Copy environment variable templates
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
```

---

### Step 2: Backend Setup & Seeding

Open PowerShell or Command Prompt:

```powershell
cd backend

# 1. Create Virtual Environment
python -m venv venv

# 2. Activate Virtual Environment
venv\Scripts\activate

# 3. Install Python Dependencies
pip install -r requirements.txt

# 4. Seed Database (Creates Users, Employees, Activity Logs, Alerts, Incidents)
python seed.py

# 5. Start FastAPI Backend Server
uvicorn app.main:app --reload --port 8000
```

Backend API Swagger documentation will be available at:
👉 **`http://localhost:8000/docs`**

---

### Step 3: Frontend Setup

Open a **second** PowerShell window:

```powershell
cd ITBIS\frontend

# 1. Install Node Packages
npm install

# 2. Start Development Server
npm run dev
```

Frontend application will open at:
👉 **`http://localhost:3000`**

---

## 🔒 Pre-Populated Demo Account Credentials

| Role | Username | Email | Password |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin@itbis.sec` | `AdminPassword123!` |
| **Security Manager** | `manager_sec` | `manager@itbis.sec` | `ManagerPassword123!` |
| **SOC Engineer** | `soc_eng` | `soc@itbis.sec` | `SocPassword123!` |
| **Security Analyst** | `analyst_l1` | `analyst@itbis.sec` | `AnalystPassword123!` |

*(Pro-tip: Use the 1-Click Quick Demo Login shortcuts on the Login page at `http://localhost:3000/login` to log in instantly as any role!)*

---

## 📑 API Endpoints Summary

### Authentication
* `POST /auth/signup` — Register new security user
* `POST /auth/login` — Authenticate and obtain JWT token
* `GET /auth/me` — Get logged-in user profile

### Employee Management
* `GET /employees` — List all monitored employees
* `POST /employees` — Add employee (*Security Manager / Admin*)
* `GET /employees/{employee_id}` — Get detailed profile & telemetry timeline
* `PUT /employees/{employee_id}` — Update employee details
* `DELETE /employees/{employee_id}` — Delete employee (*Admin Only*)

### Activity Log Ingestion (MongoDB)
* `POST /logs/ingest` — Ingest activity log document
* `GET /logs` — Filter and fetch activity log feed
* `GET /logs/{employee_id}` — Get logs for specific employee

### Security Alerts & Incidents
* `GET /alerts` — List security alerts
* `PUT /alerts/{alert_id}` — Update alert status
* `GET /incidents` — List active incident dockets
* `POST /incidents` — Create incident case
* `GET /incidents/{incident_id}` — Detailed incident docket inspection
* `PUT /incidents/{incident_id}` — Update incident status workflow

### Administration & Health
* `GET /admin/users` — List system users (*Admin Only*)
* `PUT /admin/users/{user_id}` — Change user role/status (*Admin Only*)
* `GET /dashboard/stats` — Real-time SOC dashboard metrics
* `GET /health` — Multi-database health status check

---

## 🎯 Milestone Roadmap

### Completed in Milestone 1 (Day 1 - 10)
- [x] Complete Full-Stack Architecture
- [x] Dual PostgreSQL & MongoDB Database Integrations
- [x] Fast-API REST APIs with Swagger OpenAPI Documentation
- [x] JWT Authentication & Passlib/Bcrypt Hashing
- [x] 4-Tier Role-Based Access Control (RBAC) on Backend APIs & Frontend UI
- [x] Employee Registry & Profile Telemetry Timelines
- [x] MongoDB Activity Log Ingestion (`POST /logs/ingest`)
- [x] Interactive "Test Log Ingestion" Form
- [x] Live Cybersecurity Dashboard with real-time stats and SVG charts
- [x] Alert & Incident Management Workflows
- [x] Admin User Management & System Diagnostics
- [x] Automatic Database Seeding & Easy Local Windows Execution

### Reserved for Milestone 2 (Future Machine Learning & XAI Integration)
- [ ] Isolation Forest & Autoencoder Anomaly Detection Pipeline
- [ ] Real-Time Dynamic Risk Score Computation (0-100)
- [ ] SHAP / LIME Explainable AI (XAI) Feature Importance Attribution
- [ ] Automated Behavioral Baseline Model Retraining
