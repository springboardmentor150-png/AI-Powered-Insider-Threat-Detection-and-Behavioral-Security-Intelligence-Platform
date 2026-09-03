import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Plus, ShieldX } from "lucide-react";
import { toast } from "sonner";
import { api, formatTimestamp, ROLES, type PlatformUser, type Role } from "@/api/mockData";
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
  const [users, setUsers] = useState<PlatformUser[]>(api.getPlatformUsers());
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<Role>("Security Analyst");
  const [error, setError] = useState<string | null>(null);

  if (!isAdmin(session?.role)) {
    return (
      <AppShell>
        <AccessDenied />
      </AppShell>
    );
  }

  function invite() {
    if (!email.includes("@")) {
      setError("Enter a valid email address.");
      return;
    }
    setUsers((prev) => [
      {
        id: `USR-${String(prev.length + 1).padStart(2, "0")}`,
        email: email.trim(),
        role,
        status: "Invited",
        last_login: "—",
      },
      ...prev,
    ]);
    toast.success(`Invitation sent to ${email.trim()}`);
    setEmail("");
    setRole("Security Analyst");
    setError(null);
    setOpen(false);
  }

  return (
    <AppShell>
      <PageHeader
        title="User Management"
        description="Console login accounts. These are platform users, not monitored employees."
        actions={
          <Button onClick={() => setOpen(true)}>
            <Plus className="size-4" /> Invite User
          </Button>
        }
      />

      <Card>
        <CardContent className="p-0">
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
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Invite user</DialogTitle>
            <DialogDescription>
              The invited user receives console access with the selected SOC role.
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
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite-role">Role</Label>
              <Select value={role} onValueChange={(v) => setRole(v as Role)}>
                <SelectTrigger id="invite-role" className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ROLES.map((r) => (
                    <SelectItem key={r} value={r}>
                      {r}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={invite}>Send invite</Button>
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
