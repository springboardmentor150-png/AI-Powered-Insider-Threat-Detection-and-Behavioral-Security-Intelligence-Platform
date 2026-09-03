# Insider Watch

Build a web app called "ITBIS" — Insider Threat Behavioral Intelligence System — a cybersecurity monitoring dashboard for a SOC (Security Operations Center) team.

DESIGN

- Dark theme by default (with light mode toggle), security/enterprise SaaS aesthetic — think Splunk/Datadog/CrowdStrike style

- Primary accent: deep blue/cyan; use red/orange/amber for risk severity indicators

- Clean sidebar navigation + top bar with user info and role badge

- Use cards, tables, and badges for status/severity — this is a data-dense admin tool, not a marketing site

PAGES & FLOWS

1. Login Page

   - Email + password fields, "Sign In" button, error state for invalid credentials

   - Below the form, a small note: "Roles: Security Analyst, SOC Engineer, Security Manager, Administrator"

   - Use mock authentication: accept any email/password and let me pick a role via a dropdown on the login screen (for demo purposes until backend is connected)

2. Role-Based Dashboard (content changes based on selected role)

   - Admin: system overview cards (total employees, total alerts, active incidents, users by role), quick links to User Management and Employee Management

   - Security Manager: risk overview cards (employees by risk level - Low/Medium/High/Critical), recent alerts table, department risk summary

   - Security Analyst / SOC Engineer: assigned alerts list, recent activity log feed, "My Investigations" widget

   - Use mock/sample data for all of this (5-10 fake employees, 10-15 fake alerts)

3. Employee Management (Admin & Security Manager only)

   - Table of employees: Employee ID, Name, Department, Designation, Manager, Risk Level (colored badge), Actions

   - "Add Employee" button opens a modal/drawer with a form: employee_id, name, department, designation, manager (dropdown)

   - Row click opens an Employee Detail view: profile info + a placeholder "Activity Timeline" and "Risk Score" section (mock data)

4. Activity Logs (all roles, read view)

   - Table of activity log events: Employee ID, Event Type (login / file_download / usb_connect / etc. — show as colored tags), Timestamp, Details (expandable)

   - Filter bar: filter by employee ID, event type, date range

   - Mock 15-20 sample log entries with varied event types

5. Alerts (all roles)

   - Table of alerts: Employee, Severity (Informational/Low/Medium/High/Critical as colored badges), Message, Status (Open/Investigating/Resolved), Created At

   - Clicking an alert opens a detail panel with mock incident info

6. User Management (Admin only)

   - Table of platform users (the login accounts, not employees): Email, Role, Status

   - "Invite User" button with a modal form (email, role dropdown)

STRUCTURE NOTES

- Use a persistent sidebar with these links: Dashboard, Employees, Activity Logs, Alerts, User Management (hide User Management for non-admin roles), Settings

- Show the current role clearly in the top bar and let me switch roles from a dropdown there too, so I can preview all 4 dashboards without logging out/in

- Keep all data in local component state / mock JSON files — no real backend calls yet, structure the code so API calls can be swapped in later (e.g. a single `api/mockData.js` file I can later replace with real fetch calls)

- Use React with clean component structure and Tailwind CSS

This project was built with [Lovable](https://lovable.dev).

**Live app**: https://behavior-vigil.lovable.app

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/b0862b18-79f7-4aa4-9a8d-f9a28b543331).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
