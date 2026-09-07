import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { Edit, Plus, User, Users } from "lucide-react";
import { toast } from "sonner";
import {
  departments,
  formatTimestamp,
  managers,
  ROLES,
  type Employee,
  type RiskLevel,
} from "@/api/mockData";
import { apiClient } from "@/api/client";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { RiskBadge } from "@/components/status-badges";
import { AccessDenied } from "@/routes/users";
import { canManageEmployees, useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export const Route = createFileRoute("/employees")({
  head: () => ({
    meta: [
      { title: "Employees — ITBIS Insider Threat Console" },
      {
        name: "description",
        content:
          "Manage monitored workforce records: view risk levels, departments and behavioural profiles.",
      },
    ],
  }),
  component: EmployeesPage,
});

const riskLevels: RiskLevel[] = ["Low", "Medium", "High", "Critical"];

const emptyForm = () => ({
  name: "",
  email: "",
  department: departments[0],
  designation: "",
  manager: managers[0],
  location: "",
  risk_level: "Low" as RiskLevel,
  risk_score: 0,
});

function EmployeesPage() {
  const { session } = useAuth();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [deptFilter, setDeptFilter] = useState("all");
  const [selected, setSelected] = useState<Employee | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [addOpen, setAddOpen] = useState(false);
  const [form, setForm] = useState(emptyForm());
  const [editTarget, setEditTarget] = useState<Employee | null>(null);
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const canManage = canManageEmployees(session?.role);

  // Load employees from API (falls back to mock if backend is offline)
  useEffect(() => {
    setLoading(true);
    apiClient.getEmployees()
      .then(setEmployees)
      .catch(() => {
        // Backend offline — already returns mock data from client
        toast.error("Backend offline, showing cached data.");
      })
      .finally(() => setLoading(false));
  }, []);

  const rows = useMemo(
    () => (deptFilter === "all" ? employees : employees.filter((e) => e.department === deptFilter)),
    [employees, deptFilter],
  );

  // ── Validation ─────────────────────────────────────────────────────────────
  function validate(f: typeof form) {
    const e: Record<string, string> = {};
    if (!f.name.trim()) e.name = "Name is required.";
    if (!f.email.trim() || !f.email.includes("@")) e.email = "Valid email required.";
    if (!f.designation.trim()) e.designation = "Designation is required.";
    if (!f.location.trim()) e.location = "Location is required.";
    if (f.risk_score < 0 || f.risk_score > 100) e.risk_score = "Risk score must be 0–100.";
    return e;
  }

  // ── Add employee ────────────────────────────────────────────────────────────
  async function handleAdd() {
    const errs = validate(form);
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setSaving(true);
    try {
      const created = await apiClient.createEmployee(form);
      setEmployees((prev) => [created, ...prev]);
      toast.success(`Employee ${created.name} added.`);
      setAddOpen(false);
      setForm(emptyForm());
      setErrors({});
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create employee.";
      toast.error(msg);
    } finally {
      setSaving(false);
    }
  }

  // ── Edit employee ───────────────────────────────────────────────────────────
  function openEdit(emp: Employee) {
    setEditTarget(emp);
    setForm({
      name: emp.name,
      email: emp.email,
      department: emp.department,
      designation: emp.designation,
      manager: emp.manager,
      location: emp.location,
      risk_level: emp.risk_level,
      risk_score: emp.risk_score,
    });
    setErrors({});
    setEditOpen(true);
  }

  async function handleEdit() {
    if (!editTarget) return;
    const errs = validate(form);
    if (Object.keys(errs).length) { setErrors(errs); return; }
    setSaving(true);
    try {
      const updated = await apiClient.updateEmployee(editTarget.employee_id, form);
      setEmployees((prev) => prev.map((e) => (e.employee_id === updated.employee_id ? updated : e)));
      toast.success("Employee updated.");
      setEditOpen(false);
      setEditTarget(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to update employee.";
      toast.error(msg);
    } finally {
      setSaving(false);
    }
  }

  if (!canManage) {
    return (
      <AppShell>
        <AccessDenied />
      </AppShell>
    );
  }

  return (
    <AppShell>
      <PageHeader
        title="Employees"
        description="Monitored workforce identities. Adjust risk posture or update profile details as needed."
        actions={
          <Button onClick={() => { setForm(emptyForm()); setErrors({}); setAddOpen(true); }}>
            <Plus className="size-4" /> Add Employee
          </Button>
        }
      />

      {/* Department filter */}
      <Card className="mb-5">
        <CardContent className="flex flex-wrap items-center gap-3 pt-6">
          <Select value={deptFilter} onValueChange={setDeptFilter}>
            <SelectTrigger className="w-[220px]" aria-label="Filter by department">
              <SelectValue placeholder="Department" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All departments</SelectItem>
              {departments.map((d) => (
                <SelectItem key={d} value={d}>{d}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <span className="ml-auto font-mono text-xs text-muted-foreground">
            {rows.length} / {employees.length} employees
          </span>
        </CardContent>
      </Card>

      {/* Employee table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <p className="py-10 text-center font-mono text-sm text-muted-foreground">Loading…</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead className="hidden md:table-cell">Designation</TableHead>
                  <TableHead className="hidden lg:table-cell">Manager</TableHead>
                  <TableHead>Risk level</TableHead>
                  <TableHead className="hidden xl:table-cell">Score</TableHead>
                  {canManage && <TableHead className="w-10" />}
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((emp) => (
                  <TableRow
                    key={emp.employee_id}
                    className="cursor-pointer"
                    onClick={() => setSelected(emp)}
                  >
                    <TableCell className="font-mono text-xs text-muted-foreground">
                      {emp.employee_id}
                    </TableCell>
                    <TableCell className="font-medium">{emp.name}</TableCell>
                    <TableCell>{emp.department}</TableCell>
                    <TableCell className="hidden text-muted-foreground md:table-cell">
                      {emp.designation}
                    </TableCell>
                    <TableCell className="hidden text-muted-foreground lg:table-cell">
                      {emp.manager}
                    </TableCell>
                    <TableCell>
                      <RiskBadge level={emp.risk_level} />
                    </TableCell>
                    <TableCell className="hidden font-mono text-xs xl:table-cell">
                      {emp.risk_score}
                    </TableCell>
                    {canManage && (
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label="Edit employee"
                          onClick={(e) => { e.stopPropagation(); openEdit(emp); }}
                        >
                          <Edit className="size-4" />
                        </Button>
                      </TableCell>
                    )}
                  </TableRow>
                ))}
                {rows.length === 0 && !loading && (
                  <TableRow>
                    <TableCell colSpan={8} className="py-10 text-center text-muted-foreground">
                      No employees match the current filter.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* ── Employee detail sheet ─────────────────────────────────────────────── */}
      <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
          {selected && <EmployeeDetail emp={selected} />}
        </SheetContent>
      </Sheet>

      {/* ── Add employee dialog ───────────────────────────────────────────────── */}
      <EmployeeFormDialog
        open={addOpen}
        onOpenChange={setAddOpen}
        title="Add employee"
        description="Add a new monitored identity to the workforce registry."
        form={form}
        setForm={setForm}
        errors={errors}
        saving={saving}
        onSubmit={handleAdd}
      />

      {/* ── Edit employee dialog ──────────────────────────────────────────────── */}
      <EmployeeFormDialog
        open={editOpen}
        onOpenChange={setEditOpen}
        title="Edit employee"
        description="Update workforce identity details or adjust risk posture."
        form={form}
        setForm={setForm}
        errors={errors}
        saving={saving}
        onSubmit={handleEdit}
      />
    </AppShell>
  );
}

// ── Employee detail panel ──────────────────────────────────────────────────────
function EmployeeDetail({ emp }: { emp: Employee }) {
  return (
    <>
      <SheetHeader>
        <SheetTitle className="flex items-center gap-2">
          <User className="size-5 text-muted-foreground" />
          {emp.name}
        </SheetTitle>
        <SheetDescription className="font-mono text-xs">
          {emp.employee_id} · {emp.designation}
        </SheetDescription>
      </SheetHeader>

      <div className="space-y-6 px-4 pb-8 pt-2">
        <div className="flex flex-wrap gap-2">
          <RiskBadge level={emp.risk_level} />
          <span className="inline-flex items-center gap-1.5 rounded-md border border-border bg-muted px-2 py-0.5 font-mono text-xs">
            Score: {emp.risk_score}
          </span>
        </div>

        <dl className="grid grid-cols-2 gap-4 text-sm">
          <Field label="Department" value={emp.department} />
          <Field label="Location" value={emp.location} />
          <Field label="Manager" value={emp.manager} />
          <Field label="Email" value={emp.email} mono />
          <Field label="Joined" value={formatTimestamp(emp.joined_at + "T00:00:00Z")} mono />
        </dl>

        {/* Reports to chain */}
        <div>
          <p className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
            Reporting chain
          </p>
          <div className="mt-2 rounded-md border border-border bg-surface p-3 text-sm">
            <div className="flex items-center gap-2">
              <Users className="size-4 text-muted-foreground" />
              <span>Reports to</span>
              <span className="font-medium">{emp.manager}</span>
            </div>
          </div>
        </div>
      </div>
    </>
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

// ── Shared employee form dialog ────────────────────────────────────────────────
type FormState = ReturnType<typeof emptyForm>;

function EmployeeFormDialog({
  open,
  onOpenChange,
  title,
  description,
  form,
  setForm,
  errors,
  saving,
  onSubmit,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  title: string;
  description: string;
  form: FormState;
  setForm: React.Dispatch<React.SetStateAction<FormState>>;
  errors: Record<string, string>;
  saving: boolean;
  onSubmit: () => void;
}) {
  function field(key: keyof FormState) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 sm:grid-cols-2">
          <FormField label="Full name" error={errors.name}>
            <Input placeholder="Jane Smith" value={form.name} onChange={field("name")} />
          </FormField>
          <FormField label="Work email" error={errors.email}>
            <Input placeholder="jane@northwind.co" value={form.email} onChange={field("email")} />
          </FormField>
          <FormField label="Designation" error={errors.designation}>
            <Input placeholder="Senior Analyst" value={form.designation} onChange={field("designation")} />
          </FormField>
          <FormField label="Location" error={errors.location}>
            <Input placeholder="London, UK" value={form.location} onChange={field("location")} />
          </FormField>

          <FormField label="Department">
            <Select value={form.department} onValueChange={(v) => setForm((p) => ({ ...p, department: v }))}>
              <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                {departments.map((d) => <SelectItem key={d} value={d}>{d}</SelectItem>)}
              </SelectContent>
            </Select>
          </FormField>

          <FormField label="Manager">
            <Select value={form.manager} onValueChange={(v) => setForm((p) => ({ ...p, manager: v }))}>
              <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                {managers.map((m) => <SelectItem key={m} value={m}>{m}</SelectItem>)}
              </SelectContent>
            </Select>
          </FormField>

          <FormField label="Risk level">
            <Select value={form.risk_level} onValueChange={(v) => setForm((p) => ({ ...p, risk_level: v as RiskLevel }))}>
              <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                {riskLevels.map((r) => <SelectItem key={r} value={r}>{r}</SelectItem>)}
              </SelectContent>
            </Select>
          </FormField>

          <FormField label="Risk score (0–100)" error={errors.risk_score}>
            <Input
              type="number"
              min={0}
              max={100}
              value={form.risk_score}
              onChange={(e) => setForm((p) => ({ ...p, risk_score: Number(e.target.value) }))}
            />
          </FormField>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={saving}>
            Cancel
          </Button>
          <Button onClick={onSubmit} disabled={saving}>
            {saving ? "Saving…" : "Save"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function FormField({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <Label className="text-sm">{label}</Label>
      {children}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
