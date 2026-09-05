# AI-Powered Insider Threat Detection & Behavioral Security Intelligence Platform (ITBIS)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Isolation%20Forest-F7931E.svg)](https://scikit-learn.org/)
[![Cybersecurity](https://img.shields.io/badge/SOC-MITRE%20ATT%26CK-red.svg)](https://attack.mitre.org/)

An enterprise-grade, full-stack cybersecurity intelligence platform designed to identify, analyze, and mitigate insider risks. Unlike perimeter defenses targeting external attackers, **ITBIS** evaluates behavioral telemetry from users with legitimate credentials (employees, contractors, privileged administrators) to detect credential theft, privilege abuse, abnormal data exfiltration, and intellectual property leaks.

---

## 🏛 System Architecture

The platform is structured into four cohesive layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           1. CLIENTS & ROLES LAYER                          │
│   Security Analyst  │  SOC Engineer  │  Security Manager  │  Administrator  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      2. API GATEWAY & SECURITY (FastAPI)                    │
│   - JWT Bearer Authentication (8-Hour Expiry)                              │
│   - Strict Role-Based Access Control (RBAC Dependencies)                   │
│   - CORS Middleware & Rate Limiting                                         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         3. CORE MICROSERVICES & AI                          │
│  ┌───────────────────────┐ ┌──────────────────────┐ ┌────────────────────┐  │
│  │ Identity & Profiles   │ │ Activity Ingestion   │ │ Isolation Forest   │  │
│  │ Employee CRUD         │ │ Unstructured Stream  │ │ Anomaly Detector   │  │
│  └───────────────────────┘ └──────────────────────┘ └────────────────────┘  │
│  ┌───────────────────────┐ ┌──────────────────────┐ ┌────────────────────┐  │
│  │ Composite Risk Scorer │ │ Alert Triage Engine  │ │ SOC Incident Room  │  │
│  │ 0-100 Dynamic Index   │ │ Micro-Trigger Rules  │ │ MITRE ATT&CK Maps  │  │
│  └───────────────────────┘ └──────────────────────┘ └────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           4. DATA PERSISTENCE LAYER                         │
│   Structured Relational Data:          Flexible Unstructured Telemetry:    │
│   PostgreSQL / SQLite                  MongoDB / Embedded Document Store   │
│   (Users, Employees, Alerts, Incidents)(Activity Logs, Behavioral Baselines)│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Key Capabilities

1. **Unsupervised ML Anomaly Detection (Isolation Forest)**:
   - Evaluates multi-dimensional feature vectors including egress file volume, off-hours execution ratio, removable USB operations, database record count, and privilege escalation attempts.
   - Computes statistical deviations against learned per-identity baselines.

2. **Multi-Factor Behavioral Risk Scorer (0 - 100 Index)**:
   - Aggregates anomaly model confidence with real-time heuristic triggers into continuous threat tiers:
     - `LOW` (0–34) &bull; `MEDIUM` (35–59) &bull; `HIGH` (60–79) &bull; `CRITICAL` (80–100).

3. **MITRE ATT&CK Insider Threat Correlation**:
   - Automatically maps suspicious telemetry patterns to MITRE techniques:
     - **T1052.001**: Exfiltration Over Physical Medium (USB)
     - **T1567**: Exfiltration Over Web Service / Cloud Drive
     - **T1078.004**: Valid Accounts / Off-Hours Credential Use
     - **T1005 / T1530**: Mass Database & Local System Scraping
     - **T1548 / T1098**: Abuse of Elevation Control Mechanisms

4. **Interactive Threat Simulation Lab**:
   - Built-in one-click threat injector with 4 realistic scenarios (Mass Data Exfiltration, Compromised Admin via Tor, Database Scraping, and Nominal Benign Workday).

5. **Full-Stack Role-Based Access Control (RBAC)**:
   - Enforces specific permissions across `admin`, `security_manager`, `security_analyst`, and `soc_engineer`.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. One-Click Startup (Windows)
Double-click the pre-configured scripts inside `scripts/`:
1. `scripts\start_backend.bat` &rarr; Starts FastAPI server at `http://127.0.0.1:8000`
2. `scripts\start_frontend.bat` &rarr; Starts Next.js frontend at `http://127.0.0.1:3000`

### 2. Manual Startup

#### Backend:
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```
- API Documentation (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```
- Web Application: [http://localhost:3000](http://localhost:3000)

---

## 🔑 Default Demo Accounts

All demo accounts share the password: `Security@123`

| Role | Email | Permissions & Purpose |
|---|---|---|
| **Administrator** | `admin@itbis.security` | Full system access, user provisioning, employee deletion |
| **Lead Analyst** | `analyst@itbis.security` | Alert triage, incident escalation, AI forensic reports |
| **SOC Director** | `manager@itbis.security` | Employee onboarding, baseline reviews, compliance |
| **SOC Engineer** | `soc@itbis.security` | Telemetry streaming, threat vector simulations |

*(Tip: You can switch roles instantly in the frontend using the 1-Click "Switch Role" dropdown in the navbar!)*

---

## 🧪 Running Automated Tests

Run the backend test suite:
```bash
cd backend
python -m pytest tests/test_api.py -v
```

Run the end-to-end integration test:
```bash
python scripts/test_system.py
```

---

## 📁 Repository Structure

```
itbis/
├── backend/
│   ├── app/
│   │   ├── config.py              # App configurations
│   │   ├── database.py            # Relational & Document DB connectors
│   │   ├── models.py              # SQLAlchemy DB models
│   │   ├── schemas.py             # Pydantic validation schemas
│   │   ├── auth.py                # Direct bcrypt & JWT auth logic
│   │   ├── seed_data.py           # Demo identities & baseline telemetry
│   │   ├── ml_engine/
│   │   │   ├── anomaly_detector.py # Isolation Forest behavioral engine
│   │   │   ├── risk_scorer.py      # Composite 0-100 risk scorer
│   │   │   └── threat_explainer.py # MITRE correlation & AI playbooks
│   │   └── routes/                # API router modules
│   ├── tests/
│   │   └── test_api.py            # Pytest test suite
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── app/                   # Next.js App Router pages
│   │   ├── components/            # UI components & Modals
│   │   └── lib/                   # API client & Auth context
│   └── package.json
├── scripts/
│   ├── start_backend.bat
│   ├── start_frontend.bat
│   └── test_system.py
├── README.md
└── STUDENT_GUIDE.md
```