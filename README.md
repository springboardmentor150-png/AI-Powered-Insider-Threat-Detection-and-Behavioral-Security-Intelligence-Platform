# AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform (ITBIS)

<p align="center">
  <strong>Behavioral Security Analytics • Insider Threat Detection • Security Operations</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-FastAPI-3776AB?logo=python&logoColor=white">
  <img alt="Frontend" src="https://img.shields.io/badge/Frontend-Next.js%20%7C%20React-000000?logo=nextdotjs">
  <img alt="Databases" src="https://img.shields.io/badge/Databases-PostgreSQL%20%7C%20MongoDB-336791">
  <img alt="Security" src="https://img.shields.io/badge/Security-JWT%20%7C%20RBAC-7A3E9D">
</p>

## 📌 Project Overview
The AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform (ITBIS) is a cybersecurity operations platform designed to monitor employee-related activity telemetry, identify unusual behavioral patterns, and help security teams investigate potential insider threats.

The platform treats employees as monitored entities. Employees do not sign in to ITBIS. Authorized platform users sign in to review activity, monitor alerts, manage incidents, and assess organizational security risk.

> **Project scope:** The demo uses simulated telemetry sent through application APIs. It does not claim to collect events directly from operating-system kernels or live enterprise security tools.

## 🎯 Objectives
- Collect and review employee activity events such as logins, file downloads, and access attempts.
- Maintain behavioral baselines and identify deviations from expected activity.
- Calculate employee risk indicators to support triage.
- Generate and manage security alerts and investigation incidents.
- Provide role-specific dashboards for security operations.
- Store structured platform records and flexible telemetry in appropriate databases.

## 👥 Platform Roles

| Role | Main responsibilities |
|---|---|
| **Admin** | Manage platform users and system-level configuration; review audit information where available. |
| **Security Manager** | Review organizational risk posture, employee risk, and security trends; manage employee records where authorized. |
| **Security Analyst** | Review alerts, investigate suspicious activity, and work with employee and incident information. |
| **SOC Engineer** | Monitor security events, telemetry, anomalies, and operational alert activity. |

*Note: Employees are monitored records, not platform login roles.*

## ✨ Core Features
- **Role-based access control (RBAC):** Protects platform functions according to the authenticated user's role.
- **Authentication:** Token-based authentication using JWT.
- **Employee directory:** Stores and displays monitored employee information.
- **Activity telemetry:** Receives simulated activity events through the log-ingestion API.
- **Behavioral analysis:** Evaluates event data using the detection logic implemented in the application.
- **Risk assessment:** Presents employee risk information where supported by the current analytics implementation.
- **Alert management:** Supports reviewing and tracking security alerts.
- **Incident workflow:** Supports investigation and incident status tracking.
- **Security dashboards:** Provides role-oriented operational views.
- **Security event simulator:** Enables demonstration of event ingestion without requiring live endpoint agents.
- **Audit records:** Records selected security-relevant actions where audit hooks are implemented.

> **Implementation accuracy:** Detection algorithms, dashboard metrics, audit coverage, and workflow behavior depend on the current code. Describe Isolation Forest as implemented only if it is present, configured, and tested in the submitted version.

## 🏗️ Architecture

```text
                 ┌───────────────────────────────────────────┐
                 │              PLATFORM USERS                │
                 │ Admin | Security Manager | Analyst | SOC   │
                 └─────────────────────┬─────────────────────┘
                                       │
                                       ▼
                 ┌───────────────────────────────────────────┐
                 │ Frontend: Next.js / React / TypeScript    │
                 │ Dashboards • Employee Directory • Simulator│
                 │ Alerts • Incidents • Activity Logs         │
                 └─────────────────────┬─────────────────────┘
                                       │ REST API / HTTP
                                       ▼
                 ┌───────────────────────────────────────────┐
                 │ Backend: Python / FastAPI                │
                 │ JWT Authentication • RBAC • Validation    │
                 │ Employee Management • Log Ingestion       │
                 │ Behavioral Analysis • Risk • Alert/Incident│
                 └──────────────┬────────────────┬───────────┘
                                │                │
                                ▼                ▼
                 ┌──────────────────────┐ ┌──────────────────────┐
                 │ PostgreSQL           │ │ MongoDB              │
                 │ Users                │ │ Activity telemetry   │
                 │ Employees            │ │ Behavioral baselines │
                 │ Alerts / Incidents   │ │ Anomaly evidence and │
                 │ Audit records*       │ │ flexible event data* │
                 └──────────────────────┘ └──────────────────────┘

          *Collection/table names and persistence depend on the
           current database models and configuration.
```

## 🧰 Technology Stack

| Layer | Technologies | Purpose |
|---|---|---|
| Frontend | Next.js, React, TypeScript | Web application and role-based dashboards |
| Backend | Python, FastAPI | REST APIs and application logic |
| ORM / validation | SQLAlchemy, Pydantic | Relational data access and request validation |
| Relational database | PostgreSQL | Structured platform records |
| NoSQL database | MongoDB, PyMongo | Flexible telemetry and behavioral data |
| Authentication | JWT, Passlib/Bcrypt | Token authentication and password hashing |
| API communication | REST, Axios | Frontend/backend communication |
| Development tools | Node.js, npm, Uvicorn, Git, GitHub | Build, run, and version the application |

**Machine learning:** List Scikit-learn and Isolation Forest as active technologies only if the submitted code and dependency file confirm their use. Otherwise describe the current implementation as rule-based behavioral detection.

## 🗄️ Data Storage

**PostgreSQL**  
Used for structured application records, such as:
- Platform users and roles
- Employee records
- Security alerts
- Incidents and investigation status
- Audit records, if enabled in the current implementation

**MongoDB**  
Used for flexible event and behavioral data, such as:
- Activity telemetry
- Behavioral baseline snapshots
- Anomaly evidence and supporting event details
- Risk-related documents, if stored by the current implementation

*The actual table and collection names should match the models and database initialization code in the submitted repository.*

## 🔄 End-to-End Demo Workflow
1. **Sign in:** An authorized platform user logs in.
2. **Select an employee:** The user opens the employee directory and selects a monitored employee.
3. **Generate telemetry:** Use the Security Event Simulator to submit a sample event, such as a login, file download, or unauthorized access attempt.
4. **Ingest the event:** The frontend sends the event to the backend log-ingestion endpoint.
5. **Analyze behavior:** The backend evaluates the event using the detection and analytics logic implemented in the project.
6. **Review risk and alerts:** Where the detection pipeline produces results, the user reviews the related risk information and security alerts.
7. **Investigate:** An authorized analyst reviews the evidence and uses the incident workflow when appropriate.
8. **Track response:** The security team updates incident or alert status according to the supported workflow.

*Demo note: Confirm the exact sequence and whether an event automatically creates an alert or incident against the current implementation before a live presentation.*

## 🔌 API Overview
The backend is built with FastAPI. The following route groups are described by the project; confirm exact methods and endpoint paths in the current API documentation.

| Route group | Purpose |
|---|---|
| `/auth` | Authentication and token generation |
| `/users` | Platform user management |
| `/employees` | Monitored employee records |
| `/logs` | Activity telemetry ingestion |
| `/analytics` | Behavioral analysis and risk-related operations |
| `/alerts` | Security alert review and management |
| `/incidents` | Investigation and incident tracking |
| `/docs` | Interactive FastAPI Swagger documentation |

Example local API documentation URL: `http://localhost:8000/docs`
The activity ingestion endpoint documented for the project is `POST /logs/ingest`.

## ⚙️ Prerequisites
Install and configure the following before running the project:
- Python compatible with the project's dependencies
- Node.js and npm
- PostgreSQL
- MongoDB
- Git

*Use the versions supported by the project's dependency files and local environment.*

## 🚀 Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/springboardmentor150-png/AI-Powered-Insider-Threat-Detection-and-Behavioral-Security-Intelligence-Platform.git
cd AI-Powered-Insider-Threat-Detection-and-Behavioral-Security-Intelligence-Platform
```

**2. Configure the backend environment**
Create `backend/.env` and provide your local database URL and a securely generated JWT secret:
```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/itbis
JWT_SECRET=REPLACE_WITH_A_SECURE_RANDOM_SECRET
```
- Replace placeholders with your own local configuration.
- Do not commit `.env` or real credentials to GitHub.
- Confirm `.env` is ignored by `.gitignore`.
- If a password contains URL-reserved characters, encode them correctly in the database URL.

**3. Prepare PostgreSQL and MongoDB**
- Start PostgreSQL and create the `itbis` database.
- Start MongoDB using the connection settings expected by the backend.
- Confirm the backend environment configuration matches your local services.

**4. Install and run the backend**
From the repository root, in PowerShell:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- If the virtual environment already exists, activate it rather than recreating it.
- Backend base URL: `http://localhost:8000`
- Swagger documentation: `http://localhost:8000/docs`

**5. Install and run the frontend**
Open a second terminal from the repository root:
```powershell
cd frontend
npm install
npm run dev
```
- Frontend URL: `http://localhost:3000`

## 🧪 Testing and Verification
Before submitting or demonstrating the project, verify:
- Valid login works and invalid credentials are rejected.
- Each role can access only the pages and APIs permitted for that role.
- Employee records load and authorized employee-management operations work.
- The simulator submits telemetry successfully.
- Activity events are stored and can be reviewed.
- Detection and risk results are consistent with the implemented logic.
- Alert and incident workflows work as expected.
- Data remains available after a backend restart where persistence is expected.
- The frontend production build succeeds.

*Do not report a test as passed unless it has actually been run and verified.*

## 🔐 Security Notes
- Keep database passwords, JWT secrets, and API credentials out of source control.
- Use strong, unique secrets outside local demonstrations.
- Apply least-privilege access to role-restricted operations.
- Treat simulated telemetry and demo accounts as non-production data.
- Do not use demo credentials in a deployed production environment.

## ⚠️ Limitations
- Telemetry is simulated through application APIs; native endpoint agents and live enterprise SIEM integrations are outside the stated demo scope.
- Detection quality depends on the available event data, baseline quality, thresholds, and algorithms actually implemented.
- An anomaly is an indicator for investigation, not proof of malicious activity.
- Enterprise identity-provider, firewall, EDR, and SIEM integrations may require additional implementation.
- Production deployment requires further security hardening, monitoring, secrets management, and operational testing.

## 👩‍💻 Project Author
**Ayesha Farhunnisa J**  
Individual project: AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform (ITBIS)

## 📄 License
See the `LICENSE` file for the license associated with this repository.
