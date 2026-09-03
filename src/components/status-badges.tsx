import { cn } from "@/lib/utils";
import type { AlertStatus, EventType, RiskLevel, Severity } from "@/api/mockData";

const base =
  "inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-xs font-medium tracking-tight whitespace-nowrap";

const severityStyles: Record<Severity, string> = {
  Informational: "border-info/40 bg-info/15 text-info",
  Low: "border-low/40 bg-low/15 text-low",
  Medium: "border-medium/40 bg-medium/15 text-medium",
  High: "border-high/45 bg-high/15 text-high",
  Critical: "border-critical/50 bg-critical/20 text-critical",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span className={cn(base, severityStyles[severity])}>
      <span className="size-1.5 rounded-full bg-current" />
      {severity}
    </span>
  );
}

export function RiskBadge({ level }: { level: RiskLevel }) {
  return (
    <span className={cn(base, severityStyles[level as Severity])}>
      <span className="size-1.5 rounded-full bg-current" />
      {level}
    </span>
  );
}

const statusStyles: Record<AlertStatus, string> = {
  Open: "border-high/45 bg-high/12 text-high",
  Investigating: "border-primary/45 bg-primary/12 text-primary",
  Resolved: "border-low/40 bg-low/12 text-low",
};

export function AlertStatusBadge({ status }: { status: AlertStatus }) {
  return <span className={cn(base, statusStyles[status])}>{status}</span>;
}

const eventStyles: Record<EventType, string> = {
  login: "border-info/40 bg-info/12 text-info",
  logout: "border-border bg-muted text-muted-foreground",
  file_download: "border-high/45 bg-high/12 text-high",
  file_upload: "border-primary/40 bg-primary/12 text-primary",
  usb_connect: "border-critical/45 bg-critical/15 text-critical",
  email_external: "border-medium/45 bg-medium/12 text-medium",
  vpn_access: "border-primary/40 bg-primary/12 text-primary",
  privilege_change: "border-critical/45 bg-critical/15 text-critical",
};

export function EventTag({ type }: { type: EventType }) {
  return <span className={cn(base, "font-mono", eventStyles[type])}>{type}</span>;
}

export function UserStatusBadge({ status }: { status: "Active" | "Invited" | "Suspended" }) {
  const map = {
    Active: "border-low/40 bg-low/12 text-low",
    Invited: "border-medium/45 bg-medium/12 text-medium",
    Suspended: "border-critical/45 bg-critical/15 text-critical",
  } as const;
  return <span className={cn(base, map[status])}>{status}</span>;
}

export function RoleBadge({ role, className }: { role: string; className?: string }) {
  return (
    <span
      className={cn(
        base,
        "border-primary/45 bg-primary/12 text-primary uppercase tracking-wide",
        className,
      )}
    >
      {role}
    </span>
  );
}
