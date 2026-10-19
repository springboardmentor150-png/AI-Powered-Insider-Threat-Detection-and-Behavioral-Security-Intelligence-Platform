# ITBIS Database Schema

## Users

| Field | Description |
|---|---|
| id | Unique user ID |
| email | User email |
| password_hash | Hashed password |
| role | User role |

## Employees

| Field | Description |
|---|---|
| id | Unique employee ID |
| employee_id | Employee identifier |
| name | Employee name |
| department | Department |
| designation | Job designation |
| manager_id | Manager reference |

## Incidents

| Field | Description |
|---|---|
| id | Unique incident ID |
| employee_id | Related employee |
| status | Incident status |
| severity | Severity level |
| created_at | Creation time |

## Alerts

| Field | Description |
|---|---|
| id | Unique alert ID |
| employee_id | Related employee |
| severity | Alert severity |
| message | Alert message |
| created_at | Creation time |

## MongoDB - Activity Logs

Collection: activity_logs

Fields:

- employee_id
- event_type
- timestamp
- details

## MongoDB - Behavioral Baselines

Collection: behavioral_baselines

Fields:

- employee_id
- indicator
- typical_value
- last_updated