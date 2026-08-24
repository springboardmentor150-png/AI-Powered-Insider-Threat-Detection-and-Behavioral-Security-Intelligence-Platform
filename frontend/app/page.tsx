"use client";

import { FormEvent, useState } from "react";

export default function Home() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setMessage("");
    setError("");
    setLoading(true);

    try {
      // OAuth2 requires form-encoded data
      const formData = new URLSearchParams();

      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          const errorMessage = data.detail
            .map((item: { msg?: string }) => item.msg || "Invalid input")
            .join(", ");

          setError(errorMessage);
        } else {
          setError(data.detail || "Login failed");
        }

        return;
      }

      // Store authentication information
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("username", data.username);
      localStorage.setItem("role", data.role);

      setMessage("Login successful!");

      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = "/dashboard";
      }, 500);
    } catch (err) {
      console.error("Login error:", err);

      setError(
        "Unable to connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#020617] text-white flex flex-col items-center justify-center px-6">

      {/* Header */}
      <div className="text-center mb-10">

        <div className="mx-auto mb-6 w-24 h-24 rounded-3xl bg-blue-600 flex items-center justify-center shadow-lg">
          <span className="text-5xl font-bold">
            I
          </span>
        </div>

        <h1 className="text-6xl font-bold tracking-wide">
          ITBIS
        </h1>

        <p className="text-xl text-slate-400 mt-4">
          Insider Threat & Behavioral Intelligence System
        </p>

      </div>

      {/* Login Card */}
      <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl p-10 shadow-2xl">

        <h2 className="text-4xl font-bold mb-4">
          Welcome back
        </h2>

        <p className="text-xl text-slate-400 mb-10">
          Sign in to access the security intelligence platform.
        </p>

        <form onSubmit={handleLogin}>

          {/* Username */}
          <div className="mb-7">

            <label
              htmlFor="username"
              className="block text-lg text-slate-300 mb-3"
            >
              Username
            </label>

            <input
              id="username"
              name="username"
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="Enter your username"
              required
              className="w-full rounded-xl border border-slate-700 bg-slate-800 px-6 py-5 text-xl text-white outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30"
            />

          </div>

          {/* Password */}
          <div className="mb-8">

            <label
              htmlFor="password"
              className="block text-lg text-slate-300 mb-3"
            >
              Password
            </label>

            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              required
              className="w-full rounded-xl border border-slate-700 bg-slate-800 px-6 py-5 text-xl text-white outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30"
            />

          </div>

          {/* Login button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-blue-600 px-6 py-5 text-xl font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>

        </form>

        {/* Error */}
        {error && (
          <div className="mt-6 rounded-xl border border-red-600 bg-red-950 px-6 py-4 text-lg text-red-300">
            {error}
          </div>
        )}

        {/* Success */}
        {message && (
          <div className="mt-6 rounded-xl border border-green-600 bg-green-950 px-6 py-4 text-lg text-green-300">
            {message}
          </div>
        )}

      </div>

      {/* Footer */}
      <p className="mt-8 text-slate-500">
        ITBIS Security Intelligence Platform
      </p>

    </main>
  );
}