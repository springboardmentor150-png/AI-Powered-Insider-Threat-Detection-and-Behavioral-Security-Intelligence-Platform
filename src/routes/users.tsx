import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Plus, ShieldX } from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "@/api/client";
import { formatTimestamp, ROLES, type PlatformUser, type Role } from "@/api/mockData";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { RoleBadge, UserStatusBadge } from "@/components/status-badges";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { isAdmin, useAuth } from "@/lib/auth";

export const Route = createFileRoute("/users")({
  head: () => ({
    meta: [
      { title: "User Management — ITBIS" },
      {
        name: "description",
        content:
          "Administer ITBIS console accounts: invite users, assign SOC roles and review account status.",
      },
      { property: "og:title", content: "User Management — ITBIS" },
      { property: "og:description", content: "Invite and manage ITBIS console accounts." },
    ],
  }),
  component: UsersPage,
});

function UsersPage() {
  const { session } = useAuth();
  const [users, setUsers] = useState<PlatformUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("Security Analyst");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const isAdminUser = isAdmin(session?.role);

  useEffect(() => {
    if (!isAdminUser) { setLoading(false); return; }
    apiClient.getPlatformUsers().then(setUsers).finally(() => setLoading(false));
  }, [isAdminUser]);

  if (!isAdminUser) {
    return (
      <AppShell>
        <AccessDenied />
      </AppShell>
    );
  }

  async function invite() {
    if (!email.includes("@")) { setError("Enter a valid email address."); return; }
    if (!password || password.length < 8) { setError("Password must be at least 8 characters."); return; }
    setSaving(true);
    setError(null);
    try {
      const created = await apiClient.createPlatformUser({ email: email.trim(), password, role });
      setUsers((prev) => [created, ...prev]);
      toast.success(`User ${email.trim()} created.`);
      setEmail("");
      setPassword("");
      setRole("Security Analyst");
      setOpen(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create user.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <PageHeader
        title="User Management"
        description="Console login accounts. These are platform users, not monitored employees."
        actions={
          <Button onClick={() => { setEmail(""); setPassword(""); setError(null); setOpen(true); }}>
            <Plus className="size-4" /> Invite User
          </Button>
        }
      />

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <p className="py-10 text-center font-mono text-sm text-muted-foreground">Loading…</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last login</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((u) => (
                  <TableRow key={u.id}>
                    <TableCell className="font-medium">{u.email}</TableCell>
                    <TableCell>
                      <RoleBadge role={u.role} />
                    </TableCell>
                    <TableCell>
                      <UserStatusBadge status={u.status} />
                    </TableCell>
                    <TableCell className="whitespace-nowrap font-mono text-xs text-muted-foreground">
                      {formatTimestamp(u.last_login)}
                    </TableCell>
                  </TableRow>
                ))}
                {users.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} className="py-10 text-center text-muted-foreground">
                      No users found.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Invite user</DialogTitle>
            <DialogDescription>
              Create a console account with the selected SOC role.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="invite-email">Email</Label>
              <Input
                id="invite-email"
                placeholder="new.analyst@northwind.co"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={saving}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite-password">Password</Label>
              <Input
                id="invite-password"
                type="password"
                placeholder="Min. 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={saving}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite-role">Role</Label>
              <Select value={role} onValueChange={(v) => setRole(v as Role)} disabled={saving}>
                <SelectTrigger id="invite-role" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ROLES.map((r) => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)} disabled={saving}>
              Cancel
            </Button>
            <Button onClick={invite} disabled={saving}>
              {saving ? "Creating…" : "Create user"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}

export function AccessDenied() {
  return (
    <Card className="mx-auto max-w-md">
      <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
        <span className="flex size-11 items-center justify-center rounded-md bg-critical/15 text-critical">
          <ShieldX className="size-5" />
        </span>
        <h2 className="text-lg font-semibold">Access restricted</h2>
        <p className="max-w-xs text-sm text-muted-foreground">
          Your current role does not have permission to view this section. Switch roles from the top
          bar to preview it.
        </p>
      </CardContent>
    </Card>
  );
}
