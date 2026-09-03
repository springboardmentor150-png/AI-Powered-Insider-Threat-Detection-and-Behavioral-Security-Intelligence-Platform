import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BellRing,
  Building2,
  FileSearch,
  ShieldAlert,
  Users,
  UserCog,
} from "lucide-react";
import {
  api,
  formatTimestamp,
  riskLevels,
  ROLES,
  type RiskLevel,
  type Role,
} from "@/api/mockData";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import {
  AlertStatusBadge,
  EventTag,
  RiskBadge,
  SeverityBadge,
} from "@/components/status-badges";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAuth } from "@/lib/auth";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — ITBIS Insider Threat Console" },
      {
        name: "description",
        content:
          "Role-aware insider threat dashboard: risk posture, open alerts, investigations and workforce activity at a glance.",
      },
      { property: "og:title", content: "Dashboard — ITBIS Insider Threat Console" },
      {
        property: "og:description",
        content: "Risk posture, open alerts and investigations for your SOC team.",
      },
    ],
  }),
  component: DashboardPage,
});

const employees = api.getEmployees();
const alerts = api.getAlerts();
const logs = api.getActivityLogs();
const users = api.getPlatformUsers();
const investigations = api.getInvestigations();

function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  tone = "primary",
}: {
  label: string;
  value: string | number;
  hint?: string;
  icon: typeof Users;
  tone?: "primary" | "high" | "critical" | "low";
}) {
  const tones = {
    primary: "bg-primary/12 text-primary",
    high: "bg-high/15 text-high",
    critical: "bg-critical/15 text-critical",
    low: "bg-low/15 text-low",
  } as const;
  return (
    <Card>
      <CardContent className="flex items-start justify-between gap-3 pt-6">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
            {label}
          </p>
          <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
          {hint ? <p className="mt-1 text-xs text-muted-foreground">{hint}</p> : null}
        </div>
        <span className={`flex size-9 items-center justify-center rounded-md ${tones[tone]}`}>
          <Icon className="size-4.5" />
        </span>
      </CardContent>
    </Card>
  );
}

function DashboardPage() {
  const { session } = useAuth();
  const role = session!.role;

  return (
    <AppShell>
      <PageHeader
        title={`${role} dashboard`}
        description={`Behavioural intelligence tailored to your role. Signed in as ${session!.email}.`}
      />
      {role === "Administrator" ? <AdminDashboard /> : null}
      {role === "Security Manager" ? <ManagerDashboard /> : null}
      {role === "Security Analyst" || role === "SOC Engineer" ? (
        <AnalystDashboard role={role} />
      ) : null}
    </AppShell>
  );
}

function AdminDashboard() {
  const activeIncidents = alerts.filter((a) => a.status !== "Resolved").length;
  const byRole = ROLES.map((r) => ({ role: r, count: users.filter((u) => u.role === r).length }));

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total employees" value={employees.length} icon={Users} hint="Monitored identities" />
        <StatCard label="Total alerts" value={alerts.length} icon={BellRing} hint="All time" tone="high" />
        <StatCard
          label="Active incidents"
          value={activeIncidents}
          icon={ShieldAlert}
          hint="Open or investigating"
          tone="critical"
        />
        <StatCard label="Platform users" value={users.length} icon={UserCog} hint="Console accounts" tone="low" />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Users by role</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {byRole.map(({ role, count }) => (
              <div key={role}>
                <div className="mb-1.5 flex items-center justify-between text-sm">
                  <span>{role}</span>
                  <span className="font-mono text-xs text-muted-foreground">{count}</span>
                </div>
                <Progress value={(count / users.length) * 100} />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick links</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <QuickLink to="/users" label="User Management" hint="Invite and manage console accounts" icon={UserCog} />
            <QuickLink to="/employees" label="Employee Management" hint="Workforce records and risk levels" icon={Users} />
            <QuickLink to="/activity-logs" label="Activity Logs" hint="Raw behavioural telemetry" icon={Activity} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">System event stream</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <LogTable rows={logs.slice(0, 6)} />
        </CardContent>
      </Card>
    </div>
  );
}

function QuickLink({
  to,
  label,
  hint,
  icon: Icon,
}: {
  to: "/users" | "/employees" | "/activity-logs" | "/alerts";
  label: string;
  hint: string;
  icon: typeof Users;
}) {
  return (
    <Link
      to={to}
      className="flex items-center gap-3 rounded-md border border-border bg-surface px-3 py-3 transition-colors hover:border-primary/50 hover:bg-accent/40"
    >
      <span className="flex size-8 items-center justify-center rounded-md bg-primary/12 text-primary">
        <Icon className="size-4" />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-sm font-medium">{label}</span>
        <span className="block truncate text-xs text-muted-foreground">{hint}</span>
      </span>
      <ArrowUpRight className="size-4 text-muted-foreground" />
    </Link>
  );
}

function ManagerDashboard() {
  const counts = riskLevels.map((level) => ({
    level,
    count: employees.filter((e) => e.risk_level === level).length,
  }));
  const departments = [...new Set(employees.map((e) => e.department))].map((dept) => {
    const staff = employees.filter((e) => e.department === dept);
    const avg = Math.round(staff.reduce((s, e) => s + e.risk_score, 0) / staff.length);
    return { dept, headcount: staff.length, avg };
  });
  departments.sort((a, b) => b.avg - a.avg);

  const toneFor: Record<RiskLevel, "low" | "primary" | "high" | "critical"> = {
    Low: "low",
    Medium: "primary",
    High: "high",
    Critical: "critical",
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {counts.map(({ level, count }) => (
          <StatCard
            key={level}
            label={`${level} risk`}
            value={count}
            hint="Employees at this tier"
            icon={level === "Critical" ? AlertTriangle : Users}
            tone={toneFor[level]}
          />
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Recent alerts</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead className="hidden md:table-cell">Message</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {alerts.slice(0, 7).map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="font-medium">{a.employee_name}</TableCell>
                    <TableCell>
                      <SeverityBadge severity={a.severity} />
                    </TableCell>
                    <TableCell className="hidden max-w-[22rem] truncate text-muted-foreground md:table-cell">
                      {a.message}
                    </TableCell>
                    <TableCell>
                      <AlertStatusBadge status={a.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Building2 className="size-4 text-muted-foreground" /> Department risk
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {departments.map(({ dept, headcount, avg }) => (
              <div key={dept}>
                <div className="mb-1.5 flex items-center justify-between text-sm">
                  <span>{dept}</span>
                  <span className="font-mono text-xs text-muted-foreground">
                    {avg} · {headcount} staff
                  </span>
                </div>
                <Progress value={avg} />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function AnalystDashboard({ role }: { role: Role }) {
  const assigned = api.getAlertsForRole(role);
  const open = assigned.filter((a) => a.status !== "Resolved");

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Assigned alerts" value={assigned.length} icon={BellRing} />
        <StatCard label="Open queue" value={open.length} icon={ShieldAlert} tone="high" />
        <StatCard
          label="Critical in queue"
          value={assigned.filter((a) => a.severity === "Critical").length}
          icon={AlertTriangle}
          tone="critical"
        />
        <StatCard label="My investigations" value={investigations.length} icon={FileSearch} tone="low" />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Assigned alerts</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Alert</TableHead>
                  <TableHead>Employee</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {assigned.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell>
                      <span className="font-mono text-xs text-muted-foreground">{a.id}</span>
                      <span className="block max-w-[20rem] truncate text-sm">{a.message}</span>
                    </TableCell>
                    <TableCell className="whitespace-nowrap">{a.employee_name}</TableCell>
                    <TableCell>
                      <SeverityBadge severity={a.severity} />
                    </TableCell>
                    <TableCell>
                      <AlertStatusBadge status={a.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <FileSearch className="size-4 text-muted-foreground" /> My investigations
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {investigations.map((inv) => (
              <div key={inv.id} className="rounded-md border border-border bg-surface p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-xs text-muted-foreground">{inv.id}</span>
                  <SeverityBadge severity={inv.severity} />
                </div>
                <p className="mt-1.5 text-sm font-medium">{inv.title}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  {inv.employee_name} · {inv.status} · opened {formatTimestamp(inv.opened_at)}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Activity className="size-4 text-muted-foreground" /> Recent activity feed
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <LogTable rows={logs.slice(0, 8)} />
        </CardContent>
      </Card>
    </div>
  );
}

function LogTable({ rows }: { rows: ReturnType<typeof api.getActivityLogs> }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Employee</TableHead>
          <TableHead>Event</TableHead>
          <TableHead className="hidden lg:table-cell">Details</TableHead>
          <TableHead>Timestamp</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((l) => (
          <TableRow key={l.id}>
            <TableCell className="font-mono text-xs">{l.employee_id}</TableCell>
            <TableCell>
              <EventTag type={l.event_type} />
            </TableCell>
            <TableCell className="hidden max-w-[30rem] truncate text-muted-foreground lg:table-cell">
              {l.details}
            </TableCell>
            <TableCell className="whitespace-nowrap font-mono text-xs text-muted-foreground">
              {formatTimestamp(l.timestamp)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
