"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: "▦",
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
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 border-r border-[var(--border)] bg-[var(--card)] md:flex md:flex-col">

      {/* Logo */}
      <div className="flex h-16 items-center border-b border-[var(--border)] px-5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[var(--primary)] font-bold text-white">
            I
          </div>

          <div>
            <h2 className="font-bold tracking-wide">
              ITBIS
            </h2>

            <p className="text-[10px] text-[var(--muted)]">
              SECURITY INTELLIGENCE
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">

        <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-[var(--muted)]">
          Monitoring
        </p>

        {navigation.map((item) => {
          const active = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                active
                  ? "bg-[var(--primary)] text-white"
                  : "text-[var(--muted)] hover:bg-[var(--card-hover)] hover:text-[var(--foreground)]"
              }`}
            >
              <span className="text-base">
                {item.icon}
              </span>

              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* System Status */}
      <div className="border-t border-[var(--border)] p-4">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-[var(--success)]" />

            <span className="text-xs font-medium">
              System Online
            </span>
          </div>

          <p className="mt-1 text-[10px] text-[var(--muted)]">
            ITBIS monitoring active
          </p>
        </div>
      </div>
    </aside>
  );
}