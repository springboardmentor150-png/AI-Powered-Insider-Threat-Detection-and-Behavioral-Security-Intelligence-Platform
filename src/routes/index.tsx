import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Loader2, ShieldCheck, TriangleAlert } from "lucide-react";
import { ROLES, type Role } from "@/api/mockData";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Sign in — ITBIS Insider Threat Console" },
      {
        name: "description",
        content:
          "Sign in to ITBIS, the insider threat behavioral intelligence console for security analysts, SOC engineers and security managers.",
      },
      { property: "og:title", content: "Sign in — ITBIS Insider Threat Console" },
      {
        property: "og:description",
        content: "Access the ITBIS security operations console for insider threat monitoring.",
      },
    ],
  }),
  component: LoginPage,
});

const HAS_BACKEND =
  (import.meta.env.VITE_API_URL as string | undefined) !== undefined &&
  (import.meta.env.VITE_API_URL as string).length > 0;

function LoginPage() {
  const { session, ready, signIn } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("Security Analyst");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    if (ready && session) navigate({ to: "/dashboard" });
  }, [ready, session, navigate]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("Enter both an email address and a password to continue.");
      return;
    }
    if (!email.includes("@")) {
      setError("Invalid credentials. Use a valid email address format.");
      return;
    }
    setError(null);
    setPending(true);
    try {
      await signIn(email.trim(), password, role);
      navigate({ to: "/dashboard" });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Sign-in failed. Please try again.";
      setError(msg);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-4 py-10">
      <div className="grid-backdrop absolute inset-0 opacity-60" aria-hidden />
      <div
        className="absolute -top-40 left-1/2 size-[36rem] -translate-x-1/2 rounded-full bg-primary/12 blur-3xl"
        aria-hidden
      />

      <div className="relative w-full max-w-[26rem]">
        <div className="mb-7 flex items-center gap-3">
          <span className="flex size-11 items-center justify-center rounded-lg bg-primary/15 text-primary">
            <ShieldCheck className="size-6" />
          </span>
          <div>
            <p className="text-lg font-semibold tracking-tight">ITBIS</p>
            <p className="font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
              Insider Threat Behavioral Intelligence
            </p>
          </div>
        </div>

        <div className="panel p-6">
          <h1 className="text-xl font-semibold tracking-tight">Sign in to the console</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Authenticate to access live behavioural telemetry.
          </p>

          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <div className="space-y-2">
              <Label htmlFor="email">Work email</Label>
              <Input
                id="email"
                type="text"
                autoComplete="username"
                placeholder="analyst@northwind.co"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={pending}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={pending}
              />
            </div>

            {/* Role selector only shown in mock mode — backend determines role from DB */}
            {!HAS_BACKEND && (
              <div className="space-y-2">
                <Label htmlFor="role">Sign in as</Label>
                <Select value={role} onValueChange={(v) => setRole(v as Role)}>
                  <SelectTrigger id="role" className="w-full">
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
            )}

            {error ? (
              <div className="flex items-start gap-2 rounded-md border border-destructive/45 bg-destructive/12 px-3 py-2 text-sm text-destructive">
                <TriangleAlert className="mt-0.5 size-4 shrink-0" />
                <span>{error}</span>
              </div>
            ) : null}

            <Button type="submit" className="w-full" disabled={pending}>
              {pending ? <Loader2 className="size-4 animate-spin" /> : null}
              Sign In
            </Button>
          </form>

          {HAS_BACKEND ? (
            <p className="mt-5 text-xs leading-relaxed text-muted-foreground">
              Use your registered console credentials to sign in.
            </p>
          ) : (
            <div className="mt-5 space-y-1 rounded-md border border-border bg-muted/40 px-3 py-2">
              <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
                Demo credentials (mock mode)
              </p>
              <p className="font-mono text-xs text-muted-foreground">any email · any password</p>
            </div>
          )}
        </div>

        <p className="mt-4 text-center font-mono text-[11px] uppercase tracking-widest text-muted-foreground">
          {HAS_BACKEND ? "Live backend · JWT auth" : "Demo mode · mock authentication"}
        </p>
      </div>
    </div>
  );
}
