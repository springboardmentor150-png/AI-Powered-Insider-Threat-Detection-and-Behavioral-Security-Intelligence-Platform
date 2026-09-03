"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

const ROLES = [
  {
    value: "security_analyst",
    label: "Security Analyst",
  },
  {
    value: "soc_engineer",
    label: "SOC Engineer",
  },
  {
    value: "security_manager",
    label: "Security Manager",
  },
  {
    value: "admin",
    label: "Administrator",
  },
];

export default function SignupPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [role, setRole] = useState("security_analyst");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [showPassword, setShowPassword] =
    useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (password.length < 8) {
      setError(
        "Password must contain at least 8 characters."
      );
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await api.post("/auth/signup", {
        email: email.trim(),
        password,
        role,
      });

      setSuccess(
        "Account created successfully. Redirecting to login..."
      );

      setTimeout(() => {
        router.push("/login");
      }, 1200);
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        "Unable to create account.";

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
            Create your account
          </h1>

          <p className="text-slate-500 mt-2">
            Join the ITBIS security platform.
          </p>
        </div>

        {/* Signup Card */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-7">

          {error && (
            <div className="mb-5 rounded-lg border border-red-200 bg-red-50 px-4 py-3">
              <p className="text-sm text-red-600">
                {error}
              </p>
            </div>
          )}

          {success && (
            <div className="mb-5 rounded-lg border border-green-200 bg-green-50 px-4 py-3">
              <p className="text-sm text-green-700">
                {success}
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

            {/* Role */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Platform role
              </label>

              <select
                value={role}
                onChange={(event) =>
                  setRole(event.target.value)
                }
                className="w-full border border-slate-200 rounded-lg px-4 py-3 bg-white outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
              >
                {ROLES.map((item) => (
                  <option
                    key={item.value}
                    value={item.value}
                  >
                    {item.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Password
              </label>

              <div className="relative">
                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Create a password"
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  required
                  autoComplete="new-password"
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

              <p className="text-xs text-slate-400 mt-2">
                Use at least 8 characters.
              </p>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Confirm password
              </label>

              <div className="relative">
                <input
                  type={
                    showConfirmPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(event.target.value)
                  }
                  required
                  autoComplete="new-password"
                  className="w-full border border-slate-200 rounded-lg px-4 py-3 pr-16 outline-none transition focus:border-slate-400 focus:ring-2 focus:ring-slate-100"
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowConfirmPassword(
                      (current) => !current
                    )
                  }
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-sm font-medium text-slate-500 hover:text-slate-900"
                >
                  {showConfirmPassword
                    ? "Hide"
                    : "Show"}
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
                ? "Creating account..."
                : "Create Account"}
            </button>
          </form>

          {/* Login */}
          <div className="border-t border-slate-200 mt-6 pt-6 text-center">
            <p className="text-sm text-slate-500">
              Already have an account?{" "}
              <Link
                href="/login"
                className="font-semibold text-blue-600 hover:text-blue-700"
              >
                Sign in
              </Link>
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