/**
 * Dev Progress Page
 *
 * Simple visual dashboard showing PaiiD app construction progress
 * For non-technical users to track how the app is being built
 */

import { useRouter } from "next/router";
import { useEffect } from "react";

export default function ProgressPage() {
  const _router = useRouter();

  useEffect(() => {
    // Redirect to the HTML dashboard file
    window.location.href = "/PROGRESS_DASHBOARD.html";
  }, []);

  return (
    <main
      role="main"
      aria-live="polite"
      aria-busy="true"
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        color: "#fff",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <div style={{ textAlign: "center" }} role="status">
        <h1
          style={{
            fontSize: "2em",
            marginBottom: "20px",
            background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Loading Progress Dashboard...
        </h1>
        <p style={{ color: "#94a3b8" }}>Redirecting to app progress tracker</p>
        <div
          role="progressbar"
          aria-label="Loading progress dashboard"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={undefined}
          style={{
            marginTop: "20px",
            display: "inline-block",
          }}
        >
          <div
            style={{
              width: "40px",
              height: "40px",
              border: "4px solid rgba(16, 185, 129, 0.3)",
              borderTop: "4px solid #10b981",
              borderRadius: "50%",
              animation: "spin 1s linear infinite",
            }}
          />
        </div>
      </div>
      <style jsx>{`
        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </main>
  );
}
