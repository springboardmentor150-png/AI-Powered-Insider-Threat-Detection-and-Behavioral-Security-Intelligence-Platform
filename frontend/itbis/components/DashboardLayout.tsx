"use client";

import { useEffect, useState, useRef, ReactNode } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Shield,
  LayoutDashboard,
  Users,
  Activity,
  BrainCircuit,
  AlertTriangle,
  FileText,
  Sliders,
  LogOut,
  Search,
  Bell,
  CheckCircle2,
  TrendingUp,
  ShieldAlert,
  Menu,
  X,
  User as UserIcon,
  Search as SearchIcon,
  Sun,
  Moon,
  Laptop,
  Check,
  Compass,
  FileSearch,
} from "lucide-react";
import { getAuthUser, isAuthenticated, clearAuthSession, AuthUser } from "@/lib/auth";
import { api } from "@/lib/api";

interface DashboardLayoutProps {
  children: ReactNode;
  pageTitle?: string;
  pageSubtitle?: string;
}

const NAV_ITEMS = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Employees", href: "/employees", icon: Users },
  { name: "Activity Logs", href: "/activity-logs", icon: Activity },
  { name: "Behavior Analysis", href: "/behavior-analysis", icon: BrainCircuit },
  { name: "Risk Scores", href: "/risk-scores", icon: TrendingUp },
  { name: "Investigation Center", href: "/investigations", icon: FileSearch },
  { name: "Alerts", href: "/alerts", icon: AlertTriangle },
  { name: "Incidents", href: "/incidents", icon: ShieldAlert },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "Settings", href: "/settings", icon: Sliders },
];

export default function DashboardLayout({
  children,
  pageTitle = "Security Overview",
  pageSubtitle = "Insider Threat Behavioral Intelligence Telemetry",
}: DashboardLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [openAlertCount, setOpenAlertCount] = useState<number>(0);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showNotifMenu, setShowNotifMenu] = useState(false);

  // Global Search State
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // Theme State
  const [theme, setTheme] = useState<"dark" | "light" | "system">("dark");
  const [showThemeMenu, setShowThemeMenu] = useState(false);

  useEffect(() => {
    // 1. Check Auth
    if (!isAuthenticated()) {
      router.push("/login");
    } else {
      setUser(getAuthUser());
      setCheckingAuth(false);
      fetchLiveCounts();
    }

    // 2. Load Persisted Theme
    const savedTheme = (localStorage.getItem("itbis_theme") as "dark" | "light" | "system") || "dark";
    setTheme(savedTheme);
    applyTheme(savedTheme);
  }, [router]);

  const applyTheme = (t: "dark" | "light" | "system") => {
    const root = document.documentElement;
    if (t === "light") {
      root.classList.add("light-theme");
    } else if (t === "dark") {
      root.classList.remove("light-theme");
    } else {
      // System default
      if (window.matchMedia("(prefers-color-scheme: light)").matches) {
        root.classList.add("light-theme");
      } else {
        root.classList.remove("light-theme");
      }
    }
  };

  const handleSetTheme = (newTheme: "dark" | "light" | "system") => {
    setTheme(newTheme);
    localStorage.setItem("itbis_theme", newTheme);
    applyTheme(newTheme);
    setShowThemeMenu(false);
  };

  const fetchLiveCounts = async () => {
    try {
      const [sumRes, notifRes] = await Promise.all([
        api.get("/dashboard/summary").catch(() => null),
        api.get("/notifications").catch(() => null),
      ]);
      if (sumRes?.data) {
        setOpenAlertCount(sumRes.data.open_alerts || 0);
      }
      if (notifRes?.data) {
        setNotifications(notifRes.data);
      }
    } catch {
      // safe fallback
    }
  };

  // Global search trigger
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setShowSearchDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      setSearchLoading(true);
      try {
        const res = await api.get(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
        setSearchResults(res.data.results || []);
        setShowSearchDropdown(true);
      } catch (err) {
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Click outside to close search dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    clearAuthSession();
    router.push("/login");
  };

  const markNotificationRead = async (id: number) => {
    try {
      await api.patch(`/notifications/${id}/read`);
      setNotifications((prev) => prev.filter((n) => n.id !== id));
    } catch {}
  };

  const markAllNotificationsRead = async () => {
    try {
      await api.patch("/notifications/mark-all-read");
      setNotifications([]);
      setShowNotifMenu(false);
    } catch {}
  };

  if (checkingAuth) {
    return (
      <div className="min-h-screen bg-[#050B14] flex flex-col items-center justify-center space-y-4">
        <div className="w-10 h-10 border-2 border-[#00E5FF] border-t-transparent rounded-full animate-spin"></div>
        <p className="text-xs uppercase tracking-widest text-[#00A8FF]">
          Authenticating Security Credentials...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] flex flex-col md:flex-row font-sans selection:bg-[#00A8FF]/30 selection:text-[#00E5FF]">
      {/* Background Cyber Pattern */}
      <div className="fixed inset-0 pointer-events-none opacity-15 bg-[linear-gradient(to_right,#0B1626_1px,transparent_1px),linear-gradient(to_bottom,#0B1626_1px,transparent_1px)] bg-[size:4rem_4rem]" />

      {/* Mobile Top Header */}
      <div className="md:hidden flex items-center justify-between p-4 bg-[var(--panel)] border-b border-[var(--panel-border)] z-30">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-[#00E5FF]" />
          <span className="font-bold tracking-wider text-sm">ITBIS SOC</span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 text-[var(--text-muted)] hover:text-[#00E5FF]"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Sidebar Navigation */}
      <aside
        className={`fixed md:sticky top-0 inset-y-0 left-0 w-64 bg-[var(--panel)] border-r border-[var(--panel-border)] flex flex-col justify-between z-40 transition-transform duration-300 ${
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
      >
        {/* Logo Section */}
        <div>
          <div className="p-6 border-b border-[var(--panel-border)] flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[var(--background)] border border-[#00A8FF]/40 flex items-center justify-center shadow-inner">
              <Shield className="w-5 h-5 text-[#00E5FF]" />
            </div>
            <div>
              <div className="font-black tracking-widest text-lg leading-none text-[var(--foreground)]">
                ITBIS
              </div>
              <div className="text-[10px] font-semibold tracking-wider text-[#00A8FF] uppercase mt-0.5">
                Behavioral Intel
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-[var(--text-muted)] opacity-70">
              Operations
            </div>
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === pathname ||
                (item.href !== "/dashboard" && pathname.startsWith(item.href.split("?")[0]));

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all group ${
                    isActive
                      ? "bg-[#00A8FF]/15 text-[#00E5FF] border border-[#00A8FF]/40 shadow-[0_0_10px_rgba(0,168,255,0.15)]"
                      : "text-[var(--text-muted)] hover:bg-[var(--background)] hover:text-[var(--foreground)]"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-4 h-4 transition-colors ${
                        isActive
                          ? "text-[#00E5FF]"
                          : "text-[var(--text-muted)] group-hover:text-[var(--foreground)]"
                      }`}
                    />
                    <span>{item.name}</span>
                  </div>

                  {item.name === "Alerts" && openAlertCount > 0 && (
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-950 text-[#00E5FF] border border-[#00E5FF]/40">
                      {openAlertCount}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User Profile & Logout */}
        <div className="p-4 border-t border-[var(--panel-border)] bg-[var(--background)]/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[var(--panel)] border border-[var(--panel-border)] flex items-center justify-center text-[var(--text-muted)]">
                <UserIcon className="w-4 h-4" />
              </div>
              <div className="truncate max-w-[110px]">
                <div className="text-xs font-semibold truncate text-[var(--foreground)]">
                  {user?.email.split("@")[0]}
                </div>
                <div className="text-[10px] text-[var(--text-muted)] capitalize truncate font-mono">
                  {user?.role.replace("_", " ")}
                </div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="p-2 text-[var(--text-muted)] hover:text-rose-400 hover:bg-rose-950/20 rounded-lg transition"
              title="Terminate Security Session"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Operational Header */}
        <header className="sticky top-0 bg-[var(--panel)]/90 backdrop-blur-md border-b border-[var(--panel-border)] z-20 px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-lg font-black tracking-tight text-[var(--foreground)] uppercase">
              {pageTitle}
            </h1>
            <p className="text-xs text-[var(--text-muted)] font-medium">
              {pageSubtitle}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Global Search Bar */}
            <div ref={searchRef} className="relative w-full sm:w-64">
              <SearchIcon className="w-3.5 h-3.5 absolute left-3 top-3 text-[var(--text-muted)]" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => { if (searchResults.length > 0) setShowSearchDropdown(true); }}
                placeholder="Search ITBIS (EMP, Alert, Inc)..."
                className="w-full bg-[var(--background)] border border-[var(--panel-border)] focus:border-[#00A8FF] rounded-lg pl-9 pr-3 py-1.5 text-xs text-[var(--foreground)] placeholder-[var(--text-muted)] outline-none transition"
              />

              {/* Search Dropdown Results */}
              {showSearchDropdown && (
                <div className="absolute left-0 right-0 top-11 bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl shadow-2xl overflow-hidden z-50 animate-in fade-in max-h-80 overflow-y-auto">
                  {searchLoading ? (
                    <div className="p-4 text-center text-xs text-[var(--text-muted)]">
                      Searching entities...
                    </div>
                  ) : searchResults.length > 0 ? (
                    <div className="divide-y divide-[var(--panel-border)]">
                      {searchResults.map((res, idx) => (
                        <Link
                          key={idx}
                          href={res.link}
                          onClick={() => { setShowSearchDropdown(false); setSearchQuery(""); }}
                          className="block p-3 hover:bg-[var(--background)] transition text-xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-[#00E5FF]">{res.title}</span>
                            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)]">
                              {res.category}
                            </span>
                          </div>
                          <div className="text-[11px] text-[var(--text-muted)] mt-0.5 truncate">
                            {res.subtitle}
                          </div>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 text-center text-xs text-[var(--text-muted)]">
                      No matches found for "{searchQuery}"
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Theme Toggle Menu */}
            <div className="relative">
              <button
                onClick={() => setShowThemeMenu(!showThemeMenu)}
                className="p-2 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition cursor-pointer"
                title="Theme Settings"
              >
                {theme === "light" ? <Sun className="w-4 h-4 text-amber-500" /> : theme === "dark" ? <Moon className="w-4 h-4 text-[#00E5FF]" /> : <Laptop className="w-4 h-4 text-[var(--text-muted)]" />}
              </button>

              {showThemeMenu && (
                <div className="absolute right-0 top-11 w-44 bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl shadow-2xl py-1 z-50 animate-in fade-in text-xs">
                  <div className="px-3 py-1.5 font-bold text-[10px] uppercase text-[var(--text-muted)] border-b border-[var(--panel-border)]">
                    Theme Preference
                  </div>
                  <button
                    onClick={() => handleSetTheme("dark")}
                    className="w-full px-3 py-2 text-left hover:bg-[var(--background)] flex items-center justify-between cursor-pointer"
                  >
                    <span className="flex items-center gap-2"><Moon className="w-3.5 h-3.5 text-[#00E5FF]" /> Dark (SOC Cyber)</span>
                    {theme === "dark" && <Check className="w-3.5 h-3.5 text-[#00E5FF]" />}
                  </button>
                  <button
                    onClick={() => handleSetTheme("light")}
                    className="w-full px-3 py-2 text-left hover:bg-[var(--background)] flex items-center justify-between cursor-pointer"
                  >
                    <span className="flex items-center gap-2"><Sun className="w-3.5 h-3.5 text-amber-500" /> Light Mode</span>
                    {theme === "light" && <Check className="w-3.5 h-3.5 text-[#00A8FF]" />}
                  </button>
                  <button
                    onClick={() => handleSetTheme("system")}
                    className="w-full px-3 py-2 text-left hover:bg-[var(--background)] flex items-center justify-between cursor-pointer"
                  >
                    <span className="flex items-center gap-2"><Laptop className="w-3.5 h-3.5 text-[var(--text-muted)]" /> System Default</span>
                    {theme === "system" && <Check className="w-3.5 h-3.5 text-[#00E5FF]" />}
                  </button>
                </div>
              )}
            </div>

            {/* Notification Center */}
            <div className="relative">
              <button
                onClick={() => setShowNotifMenu(!showNotifMenu)}
                className="p-2 rounded-lg bg-[var(--background)] border border-[var(--panel-border)] text-[var(--text-muted)] hover:text-[#00E5FF] transition relative cursor-pointer"
                title="SOC Notification Center"
              >
                <Bell className="w-4 h-4" />
                {notifications.length > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-cyan-500 text-[9px] font-bold font-mono text-[#050B14] flex items-center justify-center animate-pulse">
                    {notifications.length}
                  </span>
                )}
              </button>

              {/* Notification Dropdown */}
              {showNotifMenu && (
                <div className="absolute right-0 top-11 w-80 bg-[var(--panel)] border border-[var(--panel-border)] rounded-xl shadow-2xl p-4 z-50 animate-in fade-in space-y-3">
                  <div className="flex items-center justify-between border-b border-[var(--panel-border)] pb-2">
                    <span className="font-bold text-xs uppercase tracking-wider text-[var(--foreground)]">
                      SOC Notifications ({notifications.length})
                    </span>
                    {notifications.length > 0 && (
                      <button
                        onClick={markAllNotificationsRead}
                        className="text-[10px] text-[#00A8FF] hover:text-[#00E5FF] font-semibold cursor-pointer"
                      >
                        Mark All Read
                      </button>
                    )}
                  </div>

                  <div className="divide-y divide-[var(--panel-border)] max-h-64 overflow-y-auto">
                    {notifications.length > 0 ? (
                      notifications.map((n) => (
                        <div key={n.id} className="py-2.5 space-y-1 text-xs">
                          <div className="flex items-start justify-between gap-2">
                            <span className="font-semibold text-[var(--foreground)]">{n.title}</span>
                            <button
                              onClick={() => markNotificationRead(n.id)}
                              className="text-[10px] text-[var(--text-muted)] hover:text-[#00E5FF]"
                            >
                              ✕
                            </button>
                          </div>
                          <p className="text-[11px] text-[var(--text-muted)] leading-relaxed">{n.message}</p>
                          <div className="text-[9px] font-mono text-[var(--text-muted)]">
                            {new Date(n.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-6 text-xs text-[var(--text-muted)]">
                        No unread security notifications.
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 p-6 relative z-10">{children}</div>
      </main>
    </div>
  );
}
