"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api, { saveSession } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login", {
        email: email.trim(),
        password,
      });

      saveSession(
        response.data.access_token,
        response.data.role
      );

      router.push("/employees");
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        "Invalid email or password.";

      setError(
        Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : detail
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-80px)] flex items-center justify-center py-10">
      <div className="w-full max-w-md">

        {/* Branding */}
        <div className="text-center mb-7">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-slate-900 text-white text-xl font-bold shadow-lg">
            IT
          </div>

          <h1 className="text-3xl font-semibold text-slate-900 mt-4">
            Welcome back
          </h1>

          <p className="text-slate-500 mt-2">
            Sign in to your ITBIS security platform.
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-7">

          {error && (
            <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
              <p className="text-sm text-red-600">
                {error}
              </p>
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="space-y-5"
          >

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Email address
              </label>

              <input
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                required
                autoComplete="email"
                className="w-full border border-slate-200 rounded-lg px-4 py-3 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
              />
            </div>

            {/* Password */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-slate-700">
                  Password
                </label>
              </div>

              <div className="relative">
                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  required
                  autoComplete="current-password"
                  className="w-full border border-slate-200 rounded-lg px-4 py-3 pr-16 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowPassword((current) => !current)
                  }
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-sm font-medium text-slate-500 hover:text-slate-900"
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white rounded-lg py-3 font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading
                ? "Signing in..."
                : "Sign in"}
            </button>
          </form>

          {/* Signup */}
          <div className="border-t border-slate-200 mt-6 pt-6 text-center">
            <p className="text-sm text-slate-500">
              Don't have an account?{" "}
              <Link
                href="/signup"
                className="font-semibold text-blue-600 hover:text-blue-700"
              >
                Create Account
              </Link>
            </p>
          </div>
        </div>

        {/* Test Account */}
        <div className="mt-5 bg-slate-50 border border-slate-200 rounded-xl p-5">
          <p className="text-sm font-semibold text-slate-800">
            Test Account
          </p>

          <div className="mt-2 space-y-1 text-sm text-slate-500">
            <p>
              <span className="font-medium text-slate-700">
                Email:
              </span>{" "}
              admin1@company.com
            </p>

            <p>
              <span className="font-medium text-slate-700">
                Password:
              </span>{" "}
              SecurePass123
            </p>
          </div>
        </div>

        {/* Security note */}
        <p className="text-center text-xs text-slate-400 mt-5">
          Authorized ITBIS personnel only
        </p>

      </div>
    </div>
  );
}