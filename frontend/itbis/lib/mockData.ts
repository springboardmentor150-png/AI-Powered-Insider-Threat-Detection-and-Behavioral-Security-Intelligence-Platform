export interface EmployeeRecord {
  id: string;
  name: string;
  department: string;
  designation: string;
  manager: string;
  device: string;
  accessLevel: "STANDARD" | "ELEVATED" | "CRITICAL_ADMIN" | "RESTRICTED";
  riskScore: number;
  riskCategory: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  status: "ACTIVE" | "UNDER_REVIEW" | "FLAGGED" | "RESTRICTED";
  email: string;
  lastActive: string;
  anomaliesDetected: number;
}

export interface SecurityAlert {
  id: string;
  employeeId: string;
  employeeName: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  title: string;
  category: "Data Exfiltration" | "Privilege Escalation" | "Off-Hours Access" | "Unauthorized USB" | "Mass Download";
  timestamp: string;
  status: "OPEN" | "INVESTIGATING" | "RESOLVED";
}

export interface ActivityEvent {
  id: string;
  employeeId: string;
  employeeName: string;
  action: string;
  resource: string;
  riskWeight: number;
  timestamp: string;
  deviceIp: string;
}

export const MOCK_EMPLOYEES: EmployeeRecord[] = [
  {
    id: "EMP-8492",
    name: "Alexander Hayes",
    department: "Engineering",
    designation: "Principal Cloud Architect",
    manager: "Sarah Lin (VP Eng)",
    device: "MacBook Pro M3 (SEC-D-992)",
    accessLevel: "CRITICAL_ADMIN",
    riskScore: 89,
    riskCategory: "CRITICAL",
    status: "FLAGGED",
    email: "a.hayes@enterprise.corp",
    lastActive: "2 mins ago",
    anomaliesDetected: 7,
  },
  {
    id: "EMP-7310",
    name: "Elena Rostova",
    department: "Finance",
    designation: "Senior Treasury Analyst",
    manager: "David Miller (Dir Fin)",
    device: "ThinkPad X1 (SEC-D-441)",
    accessLevel: "ELEVATED",
    riskScore: 78,
    riskCategory: "HIGH",
    status: "UNDER_REVIEW",
    email: "e.rostova@enterprise.corp",
    lastActive: "14 mins ago",
    anomaliesDetected: 4,
  },
  {
    id: "EMP-6204",
    name: "Marcus Vance",
    department: "DevOps & SRE",
    designation: "Lead Infrastructure Engineer",
    manager: "Sarah Lin (VP Eng)",
    device: "Dell Precision (SEC-D-803)",
    accessLevel: "CRITICAL_ADMIN",
    riskScore: 68,
    riskCategory: "HIGH",
    status: "ACTIVE",
    email: "m.vance@enterprise.corp",
    lastActive: "41 mins ago",
    anomaliesDetected: 3,
  },
  {
    id: "EMP-5199",
    name: "Samantha Wright",
    department: "Human Resources",
    designation: "HR Business Partner",
    manager: "Rachel Adams (Chief People)",
    device: "MacBook Air (SEC-D-210)",
    accessLevel: "STANDARD",
    riskScore: 42,
    riskCategory: "MEDIUM",
    status: "ACTIVE",
    email: "s.wright@enterprise.corp",
    lastActive: "1 hour ago",
    anomaliesDetected: 1,
  },
  {
    id: "EMP-4102",
    name: "Vikram Malhotra",
    department: "Engineering",
    designation: "Senior Backend Developer",
    manager: "Alexander Hayes (Arch)",
    device: "Ubuntu Workstation (SEC-D-119)",
    accessLevel: "ELEVATED",
    riskScore: 35,
    riskCategory: "MEDIUM",
    status: "ACTIVE",
    email: "v.malhotra@enterprise.corp",
    lastActive: "3 hours ago",
    anomaliesDetected: 0,
  },
  {
    id: "EMP-3901",
    name: "Claire Dupont",
    department: "Legal & Compliance",
    designation: "Senior Regulatory Counsel",
    manager: "Arthur Vance (General Counsel)",
    device: "Surface Pro 9 (SEC-D-512)",
    accessLevel: "ELEVATED",
    riskScore: 19,
    riskCategory: "LOW",
    status: "ACTIVE",
    email: "c.dupont@enterprise.corp",
    lastActive: "5 mins ago",
    anomaliesDetected: 0,
  },
  {
    id: "EMP-2844",
    name: "Tariq Mansour",
    department: "Operations",
    designation: "Supply Chain Manager",
    manager: "Lisa Zhang (VP Ops)",
    device: "Dell Latitude (SEC-D-677)",
    accessLevel: "STANDARD",
    riskScore: 14,
    riskCategory: "LOW",
    status: "ACTIVE",
    email: "t.mansour@enterprise.corp",
    lastActive: "22 mins ago",
    anomaliesDetected: 0,
  },
  {
    id: "EMP-1088",
    name: "Jessica Chen",
    department: "Product Management",
    designation: "Group Product Manager",
    manager: "Tom Larson (CPO)",
    device: "MacBook Pro 16 (SEC-D-318)",
    accessLevel: "STANDARD",
    riskScore: 11,
    riskCategory: "LOW",
    status: "ACTIVE",
    email: "j.chen@enterprise.corp",
    lastActive: "Just now",
    anomaliesDetected: 0,
  },
];

export const MOCK_ALERTS: SecurityAlert[] = [
  {
    id: "ALT-9042",
    employeeId: "EMP-8492",
    employeeName: "Alexander Hayes",
    severity: "CRITICAL",
    category: "Data Exfiltration",
    title: "Mass database export (4.8 GB) copied to unapproved cloud storage endpoint",
    timestamp: "12 mins ago",
    status: "OPEN",
  },
  {
    id: "ALT-8819",
    employeeId: "EMP-7310",
    employeeName: "Elena Rostova",
    severity: "HIGH",
    category: "Off-Hours Access",
    title: "Repeated unauthorized financial ledger queries at 02:45 AM UTC",
    timestamp: "45 mins ago",
    status: "INVESTIGATING",
  },
  {
    id: "ALT-7650",
    employeeId: "EMP-6204",
    employeeName: "Marcus Vance",
    severity: "HIGH",
    category: "Privilege Escalation",
    title: "Attempted privilege elevation on Kubernetes production cluster",
    timestamp: "2 hours ago",
    status: "OPEN",
  },
  {
    id: "ALT-6512",
    employeeId: "EMP-5199",
    employeeName: "Samantha Wright",
    severity: "MEDIUM",
    category: "Mass Download",
    title: "Downloaded 320 executive personnel files within 10 minutes",
    timestamp: "4 hours ago",
    status: "RESOLVED",
  },
  {
    id: "ALT-5411",
    employeeId: "EMP-4102",
    employeeName: "Vikram Malhotra",
    severity: "LOW",
    category: "Off-Hours Access",
    title: "SSH session established from unfamiliar geo-IP subnet (VPN validated)",
    timestamp: "6 hours ago",
    status: "RESOLVED",
  },
];

export const MOCK_ACTIVITIES: ActivityEvent[] = [
  {
    id: "ACT-1092",
    employeeId: "EMP-8492",
    employeeName: "Alexander Hayes",
    action: "Bulk Data Query & Export",
    resource: "s3://corp-analytics-archive/q3-raw-data.tar.gz",
    riskWeight: 92,
    timestamp: "12m ago",
    deviceIp: "10.240.12.84",
  },
  {
    id: "ACT-1091",
    employeeId: "EMP-7310",
    employeeName: "Elena Rostova",
    action: "Database Read (Restricted Schema)",
    resource: "db://fin-prod-01/payroll_executive",
    riskWeight: 84,
    timestamp: "45m ago",
    deviceIp: "10.240.14.19",
  },
  {
    id: "ACT-1090",
    employeeId: "EMP-6204",
    employeeName: "Marcus Vance",
    action: "IAM Role Modification",
    resource: "iam:AttachUserPolicy / AdministratorAccess",
    riskWeight: 75,
    timestamp: "2h ago",
    deviceIp: "10.240.8.102",
  },
  {
    id: "ACT-1089",
    employeeId: "EMP-3901",
    employeeName: "Claire Dupont",
    action: "Document Access",
    resource: "sharepoint://legal/nda-merger-2026.docx",
    riskWeight: 18,
    timestamp: "3h ago",
    deviceIp: "10.240.19.41",
  },
  {
    id: "ACT-1088",
    employeeId: "EMP-1088",
    employeeName: "Jessica Chen",
    action: "Jira Issue Update",
    resource: "jira://PROD-4018",
    riskWeight: 8,
    timestamp: "4h ago",
    deviceIp: "10.240.11.55",
  },
];
