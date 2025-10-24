"use client";

import { BarChart3 } from "lucide-react";
import { useState } from "react";
import { useIsMobile } from "../hooks/useBreakpoint";
import { showError, showSuccess } from "../lib/toast";
import { theme } from "../styles/theme";
import { Button, Card } from "./ui";

interface PatternPerformance {
  pattern_type: string;
  total_occurrences: number;
  successful_trades: number;
  failed_trades: number;
  win_rate: number;
  avg_roi: number;
  avg_hold_days: number;
  best_roi: number;
  worst_roi: number;
  last_seen: string;
}

interface BacktestResult {
  symbol: string;
  start_date: string;
  end_date: string;
  patterns: PatternPerformance[];
  total_patterns: number;
  overall_win_rate: number;
  overall_avg_roi: number;
}

export default function PatternBacktestDashboard() {
  const isMobile = useIsMobile();
  const [symbol, setSymbol] = useState("SPY");
  const [lookbackDays, setLookbackDays] = useState(365);
  const [minConfidence, setMinConfidence] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);

  const runBacktest = async () => {
    if (!symbol.trim()) {
      showError("Please enter a symbol");
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const res = await fetch(
        `/api/proxy/api/ml/backtest-patterns?symbol=${symbol.toUpperCase()}&lookback_days=${lookbackDays}&min_confidence=${minConfidence}`,
        { method: "POST" }
      );

      if (!res.ok) {
        throw new Error(`Backtest failed: ${res.statusText}`);
      }

      const data = await res.json();
      setResult(data);
      showSuccess(`Backtest complete! Found ${data.total_patterns} patterns.`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      showError(`Backtest failed: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getWinRateColor = (winRate: number): string => {
    if (winRate >= 70) return theme.colors.success;
    if (winRate >= 50) return theme.colors.warning;
    return theme.colors.error;
  };

  const getROIColor = (roi: number): string => {
    if (roi >= 5) return theme.colors.success;
    if (roi >= 0) return theme.colors.warning;
    return theme.colors.error;
  };

  const formatPatternName = (pattern: string): string => {
    return pattern
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      {/* Header */}
      <div style={{ marginBottom: theme.spacing.lg }}>
        <h2
          style={{
            margin: 0,
            fontSize: isMobile ? "24px" : "32px",
            fontWeight: "700",
            color: theme.colors.text,
            textShadow: theme.glow.green,
            marginBottom: theme.spacing.xs,
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.sm,
          }}
        >
          <BarChart3 size={32} color={theme.colors.primary} />
          Pattern Backtesting Dashboard
        </h2>
        <p
          style={{
            margin: 0,
            fontSize: "14px",
            color: theme.colors.textMuted,
          }}
        >
          Analyze historical performance of detected chart patterns
        </p>
      </div>

      {/* Configuration Card */}
      <Card glow="green" style={{ marginBottom: theme.spacing.lg }}>
        <h3
          style={{
            fontSize: isMobile ? "18px" : "20px",
            fontWeight: "600",
            color: theme.colors.text,
            marginBottom: theme.spacing.lg,
          }}
        >
          Backtest Configuration
        </h3>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "repeat(3, 1fr)",
            gap: theme.spacing.md,
            marginBottom: theme.spacing.lg,
          }}
        >
          {/* Symbol Input */}
          <div>
            <label
              style={{
                display: "block",
                fontSize: "12px",
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.xs,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
              }}
            >
              Symbol
            </label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              disabled={isLoading}
              placeholder="SPY"
              style={{
                width: "100%",
                padding: "12px",
                background: "rgba(15, 23, 42, 0.5)",
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
                color: theme.colors.text,
                fontSize: "14px",
              }}
            />
          </div>

          {/* Lookback Days */}
          <div>
            <label
              style={{
                display: "block",
                fontSize: "12px",
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.xs,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
              }}
            >
              Lookback Days: {lookbackDays}
            </label>
            <input
              type="range"
              min="30"
              max="730"
              step="30"
              value={lookbackDays}
              onChange={(e) => setLookbackDays(Number(e.target.value))}
              disabled={isLoading}
              style={{
                width: "100%",
                height: "8px",
                borderRadius: "4px",
                outline: "none",
                opacity: isLoading ? 0.5 : 1,
              }}
            />
            <div
              style={{
                fontSize: "11px",
                color: theme.colors.textMuted,
                marginTop: theme.spacing.xs,
              }}
            >
              30 days - 2 years
            </div>
          </div>

          {/* Min Confidence */}
          <div>
            <label
              style={{
                display: "block",
                fontSize: "12px",
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.xs,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
              }}
            >
              Min Confidence: {(minConfidence * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0.5"
              max="0.95"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(Number(e.target.value))}
              disabled={isLoading}
              style={{
                width: "100%",
                height: "8px",
                borderRadius: "4px",
                outline: "none",
                opacity: isLoading ? 0.5 : 1,
              }}
            />
            <div
              style={{
                fontSize: "11px",
                color: theme.colors.textMuted,
                marginTop: theme.spacing.xs,
              }}
            >
              50% - 95%
            </div>
          </div>
        </div>

        <Button
          onClick={runBacktest}
          loading={isLoading}
          disabled={isLoading || !symbol.trim()}
          variant="primary"
          style={{ width: isMobile ? "100%" : "auto" }}
        >
          {isLoading ? "Running Backtest..." : "Run Pattern Backtest"}
        </Button>
      </Card>

      {/* Results */}
      {result && (
        <>
          {/* Summary Card */}
          <Card glow="cyan" style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                fontSize: isMobile ? "18px" : "20px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.lg,
              }}
            >
              📊 Backtest Summary - {result.symbol}
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: isMobile ? "1fr" : "repeat(4, 1fr)",
                gap: theme.spacing.md,
              }}
            >
              {/* Total Patterns */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: "rgba(6, 182, 212, 0.1)",
                  border: `1px solid ${theme.colors.secondary}`,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.xs,
                  }}
                >
                  TOTAL PATTERNS
                </div>
                <div
                  style={{
                    fontSize: "32px",
                    fontWeight: "700",
                    color: theme.colors.secondary,
                  }}
                >
                  {result.total_patterns}
                </div>
              </div>

              {/* Overall Win Rate */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: `rgba(${result.overall_win_rate >= 50 ? "16, 185, 129" : "239, 68, 68"}, 0.1)`,
                  border: `1px solid ${getWinRateColor(result.overall_win_rate)}`,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.xs,
                  }}
                >
                  WIN RATE
                </div>
                <div
                  style={{
                    fontSize: "32px",
                    fontWeight: "700",
                    color: getWinRateColor(result.overall_win_rate),
                  }}
                >
                  {result.overall_win_rate.toFixed(1)}%
                </div>
              </div>

              {/* Overall Avg ROI */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: `rgba(${result.overall_avg_roi >= 0 ? "16, 185, 129" : "239, 68, 68"}, 0.1)`,
                  border: `1px solid ${getROIColor(result.overall_avg_roi)}`,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.xs,
                  }}
                >
                  AVG ROI
                </div>
                <div
                  style={{
                    fontSize: "32px",
                    fontWeight: "700",
                    color: getROIColor(result.overall_avg_roi),
                  }}
                >
                  {result.overall_avg_roi >= 0 ? "+" : ""}
                  {result.overall_avg_roi.toFixed(2)}%
                </div>
              </div>

              {/* Date Range */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: "rgba(139, 92, 246, 0.1)",
                  border: `1px solid ${theme.colors.accent}`,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.xs,
                  }}
                >
                  DATE RANGE
                </div>
                <div
                  style={{
                    fontSize: "11px",
                    fontWeight: "600",
                    color: theme.colors.accent,
                  }}
                >
                  {new Date(result.start_date).toLocaleDateString()}
                  <br />→ {new Date(result.end_date).toLocaleDateString()}
                </div>
              </div>
            </div>
          </Card>

          {/* Pattern Performance Table */}
          <Card glow="purple" style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                fontSize: isMobile ? "18px" : "20px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.lg,
              }}
            >
              📈 Pattern Performance Breakdown
            </h3>

            {result.patterns.length === 0 ? (
              <div
                style={{
                  textAlign: "center",
                  padding: theme.spacing.xl,
                  color: theme.colors.textMuted,
                }}
              >
                No patterns detected during the backtest period.
                <br />
                Try adjusting the lookback days or minimum confidence.
              </div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table
                  style={{
                    width: "100%",
                    borderCollapse: "collapse",
                    fontSize: isMobile ? "12px" : "14px",
                  }}
                >
                  <thead>
                    <tr
                      style={{
                        borderBottom: `1px solid ${theme.colors.border}`,
                      }}
                    >
                      <th
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "left",
                          color: theme.colors.textMuted,
                          fontWeight: "600",
                          textTransform: "uppercase",
                          fontSize: "11px",
                        }}
                      >
                        Pattern
                      </th>
                      <th
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "center",
                          color: theme.colors.textMuted,
                          fontWeight: "600",
                          textTransform: "uppercase",
                          fontSize: "11px",
                        }}
                      >
                        Count
                      </th>
                      <th
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "center",
                          color: theme.colors.textMuted,
                          fontWeight: "600",
                          textTransform: "uppercase",
                          fontSize: "11px",
                        }}
                      >
                        Win/Loss
                      </th>
                      <th
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "center",
                          color: theme.colors.textMuted,
                          fontWeight: "600",
                          textTransform: "uppercase",
                          fontSize: "11px",
                        }}
                      >
                        Win Rate
                      </th>
                      <th
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "center",
                          color: theme.colors.textMuted,
                          fontWeight: "600",
                          textTransform: "uppercase",
                          fontSize: "11px",
                        }}
                      >
                        Avg ROI
                      </th>
                      <th
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "center",
                          color: theme.colors.textMuted,
                          fontWeight: "600",
                          textTransform: "uppercase",
                          fontSize: "11px",
                        }}
                      >
                        Best/Worst
                      </th>
                      <th
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "center",
                          color: theme.colors.textMuted,
                          fontWeight: "600",
                          textTransform: "uppercase",
                          fontSize: "11px",
                        }}
                      >
                        Avg Hold
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.patterns
                      .sort((a, b) => b.win_rate - a.win_rate)
                      .map((pattern, idx) => (
                        <tr
                          key={idx}
                          style={{
                            borderBottom: `1px solid ${theme.colors.border}`,
                          }}
                        >
                          {/* Pattern Name */}
                          <td
                            style={{
                              padding: theme.spacing.sm,
                              color: theme.colors.text,
                              fontWeight: "600",
                            }}
                          >
                            {formatPatternName(pattern.pattern_type)}
                          </td>

                          {/* Count */}
                          <td
                            style={{
                              padding: theme.spacing.sm,
                              textAlign: "center",
                              color: theme.colors.secondary,
                              fontWeight: "600",
                            }}
                          >
                            {pattern.total_occurrences}
                          </td>

                          {/* Win/Loss */}
                          <td
                            style={{
                              padding: theme.spacing.sm,
                              textAlign: "center",
                            }}
                          >
                            <span style={{ color: theme.colors.success }}>
                              {pattern.successful_trades}
                            </span>
                            {" / "}
                            <span style={{ color: theme.colors.error }}>
                              {pattern.failed_trades}
                            </span>
                          </td>

                          {/* Win Rate */}
                          <td
                            style={{
                              padding: theme.spacing.sm,
                              textAlign: "center",
                            }}
                          >
                            <div
                              style={{
                                display: "inline-block",
                                padding: "4px 12px",
                                background: `rgba(${pattern.win_rate >= 50 ? "16, 185, 129" : "239, 68, 68"}, 0.2)`,
                                border: `1px solid ${getWinRateColor(pattern.win_rate)}`,
                                borderRadius: theme.borderRadius.sm,
                                color: getWinRateColor(pattern.win_rate),
                                fontWeight: "700",
                              }}
                            >
                              {pattern.win_rate.toFixed(1)}%
                            </div>
                          </td>

                          {/* Avg ROI */}
                          <td
                            style={{
                              padding: theme.spacing.sm,
                              textAlign: "center",
                              color: getROIColor(pattern.avg_roi),
                              fontWeight: "700",
                            }}
                          >
                            {pattern.avg_roi >= 0 ? "+" : ""}
                            {pattern.avg_roi.toFixed(2)}%
                          </td>

                          {/* Best/Worst */}
                          <td
                            style={{
                              padding: theme.spacing.sm,
                              textAlign: "center",
                              fontSize: "12px",
                            }}
                          >
                            <div style={{ color: theme.colors.success }}>
                              +{pattern.best_roi.toFixed(1)}%
                            </div>
                            <div style={{ color: theme.colors.error }}>
                              {pattern.worst_roi.toFixed(1)}%
                            </div>
                          </td>

                          {/* Avg Hold */}
                          <td
                            style={{
                              padding: theme.spacing.sm,
                              textAlign: "center",
                              color: theme.colors.textMuted,
                            }}
                          >
                            {pattern.avg_hold_days.toFixed(1)}d
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
