import { createFileRoute } from "@tanstack/react-router";
import { Fragment, useEffect, useState } from "react";
import { ChevronDown, ChevronRight, FilterX } from "lucide-react";
import { apiClient } from "@/api/client";
import { eventTypes, formatTimestamp, type ActivityLog } from "@/api/mockData";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { EventTag } from "@/components/status-badges";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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

export const Route = createFileRoute("/activity-logs")({
  head: () => ({
    meta: [
      { title: "Activity Logs — ITBIS Insider Threat Console" },
      {
        name: "description",
        content:
          "Search raw behavioural telemetry: logins, file transfers, USB mounts, VPN sessions and privilege changes.",
      },
      { property: "og:title", content: "Activity Logs — ITBIS Insider Threat Console" },
      {
        property: "og:description",
        content: "Searchable behavioural telemetry across the monitored workforce.",
      },
    ],
  }),
  component: ActivityLogsPage,
});

function ActivityLogsPage() {
  const [allLogs, setAllLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [employeeId, setEmployeeId] = useState("");
  const [eventType, setEventType] = useState("all");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  // Fetch with filters — debounced via a single load on filter change
  useEffect(() => {
    setLoading(true);
    apiClient
      .getActivityLogs({
        employee_id: employeeId || undefined,
        event_type: eventType !== "all" ? eventType : undefined,
        date_from: from || undefined,
        date_to: to || undefined,
      })
      .then(setAllLogs)
      .finally(() => setLoading(false));
  }, [employeeId, eventType, from, to]);

  function reset() {
    setEmployeeId("");
    setEventType("all");
    setFrom("");
    setTo("");
  }

  return (
    <AppShell>
      <PageHeader
        title="Activity Logs"
        description="Read-only event stream from endpoint, network and identity collectors."
      />

      <Card className="mb-5">
        <CardContent className="grid gap-4 pt-6 md:grid-cols-5">
          <div className="space-y-2">
            <Label htmlFor="emp">Employee ID</Label>
            <Input
              id="emp"
              placeholder="EMP-1042"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="event">Event type</Label>
            <Select value={eventType} onValueChange={setEventType}>
              <SelectTrigger id="event" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All event types</SelectItem>
                {eventTypes.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="from">From</Label>
            <Input id="from" type="date" value={from} onChange={(e) => setFrom(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="to">To</Label>
            <Input id="to" type="date" value={to} onChange={(e) => setTo(e.target.value)} />
          </div>
          <div className="flex items-end">
            <Button variant="outline" className="w-full" onClick={reset}>
              <FilterX className="size-4" /> Clear
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <p className="py-10 text-center font-mono text-sm text-muted-foreground">Loading…</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10" />
                  <TableHead>Employee ID</TableHead>
                  <TableHead>Event type</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead className="hidden md:table-cell">Host</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {allLogs.map((l) => {
                  const open = expanded === l.id;
                  return (
                    <Fragment key={l.id}>
                      <TableRow
                        className="cursor-pointer"
                        onClick={() => setExpanded(open ? null : l.id)}
                      >
                        <TableCell className="text-muted-foreground">
                          {open ? (
                            <ChevronDown className="size-4" />
                          ) : (
                            <ChevronRight className="size-4" />
                          )}
                        </TableCell>
                        <TableCell className="font-mono text-xs">{l.employee_id}</TableCell>
                        <TableCell>
                          <EventTag type={l.event_type} />
                        </TableCell>
                        <TableCell className="whitespace-nowrap font-mono text-xs text-muted-foreground">
                          {formatTimestamp(l.timestamp)}
                        </TableCell>
                        <TableCell className="hidden font-mono text-xs text-muted-foreground md:table-cell">
                          {l.host}
                        </TableCell>
                      </TableRow>
                      {open ? (
                        <TableRow className="bg-surface hover:bg-surface">
                          <TableCell />
                          <TableCell colSpan={4} className="py-4">
                            <p className="text-sm">{l.details}</p>
                            <p className="mt-2 font-mono text-xs text-muted-foreground">
                              {l.id} · host {l.host} · src {l.ip}
                            </p>
                          </TableCell>
                        </TableRow>
                      ) : null}
                    </Fragment>
                  );
                })}
                {allLogs.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="py-10 text-center text-muted-foreground">
                      No log entries match the current filters.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </AppShell>
  );
}
