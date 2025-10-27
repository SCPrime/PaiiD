"use client";

import { AlertTriangle, PieChart, Shield, Sparkles, Target, TrendingUp } from "lucide-react";
import { useState } from "react";
import { useIsMobile } from "../hooks/useBreakpoint";
import { showError, showSuccess } from "../lib/toast";
import { theme } from "../styles/theme";
import { Button, Card } from "./ui";

// Unused interface kept for future reference
// eslint-disable-next-line @typescript-eslint/no-unused-vars
interface _Position {
  symbol: string;
  shares: number;
  current_price: number;
  market_value: number;
  weight: number;
}

interface OptimizationSuggestion {
  symbol: string;
  action: "buy" | "sell" | "hold";
  current_shares: number;
  suggested_shares: number;
  shares_delta: number;
  current_weight: number;
  target_weight: number;
  reasoning: string;
  expected_return: number;
  risk_score: number;
}

interface PortfolioMetrics {
  total_value: number;
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
  diversification_score: number;
  risk_level: "low" | "moderate" | "high";
}

interface OptimizationResult {
  current_portfolio: PortfolioMetrics;
  optimized_portfolio: PortfolioMetrics;
  suggestions: OptimizationSuggestion[];
  risk_adjusted: boolean;
  optimization_method: string;
  estimated_improvement: number;
}

export default function PortfolioOptimizer() {
  const isMobile = useIsMobile();
  const [riskTolerance, setRiskTolerance] = useState<"conservative" | "moderate" | "aggressive">(
    "moderate"
  );
  const [targetReturn, setTargetReturn] = useState(12);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [result, setResult] = useState<OptimizationResult | null>(null);

  const optimizePortfolio = async () => {
    setIsOptimizing(true);
    try {
      const res = await fetch(
        `/api/proxy/api/ml/optimize-portfolio?risk_tolerance=${riskTolerance}&target_return=${targetReturn}`,
        { method: "POST" }
      );

      if (!res.ok) throw new Error("Optimization failed");
      const data = await res.json();
      setResult(data);
      showSuccess("Portfolio optimization complete!");
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      showError(`Optimization failed: ${errorMessage}`);
    } finally {
      setIsOptimizing(false);
    }
  };

  const getRiskColor = (riskLevel: string): string => {
    switch (riskLevel) {
      case "low":
        return theme.colors.success;
      case "moderate":
        return theme.colors.warning;
      case "high":
        return theme.colors.danger;
      default:
        return theme.colors.text;
    }
  };

  const getActionColor = (action: string): string => {
    switch (action) {
      case "buy":
        return theme.colors.success;
      case "sell":
        return theme.colors.danger;
      case "hold":
        return theme.colors.textMuted;
      default:
        return theme.colors.text;
    }
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case "buy":
        return <TrendingUp size={18} color={theme.colors.success} />;
      case "sell":
        return <AlertTriangle size={18} color={theme.colors.danger} />;
      case "hold":
        return <Shield size={18} color={theme.colors.textMuted} />;
      default:
        return null;
    }
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
            textShadow: theme.glow.cyan,
            marginBottom: theme.spacing.xs,
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.sm,
          }}
        >
          <Target size={32} color={theme.colors.secondary} />
          AI Portfolio Optimizer
        </h2>
        <p
          style={{
            margin: 0,
            fontSize: "14px",
            color: theme.colors.textMuted,
          }}
        >
          ML-powered portfolio rebalancing and risk optimization
        </p>
      </div>

      {/* Configuration Card */}
      <Card glow="cyan" style={{ marginBottom: theme.spacing.lg }}>
        <h3
          style={{
            fontSize: isMobile ? "18px" : "20px",
            fontWeight: "600",
            color: theme.colors.text,
            marginBottom: theme.spacing.lg,
          }}
        >
          Optimization Parameters
        </h3>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)",
            gap: theme.spacing.lg,
            marginBottom: theme.spacing.lg,
          }}
        >
          {/* Risk Tolerance */}
          <div>
            <label
              style={{
                display: "block",
                fontSize: "12px",
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.sm,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
              }}
            >
              Risk Tolerance
            </label>
            <div style={{ display: "flex", gap: theme.spacing.xs }}>
              {["conservative", "moderate", "aggressive"].map((level) => (
                <button
                  key={level}
                  onClick={() => setRiskTolerance(level as typeof riskTolerance)}
                  disabled={isOptimizing}
                  style={{
                    flex: 1,
                    padding: "12px",
                    background:
                      riskTolerance === level
                        ? `linear-gradient(135deg, ${theme.colors.secondary}, ${theme.colors.primary})`
                        : "rgba(15, 23, 42, 0.5)",
                    border: `1px solid ${riskTolerance === level ? theme.colors.secondary : theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: "13px",
                    fontWeight: riskTolerance === level ? "700" : "400",
                    cursor: isOptimizing ? "not-allowed" : "pointer",
                    textTransform: "capitalize",
                    transition: "all 0.2s",
                  }}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Target Return */}
          <div>
            <label
              style={{
                display: "block",
                fontSize: "12px",
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.sm,
                textTransform: "uppercase",
                letterSpacing: "0.5px",
              }}
            >
              Target Annual Return: {targetReturn}%
            </label>
            <input
              type="range"
              min="5"
              max="30"
              step="1"
              value={targetReturn}
              onChange={(e) => setTargetReturn(Number(e.target.value))}
              disabled={isOptimizing}
              style={{
                width: "100%",
                height: "8px",
                borderRadius: "4px",
                outline: "none",
                opacity: isOptimizing ? 0.5 : 1,
              }}
            />
            <div
              style={{
                fontSize: "11px",
                color: theme.colors.textMuted,
                marginTop: theme.spacing.xs,
              }}
            >
              5% (conservative) - 30% (aggressive)
            </div>
          </div>
        </div>

        <Button
          onClick={optimizePortfolio}
          loading={isOptimizing}
          disabled={isOptimizing}
          variant="primary"
          style={{ width: isMobile ? "100%" : "auto" }}
        >
          {isOptimizing ? "Optimizing..." : "Optimize Portfolio"}
        </Button>
      </Card>

      {/* Results */}
      {result && (
        <>
          {/* Comparison Card */}
          <Card glow="purple" style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                fontSize: isMobile ? "18px" : "20px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.lg,
                display: "flex",
                alignItems: "center",
                gap: theme.spacing.sm,
              }}
            >
              <Sparkles size={24} color={theme.colors.accent} />
              Portfolio Comparison
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)",
                gap: theme.spacing.lg,
              }}
            >
              {/* Current Portfolio */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: "rgba(15, 23, 42, 0.5)",
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                }}
              >
                <h4
                  style={{
                    margin: 0,
                    fontSize: "16px",
                    fontWeight: "600",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.md,
                  }}
                >
                  Current Portfolio
                </h4>

                <div style={{ display: "grid", gap: theme.spacing.sm }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Total Value
                    </span>
                    <span style={{ fontSize: "16px", fontWeight: "700", color: theme.colors.text }}>
                      ${result.current_portfolio.total_value.toLocaleString()}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Expected Return
                    </span>
                    <span style={{ fontSize: "16px", fontWeight: "700", color: theme.colors.text }}>
                      {result.current_portfolio.expected_return.toFixed(2)}%
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Volatility
                    </span>
                    <span
                      style={{ fontSize: "16px", fontWeight: "700", color: theme.colors.warning }}
                    >
                      {result.current_portfolio.volatility.toFixed(2)}%
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Sharpe Ratio
                    </span>
                    <span
                      style={{ fontSize: "16px", fontWeight: "700", color: theme.colors.secondary }}
                    >
                      {result.current_portfolio.sharpe_ratio.toFixed(2)}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Diversification
                    </span>
                    <span
                      style={{
                        fontSize: "16px",
                        fontWeight: "700",
                        color: getRiskColor(result.current_portfolio.risk_level),
                      }}
                    >
                      {result.current_portfolio.diversification_score.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Optimized Portfolio */}
              <div
                style={{
                  padding: theme.spacing.md,
                  background: `linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(6, 182, 212, 0.1))`,
                  border: `2px solid ${theme.colors.success}`,
                  borderRadius: theme.borderRadius.md,
                  boxShadow: theme.glow.green,
                }}
              >
                <h4
                  style={{
                    margin: 0,
                    fontSize: "16px",
                    fontWeight: "600",
                    color: theme.colors.success,
                    marginBottom: theme.spacing.md,
                  }}
                >
                  ✨ Optimized Portfolio
                </h4>

                <div style={{ display: "grid", gap: theme.spacing.sm }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Total Value
                    </span>
                    <span style={{ fontSize: "16px", fontWeight: "700", color: theme.colors.text }}>
                      ${result.optimized_portfolio.total_value.toLocaleString()}
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Expected Return
                    </span>
                    <span
                      style={{ fontSize: "16px", fontWeight: "700", color: theme.colors.success }}
                    >
                      {result.optimized_portfolio.expected_return.toFixed(2)}%{" "}
                      <span style={{ fontSize: "12px" }}>
                        (+
                        {(
                          result.optimized_portfolio.expected_return -
                          result.current_portfolio.expected_return
                        ).toFixed(2)}
                        %)
                      </span>
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Volatility
                    </span>
                    <span
                      style={{ fontSize: "16px", fontWeight: "700", color: theme.colors.success }}
                    >
                      {result.optimized_portfolio.volatility.toFixed(2)}%{" "}
                      <span style={{ fontSize: "12px" }}>
                        (
                        {result.optimized_portfolio.volatility < result.current_portfolio.volatility
                          ? "-"
                          : "+"}
                        {Math.abs(
                          result.optimized_portfolio.volatility -
                            result.current_portfolio.volatility
                        ).toFixed(2)}
                        %)
                      </span>
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Sharpe Ratio
                    </span>
                    <span
                      style={{ fontSize: "16px", fontWeight: "700", color: theme.colors.success }}
                    >
                      {result.optimized_portfolio.sharpe_ratio.toFixed(2)}{" "}
                      <span style={{ fontSize: "12px" }}>
                        (+
                        {(
                          result.optimized_portfolio.sharpe_ratio -
                          result.current_portfolio.sharpe_ratio
                        ).toFixed(2)}
                        )
                      </span>
                    </span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>
                      Diversification
                    </span>
                    <span
                      style={{ fontSize: "16px", fontWeight: "700", color: theme.colors.success }}
                    >
                      {result.optimized_portfolio.diversification_score.toFixed(0)}%{" "}
                      <span style={{ fontSize: "12px" }}>
                        (+
                        {(
                          result.optimized_portfolio.diversification_score -
                          result.current_portfolio.diversification_score
                        ).toFixed(0)}
                        %)
                      </span>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Improvement Badge */}
            <div
              style={{
                marginTop: theme.spacing.lg,
                padding: theme.spacing.md,
                background: "rgba(16, 185, 129, 0.1)",
                border: `1px solid ${theme.colors.success}`,
                borderRadius: theme.borderRadius.md,
                textAlign: "center",
              }}
            >
              <div
                style={{
                  fontSize: "13px",
                  color: theme.colors.textMuted,
                  marginBottom: theme.spacing.xs,
                }}
              >
                Estimated Improvement
              </div>
              <div
                style={{
                  fontSize: "32px",
                  fontWeight: "700",
                  color: theme.colors.success,
                }}
              >
                +{result.estimated_improvement.toFixed(1)}%
              </div>
              <div
                style={{
                  fontSize: "12px",
                  color: theme.colors.textMuted,
                  marginTop: theme.spacing.xs,
                }}
              >
                Risk-adjusted annual return improvement
              </div>
            </div>
          </Card>

          {/* Suggestions */}
          <Card glow="green" style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                fontSize: isMobile ? "18px" : "20px",
                fontWeight: "600",
                color: theme.colors.text,
                marginBottom: theme.spacing.lg,
                display: "flex",
                alignItems: "center",
                gap: theme.spacing.sm,
              }}
            >
              <PieChart size={24} color={theme.colors.primary} />
              Rebalancing Suggestions
            </h3>

            <div style={{ display: "grid", gap: theme.spacing.md }}>
              {result.suggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: theme.spacing.md,
                    background: "rgba(15, 23, 42, 0.5)",
                    border: `1px solid ${getActionColor(suggestion.action)}`,
                    borderRadius: theme.borderRadius.md,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}>
                      <div
                        style={{
                          fontSize: "20px",
                          fontWeight: "700",
                          color: theme.colors.text,
                        }}
                      >
                        {suggestion.symbol}
                      </div>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "4px",
                          padding: "4px 12px",
                          background: `rgba(${
                            suggestion.action === "buy"
                              ? "16, 185, 129"
                              : suggestion.action === "sell"
                                ? "239, 68, 68"
                                : "148, 163, 184"
                          }, 0.2)`,
                          border: `1px solid ${getActionColor(suggestion.action)}`,
                          borderRadius: theme.borderRadius.sm,
                        }}
                      >
                        {getActionIcon(suggestion.action)}
                        <span
                          style={{
                            fontSize: "12px",
                            fontWeight: "700",
                            color: getActionColor(suggestion.action),
                            textTransform: "uppercase",
                          }}
                        >
                          {suggestion.action}
                        </span>
                      </div>
                    </div>

                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontSize: "12px", color: theme.colors.textMuted }}>
                        {suggestion.current_shares} → {suggestion.suggested_shares} shares
                      </div>
                      <div
                        style={{
                          fontSize: "16px",
                          fontWeight: "700",
                          color:
                            suggestion.shares_delta >= 0
                              ? theme.colors.success
                              : theme.colors.danger,
                        }}
                      >
                        {suggestion.shares_delta >= 0 ? "+" : ""}
                        {suggestion.shares_delta}
                      </div>
                    </div>
                  </div>

                  <div
                    style={{
                      fontSize: "13px",
                      color: theme.colors.text,
                      marginBottom: theme.spacing.sm,
                      lineHeight: "1.6",
                    }}
                  >
                    {suggestion.reasoning}
                  </div>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: isMobile ? "1fr" : "repeat(4, 1fr)",
                      gap: theme.spacing.sm,
                      fontSize: "12px",
                    }}
                  >
                    <div>
                      <span style={{ color: theme.colors.textMuted }}>Current Weight: </span>
                      <span style={{ color: theme.colors.text, fontWeight: "600" }}>
                        {suggestion.current_weight.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span style={{ color: theme.colors.textMuted }}>Target Weight: </span>
                      <span style={{ color: theme.colors.secondary, fontWeight: "600" }}>
                        {suggestion.target_weight.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span style={{ color: theme.colors.textMuted }}>Expected Return: </span>
                      <span style={{ color: theme.colors.success, fontWeight: "600" }}>
                        {suggestion.expected_return.toFixed(1)}%
                      </span>
                    </div>
                    <div>
                      <span style={{ color: theme.colors.textMuted }}>Risk Score: </span>
                      <span
                        style={{
                          color: getRiskColor(
                            suggestion.risk_score > 0.7
                              ? "high"
                              : suggestion.risk_score > 0.4
                                ? "moderate"
                                : "low"
                          ),
                          fontWeight: "600",
                        }}
                      >
                        {(suggestion.risk_score * 100).toFixed(0)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
