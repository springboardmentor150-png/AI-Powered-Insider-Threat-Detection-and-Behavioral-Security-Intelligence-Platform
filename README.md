# AI-Powered Insider Threat Detection & Behavioral Security Intelligence Platform (ITBIS)

## Milestone 3: Risk Scoring & Threat Investigation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Isolation%20Forest-F7931E.svg)](https://scikit-learn.org/)
[![UEBA](https://img.shields.io/badge/UEBA-Peer%20Comparison-blueviolet.svg)](https://en.wikipedia.org/wiki/User_and_entity_behavior_analytics)
[![Cybersecurity](https://img.shields.io/badge/SOC-MITRE%20ATT%26CK-red.svg)](https://attack.mitre.org/)

An enterprise-grade, full-stack cybersecurity intelligence platform designed to identify, analyze, and mitigate insider risks. Unlike perimeter defenses targeting external attackers, **ITBIS** evaluates behavioral telemetry from users with legitimate credentials to detect credential theft, privilege abuse, abnormal data exfiltration, and intellectual property leaks.

---

## 🏛 System Architecture (Milestone 3 Enhanced)

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
│                     3. MILESTONE 3 CORE MICROSERVICES & AI                  │
│  ┌───────────────────────┐ ┌──────────────────────┐ ┌────────────────────┐  │
│  │ Insider Risk Scorer   │ │ UEBA Peer Comparison │ │ Investigation Room │  │
│  │ 5 Weighted Factors    │ │ Dept Baseline & Trend│ │ Timeline & Evidence│  │
│  └───────────────────────┘ └──────────────────────┘ └────────────────────┘  │
│  ┌───────────────────────┐ ┌──────────────────────┐ ┌────────────────────┐  │
│  │ Alert Management      │ │ Multi-Role Dashboards│ │ Isolation Forest   │  │
│  │ Delegation & Resolve  │ │ Analyst / SOC / Mgr  │ │ Behavioral Anomaly │  │
│  └───────────────────────┘ └──────────────────────┘ └────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           4. DATA PERSISTENCE LAYER                         │
│   Structured Relational Data:          Flexible Unstructured Telemetry:    │
│   PostgreSQL / SQLite                  MongoDB / Embedded Document Store   │
│   (Users, Employees, Alerts, Incidents)(Activity Logs, Rule/ML Anomalies)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Milestone 3 Key Capabilities

1. **5-Factor Weighted Insider Risk Scoring Model (Part 1)**:
   - `Behavioral Anomalies` (35%)
   - `Privilege Misuse Indicators` (25%)
   - `Data Access Violations` (20%)
   - `Access Pattern Deviations` (10%)
   - `Historical Security Events` (10%)
   - Capped at 100 with `min(..., 100)` and calibrated thresholds (`critical` &ge; 75, `high` &ge; 50, `medium` &ge; 25, `low` &lt; 25).

2. **UEBA Intelligence Workflows (Part 2)**:
   - **Peer Group Comparison**: Evaluates an employee's risk relative to departmental peers, calculating deviation from department averages with zero-peer edge-case handling.
   - **30-Day Behavioral Trend Analysis**: Tracks daily anomaly counts to distinguish between isolated spikes and climbing risks.

3. **Threat Investigation Module (Part 3)**:
   - Automated incident creation from high/critical risk scores (rejects low/medium deviations).
   - **Chronological Incident Timeline**: Merges raw telemetry events and detected anomalies sorted in reverse chronological order.
   - **Multi-Analyst Evidence Notes**: Threaded forensic findings linked to each case file.

4. **Risk Analytics & Alert Management (Part 4)**:
   - Role-gated alert lifecycle: Assignment restricted to Admin/Security Manager, resolution open to Security Analysts.
   - **Organizational Risk Posture**: Global risk bucket distributions for executive security reporting.

5. **Role-Specific Security Dashboards (Part 5)**:
   - **Analyst Dashboard**: `/dashboard/analyst`
   - **SOC Dashboard**: `/dashboard/soc`
   - **Security Manager Dashboard**: `/dashboard/manager`

---

## 🚀 Quick Start Guide

### 1. One-Click Startup (Windows)
1. Double-click `scripts\start_backend.bat` &rarr; Starts FastAPI server at `http://127.0.0.1:8000`
2. Double-click `scripts\start_frontend.bat` &rarr; Starts Next.js frontend at `http://localhost:3000`

### 2. Manual Startup
```bash
# Backend
cd backend
python -m pip install -r requirements.txt
python run.py

# Frontend
cd frontend
npm install
npm run dev
```

---

## 🔑 Default Demo Accounts

Password for all accounts: **`Security@123`**

| Role | Email | Purpose |
|---|---|---|
| **Administrator** | `admin@itbis.security` | Full governance & user management |
| **Lead Analyst** | `analyst@itbis.security` | Alert triage, incident escalation & AI reports |
| **SOC Director / Manager** | `manager@itbis.security` | Employee onboarding, alert delegation & compliance |
| **SOC Engineer** | `soc@itbis.security` | Telemetry streaming & threat simulations |

---

## 🧪 Running Automated Tests

Run the complete backend test suite (Milestone 1 + Milestone 3):
```bash
cd backend
python -m pytest tests/test_milestone3.py tests/test_api.py -v
```

Run the end-to-end integration test:
```bash
python scripts/test_system.py
```