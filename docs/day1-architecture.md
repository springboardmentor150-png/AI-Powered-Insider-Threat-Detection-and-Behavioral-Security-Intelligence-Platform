# Day 1 - Project Architecture

## 1. Project Overview

The AI-Powered Insider Threat Detection and Behavioral Security
Intelligence Platform is designed to identify potentially risky
employee behavior.

The platform learns normal employee behavior over time and detects
significant deviations from that normal behavior.

These deviations can be investigated as possible insider-threat
signals.

## 2. Problem Being Solved

Traditional security systems may focus mainly on known threats and
fixed security rules.

This platform focuses on behavioral intelligence. It analyzes
employee activity and compares current behavior with established
behavioral patterns.

When behavior significantly deviates from the expected pattern,
the platform can generate a security signal or alert for
investigation.

## 3. Platform Users

The platform has four main user roles:

### Security Analyst

Reviews and investigates security alerts and suspicious activity.

### SOC Engineer

Monitors security events and behavioral security information.

### Security Manager

Reviews organizational security risk and behavioral trends.

### Administrator

Manages users, system settings, and audit-related information.

These roles are platform users. They are different from the
employees whose activities are being monitored.

## 4. Example Action for Each Role

| Role | Example Action |
|------|----------------|
| Security Analyst | Investigate a suspicious employee activity alert |
| SOC Engineer | Monitor security events and anomaly signals |
| Security Manager | Review organizational risk trends |
| Administrator | Manage users and system settings |



## 5. Architecture Layers

### 1. Clients / Users

This layer contains the users and client applications that interact
with the platform.

### 2. API Gateway

The API Gateway provides the entry point for requests from clients.
The project uses FastAPI for this layer.

### 3. Microservices Layer

This layer contains the main backend services of the platform,
including authentication, activity management, behavioral analysis,
alerts, incidents, users, and reports.

### 4. Data Processing & Streaming Layer

This layer processes activity and behavioral data and supports
processing of security-related events.

### 5. Data / Storage Layer

This layer stores structured and flexible data using the project's
database technologies.

### 6. External Systems & Data Sources

This layer represents external systems and sources from which
activity or security-related information can be obtained.


## 7. Architecture Diagram

                 ┌──────────────────────────┐
                 │      Clients / Users     │
                 │ Analyst | SOC | Manager  │
                 │       | Administrator    │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │       API Gateway        │
                 │         FastAPI          │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │    Microservices Layer   │
                 │ Auth | Activity | Alerts │
                 │ Behavior | Incidents     │
                 │ Users | Reports          │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ Data Processing &         │
                 │ Streaming Layer           │
                 └────────────┬─────────────┘
                              │
                              ▼
                 ┌──────────────────────────┐
                 │     Data / Storage       │
                 │ PostgreSQL | MongoDB     │
                 └────────────┬─────────────┘
                              ▲
                              │
                 ┌────────────┴─────────────┐
                 │ External Systems &       │
                 │ Data Sources             │
                 └──────────────────────────┘


## 8. Main Architecture Layers I Will Work On

The two architecture layers I will mainly work on are:

1. **Microservices Layer**

   This layer contains the backend services responsible for
   authentication, activity management, behavioral analysis,
   alerts, incidents, users, and reports.

2. **Data / Storage Layer**

   This layer manages the storage of structured and flexible
   platform data using PostgreSQL and MongoDB.