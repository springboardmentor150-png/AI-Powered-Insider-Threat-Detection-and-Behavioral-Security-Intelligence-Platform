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

---

## 🧠 Milestone 2 (Day 11 - Day 20) — Behavioral Intelligence & Machine Learning

Milestone 2 transforms raw activity logs into per-employee empirical baselines, statistical rule-based anomaly detection, and unsupervised Isolation Forest ML outlier detection.

```
Milestone 1 Activity Logs
           ↓
Behavioral Baselines (5 Indicators)
           ↓
Rule-Based Anomaly Detection (Numeric Z-Score / Set Membership)
           ↓
ML Feature Matrix (1 Row / Employee / Day)
           ↓
Isolation Forest Model Training & Decision Scoring
           ↓
ML Anomaly Results (ml_anomalies Collection)
           ↓
Combined Anomaly Report (GET /anomalies/{employee_id})
           ↓
All-Employee Top 10 Summary (GET /anomalies/summary)
```

---

### 📊 Behavioral Baselines (Day 11 - Day 14)
Baselines are calculated **per employee** to answer: *"What does normal look like for THIS specific employee?"*

#### The 5 Core Baseline Indicators:
1. `login_time` *(Numeric)*: Decimal hour mean ($\mu$) & standard deviation ($\sigma$). Example: 09:30 AM = 9.5.
2. `resource_access_frequency` *(Numeric)*: Mean daily access count ($\mu$) & standard deviation ($\sigma$) across file, app, USB, and privilege events.
3. `data_transfer_volume` *(Numeric)*: Mean daily transfer volume in MB ($\mu$) & standard deviation ($\sigma$).
4. `device_usage` *(Set-Based)*: Sorted list of known workstation/device strings.
5. `application_usage` *(Set-Based)*: Sorted list of known software applications and processes.

> [!NOTE]
> **Minimum Sample Size Requirement:** Requires at least **5 events** before establishing an active baseline. Employees with < 5 samples return `insufficient_data` and are **NOT** falsely flagged as anomalous.

---

### 🚨 Rule-Based Anomaly Detection (Day 15 - Day 16)
- **Numeric Anomaly Detector**:
  - Safety floor: $\text{spread} = \max(\sigma, 0.1)$ to prevent division by zero or inflated ratios on low variance.
  - Deviation ratio: $\text{ratio} = \frac{|\text{observed} - \mu|}{\text{spread}}$
  - Flagged if $\text{ratio} > 2.0$.
  - Severity Assignment: `critical` if $\text{ratio} > 5.0$, `high` if $\text{ratio} > 3.0$, `medium` otherwise.
- **Set-Membership Detector**:
  - Flags unknown devices or unapproved application processes with severity `high`.
- **Live Ingestion Hook**: Log ingestion (`POST /logs/ingest`) evaluates incoming logs live against baselines and immediately records detected anomalies into `rule_anomalies`.

---

### 🤖 Machine Learning Pipeline (Day 17 - Day 18)
- **Feature Matrix (`backend/app/ml_features.py`)**: Aggregates raw logs into 1 row per employee per day with features:
  - `avg_login_hour`
  - `download_count`
  - `total_download_mb`
  - `unique_devices`
  - `total_events`
- **Isolation Forest Model (`backend/app/ml_anomaly.py`)**:
  - `sklearn.ensemble.IsolationForest(n_estimators=100, contamination=0.08, random_state=42)`
  - Saves binary model to `backend/models/anomaly_model.pkl` (git-ignored).
  - Scores decision function (more negative score = higher multi-dimensional anomaly).
  - Stores flagged outlier days in MongoDB collection `ml_anomalies`.

---

### 🔌 Milestone 2 API Reference (Day 19)

| Method | Endpoint | Description | Roles Allowed |
| :--- | :--- | :--- | :--- |
| `GET` | `/anomalies/{employee_id}` | Combined anomaly report (Rule anomalies sorted by severity + ML outliers sorted by score) | All Roles |
| `GET` | `/anomalies/summary` | MongoDB aggregation for Top 10 flagged employees | All Roles |
| `GET` | `/anomalies/baselines/{employee_id}` | Fetch baseline indicators for employee | All Roles |
| `POST` | `/anomalies/generate-baselines` | Trigger baseline computation for employee or `ALL` | All Roles |
| `POST` | `/anomalies/run-ml` | Trigger Isolation Forest feature engineering & ML pipeline | All Roles |

---

### 🛠️ How to Run & Test Milestone 2

#### 1. Generate Baselines & Seed Data
```powershell
# Run seed script (generates 7-day baseline logs, computes baselines, seeds test anomalies, runs ML pipeline)
backend\venv\Scripts\python.exe backend/seed.py
```

#### 2. Run Baseline Generator Independently
```powershell
backend\venv\Scripts\python.exe backend/scripts/generate_baselines.py
```

#### 3. Run Isolation Forest ML Detection Pipeline Independently
```powershell
backend\venv\Scripts\python.exe backend/scripts/run_ml_detection.py --contamination 0.08
```

#### 4. Execute Automated Test Suite
```powershell
backend\venv\Scripts\python.exe -m unittest backend/tests/test_milestone2.py
```

---

### 🎬 5-7 Minute Milestone 2 Demo Flow Guide

1. **Start System**:
   - Backend: `backend\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000`
   - Frontend: `cd frontend && npm run dev`
   - Open UI at `http://localhost:3000/login` -> Click **1-Click Security Analyst Login**.
2. **Navigate to Behavioral Intel**:
   - Click **Behavioral Intel** in the sidebar navigation (`http://localhost:3000/anomalies`).
3. **Show Employee Baseline**:
   - Select `EMP1002` -> Switch to **Behavioral Baselines** tab.
   - Explain typical login time (~09:15 AM), daily access frequency, data transfer volume (~20 MB), known devices (`Dell-Latitude-7420`), and sample size ($N=7$).
4. **Demonstrate Rule-Based Anomaly**:
   - Switch to **Combined Anomaly Report** tab.
   - Show `unusual_login_time` (03:15 AM login, Deviation ratio 24.3x), `abnormal_data_download` (650.0 MB download), and `suspicious_device_usage` (`Rogue-Kingston-Exfil-128GB`).
5. **Demonstrate Live Log Ingestion Anomaly Hook**:
   - Click **Simulate Off-Hours Event** button at the top.
   - Show live Toast alert and instant insertion of anomaly into report.
6. **Show Isolation Forest ML Outliers**:
   - Point out the **Isolation Forest Outlier Days** card showing `EMP1002` (Decision score `-0.3544`, 650 MB download, 2 devices).
7. **Show Top Flagged Leaderboard**:
   - Switch to **Top Flagged Employees** tab.
   - Display real MongoDB aggregation pipeline ranking `EMP1002` (#1 with 5 flags) and `EMP1004` (#2 with 2 flags).

---

### 💡 Engineering Decisions & Tuning Rationale

- **Why Per-Employee Baselines?** An engineer downloading 500 MB source code daily is normal, whereas an HR analyst downloading 500 MB is anomalous. Per-employee baselines eliminate false positives inherent in global static thresholds.
- **Why Rule-Based + ML Isolation Forest?** Rule-based detection catches known univariate boundary violations (e.g. 3 AM login). Isolation Forest catches subtle multi-dimensional metric combinations (e.g. normal login hour + slightly higher downloads + 2 devices) that no single rule flags.
- **Why Safety Floor `spread = max(normal_range, 0.1)`?** Prevents division-by-zero errors and stops standard deviation values near zero from creating astronomical deviation ratios.
- **Why Contamination = 0.08?** Tuned specifically for enterprise insider threat telemetry where true malicious or highly suspicious outlier employee-days represent 5-10% of total activity logs.

