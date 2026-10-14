# AI-Powered Insider Threat Detection & Behavioral Security Intelligence Platform (ITBIS)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.3+-black.svg)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-47A248.svg)](https://www.mongodb.com/)

An enterprise-grade **User and Entity Behavior Analytics (UEBA)** intelligence system designed to detect insider risks, data exfiltration, privilege misuse, and access pattern anomalies across organizations using statistical baselining and unsupervised machine learning (*Isolation Forest*).

---

## 1. Problem Statement & Motivation

Traditional perimeter security models guard against external threats but struggle to detect malicious or compromised insiders who already hold legitimate credentials. ITBIS continuously analyzes employee behavioral telemetry, constructs dynamic baselines, and combines multi-source signals into a calibrated risk score to identify abnormal deviations before damage occurs.

---

## 2. System Architecture

The ITBIS platform is built as a layered modular system:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        1. CLIENTS & ROLES LAYER                        │
│   • Security Analyst   • SOC Engineer   • Security Manager   • Admin   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTPS / REST / JWT
┌──────────────────────────────────▼─────────────────────────────────────┐
│                    2. API GATEWAY & SECURITY LAYER                     │
│    • FastAPI Router       • JWT Authentication    • Role-Based Access  │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼─────────────────────────────────────┐
│                      3. INTELLIGENCE SERVICES                          │
│   • Log Ingestion Pipeline      • Behavioral Profiling (6 Indicators)  │
│   • Statistical Anomaly (Z-Score) • ML Anomaly Engine (IsolationForest)│
│   • 5-Factor Weighted Scoring   • Peer Group Comparison & UEBA Trends  │
│   • Incident Investigation      • In-Memory PDF & Excel Export Engine  │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼─────────────────────────────────────┐
│                       4. HYBRID DATA STORAGE                           │
│   • PostgreSQL (Structured):    Users, Employees, Incidents, Alerts    │
│   • MongoDB (Telemetry & Logs): Activity Logs, Behavioral Baselines,   │
│                                 Rule Anomalies, ML Anomaly Records     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Features Across Milestones

### Milestone 1: Core Setup & Ingestion
* **Hybrid Database**: Relational schema in PostgreSQL and flexible activity documents in MongoDB.
* **Authentication & RBAC**: One-way bcrypt password hashing, 8-hour JWT authentication, and fine-grained `require_role()` route protection.
* **Employee Directory**: Full CRUD endpoints (`/employees`).
* **Activity Log Ingestion**: High-throughput telemetry ingestion pipeline (`POST /logs/ingest`).

### Milestone 2: Behavioral Analytics & Anomaly Detection
* **Behavioral Baselines**: Computes historical statistical profiles across 6 key indicators:
  1. Login Times (`avg_login_hour`)
  2. Resource Access Frequency
  3. Device Usage Patterns
  4. Application Usage Profiles
  5. Data Transfer Volumes
  6. Communication Patterns
* **Statistical Anomaly Detection**: Configurable $Z$-score outlier checks ($Z > 2.5$) with safety variance guards.
* **Machine Learning Outlier Engine**: Unsupervised `IsolationForest` detecting multi-indicator correlated anomalies (`/anomalies/report`).

### Milestone 3: Risk Scoring & Threat Investigation
* **5-Factor Weighted Risk Scoring Model**:
  $$\text{Risk Score} = 0.35 \times \text{Behavioral} + 0.25 \times \text{Privilege} + 0.20 \times \text{Data Access} + 0.10 \times \text{Access Pattern} + 0.10 \times \text{Historical}$$
  * Bounded between 0 and 100 with category calibration: `Critical` ($\ge 75$), `High` ($\ge 50$), `Medium` ($\ge 25$), `Low` ($< 25$).
* **UEBA Intelligence**: Peer group comparison against departmental coworkers and 14-day/30-day behavioral trend directions (`stable`, `increasing`, `decreasing`).
* **Investigation Workflow**: Automatic incident ticket creation for high/critical findings (`POST /incidents/create-from-risk/{id}`), analyst investigation evidence notes, and chronological timeline reconstruction merging activity logs, rule alerts, and ML anomalies.
* **Alert Escalation**: SLA threshold escalation for overdue unassigned alerts.

### Milestone 4: Reports, Dashboards & Deployment
* **4 Role-Specific Dashboards**:
  1. **Security Analyst Dashboard** (`/dashboard/analyst`): Open alert triage, active investigations, top risk personnel.
  2. **SOC Engineer Dashboard** (`/dashboard/soc`): Threat volume, severity counts, 7-day anomaly trend curve.
  3. **Security Manager Dashboard** (`/dashboard/manager`): Organizational risk posture, resolution SLA metrics, compliance posture.
  4. **Platform Admin Dashboard** (`/dashboard/admin`): User counts, role breakdown, system health indicators.
* **In-Memory Reporting & Export Engine**:
  * **Employee Risk Dossiers (PDF)**: Detailed report cards with sub-scores and recent anomaly traces.
  * **Compliance Summary Reports (PDF)**: Comprehensive audit reports aligning with ISO/IEC 27001, SOC 2, and NIST SP 800-53 controls.
  * **Bulk Risk Scores (Excel)**: Formatted `.xlsx` sorted descending by risk score, with optional department filtering.
  * **Security Incident Records (Excel)**: Incident ticket audit dump with status filtering.
  * **Report Catalog**: Single source of truth at `/reports/catalog`.
* **Containerization**: Full multi-service `docker-compose.yml` configuration.

---

## 4. Tech Stack

* **Backend**: Python 3.11+, FastAPI, SQLAlchemy, PyMongo, Pydantic, Scikit-learn, ReportLab, Pandas, OpenPyXL, Uvicorn.
* **Frontend**: Next.js 16 (App Router, Turbopack), React 19, TypeScript, Tailwind CSS, Axios.
* **Databases**: PostgreSQL 15, MongoDB 7.0.
* **DevOps**: Docker, Docker Compose.

---

## 5. Local Setup Instructions

### Prerequisites
* Python 3.11 or higher
* Node.js 20 or higher & npm
* PostgreSQL running locally on port `5432`
* MongoDB running locally on port `27017`

### 1. Clone Repository
```bash
git clone https://github.com/your-username/AI-Powered-Insider-Threat-Detection-and-Behavioral-Security-Intelligence-Platform.git
cd AI-Powered-Insider-Threat-Detection-and-Behavioral-Security-Intelligence-Platform
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

#### Note on Machine Learning Model Regeneration:
> **Important:** Trained machine learning binary model files (`.pkl`) are intentionally excluded from version control via `.gitignore`. To generate behavioral baselines and train the Isolation Forest model on seeded data, execute:
> ```bash
> python app/scripts/generate_baselines.py
> python app/scripts/run_ml_detection.py
> ```

#### Start Backend API:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at `http://localhost:3000`.

---

## 6. Docker Deployment

To launch all four services (FastAPI Backend, Next.js Frontend, PostgreSQL, and MongoDB) with a single command:

```bash
docker-compose up --build
```

Access points:
* Frontend: `http://localhost:3000`
* Backend API: `http://localhost:8000`
* Interactive API Docs: `http://localhost:8000/docs`

---

## 7. Testing & Quality Assurance

Run the automated test battery:

```bash
cd backend

# End-to-end integration pipeline:
python tests/test_full_pipeline.py

# Comprehensive milestone test suite:
python test_milestones_complete.py

# Alert SLA escalation logic test:
python test_escalation_logic.py

# UEBA 14-day trend analysis test:
python test_ueba_trend.py
```

Frontend production verification:
```bash
cd frontend
npm run build
```

---

## 8. License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
