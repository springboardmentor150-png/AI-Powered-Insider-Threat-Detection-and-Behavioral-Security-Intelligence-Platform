import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { useEffect, useState, type ReactNode } from "react";
import {
  Activity,
  BellRing,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Settings,
  ShieldCheck,
  Sun,
  Users,
  UserCog,
} from "lucide-react";
import { ROLES, type Role } from "@/api/mockData";
import { canManageEmployees, isAdmin, useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { RoleBadge } from "@/components/status-badges";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

type NavItem = {
  label: string;
  to: string;
  icon: typeof LayoutDashboard;
  visible: (role: Role) => boolean;
};

const NAV: NavItem[] = [
  { label: "Dashboard", to: "/dashboard", icon: LayoutDashboard, visible: () => true },
  { label: "Employees", to: "/employees", icon: Users, visible: canManageEmployees },
  { label: "Activity Logs", to: "/activity-logs", icon: Activity, visible: () => true },
  { label: "Alerts", to: "/alerts", icon: BellRing, visible: () => true },
  { label: "User Management", to: "/users", icon: UserCog, visible: isAdmin },
  { label: "Settings", to: "/settings", icon: Settings, visible: () => true },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { session, ready, signOut, setRole } = useAuth();
  const { theme, toggle } = useTheme();
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (ready && !session) navigate({ to: "/" });
  }, [ready, session, navigate]);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  if (!ready || !session) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <p className="font-mono text-sm text-muted-foreground">Restoring session…</p>
      </div>
    );
  }

  const role = session.role;
  const items = NAV.filter((i) => i.visible(role));

  return (
    <div className="flex min-h-screen w-full bg-background">
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-sidebar-border bg-sidebar transition-transform lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-16 items-center gap-2.5 border-b border-sidebar-border px-5">
          <span className="flex size-8 items-center justify-center rounded-md bg-primary/15 text-primary">
            <ShieldCheck className="size-4.5" />
          </span>
          <div className="leading-tight">
            <p className="text-sm font-semibold tracking-tight text-sidebar-foreground">ITBIS</p>
            <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
              Threat Intelligence
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-3">
          {items.map(({ label, to, icon: Icon }) => {
            const active = pathname === to || pathname.startsWith(to + "/");
            return (
              <Link
                key={to}
                to={to}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground shadow-[inset_2px_0_0_0_var(--color-primary)]"
                    : "text-muted-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-foreground",
                )}
              >
                <Icon className="size-4" />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-sidebar-border p-4">
          <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
            Signed in as
          </p>
          <p className="truncate text-sm font-medium text-sidebar-foreground">{session.email}</p>
          <Button variant="ghost" size="sm" className="mt-3 w-full justify-start" onClick={signOut}>
            <LogOut className="size-4" /> Sign out
          </Button>
        </div>
      </aside>

      {mobileOpen ? (
        <button
          aria-label="Close navigation"
          className="fixed inset-0 z-30 bg-background/70 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      ) : null}

      <div className="flex min-w-0 flex-1 flex-col lg:pl-64">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-border bg-surface/85 px-4 backdrop-blur lg:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setMobileOpen(true)}
            aria-label="Open navigation"
          >
            <Menu className="size-5" />
          </Button>

          <div className="hidden items-center gap-2 sm:flex">
            <span className="size-2 animate-pulse rounded-full bg-low" />
            <span className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
              Monitoring live · 9 endpoints
            </span>
          </div>

          <div className="ml-auto flex items-center gap-2 sm:gap-3">
            <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
              {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
            </Button>

            <div className="hidden md:block">
              <RoleBadge role={role} />
            </div>

            <Select value={role} onValueChange={(v) => setRole(v as Role)}>
              <SelectTrigger className="w-[168px]" aria-label="Switch role">
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

            <div className="flex size-9 items-center justify-center rounded-full border border-border bg-primary/12 font-mono text-xs font-semibold text-primary">
              {session.email.slice(0, 2).toUpperCase()}
            </div>
          </div>
        </header>

        <main className="min-w-0 flex-1 px-4 py-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}
