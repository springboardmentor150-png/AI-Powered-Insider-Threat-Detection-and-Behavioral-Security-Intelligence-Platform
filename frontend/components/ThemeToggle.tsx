"use client";

import { useEffect, useState } from "react";

type Theme = "dark" | "light";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("dark");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem("itbis-theme") as Theme | null;

    const initialTheme: Theme =
      savedTheme === "light" || savedTheme === "dark"
        ? savedTheme
        : "dark";

    setTheme(initialTheme);
    document.documentElement.classList.remove("dark", "light");
    document.documentElement.classList.add(initialTheme);

    setMounted(true);
  }, []);

  const toggleTheme = () => {
    const nextTheme: Theme = theme === "dark" ? "light" : "dark";

    setTheme(nextTheme);

    document.documentElement.classList.remove("dark", "light");
    document.documentElement.classList.add(nextTheme);

    localStorage.setItem("itbis-theme", nextTheme);
  };

  if (!mounted) {
    return (
      <button
        type="button"
        aria-label="Change theme"
        className="h-10 w-10 rounded-lg border border-[var(--border)] bg-[var(--card)]"
      />
    );
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${
        theme === "dark" ? "light" : "dark"
      } mode`}
      title={`Switch to ${
        theme === "dark" ? "light" : "dark"
      } mode`}
      className="flex h-10 w-10 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--card)] text-lg text-[var(--foreground)] transition-all duration-200 hover:bg-[var(--card-hover)]"
    >
      {theme === "dark" ? "☀" : "☾"}
    </button>
  );
}