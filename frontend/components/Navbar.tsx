"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";
import api from "@/lib/api";

type UserData = {
  user_id: number;
  email: string;
  role: string;
};

interface SearchResults {
  query: string;
  total_matches: number;
  employees: Array<{ employee_code: string; name: string; department: string; role: string }>;
  incidents: Array<{ id: number; incident_type: string; severity: string; status: string; employee_name?: string; employee_code?: string; department?: string }>;
  alerts: Array<{ id: number; message: string; severity: string; status: string; employee_name?: string; employee_code?: string }>;
  activity_logs: Array<{ employee_code?: string; ip_address?: string; event_type?: string; application?: string; resource?: string; action?: string; timestamp?: string }>;
}

interface NotificationItem {
  id?: number;
  alert_id?: number;
  title?: string;
  message: string;
  severity: string;
  employee_code?: string;
  timestamp?: string;
}

const getNotifKey = (n: NotificationItem, idx?: number): string => {
  if (n.id) return `notif-id-${n.id}`;
  if (n.alert_id) return `notif-alert-${n.alert_id}`;
  return `notif-msg-${n.message}-${n.timestamp || idx || 0}`;
};

export default function Navbar() {
  const [user, setUser] = useState<UserData | null>(null);

  // Global Threat Search State
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResults | null>(null);
  const [searching, setSearching] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // Profile Dropdown & Modal State
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);

  const formatRole = (role?: string) => {
    if (!role) return "Operator";
    return role
      .split("_")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
      .join(" ");
  };

  // Live Notification State
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [readNotifKeys, setReadNotifKeys] = useState<Set<string>>(new Set());
  const [showNotifDrawer, setShowNotifDrawer] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [liveToast, setLiveToast] = useState<NotificationItem | null>(null);
  const notifRef = useRef<HTMLDivElement>(null);

  // Check if a specific notification is read
  const isNotificationRead = (n: NotificationItem, idx?: number) => {
    return readNotifKeys.has(getNotifKey(n, idx));
  };

  // Compute count of genuinely unread/unviewed notifications
  const unreadCount = notifications.filter((n, idx) => !isNotificationRead(n, idx)).length;

  // Mark all currently loaded notifications as read / viewed
  const markAllAsRead = (itemsToMark?: NotificationItem[]) => {
    const list = itemsToMark || notifications;
    setReadNotifKeys((prev) => {
      const next = new Set(prev);
      list.forEach((n, idx) => next.add(getNotifKey(n, idx)));
      try {
        localStorage.setItem("itbis-read-notifications", JSON.stringify(Array.from(next)));
      } catch {}
      return next;
    });
  };

  // Clear all notifications completely
  const clearAllNotifications = () => {
    markAllAsRead();
    setNotifications([]);
    try {
      localStorage.setItem("itbis-notifications-cleared-time", new Date().toISOString());
    } catch {}
  };

  // Dismiss an individual notification
  const dismissNotification = (n: NotificationItem, idx: number) => {
    const key = getNotifKey(n, idx);
    setReadNotifKeys((prev) => {
      const next = new Set(prev);
      next.add(key);
      try {
        localStorage.setItem("itbis-read-notifications", JSON.stringify(Array.from(next)));
      } catch {}
      return next;
    });
    setNotifications((prev) => prev.filter((_, i) => i !== idx));
  };

  // When clicking the bell icon, open drawer and mark notifications as viewed
  const handleToggleDrawer = () => {
    setShowNotifDrawer((prev) => {
      const nextState = !prev;
      if (nextState) {
        // User has opened drawer to view notifications -> mark them all as viewed!
        markAllAsRead();
      }
      return nextState;
    });
  };

  useEffect(() => {
    const storedUser = localStorage.getItem("itbis-user");
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        setUser(null);
      }
    }

    // Load previously read notification keys from localStorage
    try {
      const storedRead = localStorage.getItem("itbis-read-notifications");
      if (storedRead) {
        setReadNotifKeys(new Set(JSON.parse(storedRead)));
      }
    } catch {}

    // Initial notifications fetch
    api
      .get("/notifications")
      .then((res) => {
        if (res.data?.notifications) {
          const clearedTimeStr = localStorage.getItem("itbis-notifications-cleared-time");
          let loaded = res.data.notifications as NotificationItem[];
          if (clearedTimeStr) {
            const clearedTime = new Date(clearedTimeStr).getTime();
            loaded = loaded.filter((n) => {
              if (!n.timestamp) return true;
              return new Date(n.timestamp).getTime() > clearedTime;
            });
          }
          setNotifications(loaded);
        }
      })
      .catch(() => {});

    // WebSocket connection for real-time threat notifications
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket("ws://localhost:8000/ws/alerts");
      ws.onopen = () => setWsConnected(true);
      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const newNotif: NotificationItem = {
            id: payload.id || payload.alert_id,
            alert_id: payload.alert_id || payload.id,
            title: payload.title || "Live Security Threat",
            message: payload.message || "New anomaly detected by UEBA engine.",
            severity: payload.severity || "high",
            timestamp: payload.timestamp || new Date().toISOString(),
          };
          setNotifications((prev) => [newNotif, ...prev.slice(0, 19)]);
          setLiveToast(newNotif);
          setTimeout(() => setLiveToast(null), 6000);
        } catch {}
      };
      ws.onerror = () => setWsConnected(false);
      ws.onclose = () => setWsConnected(false);
    } catch {
      setWsConnected(false);
    }

    // Close dropdowns on outside click
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowSearchDropdown(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setShowNotifDrawer(false);
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setShowProfileDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      if (ws) ws.close();
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Debounced search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults(null);
      setShowSearchDropdown(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setSearching(true);
        const res = await api.get(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
        setSearchResults(res.data);
        setShowSearchDropdown(true);
      } catch (err: any) {
        if (err?.name !== "CanceledError" && err?.code !== "ERR_CANCELED") {
          console.warn("Search request failed:", err?.message || err);
        }
      } finally {
        setSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleLogout = () => {
    localStorage.removeItem("itbis-token");
    localStorage.removeItem("itbis-user");
    window.location.href = "/login";
  };

  return (
    <>
      <header className="flex h-16 items-center justify-between border-b border-[var(--border)] bg-[var(--card)] px-6 relative z-30">
        {/* Left: Branding & Search */}
        <div className="flex items-center gap-6 flex-1 max-w-2xl">
          <div className="hidden lg:block">
            <h1 className="text-base font-bold text-[var(--foreground)]">Security Console</h1>
            <p className="text-[10px] text-[var(--muted)]">Insider Threat Behavioral Intelligence System</p>
          </div>

          {/* Global Threat Hunting Search Bar */}
          <div ref={searchRef} className="relative flex-1 max-w-md">
            <div className="flex items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 focus-within:border-[var(--primary)] transition shadow-inner">
              <span className="text-xs text-[var(--muted)]">🔍</span>
              <input
                type="text"
                value={searchQuery}
                onFocus={() => {
                  if (searchResults && searchResults.total_matches > 0) {
                    setShowSearchDropdown(true);
                  }
                }}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && searchResults && searchResults.total_matches > 0) {
                    setShowSearchDropdown(false);
                    if (searchResults.employees.length > 0) {
                      window.location.href = `/employees/${searchResults.employees[0].employee_code}`;
                    } else if (searchResults.incidents.length > 0) {
                      window.location.href = `/incidents?id=${searchResults.incidents[0].id}`;
                    } else if (searchResults.alerts.length > 0) {
                      window.location.href = `/incidents`;
                    } else if (searchResults.activity_logs.length > 0 && searchResults.activity_logs[0].employee_code) {
                      window.location.href = `/activity?employee=${searchResults.activity_logs[0].employee_code}`;
                    }
                  }
                }}
                placeholder="Threat Search (e.g. #15, Vikram, EMP001, IP)..."
                className="w-full bg-transparent text-xs text-[var(--foreground)] placeholder-[var(--muted)] outline-none"
              />
              {searching && (
                <div className="h-3 w-3 animate-spin rounded-full border border-[var(--border)] border-t-[var(--primary)] shrink-0" />
              )}
            </div>

            {/* Instant Search Dropdown */}
            {showSearchDropdown && searchResults && (
              <div className="absolute left-0 right-0 top-11 z-50 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-4 shadow-2xl space-y-3 max-h-96 overflow-y-auto">
                <div className="flex items-center justify-between border-b border-[var(--border)] pb-2 text-[11px] text-[var(--muted)]">
                  <span>Search results for &quot;{searchResults.query}&quot;</span>
                  <span className="font-bold text-[var(--foreground)]">{searchResults.total_matches} matches</span>
                </div>

                {/* Employees */}
                {searchResults.employees.length > 0 && (
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--muted)] mb-1.5">Employees</p>
                    <div className="space-y-1">
                      {searchResults.employees.map((e) => (
                        <Link
                          key={e.employee_code}
                          href={`/employees/${e.employee_code}`}
                          onClick={() => setShowSearchDropdown(false)}
                          className="flex items-center justify-between rounded-lg p-2 text-xs hover:bg-[var(--card-hover)] transition"
                        >
                          <span className="font-semibold text-[var(--foreground)]">{e.name}</span>
                          <span className="font-mono text-[10px] text-[var(--primary)]">{e.employee_code} • {e.department}</span>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}

                {/* Incidents */}
                {searchResults.incidents.length > 0 && (
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--muted)] mb-1.5">Security Incidents</p>
                    <div className="space-y-1">
                      {searchResults.incidents.map((inc) => (
                        <Link
                          key={inc.id}
                          href={`/incidents?id=${inc.id}`}
                          onClick={() => setShowSearchDropdown(false)}
                          className="flex items-center justify-between rounded-lg p-2 text-xs hover:bg-[var(--card-hover)] transition"
                        >
                          <div className="flex flex-col min-w-0 pr-2">
                            <span className="font-medium text-[var(--foreground)] truncate">
                              Incident #{inc.id}: {inc.incident_type}
                            </span>
                            <span className="text-[10px] text-[var(--muted)] truncate">
                              Subject: {inc.employee_name || inc.employee_code || "Unknown"} {inc.department ? `(${inc.department})` : ""}
                            </span>
                          </div>
                          <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${
                            inc.severity === "critical" ? "bg-red-950/60 text-red-400" :
                            inc.severity === "high" ? "bg-orange-950/60 text-orange-400" :
                            "bg-amber-950/60 text-amber-400"
                          }`}>
                            {inc.severity}
                          </span>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}

                {/* Alerts */}
                {searchResults.alerts.length > 0 && (
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--muted)] mb-1.5">Alerts</p>
                    <div className="space-y-1">
                      {searchResults.alerts.map((al) => (
                        <Link
                          key={al.id}
                          href="/incidents"
                          onClick={() => setShowSearchDropdown(false)}
                          className="flex items-center justify-between rounded-lg p-2 text-xs hover:bg-[var(--card-hover)] transition"
                        >
                          <div className="flex flex-col min-w-0 pr-2">
                            <span className="truncate text-xs text-[var(--foreground)]">Alert #{al.id}: {al.message}</span>
                            {al.employee_name && (
                              <span className="text-[10px] text-[var(--muted)]">Target: {al.employee_name} ({al.employee_code})</span>
                            )}
                          </div>
                          <span className="shrink-0 rounded bg-amber-950/60 px-1.5 py-0.5 text-[10px] font-bold uppercase text-amber-400">
                            {al.severity}
                          </span>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}

                {/* Activity Logs */}
                {searchResults.activity_logs && searchResults.activity_logs.length > 0 && (
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--muted)] mb-1.5">Telemetry & Activity Logs</p>
                    <div className="space-y-1">
                      {searchResults.activity_logs.map((act, idx) => (
                        <Link
                          key={idx}
                          href={`/activity${act.employee_code ? `?employee=${act.employee_code}` : ""}`}
                          onClick={() => setShowSearchDropdown(false)}
                          className="flex items-center justify-between rounded-lg p-2 text-xs hover:bg-[var(--card-hover)] transition"
                        >
                          <div className="flex flex-col min-w-0 pr-2">
                            <span className="font-mono text-xs text-[var(--foreground)] truncate">
                              {act.event_type || act.action || "Activity Event"} • {act.application || act.resource || "System"}
                            </span>
                            <span className="text-[10px] text-[var(--muted)]">
                              {act.employee_code ? `EMP: ${act.employee_code}` : ""} {act.ip_address ? `• IP: ${act.ip_address}` : ""}
                            </span>
                          </div>
                          {act.timestamp && (
                            <span className="shrink-0 text-[9px] text-[var(--muted)] font-mono">
                              {new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          )}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}

                {searchResults.total_matches === 0 && (
                  <p className="text-center text-xs text-[var(--muted)] py-3">No matching entities found.</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right: Notifications, Theme & Profile */}
        <div className="flex items-center gap-3.5">
          {/* Live Notification Bell */}
          <div ref={notifRef} className="relative">
            <button
              onClick={handleToggleDrawer}
              className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--background)] hover:border-[var(--primary)] transition cursor-pointer"
              title={unreadCount > 0 ? `${unreadCount} New Threat Notifications` : "Real-Time Alerts Feed"}
            >
              <span className="text-sm">🔔</span>
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-bold text-white shadow-sm animate-pulse">
                  {Math.min(99, unreadCount)}
                </span>
              )}
            </button>

            {/* Notification Drawer */}
            {showNotifDrawer && (
              <div className="absolute right-0 top-12 z-50 w-80 sm:w-96 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-4 shadow-2xl space-y-3">
                <div className="flex items-center justify-between border-b border-[var(--border)] pb-2.5">
                  <div className="flex items-center gap-2">
                    <h4 className="text-xs font-bold text-[var(--foreground)]">Real-Time Threat Feed</h4>
                    <span
                      className={`h-2 w-2 rounded-full ${wsConnected ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`}
                      title={wsConnected ? "Live WebSocket Feed Connected" : "Connecting..."}
                    />
                    <span className="rounded-full bg-[var(--background)] px-2 py-0.5 text-[10px] font-semibold text-[var(--muted)] border border-[var(--border)]">
                      {unreadCount > 0 ? `${unreadCount} New` : "All Viewed"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    {notifications.length > 0 && (
                      <button
                        onClick={clearAllNotifications}
                        className="text-[10px] text-[var(--muted)] hover:text-red-400 font-medium transition cursor-pointer"
                        title="Clear all notifications from view"
                      >
                        Clear All
                      </button>
                    )}
                    <Link
                      href="/incidents"
                      onClick={() => setShowNotifDrawer(false)}
                      className="text-[10px] font-semibold text-[var(--primary)] hover:underline"
                    >
                      Queue →
                    </Link>
                  </div>
                </div>

                <div className="space-y-2 max-h-80 overflow-y-auto pr-0.5">
                  {notifications.length === 0 ? (
                    <div className="py-6 text-center space-y-1">
                      <div className="text-xl">✓</div>
                      <p className="text-xs font-semibold text-[var(--foreground)]">All caught up!</p>
                      <p className="text-[11px] text-[var(--muted)]">No active threat notifications.</p>
                    </div>
                  ) : (
                    notifications.map((n, idx) => {
                      const isRead = isNotificationRead(n, idx);
                      return (
                        <div
                          key={idx}
                          onClick={() => {
                            dismissNotification(n, idx);
                            setShowNotifDrawer(false);
                            window.location.href = `/incidents${n.alert_id || n.id ? `?id=${n.alert_id || n.id}` : ""}`;
                          }}
                          className={`group relative rounded-xl border p-2.5 text-xs space-y-1 transition cursor-pointer ${
                            isRead
                              ? "border-[var(--border)] bg-[var(--background)] opacity-75 hover:opacity-100 hover:border-[var(--primary)]"
                              : "border-red-500/40 bg-red-950/20 hover:border-red-500"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5 min-w-0 pr-2">
                              {!isRead && (
                                <span className="h-1.5 w-1.5 rounded-full bg-red-500 shrink-0" title="Unread" />
                              )}
                              <span className="font-semibold text-red-400 truncate">
                                {n.title || "Security Threat Alert"}
                              </span>
                            </div>
                            <div className="flex items-center gap-1.5 shrink-0">
                              <span className="text-[9px] uppercase font-bold text-[var(--muted)]">
                                {n.severity}
                              </span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  dismissNotification(n, idx);
                                }}
                                className="text-[11px] text-[var(--muted)] hover:text-red-400 opacity-60 hover:opacity-100 font-bold px-1 cursor-pointer"
                                title="Dismiss notification"
                              >
                                ✕
                              </button>
                            </div>
                          </div>
                          <p className="text-[11px] text-[var(--muted)] line-clamp-2">{n.message}</p>
                          <div className="flex items-center justify-between pt-0.5 text-[9px] text-[var(--muted)]">
                            {n.employee_code && <span>Target: {n.employee_code}</span>}
                            {n.timestamp && (
                              <span className="ml-auto font-mono">
                                {new Date(n.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            )}
          </div>

          <ThemeToggle />

          {/* User Profile & Role Dropdown Button */}
          <div className="relative" ref={profileRef}>
            <button
              onClick={() => setShowProfileDropdown((prev) => !prev)}
              className="flex items-center gap-2.5 rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-xs font-semibold text-[var(--foreground)] transition hover:border-[var(--primary)]/50 hover:bg-[var(--card)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/20"
              aria-expanded={showProfileDropdown}
              aria-haspopup="true"
              title="User menu"
            >
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--primary)] font-bold text-xs text-white shadow-sm">
                {user?.role?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || "U"}
              </div>
              <span className="hidden sm:inline capitalize font-semibold tracking-wide text-[var(--foreground)]">
                {formatRole(user?.role)}
              </span>
              <svg
                className={`h-3.5 w-3.5 text-[var(--muted)] transition-transform duration-200 ${
                  showProfileDropdown ? "rotate-180" : ""
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown Menu */}
            {showProfileDropdown && (
              <div className="absolute right-0 top-11 z-50 w-60 rounded-2xl border border-[var(--border)] bg-[var(--card)] p-2 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-top-2 duration-150">
                {/* Header Profile Identity */}
                <div className="px-3 py-2.5 border-b border-[var(--border)] mb-1">
                  <div className="flex items-center gap-2.5 mb-1.5">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--primary)]/20 font-bold text-xs text-[var(--primary)]">
                      {user?.role?.charAt(0).toUpperCase() || "U"}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="inline-block rounded bg-[var(--primary)]/15 px-1.5 py-0.5 text-[10px] font-semibold text-[var(--primary)] uppercase tracking-wider">
                        {formatRole(user?.role)}
                      </div>
                      <p className="text-xs text-[var(--muted)] truncate mt-0.5" title={user?.email}>
                        {user?.email || "operator@itbis.local"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 font-medium">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Active Session
                  </div>
                </div>

                {/* Dropdown Action Buttons */}
                <div className="space-y-1">
                  <button
                    onClick={() => {
                      setShowProfileDropdown(false);
                      setShowProfileModal(true);
                    }}
                    className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-[var(--foreground)] hover:bg-[var(--background)] hover:text-[var(--primary)] transition"
                  >
                    <svg className="h-4 w-4 text-[var(--muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>Profile</span>
                  </button>

                  {user?.role === "admin" && (
                    <Link
                      href="/admin/users"
                      onClick={() => setShowProfileDropdown(false)}
                      className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-[var(--foreground)] hover:bg-[var(--background)] hover:text-[var(--primary)] transition"
                    >
                      <svg className="h-4 w-4 text-[var(--muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                      <span>Manage Users</span>
                    </Link>
                  )}
                </div>

                <div className="my-1 border-t border-[var(--border)]" />

                <button
                  onClick={() => {
                    setShowProfileDropdown(false);
                    handleLogout();
                  }}
                  className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold text-red-400 hover:bg-red-500/10 hover:text-red-300 transition"
                >
                  <svg className="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>Log Out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Floating Live WebSocket Alert Toast */}
      {liveToast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-2xl border border-red-500/40 bg-red-950/90 p-4 shadow-2xl backdrop-blur-md text-xs text-white max-w-sm animate-bounce">
          <span className="text-xl">🚨</span>
          <div>
            <p className="font-bold text-red-200">{liveToast.title}</p>
            <p className="text-[11px] text-red-100/90">{liveToast.message}</p>
          </div>
          <button onClick={() => setLiveToast(null)} className="ml-auto text-xs text-red-300 hover:text-white font-bold">
            ✕
          </button>
        </div>
      )}

      {/* Operator Security Profile Modal */}
      {showProfileModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200"
          onClick={() => setShowProfileModal(false)}
        >
          <div 
            className="relative w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--card)] p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-[var(--border)] pb-4 mb-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--primary)] font-bold text-sm text-white shadow-md">
                  {user?.role?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || "U"}
                </div>
                <div>
                  <h3 className="text-base font-bold text-[var(--foreground)]">Operator Profile</h3>
                  <p className="text-xs text-[var(--muted)]">Security Console Credentials & Access</p>
                </div>
              </div>
              <button
                onClick={() => setShowProfileModal(false)}
                className="rounded-lg p-1 text-[var(--muted)] hover:bg-[var(--background)] hover:text-[var(--foreground)] transition"
              >
                ✕
              </button>
            </div>

            {/* Profile Information Details */}
            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between rounded-xl bg-[var(--background)] p-3 border border-[var(--border)]">
                <span className="text-[var(--muted)] font-medium">Assigned Role</span>
                <span className="rounded bg-[var(--primary)]/15 px-2.5 py-0.5 font-bold uppercase text-[var(--primary)] tracking-wider">
                  {formatRole(user?.role)}
                </span>
              </div>

              <div className="flex items-center justify-between rounded-xl bg-[var(--background)] p-3 border border-[var(--border)]">
                <span className="text-[var(--muted)] font-medium">Email Address</span>
                <span className="font-semibold text-[var(--foreground)]">{user?.email || "N/A"}</span>
              </div>

              <div className="flex items-center justify-between rounded-xl bg-[var(--background)] p-3 border border-[var(--border)]">
                <span className="text-[var(--muted)] font-medium">Operator ID</span>
                <span className="font-mono text-[var(--foreground)] font-semibold">#{user?.user_id || "1"}</span>
              </div>

              <div className="rounded-xl bg-[var(--background)] p-3 border border-[var(--border)]">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[var(--muted)] font-medium">Clearance & Permissions</span>
                  <span className="text-emerald-400 font-semibold text-[11px] bg-emerald-500/10 px-2 py-0.5 rounded">Authorized</span>
                </div>
                <p className="text-[11px] text-[var(--muted)] leading-relaxed">
                  {user?.role === "admin"
                    ? "Level 4 Clearance: Full administrative privileges, user management, policy creation, and incident resolution."
                    : user?.role === "security_analyst"
                    ? "Level 3 Clearance: Anomaly inspection, live telemetry review, and incident triage authorization."
                    : "Standard Operational Clearance: Behavioral analytics inspection and telemetry monitoring."}
                </p>
              </div>

              <div className="flex items-center justify-between rounded-xl bg-[var(--background)] p-3 border border-[var(--border)]">
                <span className="text-[var(--muted)] font-medium">Session Status</span>
                <span className="flex items-center gap-1.5 text-emerald-400 font-semibold text-[11px]">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  Authenticated & Active
                </span>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="mt-5 flex items-center justify-end gap-2.5 pt-3 border-t border-[var(--border)]">
              <button
                onClick={() => setShowProfileModal(false)}
                className="rounded-xl border border-[var(--border)] px-4 py-2 text-xs font-semibold text-[var(--foreground)] hover:bg-[var(--background)] transition"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setShowProfileModal(false);
                  handleLogout();
                }}
                className="flex items-center gap-1.5 rounded-xl bg-red-500/15 border border-red-500/30 px-4 py-2 text-xs font-semibold text-red-400 hover:bg-red-500/25 transition"
              >
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span>Log Out</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}