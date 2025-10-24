"use client";

import { useMemo } from "react";
import { usePositionUpdates } from "../../hooks/usePositionUpdates";
import { useMarketStream } from "../../hooks/useMarketStream";

const QA_DISABLED = process.env.NODE_ENV === "production";
const DEFAULT_SYMBOLS = ["AAPL", "MSFT", "TSLA"];

export default function StreamingHarnessPage() {
  if (QA_DISABLED) {
    return (
      <main
        style={{ padding: "2rem", fontFamily: "system-ui", color: "#0f172a" }}
        data-testid="qa-disabled"
      >
        <h1>Streaming QA Harness</h1>
        <p>This harness is disabled in production builds.</p>
      </main>
    );
  }

  const {
    positions,
    connected: positionsConnected,
    connecting: positionsConnecting,
    error: positionsError,
    lastUpdate: positionsLastUpdate,
    lastHeartbeat: positionsLastHeartbeat,
    reconnect,
  } = usePositionUpdates({
    debug: true,
    heartbeatTimeout: 5,
    maxReconnectAttempts: 3,
  });

  const {
    prices,
    connected: marketConnected,
    connecting: marketConnecting,
    error: marketError,
    lastUpdate: marketLastUpdate,
    lastHeartbeat: marketLastHeartbeat,
  } = useMarketStream(DEFAULT_SYMBOLS, {
    debug: true,
    heartbeatTimeout: 5,
    maxReconnectAttempts: 3,
  });

  const positionSummary = useMemo(
    () =>
      positions.map((position) => `${position.symbol}:${position.qty}`).join(", ") || "none",
    [positions]
  );

  const priceSymbols = useMemo(
    () => Object.keys(prices).sort().join(", ") || "none",
    [prices]
  );

  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "2rem",
        fontFamily: "system-ui",
        background: "#f1f5f9",
        color: "#0f172a",
      }}
      data-testid="qa-harness"
    >
      <header style={{ marginBottom: "1.5rem" }}>
        <h1 style={{ margin: 0 }}>Streaming QA Harness</h1>
        <p style={{ margin: "0.25rem 0", color: "#475569" }}>
          Synthetic harness for validating SSE recovery, telemetry hooks, and regression scenarios.
        </p>
        <button
          type="button"
          onClick={reconnect}
          data-testid="positions-reconnect"
          style={{
            padding: "0.5rem 1rem",
            marginTop: "0.75rem",
            borderRadius: "0.5rem",
            border: "1px solid #0f172a",
            background: "white",
            cursor: "pointer",
          }}
        >
          Force Reconnect
        </button>
      </header>

      <section
        style={{
          display: "grid",
          gap: "1.5rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
        }}
      >
        <article style={{ background: "white", padding: "1rem", borderRadius: "1rem" }}>
          <h2 style={{ marginTop: 0 }}>Positions Stream</h2>
          <p data-testid="positions-connection">
            Status: {positionsConnecting ? "CONNECTING" : positionsConnected ? "CONNECTED" : "DISCONNECTED"}
          </p>
          <p data-testid="positions-count">Positions: {positions.length}</p>
          <p data-testid="positions-summary">Symbols: {positionSummary}</p>
          <p data-testid="positions-last-update">
            Last Update: {positionsLastUpdate ? positionsLastUpdate.toISOString() : "none"}
          </p>
          <p data-testid="positions-last-heartbeat">
            Last Heartbeat: {positionsLastHeartbeat ? positionsLastHeartbeat.toISOString() : "none"}
          </p>
          <p data-testid="positions-error" style={{ color: "#b91c1c" }}>
            Error: {positionsError ?? "none"}
          </p>
          <pre
            data-testid="positions-json"
            style={{
              background: "#0f172a",
              color: "#e2e8f0",
              padding: "0.75rem",
              borderRadius: "0.75rem",
              overflowX: "auto",
              maxHeight: "220px",
            }}
          >
            {JSON.stringify(positions, null, 2)}
          </pre>
        </article>

        <article style={{ background: "white", padding: "1rem", borderRadius: "1rem" }}>
          <h2 style={{ marginTop: 0 }}>Market Prices Stream</h2>
          <p data-testid="market-connection">
            Status: {marketConnecting ? "CONNECTING" : marketConnected ? "CONNECTED" : "DISCONNECTED"}
          </p>
          <p data-testid="market-symbols">Active Symbols: {priceSymbols}</p>
          <p data-testid="market-last-update">
            Last Update: {marketLastUpdate ? marketLastUpdate.toISOString() : "none"}
          </p>
          <p data-testid="market-last-heartbeat">
            Last Heartbeat: {marketLastHeartbeat ? marketLastHeartbeat.toISOString() : "none"}
          </p>
          <p data-testid="market-error" style={{ color: "#b91c1c" }}>
            Error: {marketError ?? "none"}
          </p>
          <pre
            data-testid="market-json"
            style={{
              background: "#0f172a",
              color: "#e2e8f0",
              padding: "0.75rem",
              borderRadius: "0.75rem",
              overflowX: "auto",
              maxHeight: "220px",
            }}
          >
            {JSON.stringify(prices, null, 2)}
          </pre>
        </article>

        <article style={{ background: "white", padding: "1rem", borderRadius: "1rem" }}>
          <h2 style={{ marginTop: 0 }}>Monitoring Signals</h2>
          <p style={{ margin: "0.5rem 0" }}>
            Listen for <code>paiid:stream-event</code> events to capture telemetry output during tests.
          </p>
          <p style={{ margin: "0.5rem 0" }}>
            Debug logging is enabled to surface instrumentation through browser consoles while QA executes
            regression steps.
          </p>
          <p data-testid="qa-harness-ready" style={{ fontWeight: 600, color: "#0f766e" }}>
            Harness Ready
          </p>
        </article>
      </section>
    </main>
  );
}
