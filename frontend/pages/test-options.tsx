import { useState } from "react";
import OptionsChain from "../components/trading/OptionsChain";

/**
 * Test page for OptionsChain component
 * Navigate to /test-options to view
 */
export default function TestOptionsPage() {
  const [showChain, setShowChain] = useState(false);
  const [symbol, setSymbol] = useState("SPY");

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0f172a",
        padding: "40px 20px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          background: "rgba(30, 41, 59, 0.8)",
          borderRadius: "16px",
          padding: "32px",
          maxWidth: "500px",
          width: "100%",
          border: "1px solid rgba(148, 163, 184, 0.2)",
        }}
      >
        <h1 style={{ color: "white", fontSize: "32px", marginBottom: "24px", textAlign: "center" }}>
          Options Chain Test
        </h1>

        <div style={{ marginBottom: "24px" }}>
          <label style={{ color: "#cbd5e1", fontSize: "14px", display: "block", marginBottom: "8px" }}>
            Symbol:
          </label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Enter symbol (e.g., SPY, AAPL)"
            style={{
              width: "100%",
              padding: "12px 16px",
              background: "rgba(15, 23, 42, 0.6)",
              border: "1px solid rgba(148, 163, 184, 0.2)",
              borderRadius: "8px",
              color: "white",
              fontSize: "16px",
            }}
          />
        </div>

        <button
          onClick={() => setShowChain(true)}
          disabled={!symbol}
          style={{
            width: "100%",
            padding: "16px",
            background: symbol ? "rgba(16, 185, 129, 0.2)" : "rgba(100, 116, 139, 0.2)",
            color: symbol ? "#10b981" : "#64748b",
            border: `1px solid ${symbol ? "rgba(16, 185, 129, 0.3)" : "rgba(100, 116, 139, 0.3)"}`,
            borderRadius: "8px",
            cursor: symbol ? "pointer" : "not-allowed",
            fontSize: "16px",
            fontWeight: "600",
          }}
        >
          Load Options Chain
        </button>

        <div
          style={{
            marginTop: "24px",
            padding: "16px",
            background: "rgba(59, 130, 246, 0.1)",
            border: "1px solid rgba(59, 130, 246, 0.3)",
            borderRadius: "8px",
          }}
        >
          <p style={{ color: "#93c5fd", fontSize: "14px", margin: 0 }}>
            <strong>Test Instructions:</strong>
            <br />
            1. Enter a symbol (SPY, AAPL, TSLA, etc.)
            <br />
            2. Click "Load Options Chain"
            <br />
            3. Component will fetch live data from backend
            <br />
            4. View Greeks (Delta, Gamma, Theta, Vega)
            <br />
            5. Filter by Calls/Puts/Both
            <br />
            6. Select different expirations
          </p>
        </div>
      </div>

      {showChain && (
        <OptionsChain
          symbol={symbol}
          onClose={() => setShowChain(false)}
        />
      )}
    </div>
  );
}
