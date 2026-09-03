import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { api, formatTimestamp, severities, type Severity, type ThreatAlert } from "@/api/mockData";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { AlertStatusBadge, SeverityBadge } from "@/components/status-badges";
import { Card, CardContent } from "@/components/ui/card";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export const Route = createFileRoute("/alerts")({
  head: () => ({
    meta: [
      { title: "Alerts — ITBIS Insider Threat Console" },
      {
        name: "description",
        content:
          "Triage insider threat alerts by severity and status, and open incident detail for any detection.",
      },
      { property: "og:title", content: "Alerts — ITBIS Insider Threat Console" },
      { property: "og:description", content: "Insider threat alert queue and incident detail." },
    ],
  }),
  component: AlertsPage,
});

const allAlerts = api.getAlerts();

function AlertsPage() {
  const [severity, setSeverity] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [selected, setSelected] = useState<ThreatAlert | null>(null);

  const rows = useMemo(
    () =>
      allAlerts.filter(
        (a) =>
          (severity === "all" || a.severity === severity) &&
          (status === "all" || a.status === status),
      ),
    [severity, status],
  );

  return (
    <AppShell>
      <PageHeader
        title="Alerts"
        description="Behavioural detections raised by the ITBIS rule engine. Click a row for incident detail."
      />

      <Card className="mb-5">
        <CardContent className="flex flex-wrap items-center gap-3 pt-6">
          <Select value={severity} onValueChange={setSeverity}>
            <SelectTrigger className="w-[190px]" aria-label="Filter by severity">
              <SelectValue placeholder="Severity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All severities</SelectItem>
              {severities.map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger className="w-[180px]" aria-label="Filter by status">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              {["Open", "Investigating", "Resolved"].map((s) => (
                <SelectItem key={s} value={s}>
                  {s}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <span className="ml-auto font-mono text-xs text-muted-foreground">
            {rows.length} / {allAlerts.length} alerts
          </span>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Alert</TableHead>
                <TableHead>Employee</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead className="hidden lg:table-cell">Message</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created at</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((a) => (
                <TableRow
                  key={a.id}
                  className="cursor-pointer"
                  onClick={() => setSelected(a)}
                >
                  <TableCell className="font-mono text-xs text-muted-foreground">{a.id}</TableCell>
                  <TableCell className="whitespace-nowrap font-medium">{a.employee_name}</TableCell>
                  <TableCell>
                    <SeverityBadge severity={a.severity} />
                  </TableCell>
                  <TableCell className="hidden max-w-[26rem] truncate text-muted-foreground lg:table-cell">
                    {a.message}
                  </TableCell>
                  <TableCell>
                    <AlertStatusBadge status={a.status} />
                  </TableCell>
                  <TableCell className="whitespace-nowrap font-mono text-xs text-muted-foreground">
                    {formatTimestamp(a.created_at)}
                  </TableCell>
                </TableRow>
              ))}
              {rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="py-10 text-center text-muted-foreground">
                    No alerts match the current filters.
                  </TableCell>
                </TableRow>
              ) : null}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
          {selected ? (
            <>
              <SheetHeader>
                <SheetTitle className="pr-6">{selected.message}</SheetTitle>
                <SheetDescription className="font-mono text-xs">
                  {selected.id} · {selected.rule}
                </SheetDescription>
              </SheetHeader>

              <div className="space-y-5 px-4 pb-8">
                <div className="flex flex-wrap gap-2">
                  <SeverityBadge severity={selected.severity as Severity} />
                  <AlertStatusBadge status={selected.status} />
                </div>

                <dl className="grid grid-cols-2 gap-4 text-sm">
                  <Field label="Employee" value={selected.employee_name} />
                  <Field label="Employee ID" value={selected.employee_id} mono />
                  <Field label="Assigned to" value={selected.assigned_to} />
                  <Field label="Created" value={formatTimestamp(selected.created_at)} mono />
                </dl>

                <div>
                  <p className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
                    Incident narrative
                  </p>
                  <p className="mt-2 text-sm leading-relaxed">{selected.narrative}</p>
                </div>

                <div>
                  <p className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
                    Correlated activity
                  </p>
                  <ul className="mt-2 space-y-2">
                    {api.getActivityLogsForEmployee(selected.employee_id).slice(0, 4).map((l) => (
                      <li key={l.id} className="rounded-md border border-border bg-surface p-3 text-sm">
                        <span className="font-mono text-xs text-muted-foreground">
                          {formatTimestamp(l.timestamp)} · {l.host}
                        </span>
                        <span className="mt-1 block">{l.details}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </>
          ) : null}
        </SheetContent>
      </Sheet>
    </AppShell>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
        {label}
      </dt>
      <dd className={mono ? "mt-1 font-mono text-xs" : "mt-1 font-medium"}>{value}</dd>
    </div>
  );
}
