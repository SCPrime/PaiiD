"use client";

import { useState, useEffect, useCallback } from "react";
import { useMarketStream } from "../hooks/useMarketStream";

export default function StatusBar() {
  const [status, setStatus] = useState<"checking" | "healthy" | "error">("checking");
  const [message, setMessage] = useState("Initializing system check...");
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  // Monitor market data stream connection (no symbols = just track connection)
  const { connected: marketStreamConnected } = useMarketStream([], { debug: false });

  const fetchHealth = useCallback(async () => {
    try {
      setStatus("checking");
      setMessage("Checking backend health... (may take 5-10s on first load)");

      const res = await fetch("/api/proxy/api/health", {
        headers: {
          "cache-control": "no-cache",
          pragma: "no-cache",
        },
      });

      if (!res.ok) {
        throw new Error(`Backend returned status ${res.status}`);
      }

      const data = await res.json();
      // eslint-disable-next-line no-console
      console.info("Health check response:", data);

      setStatus("healthy");
      const redisStatus = data.redis?.status || "not configured";
      const streamStatus = marketStreamConnected ? "Live" : "Offline";
      setMessage(
        `✓ System operational • Backend: Online • Redis: ${redisStatus} • Market Data: ${streamStatus}`
      );
      setLastCheck(new Date());
    } catch (error) {
      console.error("Health check failed:", error);
      const messageText = error instanceof Error ? error.message : "Cannot connect";
      setStatus("error");
      setMessage(`Backend error: ${messageText}`);
    }
  }, [marketStreamConnected]);

  useEffect(() => {
    // eslint-disable-next-line no-console
    console.info("StatusBar mounted, starting health checks");
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => {
      // eslint-disable-next-line no-console
      console.info("StatusBar unmounting, clearing interval");
      clearInterval(interval);
    };
  }, [fetchHealth]);

  const statusStyles = {
    checking: "bg-yellow-100 border-yellow-300 text-yellow-800",
    healthy: "bg-green-100 border-green-300 text-green-800",
    error: "bg-red-100 border-red-300 text-red-800",
  };

  const pulseColors = {
    checking: "bg-yellow-500",
    healthy: "bg-green-500",
    error: "bg-red-500",
  };

  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg border ${statusStyles[status]}`}>
      <div className={`w-3 h-3 rounded-full ${pulseColors[status]} animate-pulse`} />
      <span className="text-sm font-medium flex-1">{message}</span>
      {status === "error" && (
        <button onClick={fetchHealth} className="text-xs font-medium underline hover:no-underline">
          Retry
        </button>
      )}
      {lastCheck && status === "healthy" && (
        <span className="text-xs opacity-60">Last: {lastCheck.toLocaleTimeString()}</span>
      )}
    </div>
  );
}
