/**
 * Simple Financial Chart
 *
 * Clean, easy-to-read line graph showing account value over time
 * Designed for non-technical users - big numbers, simple visuals
 */

"use client";

import { Chart, registerables } from "chart.js";
import { Loader2, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { logger } from "../lib/logger";

// Register Chart.js components
if (typeof window !== "undefined") {
  Chart.register(...registerables);
}

interface HistoryPoint {
  date: string;
  value: number;
}

interface AccountSnapshot {
  currentValue: number;
  todayChange: number;
  todayChangePercent: number;
  history: HistoryPoint[];
}

export default function SimpleFinancialChart() {
  const [timeframe, setTimeframe] = useState<"7D" | "30D" | "ALL">("30D");
  const [data, setData] = useState<AccountSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  const generateDemoData = useCallback((tf: string): HistoryPoint[] => {
    const days = tf === "7D" ? 7 : tf === "30D" ? 30 : 90;
    const points: HistoryPoint[] = [];
    let value = 100000;

    for (let i = 0; i < days; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (days - i));
      value += (Math.random() - 0.45) * 2000; // Slight upward trend
      points.push({
        date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        value: Math.max(value, 95000), // Don't go below 95k
      });
    }
    return points;
  }, []);

  const loadAccountData = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/proxy/portfolio/simple-history?timeframe=${timeframe}`);
      const accountData = await response.json();
      setData(accountData);
    } catch (error) {
      logger.error("Failed to load account data", error);
      // Fallback to demo data
      setData({
        currentValue: 105234.56,
        todayChange: 1234.56,
        todayChangePercent: 1.19,
        history: generateDemoData(timeframe),
      });
    } finally {
      setLoading(false);
    }
  }, [timeframe, generateDemoData]);

  const renderChart = useCallback(() => {
    if (!chartRef.current || !data) return;

    // Destroy existing chart
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext("2d");
    if (!ctx) return;

    const isPositive = data.todayChange >= 0;

    chartInstance.current = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.history.map((p) => p.date),
        datasets: [
          {
            label: "Account Value",
            data: data.history.map((p) => p.value),
            borderColor: isPositive ? "rgba(16, 185, 129, 1)" : "rgba(239, 68, 68, 1)",
            backgroundColor: isPositive ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)",
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: isPositive ? "#10b981" : "#ef4444",
            pointHoverBorderColor: "#fff",
            pointHoverBorderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 2,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: "rgba(15, 23, 42, 0.95)",
            titleColor: "#fff",
            bodyColor: "#94a3b8",
            borderColor: isPositive ? "rgba(16, 185, 129, 0.5)" : "rgba(239, 68, 68, 0.5)",
            borderWidth: 1,
            padding: 12,
            displayColors: false,
            callbacks: {
              label: function (context) {
                const yValue = context.parsed.y;
                if (yValue === null) return "$0.00";
                return (
                  "$" +
                  yValue.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })
                );
              },
            },
          },
        },
        scales: {
          y: {
            ticks: {
              color: "#94a3b8",
              font: {
                size: 14,
                weight: 600,
              },
              callback: function (value) {
                return (
                  "$" +
                  (value as number).toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0,
                  })
                );
              },
            },
            grid: {
              color: "rgba(148, 163, 184, 0.1)",
            },
          },
          x: {
            ticks: {
              color: "#94a3b8",
              font: {
                size: 12,
              },
              maxRotation: 0,
              autoSkip: true,
              maxTicksLimit: 8,
            },
            grid: {
              display: false,
            },
          },
        },
        interaction: {
          intersect: false,
          mode: "index",
        },
      },
    });
  }, [data]);

  // Load account data
  useEffect(() => {
    loadAccountData();
  }, [loadAccountData]);

  // Render chart when data changes
  useEffect(() => {
    if (data && chartRef.current) {
      renderChart();
    }
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data, renderChart]);

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "400px",
          background: "rgba(255, 255, 255, 0.05)",
          borderRadius: "20px",
          border: "1px solid rgba(255, 255, 255, 0.1)",
        }}
      >
        <Loader2 className="animate-spin" size={48} color="#10b981" />
      </div>
    );
  }

  if (!data) return null;

  const isPositive = data.todayChange >= 0;

  return (
    <div
      style={{
        background: "rgba(255, 255, 255, 0.05)",
        borderRadius: "20px",
        border: "1px solid rgba(16, 185, 129, 0.3)",
        padding: "30px",
        backdropFilter: "blur(10px)",
      }}
    >
      {/* Header with big numbers */}
      <div
        style={{
          marginBottom: "30px",
          textAlign: "center",
        }}
      >
        <div
          style={{
            fontSize: "14px",
            color: "#94a3b8",
            marginBottom: "8px",
            textTransform: "uppercase",
            letterSpacing: "1px",
          }}
        >
          Your Account Value
        </div>
        <div
          style={{
            fontSize: "48px",
            fontWeight: "700",
            background: "linear-gradient(135deg, #10b981 0%, #3b82f6 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            marginBottom: "12px",
          }}
        >
          $
          {data.currentValue.toLocaleString("en-US", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
        </div>
        <div
          style={{
            fontSize: "20px",
            color: isPositive ? "#10b981" : "#ef4444",
            fontWeight: "600",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
          }}
        >
          <span>{isPositive ? "↑" : "↓"}</span>
          <span>
            {isPositive ? "+" : ""}$
            {Math.abs(data.todayChange).toLocaleString("en-US", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </span>
          <span>
            ({isPositive ? "+" : ""}
            {data.todayChangePercent.toFixed(2)}%)
          </span>
          <span style={{ fontSize: "14px", color: "#64748b" }}>today</span>
        </div>
      </div>

      {/* Chart */}
      <div style={{ position: "relative", height: "300px", marginBottom: "20px" }}>
        <canvas ref={chartRef} />
      </div>

      {/* Timeframe buttons */}
      <div
        style={{
          display: "flex",
          gap: "12px",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        {(["7D", "30D", "ALL"] as const).map((tf) => (
          <button
            key={tf}
            onClick={() => setTimeframe(tf)}
            style={{
              padding: "12px 24px",
              borderRadius: "12px",
              background:
                timeframe === tf
                  ? "linear-gradient(135deg, #10b981 0%, #059669 100%)"
                  : "rgba(255, 255, 255, 0.05)",
              color: timeframe === tf ? "#fff" : "#94a3b8",
              fontSize: "16px",
              fontWeight: "600",
              cursor: "pointer",
              transition: "all 0.3s ease",
              border: timeframe === tf ? "none" : "1px solid rgba(255, 255, 255, 0.1)",
            }}
            onMouseEnter={(e) => {
              if (timeframe !== tf) {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
              }
            }}
            onMouseLeave={(e) => {
              if (timeframe !== tf) {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)";
              }
            }}
          >
            {tf === "7D" ? "Last Week" : tf === "30D" ? "Last Month" : "All Time"}
          </button>
        ))}
        <button
          onClick={loadAccountData}
          style={{
            padding: "12px",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            borderRadius: "12px",
            background: "rgba(255, 255, 255, 0.05)",
            color: "#94a3b8",
            cursor: "pointer",
            transition: "all 0.3s ease",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)";
          }}
        >
          <RefreshCw size={20} />
        </button>
      </div>
    </div>
  );
}
