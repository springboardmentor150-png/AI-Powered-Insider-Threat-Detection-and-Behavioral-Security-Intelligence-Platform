"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import ThemeToggle from "@/components/ThemeToggle";
import api from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("security_analyst");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/auth/signup", {
        email,
        password,
        role,
      });

      // If token is returned, automatically store and authenticate
      if (response.data.access_token) {
        localStorage.setItem("itbis-token", response.data.access_token);
        localStorage.setItem(
          "itbis-user",
          JSON.stringify({
            user_id: response.data.user_id,
            email: response.data.email,
            role: response.data.role,
          })
        );
        router.push("/dashboard");
      } else {
        // Fallback: navigate to login
        router.push("/login?registered=true");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Registration failed. Please try a different email or try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <div className="flex min-h-screen items-center justify-center p-6">
        <div className="w-full max-w-md">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--primary)] font-bold text-white">
                  I
                </div>
                <div>
                  <h1 className="text-2xl font-bold tracking-tight">ITBIS</h1>
                  <p className="text-xs text-[var(--muted)]">
                    Security Intelligence Platform
                  </p>
                </div>
              </div>
            </div>
            <ThemeToggle />
          </div>

          {/* Signup Card */}
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-8 shadow-2xl">
            <div className="mb-7">
              <h2 className="text-2xl font-semibold">Create an account</h2>
              <p className="mt-2 text-sm text-[var(--muted)]">
                Register for authorized security console access.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div>
                <label
                  htmlFor="email"
                  className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-[var(--muted)]"
                >
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@company.com"
                  required
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                />
              </div>

              {/* Role Selection */}
              <div>
                <label
                  htmlFor="role"
                  className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-[var(--muted)]"
                >
                  Operational Role
                </label>
                <select
                  id="role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                >
                  <option value="security_analyst">Security Analyst (Threat Investigation)</option>
                  <option value="soc_engineer">SOC Engineer (Operations & Feeds)</option>
                  <option value="security_manager">Security Manager (Risk & Governance)</option>
                </select>
              </div>

              {/* Password */}
              <div>
                <label
                  htmlFor="password"
                  className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-[var(--muted)]"
                >
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create a strong password"
                  required
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                />
              </div>

              {/* Confirm Password */}
              <div>
                <label
                  htmlFor="confirm-password"
                  className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-[var(--muted)]"
                >
                  Confirm Password
                </label>
                <input
                  id="confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter your password"
                  required
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                />
              </div>

              {/* Error message */}
              {error && (
                <div className="rounded-xl border border-[var(--danger)]/30 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger)]">
                  {error}
                </div>
              )}

              {/* Submit button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-[var(--primary)] px-5 py-3 font-semibold text-white transition hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Creating account..." : "Sign up"}
              </button>
            </form>

            {/* Link to login */}
            <div className="mt-6 text-center text-xs text-[var(--muted)]">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-semibold text-[var(--primary)] hover:underline"
              >
                Sign in
              </Link>
            </div>
          </div>

          <p className="mt-6 text-center text-xs text-[var(--muted)]">
            ITBIS • Insider Threat Behavioral Intelligence System
          </p>
        </div>
      </div>
    </main>
  );
}
