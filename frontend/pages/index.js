import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/dashboard");
    }
  }, []);

  return (
    <div className="container" style={{ marginTop: "100px", textAlign: "center" }}>
      <h1>AI-Powered Insider Threat Detection</h1>
      <p style={{ fontSize: "18px", color: "#666", marginTop: "8px" }}>
        Behavioral Security Intelligence Platform
      </p>
      <div style={{ marginTop: "32px", display: "flex", gap: "12px", justifyContent: "center" }}>
        <a href="/login" className="btn btn-primary" style={{ padding: "12px 24px" }}>
          Login
        </a>
        <a href="/signup" className="btn" style={{ padding: "12px 24px", border: "1px solid #dadce0" }}>
          Sign Up
        </a>
      </div>
    </div>
  );
}
