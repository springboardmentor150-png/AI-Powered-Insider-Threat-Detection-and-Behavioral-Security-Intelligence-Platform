"use client";

import { useState, useEffect, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Shield,
  Lock,
  Mail,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
  Loader2,
  KeyRound,
  ArrowRight,
} from "lucide-react";
import { api, getApiBaseUrl } from "@/lib/api";
import { setAuthSession, isAuthenticated } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [forgotNotice, setForgotNotice] = useState(false);

  // If already authenticated, redirect straight to SOC console
  useEffect(() => {
    if (isAuthenticated()) {
      router.push("/dashboard");
    }
  }, [router]);

  // Quick-fill helper for registered accounts
  const fillCredentials = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setForgotNotice(false);

    if (!email.trim() || !password) {
      setError("Please enter both email and password.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/auth/login", {
        email: email.trim(),
        password: password,
      });

      if (response.data && response.data.access_token) {
        setAuthSession(response.data);
        setSuccess(true);
        setTimeout(() => {
          router.push("/dashboard");
        }, 500);
      } else {
        setError("Invalid response received from security authentication server.");
      }
    } catch (err: unknown) {
      const axiosErr = err as {
        response?: { status?: number; data?: { detail?: string } };
        message?: string;
      };
      if (axiosErr.response) {
        if (axiosErr.response.status === 401) {
          setError("Invalid email or password. Please verify your credentials.");
        } else if (axiosErr.response.data?.detail) {
          setError(
            typeof axiosErr.response.data.detail === "string"
              ? axiosErr.response.data.detail
              : "Authentication failed."
          );
        } else {
          setError("Authentication service rejected the login request.");
        }
      } else {
        setError(
          `Security backend is currently unreachable at ${getApiBaseUrl()}. Please verify backend service.`
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050B14] flex flex-col items-center justify-center p-4 selection:bg-[#00A8FF]/30 selection:text-[#00E5FF]">
      {/* Background Cyber Grid Lines */}
      <div className="fixed inset-0 pointer-events-none opacity-20 bg-[linear-gradient(to_right,#0B1626_1px,transparent_1px),linear-gradient(to_bottom,#0B1626_1px,transparent_1px)] bg-[size:4rem_4rem]" />

      <div className="relative w-full max-w-md">
        {/* Top Glow Accent */}
        <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-48 h-1 bg-gradient-to-r from-transparent via-[#00E5FF] to-transparent rounded-full opacity-70 blur-[1px]" />

        <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-8 shadow-2xl shadow-[#00A8FF]/5 relative">
          {/* Header */}
          <div className="text-center mb-6">
            <Link
              href="/"
              className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#050B14] border border-[#132B45] text-[#00E5FF] mb-3 shadow-inner hover:border-[#00A8FF] transition cursor-pointer"
            >
              <Shield className="w-6 h-6 text-[#00E5FF]" />
            </Link>
            <h1 className="text-2xl font-black tracking-wider text-[#F4F8FF] uppercase">
              ITBIS
            </h1>
            <p className="text-xs font-semibold tracking-widest text-[#00A8FF] uppercase mt-1">
              Security Operations Console
            </p>
            <p className="text-xs text-[#8E9EB5] mt-1.5">
              Enter authorized credentials to access SOC intelligence.
            </p>
          </div>

          {/* Quick-Fill Demo Pills */}
          <div className="mb-6 p-3 rounded-lg bg-[#050B14] border border-[#132B45] text-xs">
            <div className="flex items-center justify-between text-[10px] uppercase font-mono text-[#8E9EB5] mb-2">
              <span className="flex items-center gap-1">
                <KeyRound className="w-3 h-3 text-[#00E5FF]" /> Registered SOC Profiles:
              </span>
              <span>Click to auto-fill</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => fillCredentials("admin@itbis.cyber", "AdminPassword123!")}
                className="px-2.5 py-1.5 rounded bg-[#0B1626] hover:bg-[#132B45] border border-[#132B45] hover:border-[#00A8FF] text-[11px] text-left transition cursor-pointer flex flex-col"
              >
                <span className="font-bold text-[#F4F8FF]">Admin SOC</span>
                <span className="text-[10px] text-[#00E5FF] font-mono truncate">admin@itbis.cyber</span>
              </button>
              <button
                type="button"
                onClick={() => fillCredentials("analyst@itbis.cyber", "AnalystPassword123!")}
                className="px-2.5 py-1.5 rounded bg-[#0B1626] hover:bg-[#132B45] border border-[#132B45] hover:border-[#00A8FF] text-[11px] text-left transition cursor-pointer flex flex-col"
              >
                <span className="font-bold text-[#F4F8FF]">Analyst SOC</span>
                <span className="text-[10px] text-[#00A8FF] font-mono truncate">analyst@itbis.cyber</span>
              </button>
            </div>
          </div>

          {/* Status Alerts */}
          {error && (
            <div className="mb-6 p-3.5 rounded-lg bg-[#050B14] border border-cyan-900/60 text-cyan-200 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-[#00E5FF] shrink-0 mt-0.5" />
              <div className="flex-1">
                <span className="font-semibold text-[#00E5FF]">Access Alert: </span>
                <span>{error}</span>
              </div>
            </div>
          )}

          {success && (
            <div className="mb-6 p-3.5 rounded-lg bg-[#050B14] border border-cyan-500/50 text-[#00E5FF] text-xs flex items-center gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-[#00E5FF] shrink-0" />
              <span>Authentication approved. Redirecting to SOC console...</span>
            </div>
          )}

          {forgotNotice && (
            <div className="mb-6 p-3.5 rounded-lg bg-[#050B14] border border-[#132B45] text-[#8E9EB5] text-xs">
              <span className="text-[#00A8FF] font-semibold">Self-Service Reset Notice: </span>
              Please contact your Security Administrator to initiate an authorized credential recovery.
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#8E9EB5] uppercase tracking-wider mb-2">
                Operator Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#8E9EB5]">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@itbis.cyber"
                  required
                  disabled={loading || success}
                  className="w-full pl-10 pr-4 py-2.5 bg-[#050B14] border border-[#132B45] rounded-lg text-sm text-[#F4F8FF] placeholder-[#8E9EB5]/40 focus:outline-none focus:border-[#00A8FF] focus:ring-1 focus:ring-[#00A8FF] transition disabled:opacity-50"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-xs font-semibold text-[#8E9EB5] uppercase tracking-wider">
                  Access Key / Password
                </label>
                <button
                  type="button"
                  onClick={() => setForgotNotice(true)}
                  className="text-xs text-[#00A8FF] hover:text-[#00E5FF] transition cursor-pointer"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#8E9EB5]">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  disabled={loading || success}
                  className="w-full pl-10 pr-10 py-2.5 bg-[#050B14] border border-[#132B45] rounded-lg text-sm text-[#F4F8FF] placeholder-[#8E9EB5]/40 focus:outline-none focus:border-[#00A8FF] focus:ring-1 focus:ring-[#00A8FF] transition disabled:opacity-50"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-[#8E9EB5] hover:text-[#00E5FF] transition cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || success}
              className="w-full mt-6 py-2.5 px-4 bg-[#00A8FF] hover:bg-[#00E5FF] text-[#050B14] font-bold text-sm tracking-wide rounded-lg transition duration-200 flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-[#00A8FF]/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-[#050B14]" />
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4" />
                  <span>Sign In to SOC Console</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Footer Link */}
          <div className="mt-8 pt-6 border-t border-[#132B45] flex items-center justify-between text-xs text-[#8E9EB5]">
            <Link
              href="/"
              className="text-[#8E9EB5] hover:text-[#00E5FF] transition flex items-center gap-1"
            >
              ← Back to Welcome
            </Link>
            <div className="text-right">
              <span className="text-[#8E9EB5]/70">New Operator? </span>
              <Link
                href="/signup"
                className="font-semibold text-[#00A8FF] hover:text-[#00E5FF] transition underline underline-offset-4"
              >
                Sign up
              </Link>
            </div>
          </div>
        </div>

        {/* Console Meta Status */}
        <div className="mt-6 text-center text-[10px] text-[#8E9EB5]/60 flex items-center justify-center gap-4">
          <span>SEC PROTOCOL: TLS 1.3</span>
          <span>•</span>
          <span>AUTH: JWT RS256/HS256</span>
          <span>•</span>
          <span className="text-[#00E5FF]">SYSTEM OPERATIONAL</span>
        </div>
      </div>
    </div>
  );
}
