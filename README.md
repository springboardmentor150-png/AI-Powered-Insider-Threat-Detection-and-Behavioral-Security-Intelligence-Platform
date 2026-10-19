# AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform (ITBIS)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16.3-black.svg)](https://nextjs.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Isolation%20Forest-F7931E.svg)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Cloud%20Ready-2496ED.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/GitHub%20Actions-Automated%20Build-2088FF.svg)](https://github.com/features/actions)

An enterprise-grade, full-stack cybersecurity behavioral intelligence system built to analyze internal user telemetry, detect privilege anomalies, compute 5-factor risk scores, and mitigate insider risks before data exfiltration occurs.

---

## 🎓 Student & Submission Details

- **Student Name:** Surampudi Durga Naga Venkata Sita Chinmai
- **Email:** sitasurampudi225@gmail.com
- **Target Repository:** [AI-Powered-Insider-Threat-Detection-and-Behavioral-Security-Intelligence-Platform](https://github.com/springboardmentor150-png/AI-Powered-Insider-Threat-Detection-and-Behavioral-Security-Intelligence-Platform)
- **Branch:** `student-chinmai` (also published as `student-sita`)

---

## 🎥 Project Demo Video

- **Video Walkthrough (Google Drive):** [Watch ITBIS Project Demo Video](https://drive.google.com/file/d/1NPTyebxSGImSoT8PAZIUhLeznF_e6Ash/view?usp=sharing)
- *Direct Link:* `https://drive.google.com/file/d/1NPTyebxSGImSoT8PAZIUhLeznF_e6Ash/view?usp=sharing`

---

## 🏛 System Architecture & Milestones Completed

### 1. Milestone 1 — Core Ingestion, Relational Schema & JWT RBAC
- FastAPI backend with SQLAlchemy ORM (PostgreSQL & SQLite compatibility).
- JWT Bearer authentication with 4 SOC security roles:
  - **Admin** (`admin@itbis.security`): System governance, user management, and compliance exports.
  - **Security Analyst** (`analyst@itbis.security`): Alert triage, risk scoring, and incident escalation.
  - **Security Manager** (`manager@itbis.security`): Employee management, case note delegation, and executive oversight.
  - **SOC Engineer** (`soc@itbis.security`): Real-time telemetry ingestion and test event simulation.
- Default test credentials: `Security@123` across all seeded SOC roles.

### 2. Milestone 2 — Behavioral Profiling & ML Anomaly Detection
- **Statistical Baselines**: 7-day rolling window for typical login hours, download volumes, devices, and IP ranges.
- **Rule-Based Anomaly Engine**: 8 rule detectors flagging off-hours access, volume spikes, privilege escalations, and sensitive data access.
- **Unsupervised Machine Learning**: Scikit-Learn `IsolationForest` detecting anomalous behavior across multidimensional telemetry features.
- **Dual Telemetry Persistence**: MongoDB support with graceful persistent local JSON buffer (`/app/data/activity_logs.json`).

### 3. Milestone 3 — 5-Factor Risk Scoring, UEBA & Incident Dossiers
- **Calibrated Risk Engine (100-Point Model)**:
  - Behavioral anomalies: 35%
  - Privilege misuse: 25%
  - Data access violations: 20%
  - Access pattern deviations: 10%
  - Historical security events: 10%
- Risk buckets: `Critical` (&ge; 75), `High` (&ge; 50), `Medium` (&ge; 25), `Low` (< 25).
- **Incident Investigation Room**: Reverse-chronological activity timelines, heatmap distribution, and multi-analyst evidence notes.
- **UEBA Peer Group Analysis**: Statistical peer comparisons against department averages.

### 4. Milestone 4 — Enterprise SOC UI, Reports & Cloud Deployment
- **Dark SOC Frontend**: Next.js 16 + React 19 + Tailwind CSS + Lucide React.
  - 13 fully integrated SOC dashboard routes.
  - Interactive activity log search, filters, pagination, and real-time event simulation.
  - PDF executive report and compliance audit exports (ReportLab) + Excel/CSV spreadsheets.
- **Docker & Cloud Deployment (Zero Local Docker Requirement)**:
  - `backend/Dockerfile`: Linux `python:3.11-slim`, non-root execution, dynamic `$PORT` binding.
  - `frontend/itbis/Dockerfile`: Linux `node:20-alpine` multi-stage container.
  - `.github/workflows/docker-build.yml`: Automated GitHub Actions workflow compiling images on GitHub-hosted Linux runners.
  - `render.yaml`: 1-click cloud Blueprint for Render with managed PostgreSQL.

---

## 🧪 Automated Test Verification

| Test Suite | Result | Details |
|---|---|---|
| **Backend Unit & Integration Tests** | **114 Passed** (0 Failures) | Pytest covering Isolation Forest, risk scoring, RBAC, UEBA |
| **Live End-to-End System Tests** | **43 / 43 Passed** (0 Failures) | Live verification across all endpoints and 13 frontend pages |
| **Frontend Production Build** | **16 / 16 Routes Static** | Next.js 16 App Router build compiled with zero errors |

---

## 🚀 Quick Start Guide

### Option A: Local Development
```bash
# 1. Start Backend (Port 8000)
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 2. Start Frontend (Port 3000)
cd frontend/itbis
npm install
npm run dev
```

### Option B: Cloud Docker Build (GitHub Actions)
Pushing to GitHub automatically triggers `.github/workflows/docker-build.yml`, which runs all tests and builds both Docker containers on GitHub's `ubuntu-latest` cloud runners.

### Option C: 1-Click Render Deployment
Link this repository on [Render](https://dashboard.render.com/) as a **Blueprint**. Render will deploy:
- `itbis-backend` (Docker)
- `itbis-frontend` (Docker)
- `itbis-postgres` (Managed PostgreSQL)
