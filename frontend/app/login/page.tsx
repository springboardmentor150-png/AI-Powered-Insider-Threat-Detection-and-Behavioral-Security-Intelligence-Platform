"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import ThemeToggle from "@/components/ThemeToggle";
import api from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login", null, {
        params: {
          email,
          password,
        },
      });

      // Store JWT token
      localStorage.setItem(
        "itbis-token",
        response.data.access_token
      );

      // Store basic user information
      localStorage.setItem(
        "itbis-user",
        JSON.stringify({
          user_id: response.data.user_id,
          email: response.data.email,
          role: response.data.role,
        })
      );

      // Redirect after successful login
      router.push("/dashboard");
    } catch (error: any) {
      setError(
        error.response?.data?.detail ||
          "Login failed. Please check your credentials."
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
                  <h1 className="text-2xl font-bold tracking-tight">
                    ITBIS
                  </h1>

                  <p className="text-xs text-[var(--muted)]">
                    Security Intelligence Platform
                  </p>
                </div>
              </div>
            </div>

            <ThemeToggle />
          </div>

          {/* Login Card */}
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--card)] p-8 shadow-2xl">

            <div className="mb-7">
              <h2 className="text-2xl font-semibold">
                Welcome back
              </h2>

              <p className="mt-2 text-sm text-[var(--muted)]">
                Sign in to access the ITBIS security console.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">

              {/* Email */}
              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-sm font-medium"
                >
                  Email address
                </label>

                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="analyst@company.com"
                  required
                  className="w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm outline-none transition focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                />
              </div>

              {/* Password */}
              <div>
                <label
                  htmlFor="password"
                  className="mb-2 block text-sm font-medium"
                >
                  Password
                </label>

                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
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
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>

            {/* Security indicator */}
            <div className="mt-6 flex items-center justify-center gap-2 text-xs text-[var(--muted)]">
              <span className="h-2 w-2 rounded-full bg-[var(--success)]" />
              Secure authentication enabled
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