import { createFileRoute } from "@tanstack/react-router";
import { Moon, Sun } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { PageHeader } from "@/components/page-header";
import { RoleBadge } from "@/components/status-badges";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings — ITBIS" },
      {
        name: "description",
        content: "Manage ITBIS console appearance, detection preferences and session details.",
      },
      { property: "og:title", content: "Settings — ITBIS" },
      { property: "og:description", content: "Console appearance and detection preferences." },
    ],
  }),
  component: SettingsPage,
});

function SettingsPage() {
  const { session, signOut } = useAuth();
  const { theme, toggle } = useTheme();

  return (
    <AppShell>
      <PageHeader
        title="Settings"
        description="Console preferences for this workstation. Detection tuning is mocked in the demo."
      />

      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Appearance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3">
              <div className="flex items-center gap-3">
                {theme === "dark" ? <Moon className="size-4" /> : <Sun className="size-4" />}
                <div>
                  <p className="text-sm font-medium">
                    {theme === "dark" ? "Dark theme" : "Light theme"}
                  </p>
                  <p className="text-xs text-muted-foreground">Dark is the SOC default.</p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={toggle}>
                Switch
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Session</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Signed in as</span>
              <span className="font-medium">{session?.email}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Active role</span>
              {session ? <RoleBadge role={session.role} /> : null}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Auth mode</span>
              <span className="font-mono text-xs">mock / local</span>
            </div>
            <Button variant="outline" size="sm" onClick={signOut}>
              Sign out
            </Button>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Detection preferences</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              ["usb", "Alert on unregistered USB mass storage", true],
              ["egress", "Alert on unsanctioned egress channels", true],
              ["hours", "Flag off-baseline working hours", true],
              ["digest", "Email me a daily risk digest", false],
            ].map(([id, label, on]) => (
              <div
                key={id as string}
                className="flex items-center justify-between rounded-md border border-border bg-surface px-4 py-3"
              >
                <Label htmlFor={id as string} className="text-sm font-normal">
                  {label as string}
                </Label>
                <Switch id={id as string} defaultChecked={on as boolean} />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
