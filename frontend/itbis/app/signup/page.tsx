"use client";

import { useState, FormEvent, useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Shield, Lock, Mail, UserCheck, Eye, EyeOff, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";
import { api } from "@/lib/api";

const ROLES = [
  { value: "security_analyst", label: "Security Analyst (Default)" },
  { value: "soc_engineer", label: "SOC Engineer" },
  { value: "security_manager", label: "Security Manager" },
  { value: "admin", label: "System Administrator" },
];

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [role, setRole] = useState("security_analyst");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Password strength calculation
  const strength = useMemo(() => {
    if (!password) return { score: 0, label: "None", color: "bg-slate-700" };
    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;

    if (score <= 1) return { score: 1, label: "Weak", width: "w-1/4", color: "bg-slate-500" };
    if (score === 2) return { score: 2, label: "Fair", width: "w-2/4", color: "bg-[#00A8FF]/60" };
    if (score === 3) return { score: 3, label: "Good", width: "w-3/4", color: "bg-[#00A8FF]" };
    return { score: 4, label: "Strong (SOC Compliant)", width: "w-full", color: "bg-[#00E5FF]" };
  }, [password]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email.trim()) {
      setError("Email address is required.");
      return;
    }

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match. Please verify.");
      return;
    }

    setLoading(true);

    try {
      const response = await api.post("/auth/signup", {
        email: email.trim(),
        password: password,
        role: role,
      });

      if (response.status === 201 || response.data?.message) {
        setSuccess(true);
        setTimeout(() => {
          router.push("/login");
        }, 1500);
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } }; message?: string };
      if (axiosErr.response) {
        if (axiosErr.response.status === 400) {
          setError("Email already registered in ITBIS system.");
        } else if (axiosErr.response.data?.detail) {
          setError(typeof axiosErr.response.data.detail === "string" ? axiosErr.response.data.detail : "Registration failed.");
        } else {
          setError("Server rejected registration request.");
        }
      } else {
        setError("Security server is currently unavailable. Please verify backend service connection.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050B14] flex flex-col items-center justify-center p-4 selection:bg-[#00A8FF]/30 selection:text-[#00E5FF]">
      {/* Background Cyber Grid Lines */}
      <div className="fixed inset-0 pointer-events-none opacity-20 bg-[linear-gradient(to_right,#0B1626_1px,transparent_1px),linear-gradient(to_bottom,#0B1626_1px,transparent_1px)] bg-[size:4rem_4rem]" />

      <div className="relative w-full max-w-md my-8">
        {/* Top Glow Accent */}
        <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-48 h-1 bg-gradient-to-r from-transparent via-[#00A8FF] to-transparent rounded-full opacity-70 blur-[1px]" />

        <div className="bg-[#0B1626] border border-[#132B45] rounded-xl p-8 shadow-2xl shadow-[#00A8FF]/5 relative">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#050B14] border border-[#132B45] text-[#00A8FF] mb-4 shadow-inner">
              <Shield className="w-6 h-6 text-[#00A8FF]" />
            </div>
            <h1 className="text-2xl font-black tracking-wider text-[#F4F8FF] uppercase">
              ITBIS
            </h1>
            <p className="text-xs font-semibold tracking-widest text-[#00E5FF] uppercase mt-1">
              Operator Enrollment
            </p>
            <p className="text-xs text-[#8E9EB5] mt-2">
              Register an authorized security operations profile.
            </p>
          </div>

          {/* Status Alerts */}
          {error && (
            <div className="mb-6 p-3.5 rounded-lg bg-[#050B14] border border-cyan-900/60 text-cyan-200 text-xs flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-[#00E5FF] shrink-0 mt-0.5" />
              <div className="flex-1">
                <span className="font-semibold text-[#00E5FF]">Registration Notice: </span>
                <span>{error}</span>
              </div>
            </div>
          )}

          {success && (
            <div className="mb-6 p-3.5 rounded-lg bg-[#050B14] border border-cyan-500/50 text-[#00E5FF] text-xs flex items-center gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-[#00E5FF] shrink-0" />
              <div>
                <p className="font-semibold">Account created successfully</p>
                <p className="text-[11px] text-[#8E9EB5]">Redirecting to authentication console...</p>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-[#8E9EB5] uppercase tracking-wider mb-2">
                Operator Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#8E9EB5]">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@security.itbis"
                  required
                  disabled={loading || success}
                  className="w-full pl-10 pr-4 py-2.5 bg-[#050B14] border border-[#132B45] rounded-lg text-sm text-[#F4F8FF] placeholder-[#8E9EB5]/40 focus:outline-none focus:border-[#00A8FF] focus:ring-1 focus:ring-[#00A8FF] transition disabled:opacity-50"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#8E9EB5] uppercase tracking-wider mb-2">
                Security Role Assignment
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#8E9EB5]">
                  <UserCheck className="w-4 h-4" />
                </div>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  disabled={loading || success}
                  className="w-full pl-10 pr-4 py-2.5 bg-[#050B14] border border-[#132B45] rounded-lg text-sm text-[#F4F8FF] focus:outline-none focus:border-[#00A8FF] focus:ring-1 focus:ring-[#00A8FF] transition disabled:opacity-50 appearance-none cursor-pointer"
                >
                  {ROLES.map((r) => (
                    <option key={r.value} value={r.value} className="bg-[#0B1626] text-[#F4F8FF]">
                      {r.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#8E9EB5] uppercase tracking-wider mb-2">
                Access Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#8E9EB5]">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min. 8 characters"
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

              {/* Password Strength Meter */}
              {password && (
                <div className="mt-2">
                  <div className="flex justify-between text-[11px] text-[#8E9EB5] mb-1">
                    <span>Password Strength</span>
                    <span className="font-mono text-[#00E5FF]">{strength.label}</span>
                  </div>
                  <div className="w-full h-1.5 bg-[#050B14] rounded-full overflow-hidden border border-[#132B45]">
                    <div
                      className={`h-full ${strength.color} ${strength.width} transition-all duration-300`}
                    />
                  </div>
                </div>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#8E9EB5] uppercase tracking-wider mb-2">
                Confirm Access Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#8E9EB5]">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter password"
                  required
                  disabled={loading || success}
                  className="w-full pl-10 pr-4 py-2.5 bg-[#050B14] border border-[#132B45] rounded-lg text-sm text-[#F4F8FF] placeholder-[#8E9EB5]/40 focus:outline-none focus:border-[#00A8FF] focus:ring-1 focus:ring-[#00A8FF] transition disabled:opacity-50"
                />
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
                  <span>Enrolling Operator...</span>
                </>
              ) : (
                <span>Register Operator</span>
              )}
            </button>
          </form>

          {/* Footer Link */}
          <div className="mt-8 pt-6 border-t border-[#132B45] text-center text-xs text-[#8E9EB5]">
            Already authorized?{" "}
            <Link
              href="/login"
              className="font-semibold text-[#00A8FF] hover:text-[#00E5FF] transition underline underline-offset-4"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
