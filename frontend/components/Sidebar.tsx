"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const baseNavigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: "▦",
  },
  {
    name: "Incidents & Alerts",
    href: "/incidents",
    icon: "🚨",
  },
  {
    name: "Employees",
    href: "/employees",
    icon: "♙",
  },
  {
    name: "Activity Logs",
    href: "/activity",
    icon: "◷",
  },
  {
    name: "Reports & Exports",
    href: "/reports",
    icon: "▤",
  },
  {
    name: "Audit Trail",
    href: "/audit-logs",
    icon: "📜",
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("itbis-user");
      if (stored) {
        const u = JSON.parse(stored);
        const r = (u.role || "").toLowerCase();
        setIsAdmin(r === "admin" || r === "administrator");
      }
    } catch {}
  }, []);

  const navItems = [
    ...baseNavigation,
    ...(isAdmin
      ? [
          {
            name: "User Management",
            href: "/admin/users",
            icon: "⚙️",
          },
        ]
      : []),
  ];

  return (
    <aside className="hidden w-64 shrink-0 border-r border-[var(--border)] bg-[var(--card)] md:flex md:flex-col h-screen sticky top-0 z-20">
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center border-b border-[var(--border)] px-5">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--primary)] font-bold text-white shadow-sm">
            I
          </div>

          <div>
            <h2 className="font-bold tracking-wide">ITBIS</h2>
            <p className="text-[10px] text-[var(--muted)]">SECURITY INTELLIGENCE</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4 overflow-y-auto">
        <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-[var(--muted)]">
          Operations Center
        </p>

        {navItems.map((item) => {
          const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                active
                  ? "bg-[var(--primary)] text-white shadow-sm"
                  : "text-[var(--muted)] hover:bg-[var(--card-hover)] hover:text-[var(--foreground)]"
              }`}
            >
              <span className="text-base">{item.icon}</span>
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* System Status */}
      <div className="shrink-0 border-t border-[var(--border)] p-4">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-[var(--success)] animate-pulse" />
            <span className="text-xs font-semibold">Active UEBA Engine</span>
          </div>

          <p className="mt-1 text-[10px] text-[var(--muted)]">Continuous behavioral threat monitoring</p>
        </div>
      </div>
    </aside>
  );
}