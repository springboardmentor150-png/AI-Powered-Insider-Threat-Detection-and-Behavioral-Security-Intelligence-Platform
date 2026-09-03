"use client";

import ThemeToggle from "@/components/ThemeToggle";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[var(--background)] p-6 text-[var(--foreground)]">
      <div className="w-full max-w-xl rounded-2xl border border-[var(--border)] bg-[var(--card)] p-8 shadow-2xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              ITBIS
            </h1>

            <p className="mt-1 text-sm text-[var(--muted)]">
              Insider Threat Behavioral Intelligence System
            </p>
          </div>

          <ThemeToggle />
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-sm text-[var(--muted)]">
              Theme System
            </p>

            <h2 className="mt-1 text-xl font-semibold">
              Dark & Light Mode
            </h2>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="rounded-xl border border-[var(--border)] p-4">
              <div className="mb-2 h-3 w-3 rounded-full bg-[var(--primary)]" />
              <p className="text-sm">Primary</p>
            </div>

            <div className="rounded-xl border border-[var(--border)] p-4">
              <div className="mb-2 h-3 w-3 rounded-full bg-[var(--accent)]" />
              <p className="text-sm">Accent</p>
            </div>

            <div className="rounded-xl border border-[var(--border)] p-4">
              <div className="mb-2 h-3 w-3 rounded-full bg-[var(--success)]" />
              <p className="text-sm">Success</p>
            </div>
          </div>

          <button
            type="button"
            className="w-full rounded-xl bg-[var(--primary)] px-5 py-3 font-semibold text-white transition hover:bg-[var(--primary-hover)]"
          >
            ITBIS Primary Button
          </button>
        </div>
      </div>
    </main>
  );
}