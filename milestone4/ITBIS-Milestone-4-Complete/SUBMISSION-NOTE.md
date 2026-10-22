# Milestone 4 Submission

**Project:** AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform  
**Prepared by:** K Subramanya Karanth

This folder contains the Milestone 4 demonstration package for Analytics, Testing & Deployment. The project README contains setup instructions, demo credentials, and the package scope note.

## Scope and data note

The supplied application uses in-memory demonstration records. The Docker Compose file includes PostgreSQL and MongoDB services, but the application code in this package does not persist its records to those services. Dashboard values, sample risks, incidents, and log records should be treated as demonstration data, not operational telemetry or measured model performance.

## Contents

- `backend/` — FastAPI application, dependency list, Dockerfile, and API test cases
- `frontend/` — Next.js interface and Dockerfile
- `docker-compose.yml` — backend, frontend, PostgreSQL, and MongoDB service definitions
- `README.md` — setup, demo access, and test commands
- `LICENSE` — included project license

The test file documents API coverage; this note does not claim that the tests were executed or passed.
