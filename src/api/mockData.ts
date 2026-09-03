/**
 * Mock data layer for ITBIS.
 *
 * Everything the UI needs goes through the exported `api` object below.
 * Swap the function bodies for real `fetch()` calls later — the shapes and
 * signatures are the contract the UI depends on.
 */

export type Role = "Security Analyst" | "SOC Engineer" | "Security Manager" | "Administrator";

export const ROLES: Role[] = [
  "Security Analyst",
  "SOC Engineer",
  "Security Manager",
  "Administrator",
];

export type RiskLevel = "Low" | "Medium" | "High" | "Critical";
export type Severity = "Informational" | "Low" | "Medium" | "High" | "Critical";
export type AlertStatus = "Open" | "Investigating" | "Resolved";
export type EventType =
  | "login"
  | "logout"
  | "file_download"
  | "file_upload"
  | "usb_connect"
  | "email_external"
  | "vpn_access"
  | "privilege_change";

export interface Employee {
  employee_id: string;
  name: string;
  department: string;
  designation: string;
  manager: string;
  risk_level: RiskLevel;
  risk_score: number;
  email: string;
  location: string;
  joined_at: string;
}

export interface ActivityLog {
  id: string;
  employee_id: string;
  event_type: EventType;
  timestamp: string;
  details: string;
  host: string;
  ip: string;
}

export interface ThreatAlert {
  id: string;
  employee_id: string;
  employee_name: string;
  severity: Severity;
  message: string;
  status: AlertStatus;
  created_at: string;
  assigned_to: Role;
  rule: string;
  narrative: string;
}

export interface PlatformUser {
  id: string;
  email: string;
  role: Role;
  status: "Active" | "Invited" | "Suspended";
  last_login: string;
}

export const employees: Employee[] = [
  {
    employee_id: "EMP-1042",
    name: "Ana Delgado",
    department: "Finance",
    designation: "Senior Accountant",
    manager: "Priya Raman",
    risk_level: "Critical",
    risk_score: 92,
    email: "ana.delgado@northwind.co",
    location: "Madrid, ES",
    joined_at: "2019-04-08",
  },
  {
    employee_id: "EMP-1103",
    name: "Marcus Chen",
    department: "Engineering",
    designation: "Staff Engineer",
    manager: "Dieter Roth",
    risk_level: "High",
    risk_score: 78,
    email: "marcus.chen@northwind.co",
    location: "Austin, US",
    joined_at: "2021-01-19",
  },
  {
    employee_id: "EMP-1188",
    name: "Sofia Ibrahim",
    department: "Sales",
    designation: "Account Executive",
    manager: "Karen Blake",
    risk_level: "High",
    risk_score: 71,
    email: "sofia.ibrahim@northwind.co",
    location: "Dubai, AE",
    joined_at: "2022-07-04",
  },
  {
    employee_id: "EMP-1211",
    name: "Tom Averill",
    department: "IT Operations",
    designation: "Systems Administrator",
    manager: "Dieter Roth",
    risk_level: "Medium",
    risk_score: 54,
    email: "tom.averill@northwind.co",
    location: "Manchester, UK",
    joined_at: "2018-11-27",
  },
  {
    employee_id: "EMP-1274",
    name: "Leah Okonkwo",
    department: "Human Resources",
    designation: "HR Business Partner",
    manager: "Priya Raman",
    risk_level: "Medium",
    risk_score: 47,
    email: "leah.okonkwo@northwind.co",
    location: "Lagos, NG",
    joined_at: "2020-09-15",
  },
  {
    employee_id: "EMP-1309",
    name: "Ravi Menon",
    department: "Engineering",
    designation: "Data Engineer",
    manager: "Dieter Roth",
    risk_level: "Low",
    risk_score: 22,
    email: "ravi.menon@northwind.co",
    location: "Bengaluru, IN",
    joined_at: "2023-02-06",
  },
  {
    employee_id: "EMP-1355",
    name: "Grace Lindqvist",
    department: "Legal",
    designation: "Counsel",
    manager: "Karen Blake",
    risk_level: "Low",
    risk_score: 15,
    email: "grace.lindqvist@northwind.co",
    location: "Stockholm, SE",
    joined_at: "2022-03-21",
  },
  {
    employee_id: "EMP-1402",
    name: "Yusuf Demir",
    department: "Finance",
    designation: "Financial Analyst",
    manager: "Priya Raman",
    risk_level: "Medium",
    risk_score: 58,
    email: "yusuf.demir@northwind.co",
    location: "Istanbul, TR",
    joined_at: "2021-06-30",
  },
  {
    employee_id: "EMP-1466",
    name: "Nina Petrova",
    department: "Sales",
    designation: "Sales Engineer",
    manager: "Karen Blake",
    risk_level: "Low",
    risk_score: 31,
    email: "nina.petrova@northwind.co",
    location: "Warsaw, PL",
    joined_at: "2023-08-14",
  },
];

export const managers: string[] = ["Priya Raman", "Dieter Roth", "Karen Blake", "Elena Vasquez"];

export const departments: string[] = [
  "Finance",
  "Engineering",
  "Sales",
  "IT Operations",
  "Human Resources",
  "Legal",
];

export const activityLogs: ActivityLog[] = [
  {
    id: "LOG-9001",
    employee_id: "EMP-1042",
    event_type: "file_download",
    timestamp: "2026-09-03T02:14:00Z",
    details: "Downloaded 412 files (1.8 GB) from /finance/forecasts outside working hours.",
    host: "FIN-WKS-08",
    ip: "10.22.4.91",
  },
  {
    id: "LOG-9002",
    employee_id: "EMP-1042",
    event_type: "usb_connect",
    timestamp: "2026-09-03T02:31:00Z",
    details: "Unregistered mass-storage device (SanDisk Ultra, 128 GB) mounted.",
    host: "FIN-WKS-08",
    ip: "10.22.4.91",
  },
  {
    id: "LOG-9003",
    employee_id: "EMP-1103",
    event_type: "privilege_change",
    timestamp: "2026-09-02T18:05:00Z",
    details: "Added self to group 'prod-db-readers' via automation token.",
    host: "ENG-BUILD-02",
    ip: "10.31.9.14",
  },
  {
    id: "LOG-9004",
    employee_id: "EMP-1188",
    event_type: "email_external",
    timestamp: "2026-09-02T16:44:00Z",
    details: "Sent pipeline export (3.1 MB) to personal address s.ibrahim@fastmail.com.",
    host: "SAL-LAP-17",
    ip: "10.44.2.7",
  },
  {
    id: "LOG-9005",
    employee_id: "EMP-1211",
    event_type: "vpn_access",
    timestamp: "2026-09-02T13:12:00Z",
    details: "VPN session from new ASN (Hetzner, DE) — no prior history for this account.",
    host: "ITO-JUMP-01",
    ip: "88.198.44.10",
  },
  {
    id: "LOG-9006",
    employee_id: "EMP-1274",
    event_type: "login",
    timestamp: "2026-09-02T09:02:00Z",
    details: "SSO login succeeded after 4 failed attempts.",
    host: "HR-WKS-03",
    ip: "10.12.7.33",
  },
  {
    id: "LOG-9007",
    employee_id: "EMP-1309",
    event_type: "file_upload",
    timestamp: "2026-09-02T08:41:00Z",
    details: "Uploaded 12 MB dataset to approved internal artifact store.",
    host: "ENG-WKS-21",
    ip: "10.31.9.55",
  },
  {
    id: "LOG-9008",
    employee_id: "EMP-1402",
    event_type: "file_download",
    timestamp: "2026-09-01T22:58:00Z",
    details: "Bulk export of vendor payment records (86 rows).",
    host: "FIN-WKS-12",
    ip: "10.22.4.60",
  },
  {
    id: "LOG-9009",
    employee_id: "EMP-1042",
    event_type: "login",
    timestamp: "2026-09-01T21:47:00Z",
    details: "Login from unmanaged device fingerprint.",
    host: "UNKNOWN",
    ip: "77.90.14.201",
  },
  {
    id: "LOG-9010",
    employee_id: "EMP-1466",
    event_type: "logout",
    timestamp: "2026-09-01T18:30:00Z",
    details: "Normal session end.",
    host: "SAL-LAP-04",
    ip: "10.44.2.19",
  },
  {
    id: "LOG-9011",
    employee_id: "EMP-1103",
    event_type: "file_download",
    timestamp: "2026-09-01T17:22:00Z",
    details: "Cloned 3 private repositories to local disk.",
    host: "ENG-BUILD-02",
    ip: "10.31.9.14",
  },
  {
    id: "LOG-9012",
    employee_id: "EMP-1355",
    event_type: "login",
    timestamp: "2026-09-01T09:15:00Z",
    details: "Routine SSO login from managed laptop.",
    host: "LEG-LAP-02",
    ip: "10.55.1.8",
  },
  {
    id: "LOG-9013",
    employee_id: "EMP-1188",
    event_type: "usb_connect",
    timestamp: "2026-08-31T20:10:00Z",
    details: "Approved encrypted USB token mounted for signing.",
    host: "SAL-LAP-17",
    ip: "10.44.2.7",
  },
  {
    id: "LOG-9014",
    employee_id: "EMP-1211",
    event_type: "privilege_change",
    timestamp: "2026-08-31T15:48:00Z",
    details: "Granted temporary domain-admin (ticket CHG-8842, approved).",
    host: "ITO-JUMP-01",
    ip: "10.9.0.4",
  },
  {
    id: "LOG-9015",
    employee_id: "EMP-1274",
    event_type: "email_external",
    timestamp: "2026-08-31T11:05:00Z",
    details: "Sent offer letter PDF to candidate domain.",
    host: "HR-WKS-03",
    ip: "10.12.7.33",
  },
  {
    id: "LOG-9016",
    employee_id: "EMP-1402",
    event_type: "vpn_access",
    timestamp: "2026-08-30T23:40:00Z",
    details: "VPN session at 23:40 local — 2.5 sigma above baseline hours.",
    host: "FIN-WKS-12",
    ip: "10.22.4.60",
  },
  {
    id: "LOG-9017",
    employee_id: "EMP-1309",
    event_type: "login",
    timestamp: "2026-08-30T08:12:00Z",
    details: "Routine login, MFA satisfied via hardware key.",
    host: "ENG-WKS-21",
    ip: "10.31.9.55",
  },
  {
    id: "LOG-9018",
    employee_id: "EMP-1042",
    event_type: "email_external",
    timestamp: "2026-08-29T19:26:00Z",
    details: "Zip archive (740 MB) sent to external file-transfer service.",
    host: "FIN-WKS-08",
    ip: "10.22.4.91",
  },
  {
    id: "LOG-9019",
    employee_id: "EMP-1466",
    event_type: "file_upload",
    timestamp: "2026-08-29T14:03:00Z",
    details: "Uploaded demo assets to shared drive.",
    host: "SAL-LAP-04",
    ip: "10.44.2.19",
  },
  {
    id: "LOG-9020",
    employee_id: "EMP-1103",
    event_type: "vpn_access",
    timestamp: "2026-08-28T03:19:00Z",
    details: "Concurrent VPN sessions from two countries within 9 minutes.",
    host: "ENG-BUILD-02",
    ip: "203.0.113.44",
  },
];

export const alerts: ThreatAlert[] = [
  {
    id: "ALR-4401",
    employee_id: "EMP-1042",
    employee_name: "Ana Delgado",
    severity: "Critical",
    message: "Mass data staging followed by unregistered USB mount",
    status: "Investigating",
    created_at: "2026-09-03T02:35:00Z",
    assigned_to: "Security Analyst",
    rule: "ITBIS-R014 · Exfiltration staging chain",
    narrative:
      "412 finance forecast files were pulled at 02:14 UTC, then an unregistered 128 GB USB device was mounted 17 minutes later on the same host. Behavioural baseline for this account shows no prior after-hours bulk access.",
  },
  {
    id: "ALR-4402",
    employee_id: "EMP-1103",
    employee_name: "Marcus Chen",
    severity: "High",
    message: "Self-granted production database privileges",
    status: "Open",
    created_at: "2026-09-02T18:07:00Z",
    assigned_to: "SOC Engineer",
    rule: "ITBIS-R008 · Privilege self-escalation",
    narrative:
      "An automation token belonging to this user added the account to prod-db-readers with no matching change ticket. Repository cloning activity was observed on the same host earlier in the day.",
  },
  {
    id: "ALR-4403",
    employee_id: "EMP-1188",
    employee_name: "Sofia Ibrahim",
    severity: "High",
    message: "Customer pipeline export sent to personal mailbox",
    status: "Investigating",
    created_at: "2026-09-02T16:50:00Z",
    assigned_to: "Security Analyst",
    rule: "ITBIS-R003 · Sensitive data to personal domain",
    narrative:
      "A 3.1 MB CRM pipeline export was mailed to a personal address. The account is inside a flagged retention window (resignation submitted 2026-08-28).",
  },
  {
    id: "ALR-4404",
    employee_id: "EMP-1211",
    employee_name: "Tom Averill",
    severity: "Medium",
    message: "VPN access from previously unseen hosting provider",
    status: "Open",
    created_at: "2026-09-02T13:20:00Z",
    assigned_to: "SOC Engineer",
    rule: "ITBIS-R021 · Anomalous network origin",
    narrative:
      "Session originated from a datacentre ASN in Germany. No travel record and no prior sessions from this ASN in 180 days of history.",
  },
  {
    id: "ALR-4405",
    employee_id: "EMP-1042",
    employee_name: "Ana Delgado",
    severity: "Critical",
    message: "740 MB archive uploaded to external transfer service",
    status: "Open",
    created_at: "2026-08-29T19:30:00Z",
    assigned_to: "Security Manager",
    rule: "ITBIS-R002 · Unsanctioned egress channel",
    narrative:
      "Archive size and destination are both outside policy. DLP inspection was bypassed because the transfer used an unmanaged browser profile.",
  },
  {
    id: "ALR-4406",
    employee_id: "EMP-1274",
    employee_name: "Leah Okonkwo",
    severity: "Low",
    message: "Repeated failed logins before successful SSO",
    status: "Resolved",
    created_at: "2026-09-02T09:05:00Z",
    assigned_to: "Security Analyst",
    rule: "ITBIS-R031 · Credential friction",
    narrative:
      "Four failed attempts then success from the usual managed workstation. User confirmed a password manager sync issue. Closed as benign.",
  },
  {
    id: "ALR-4407",
    employee_id: "EMP-1402",
    employee_name: "Yusuf Demir",
    severity: "Medium",
    message: "Off-hours bulk export of vendor payment records",
    status: "Investigating",
    created_at: "2026-09-01T23:02:00Z",
    assigned_to: "Security Analyst",
    rule: "ITBIS-R011 · Off-baseline data access",
    narrative:
      "86 vendor payment rows exported at 22:58 UTC. Volume is within role norms but the access hour is 2.5 sigma above the user baseline.",
  },
  {
    id: "ALR-4408",
    employee_id: "EMP-1103",
    employee_name: "Marcus Chen",
    severity: "High",
    message: "Impossible travel — concurrent VPN sessions",
    status: "Open",
    created_at: "2026-08-28T03:25:00Z",
    assigned_to: "SOC Engineer",
    rule: "ITBIS-R017 · Impossible travel",
    narrative:
      "Two authenticated sessions nine minutes apart from geographically incompatible origins. Second session used a stale refresh token.",
  },
  {
    id: "ALR-4409",
    employee_id: "EMP-1309",
    employee_name: "Ravi Menon",
    severity: "Informational",
    message: "First-time use of approved artifact store",
    status: "Resolved",
    created_at: "2026-09-02T08:45:00Z",
    assigned_to: "SOC Engineer",
    rule: "ITBIS-R044 · New tool adoption",
    narrative: "Baseline enrichment event only. No policy violation detected.",
  },
  {
    id: "ALR-4410",
    employee_id: "EMP-1188",
    employee_name: "Sofia Ibrahim",
    severity: "Medium",
    message: "Sustained increase in CRM record views",
    status: "Investigating",
    created_at: "2026-08-30T10:14:00Z",
    assigned_to: "Security Manager",
    rule: "ITBIS-R009 · Access volume drift",
    narrative:
      "Record views up 340% over a rolling 14-day window versus peer group in the same territory.",
  },
  {
    id: "ALR-4411",
    employee_id: "EMP-1211",
    employee_name: "Tom Averill",
    severity: "Low",
    message: "Temporary domain-admin grant exceeded window",
    status: "Resolved",
    created_at: "2026-08-31T18:02:00Z",
    assigned_to: "SOC Engineer",
    rule: "ITBIS-R027 · Standing privilege drift",
    narrative: "Elevated role held 40 minutes past the approved window. Auto-revoked by policy.",
  },
  {
    id: "ALR-4412",
    employee_id: "EMP-1355",
    employee_name: "Grace Lindqvist",
    severity: "Informational",
    message: "Legal hold document set accessed",
    status: "Resolved",
    created_at: "2026-09-01T09:20:00Z",
    assigned_to: "Security Manager",
    rule: "ITBIS-R052 · Monitored collection access",
    narrative: "Access is expected for this role. Logged for audit completeness.",
  },
  {
    id: "ALR-4413",
    employee_id: "EMP-1466",
    employee_name: "Nina Petrova",
    severity: "Low",
    message: "Large asset upload to shared drive",
    status: "Open",
    created_at: "2026-08-29T14:10:00Z",
    assigned_to: "Security Analyst",
    rule: "ITBIS-R019 · Volume anomaly",
    narrative: "Upload volume above personal baseline but destination is a sanctioned drive.",
  },
  {
    id: "ALR-4414",
    employee_id: "EMP-1042",
    employee_name: "Ana Delgado",
    severity: "High",
    message: "Login from unmanaged device fingerprint",
    status: "Investigating",
    created_at: "2026-09-01T21:52:00Z",
    assigned_to: "Security Analyst",
    rule: "ITBIS-R006 · Unmanaged endpoint",
    narrative:
      "Device fingerprint has never been seen for this identity and failed posture checks (no disk encryption reported).",
  },
];

export const platformUsers: PlatformUser[] = [
  {
    id: "USR-01",
    email: "priya.raman@northwind.co",
    role: "Security Manager",
    status: "Active",
    last_login: "2026-09-03T07:41:00Z",
  },
  {
    id: "USR-02",
    email: "dieter.roth@northwind.co",
    role: "Administrator",
    status: "Active",
    last_login: "2026-09-03T06:12:00Z",
  },
  {
    id: "USR-03",
    email: "jonas.hale@northwind.co",
    role: "Security Analyst",
    status: "Active",
    last_login: "2026-09-03T08:03:00Z",
  },
  {
    id: "USR-04",
    email: "mei.tanaka@northwind.co",
    role: "SOC Engineer",
    status: "Active",
    last_login: "2026-09-02T22:55:00Z",
  },
  {
    id: "USR-05",
    email: "omar.said@northwind.co",
    role: "Security Analyst",
    status: "Invited",
    last_login: "—",
  },
  {
    id: "USR-06",
    email: "karen.blake@northwind.co",
    role: "Security Manager",
    status: "Active",
    last_login: "2026-09-01T16:20:00Z",
  },
  {
    id: "USR-07",
    email: "legacy.svc@northwind.co",
    role: "SOC Engineer",
    status: "Suspended",
    last_login: "2026-06-14T09:00:00Z",
  },
];

export interface Investigation {
  id: string;
  title: string;
  employee_name: string;
  status: "Triage" | "In progress" | "Awaiting review";
  severity: Severity;
  opened_at: string;
}

export const investigations: Investigation[] = [
  {
    id: "INV-221",
    title: "Finance forecast exfiltration chain",
    employee_name: "Ana Delgado",
    status: "In progress",
    severity: "Critical",
    opened_at: "2026-09-03T03:10:00Z",
  },
  {
    id: "INV-222",
    title: "Prod database privilege escalation",
    employee_name: "Marcus Chen",
    status: "Triage",
    severity: "High",
    opened_at: "2026-09-02T18:40:00Z",
  },
  {
    id: "INV-219",
    title: "CRM export to personal mailbox",
    employee_name: "Sofia Ibrahim",
    status: "Awaiting review",
    severity: "High",
    opened_at: "2026-09-02T17:15:00Z",
  },
  {
    id: "INV-216",
    title: "Off-hours vendor payment exports",
    employee_name: "Yusuf Demir",
    status: "In progress",
    severity: "Medium",
    opened_at: "2026-09-01T23:30:00Z",
  },
];

/* ------------------------------------------------------------------ */
/* API surface — replace these bodies with fetch() calls when the      */
/* backend lands. Signatures should stay identical.                    */
/* ------------------------------------------------------------------ */

export const api = {
  getEmployees: (): Employee[] => employees,
  getEmployee: (id: string): Employee | undefined =>
    employees.find((e) => e.employee_id === id),
  getActivityLogs: (): ActivityLog[] => activityLogs,
  getActivityLogsForEmployee: (id: string): ActivityLog[] =>
    activityLogs.filter((l) => l.employee_id === id),
  getAlerts: (): ThreatAlert[] => alerts,
  getAlertsForRole: (role: Role): ThreatAlert[] =>
    alerts.filter((a) => a.assigned_to === role),
  getPlatformUsers: (): PlatformUser[] => platformUsers,
  getInvestigations: (): Investigation[] => investigations,
  getManagers: (): string[] => managers,
  getDepartments: (): string[] => departments,
};

export const riskLevels: RiskLevel[] = ["Low", "Medium", "High", "Critical"];
export const severities: Severity[] = ["Informational", "Low", "Medium", "High", "Critical"];
export const eventTypes: EventType[] = [
  "login",
  "logout",
  "file_download",
  "file_upload",
  "usb_connect",
  "email_external",
  "vpn_access",
  "privilege_change",
];

export function formatTimestamp(iso: string): string {
  if (!iso || iso === "—") return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toISOString().replace("T", " ").slice(0, 16) + " UTC";
}
