"use client";

import { useEffect, useState } from "react";
import ThemeToggle from "@/components/ThemeToggle";

type UserData = {
  user_id: number;
  email: string;
  role: string;
};

export default function Navbar() {
  const [user, setUser] = useState<UserData | null>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("itbis-user");

    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        setUser(null);
      }
    }
  }, []);

  return (
    <header className="flex h-16 items-center justify-between border-b border-[var(--border)] bg-[var(--card)] px-6">
      <div>
        <h1 className="text-lg font-semibold">
          Security Console
        </h1>

        <p className="text-xs text-[var(--muted)]">
          Insider Threat Behavioral Intelligence System
        </p>
      </div>

      <div className="flex items-center gap-4">
        <ThemeToggle />

        <div className="hidden text-right sm:block">
          <p className="text-sm font-medium">
            {user?.email || "ITBIS User"}
          </p>

          <p className="text-xs capitalize text-[var(--muted)]">
            {user?.role || "user"}
          </p>
        </div>

        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--primary)] font-semibold text-white">
          {user?.email?.charAt(0).toUpperCase() || "U"}
        </div>
      </div>
    </header>
  );
}