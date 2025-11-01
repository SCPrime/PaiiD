"use client";
import {
  Brain,
  ChevronDown,
  ChevronUp,
  DollarSign,
  RefreshCw,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { useEffect, useState, type CSSProperties } from "react";
import { useIsMobile } from "../hooks/useBreakpoint";
import { alpaca, formatPosition } from "../lib/alpaca";
import { logger } from "../lib/logger";
import { theme } from "../styles/theme";
import { Button, Card } from "./ui";
import { EmptyState, ErrorState, SkeletonCard, Spinner } from "./ui/LoadingStates";

const withAlpha = (hex: string, alpha: number) => {
  const cleaned = hex.replace("#", "");
  const bigint = parseInt(cleaned, 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

const glassSurface = (overrides: CSSProperties = {}) => ({
  backgroundColor: theme.background.card,
  backdropFilter: theme.blur.light,
  border: `1px solid ${theme.colors.border}`,
  borderRadius: theme.borderRadius.md,
  ...overrides,
});
// import { usePositionUpdates } from "../hooks/usePositionUpdates"; // DISABLED: Using REST API instead

interface Position {
  symbol: string;
  qty: number;
  avgEntryPrice: number;
  currentPrice: number;
  marketValue: number;
  unrealizedPL: number;
  unrealizedPLPercent: number;
  side: "long" | "short";
  dayChange: number;
  dayChangePercent: number;
}

interface PortfolioMetrics {
  totalValue: number;
  buyingPower: number;
  totalPL: number;
  totalPLPercent: number;
  dayPL: number;
  dayPLPercent: number;
  positionCount: number;
}

interface AIPositionAnalysis {
  symbol: string;
  recommendation: "HOLD" | "ADD" | "TRIM" | "EXIT";
  confidence: number;
  riskScore: "LOW" | "MEDIUM" | "HIGH";
  sentiment: string;
  suggestedAction: string;
  exitStrategy?: {
    profitTarget: number;
    stopLoss: number;
  };
  currentPrice: number;
  analysis: string;
}

export default function ActivePositions() {
  const isMobile = useIsMobile();
  const [positions, setPositions] = useState<Position[]>([]);
  const [metrics, setMetrics] = useState<PortfolioMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<"symbol" | "pl" | "plPercent" | "value">("symbol");

  // AI Analysis state
  const [aiAnalysisMap, setAiAnalysisMap] = useState<Record<string, AIPositionAnalysis>>({});
  const [aiLoadingMap, setAiLoadingMap] = useState<Record<string, boolean>>({});
  const [aiErrorMap, setAiErrorMap] = useState<Record<string, string>>({});
  const [expandedPositions, setExpandedPositions] = useState<Set<string>>(new Set());

  // DISABLED: Real-time position updates via SSE (not working reliably)
  // Switched to REST API polling instead
  // const {
  //   positions: streamedPositions,
  //   connected,
  //   connecting,
  //   error: _streamError,
  //   reconnect: _reconnect,
  // } = usePositionUpdates({
  //   autoReconnect: true,
  //   maxReconnectAttempts: 5,
  //   debug: false,
  // });

  // // Use streamed positions when available
  // useEffect(() => {
  //   if (streamedPositions.length > 0) {
  //     setPositions(streamedPositions);
  //     calculateMetrics(streamedPositions);
  //   }
  // }, [streamedPositions]);

  // Initial load and polling via REST API
  useEffect(() => {
    loadPositions();
    // Poll every 5 seconds for position updates
    const interval = setInterval(loadPositions, 5000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Calculate portfolio metrics from positions
  const calculateMetrics = async (positionsList: Position[]) => {
    try {
      // Fetch account data for buying power
      const account = await alpaca.getAccount();

      const totalValue = positionsList.reduce((sum, p) => sum + p.marketValue, 0);
      const totalPL = positionsList.reduce((sum, p) => sum + p.unrealizedPL, 0);
      const totalCost = positionsList.reduce((sum, p) => sum + p.avgEntryPrice * p.qty, 0);
      const dayPL = positionsList.reduce((sum, p) => sum + p.dayChange * p.qty, 0);

      const calculatedMetrics: PortfolioMetrics = {
        totalValue,
        buyingPower: parseFloat(account.buying_power),
        totalPL,
        totalPLPercent: totalCost > 0 ? (totalPL / totalCost) * 100 : 0,
        dayPL,
        dayPLPercent: totalValue - dayPL > 0 ? (dayPL / (totalValue - dayPL)) * 100 : 0,
        positionCount: positionsList.length,
      };

      setMetrics(calculatedMetrics);
    } catch (error) {
      logger.error("Failed to calculate metrics", error);
    }
  };

  const loadPositions = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch positions from Alpaca
      const alpacaPositions = await alpaca.getPositions();

      // Format positions for UI
      const formattedPositions: Position[] = alpacaPositions.map(formatPosition);

      setPositions(formattedPositions);
      await calculateMetrics(formattedPositions);
    } catch (error) {
      logger.error("Failed to load positions", error);
      setError(error instanceof Error ? error.message : "Failed to load positions");
      // Keep existing data if refresh fails
    } finally {
      setLoading(false);
    }
  };

  const sortPositions = (positions: Position[]) => {
    return [...positions].sort((a, b) => {
      switch (sortBy) {
        case "symbol":
          return a.symbol.localeCompare(b.symbol);
        case "pl":
          return b.unrealizedPL - a.unrealizedPL;
        case "plPercent":
          return b.unrealizedPLPercent - a.unrealizedPLPercent;
        case "value":
          return b.marketValue - a.marketValue;
        default:
          return 0;
      }
    });
  };

  // Fetch AI analysis for a position
  const fetchAIAnalysis = async (symbol: string) => {
    setAiLoadingMap((prev) => ({ ...prev, [symbol]: true }));
    setAiErrorMap((prev) => ({ ...prev, [symbol]: "" }));

    try {
      const response = await fetch(`/api/proxy/api/ai/analyze-symbol/${symbol}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch AI analysis: ${response.statusText}`);
      }

      const data = await response.json();

      // Transform the analyze-symbol response to position analysis format
      const analysis: AIPositionAnalysis = {
        symbol: data.symbol,
        recommendation: data.momentum?.toLowerCase().includes("bullish")
          ? "ADD"
          : data.momentum?.toLowerCase().includes("bearish")
            ? "TRIM"
            : "HOLD",
        confidence: data.confidence_score || 0,
        riskScore: data.risk_assessment?.toLowerCase().includes("low")
          ? "LOW"
          : data.risk_assessment?.toLowerCase().includes("high")
            ? "HIGH"
            : "MEDIUM",
        sentiment: data.momentum || "Neutral",
        suggestedAction: data.entry_suggestion || data.summary || "",
        exitStrategy: data.take_profit_suggestion
          ? {
              profitTarget: data.take_profit_suggestion,
              stopLoss: data.stop_loss_suggestion,
            }
          : undefined,
        currentPrice: data.current_price,
        analysis: data.analysis || data.summary || "",
      };

      setAiAnalysisMap((prev) => ({ ...prev, [symbol]: analysis }));
    } catch (error: unknown) {
      logger.error(`AI analysis error for ${symbol}`, error);
      setAiErrorMap((prev) => ({
        ...prev,
        [symbol]: error instanceof Error ? error.message : "Unknown error",
      }));
    } finally {
      setAiLoadingMap((prev) => ({ ...prev, [symbol]: false }));
    }
  };

  // Toggle AI analysis panel for a position
  const toggleAIAnalysis = (symbol: string) => {
    const newExpanded = new Set(expandedPositions);

    if (newExpanded.has(symbol)) {
      newExpanded.delete(symbol);
    } else {
      newExpanded.add(symbol);
      // Fetch AI analysis if not already loaded
      if (!aiAnalysisMap[symbol] && !aiLoadingMap[symbol]) {
        fetchAIAnalysis(symbol);
      }
    }

    setExpandedPositions(newExpanded);
  };

  // Get color for recommendation badge
  const getRecommendationColor = (recommendation: string) => {
    switch (recommendation) {
      case "HOLD":
        return {
          bg: withAlpha(theme.colors.accent, 0.2),
          border: theme.colors.accent,
          text: theme.colors.accent,
        };
      case "ADD":
        return {
          bg: withAlpha(theme.colors.primary, 0.2),
          border: theme.colors.primary,
          text: theme.colors.primary,
        };
      case "TRIM":
        return {
          bg: withAlpha(theme.colors.warning, 0.2),
          border: theme.colors.warning,
          text: theme.colors.warning,
        };
      case "EXIT":
        return {
          bg: withAlpha(theme.colors.danger, 0.2),
          border: theme.colors.danger,
          text: theme.colors.danger,
        };
      default:
        return {
          bg: withAlpha(theme.colors.textMuted, 0.25),
          border: theme.colors.textMuted,
          text: theme.colors.textMuted,
        };
    }
  };

  // Get color for risk score badge
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "LOW":
        return {
          bg: withAlpha(theme.colors.primary, 0.2),
          border: theme.colors.primary,
          text: theme.colors.primary,
        };
      case "MEDIUM":
        return {
          bg: withAlpha(theme.colors.warning, 0.2),
          border: theme.colors.warning,
          text: theme.colors.warning,
        };
      case "HIGH":
        return {
          bg: withAlpha(theme.colors.danger, 0.2),
          border: theme.colors.danger,
          text: theme.colors.danger,
        };
      default:
        return {
          bg: withAlpha(theme.colors.textMuted, 0.25),
          border: theme.colors.textMuted,
          text: theme.colors.textMuted,
        };
    }
  };

  // Add keyframes animation to document head (only once)
  useEffect(() => {
    const styleId = "spinner-keyframes";
    if (!document.getElementById(styleId)) {
      const style = document.createElement("style");
      style.id = styleId;
      style.textContent = `
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `;
      document.head.appendChild(style);
    }
  }, []);

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      {/* Header with PaiiD Logo */}
      <div
        style={{
          display: "flex",
          flexDirection: isMobile ? "column" : "row",
          alignItems: isMobile ? "flex-start" : "center",
          justifyContent: "space-between",
          gap: isMobile ? theme.spacing.sm : 0,
          marginBottom: theme.spacing.lg,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: isMobile ? theme.spacing.sm : theme.spacing.md,
          }}
        >
          {/* PaiiD Logo */}
          <div style={{ fontSize: isMobile ? "28px" : "42px", fontWeight: "900", lineHeight: "1" }}>
            <span
              style={{
                background: `linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.secondary} 100%)`, // backdrop-filter not required (text gradient)
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                filter: `drop-shadow(0 3px 8px ${withAlpha(theme.colors.primary, 0.4)})`,
              }}
            >
              P
            </span>
            <span
              style={{
                background: `linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.secondary} 100%)`, // backdrop-filter not required (text gradient)
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                textShadow: `0 0 18px ${withAlpha(theme.colors.aiGlow, 0.75)}, 0 0 36px ${withAlpha(theme.colors.aiGlow, 0.45)}`,
                animation: "glow-ai 3s ease-in-out infinite",
              }}
            >
              aii
            </span>
            <span
              style={{
                background: `linear-gradient(135deg, ${theme.colors.primary} 0%, ${theme.colors.secondary} 100%)`, // backdrop-filter not required (text gradient)
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                filter: `drop-shadow(0 3px 8px ${withAlpha(theme.colors.primary, 0.4)})`,
              }}
            >
              D
            </span>
          </div>

          <TrendingUp size={isMobile ? 24 : 32} color={theme.colors.primary} />
          <h1
            style={{
              margin: 0,
              fontSize: isMobile ? "24px" : "32px",
              fontWeight: "700",
              color: theme.colors.text,
              textShadow: theme.glow.green,
            }}
          >
            Active Positions
          </h1>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.sm,
            width: isMobile ? "100%" : "auto",
          }}
        >
          {/* Connection Status Indicator - REMOVED: Now using REST API polling instead of SSE */}

          <Button
            variant="secondary"
            size="sm"
            onClick={loadPositions}
            style={{ flex: isMobile ? "1" : "none" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.xs }}>
              <RefreshCw size={16} />
              {!isMobile && "Refresh"}
            </div>
          </Button>
        </div>
      </div>

      {/* Error State */}
      {error && !loading && (
        <ErrorState message={error} onRetry={loadPositions} isRetrying={loading} />
      )}

      {/* Loading State with Skeleton Screens */}
      {loading && positions.length === 0 ? (
        <Card>
          <div style={{ padding: theme.spacing.md }}>
            <SkeletonCard height="100px" />
            <SkeletonCard height="100px" />
            <SkeletonCard height="100px" />
          </div>
        </Card>
      ) : (
        <>
          {/* Portfolio Metrics */}
          {metrics && (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: isMobile ? "1fr" : "repeat(auto-fit, minmax(200px, 1fr))",
                gap: theme.spacing.md,
                marginBottom: theme.spacing.lg,
              }}
            >
              <MetricCard
                icon={<DollarSign size={20} color={theme.colors.secondary} />}
                label="Total Value"
                value={`$${metrics.totalValue.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              />
              <MetricCard
                icon={<DollarSign size={20} color={theme.colors.info} />}
                label="Buying Power"
                value={`$${metrics.buyingPower.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              />
              <MetricCard
                icon={
                  metrics.totalPL >= 0 ? (
                    <TrendingUp size={20} color={theme.colors.primary} />
                  ) : (
                    <TrendingDown size={20} color={theme.colors.danger} />
                  )
                }
                label="Total P&L"
                value={`${metrics.totalPL >= 0 ? "+" : ""}$${Math.abs(metrics.totalPL).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                subValue={`${metrics.totalPLPercent >= 0 ? "+" : ""}${metrics.totalPLPercent.toFixed(2)}%`}
                valueColor={metrics.totalPL >= 0 ? theme.colors.primary : theme.colors.danger}
              />
              <MetricCard
                icon={
                  metrics.dayPL >= 0 ? (
                    <TrendingUp size={20} color={theme.colors.primary} />
                  ) : (
                    <TrendingDown size={20} color={theme.colors.danger} />
                  )
                }
                label="Today's P&L"
                value={`${metrics.dayPL >= 0 ? "+" : ""}$${Math.abs(metrics.dayPL).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                subValue={`${metrics.dayPLPercent >= 0 ? "+" : ""}${metrics.dayPLPercent.toFixed(2)}%`}
                valueColor={metrics.dayPL >= 0 ? theme.colors.primary : theme.colors.danger}
              />
            </div>
          )}

          {/* Sort Controls */}
          <Card style={{ marginBottom: theme.spacing.md, padding: theme.spacing.md }}>
            <div
              style={{
                display: "flex",
                flexDirection: isMobile ? "column" : "row",
                alignItems: isMobile ? "flex-start" : "center",
                gap: theme.spacing.sm,
              }}
            >
              <span style={{ color: theme.colors.textMuted, fontSize: "14px" }}>Sort by:</span>
              <div style={{ display: "flex", gap: theme.spacing.sm, flexWrap: "wrap" }}>
                {(["symbol", "pl", "plPercent", "value"] as const).map((sort) => (
                  <button
                    key={sort}
                    onClick={() => setSortBy(sort)}
                    style={{
                      ...glassSurface({
                        padding: `${theme.spacing.xs} ${theme.spacing.md}`,
                        borderRadius: theme.borderRadius.sm,
                        backgroundColor:
                          sortBy === sort
                            ? withAlpha(theme.colors.primary, 0.25)
                            : theme.background.input,
                        border: `1px solid ${
                          sortBy === sort
                            ? withAlpha(theme.colors.primary, 0.4)
                            : theme.colors.border
                        }`,
                      }),
                      boxShadow: sortBy === sort ? theme.glow.teal : "none",
                      color: theme.colors.text,
                      cursor: "pointer",
                      fontSize: "14px",
                      fontWeight: sortBy === sort ? "600" : "400",
                      transition: theme.transitions.fast,
                    }}
                  >
                    {sort === "pl"
                      ? "P&L"
                      : sort === "plPercent"
                        ? "P&L %"
                        : sort.charAt(0).toUpperCase() + sort.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </Card>

          {/* Positions List */}
          {positions.length === 0 && !error ? (
            <EmptyState
              icon="📊"
              title="No Active Positions"
              description="You don't have any open positions yet. Execute a trade to get started!"
              actionLabel="Execute Trade"
              onAction={() => {
                // Navigate to execute trade workflow
                const event = new CustomEvent("workflow-select", {
                  detail: { workflow: "execute" },
                });
                window.dispatchEvent(event);
              }}
            />
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.md }}>
              {sortPositions(positions).map((position) => (
                <Card key={position.symbol} glow={position.unrealizedPL >= 0 ? "green" : undefined}>
                  <div
                    style={{
                      display: "flex",
                      flexDirection: isMobile ? "column" : "row",
                      justifyContent: "space-between",
                      gap: isMobile ? theme.spacing.sm : 0,
                      marginBottom: theme.spacing.md,
                    }}
                  >
                    <div>
                      <h3
                        style={{
                          margin: 0,
                          fontSize: isMobile ? "20px" : "24px",
                          fontWeight: "700",
                          color: theme.colors.text,
                        }}
                      >
                        {position.symbol}
                      </h3>
                      <p
                        style={{
                          margin: `${theme.spacing.xs} 0 0 0`,
                          color: theme.colors.textMuted,
                          fontSize: "14px",
                        }}
                      >
                        {position.qty} shares @ ${position.avgEntryPrice.toFixed(2)}
                      </p>
                    </div>
                    <div style={{ textAlign: isMobile ? "left" : "right" }}>
                      <p
                        style={{
                          margin: 0,
                          fontSize: isMobile ? "20px" : "24px",
                          fontWeight: "700",
                          color: theme.colors.text,
                        }}
                      >
                        ${position.currentPrice.toFixed(2)}
                      </p>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: theme.spacing.xs,
                          justifyContent: "flex-end",
                        }}
                      >
                        {position.dayChange >= 0 ? (
                          <TrendingUp size={16} color={theme.colors.primary} />
                        ) : (
                          <TrendingDown size={16} color={theme.colors.danger} />
                        )}
                        <span
                          style={{
                            fontSize: "14px",
                            fontWeight: "500",
                            color:
                              position.dayChange >= 0 ? theme.colors.primary : theme.colors.danger,
                          }}
                        >
                          {position.dayChange >= 0 ? "+" : ""}
                          {position.dayChange.toFixed(2)} (
                          {position.dayChangePercent >= 0 ? "+" : ""}
                          {position.dayChangePercent.toFixed(2)}%)
                        </span>
                      </div>
                    </div>
                  </div>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: isMobile ? "1fr" : "repeat(3, 1fr)",
                      gap: theme.spacing.md,
                      paddingTop: theme.spacing.md,
                      borderTop: `1px solid ${theme.colors.border}`,
                    }}
                  >
                    <div>
                      <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                        Market Value
                      </p>
                      <p
                        style={{
                          fontSize: "18px",
                          fontWeight: "600",
                          color: theme.colors.text,
                          margin: `${theme.spacing.xs} 0 0 0`,
                        }}
                      >
                        $
                        {position.marketValue.toLocaleString("en-US", {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </p>
                    </div>
                    <div>
                      <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                        Unrealized P&L
                      </p>
                      <p
                        style={{
                          fontSize: "18px",
                          fontWeight: "600",
                          color:
                            position.unrealizedPL >= 0 ? theme.colors.primary : theme.colors.danger,
                          margin: `${theme.spacing.xs} 0 0 0`,
                        }}
                      >
                        {position.unrealizedPL >= 0 ? "+" : ""}$
                        {Math.abs(position.unrealizedPL).toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>
                        Return
                      </p>
                      <p
                        style={{
                          fontSize: "18px",
                          fontWeight: "600",
                          color:
                            position.unrealizedPLPercent >= 0
                              ? theme.colors.primary
                              : theme.colors.danger,
                          margin: `${theme.spacing.xs} 0 0 0`,
                        }}
                      >
                        {position.unrealizedPLPercent >= 0 ? "+" : ""}
                        {position.unrealizedPLPercent.toFixed(2)}%
                      </p>
                    </div>
                  </div>

                  {/* AI Insights Button */}
                  <Button
                    variant="secondary"
                    size="sm"
                    style={{
                      marginTop: theme.spacing.md,
                      width: "100%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: theme.spacing.xs,
                    }}
                    onClick={() => toggleAIAnalysis(position.symbol)}
                  >
                    <Brain size={18} />
                    <span>
                      {expandedPositions.has(position.symbol) ? "Hide" : "Show"} AI Insights
                    </span>
                    {expandedPositions.has(position.symbol) ? (
                      <ChevronUp size={16} />
                    ) : (
                      <ChevronDown size={16} />
                    )}
                  </Button>

                  {/* AI Analysis Panel */}
                  {expandedPositions.has(position.symbol) && (
                    <div
                      style={{
                        ...glassSurface({
                          padding: theme.spacing.lg,
                          borderRadius: theme.borderRadius.lg,
                          backgroundColor: aiAnalysisMap[position.symbol]
                            ? theme.background.input
                            : withAlpha(theme.colors.textMuted, 0.12),
                          border: `1px solid ${
                            aiAnalysisMap[position.symbol]
                              ? withAlpha(theme.colors.primary, 0.45)
                              : theme.colors.border
                          }`,
                        }),
                        marginTop: theme.spacing.md,
                        boxShadow: aiAnalysisMap[position.symbol]
                          ? `0 0 15px ${withAlpha(theme.colors.aiGlow, 0.35)}`
                          : "none",
                        transition: "all 0.3s ease",
                      }}
                    >
                      {/* Loading State */}
                      {aiLoadingMap[position.symbol] && (
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: theme.spacing.sm,
                            color: theme.colors.textMuted,
                            fontSize: "13px",
                          }}
                        >
                          <Spinner size="small" color={theme.colors.primary} />
                          <span>Analyzing {position.symbol}...</span>
                        </div>
                      )}

                      {/* Error State */}
                      {aiErrorMap[position.symbol] && !aiLoadingMap[position.symbol] && (
                        <div
                          style={{
                            color: theme.colors.danger,
                            fontSize: "13px",
                            display: "flex",
                            alignItems: "center",
                            gap: theme.spacing.sm,
                          }}
                        >
                          <span>⚠️</span>
                          <span>AI analysis unavailable: {aiErrorMap[position.symbol]}</span>
                        </div>
                      )}

                      {/* AI Analysis Display */}
                      {aiAnalysisMap[position.symbol] && !aiLoadingMap[position.symbol] && (
                        <div>
                          {/* Header with Recommendation and Confidence */}
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "space-between",
                              marginBottom: theme.spacing.md,
                              flexWrap: isMobile ? "wrap" : "nowrap",
                              gap: theme.spacing.sm,
                            }}
                          >
                            <h4
                              style={{
                                margin: 0,
                                fontSize: "16px",
                                fontWeight: "600",
                                color: theme.colors.text,
                                display: "flex",
                                alignItems: "center",
                                gap: "8px",
                              }}
                            >
                              <span>🤖</span>
                              <span>PaπD AI Analysis</span>
                            </h4>

                            {/* Recommendation Badge */}
                            <div
                              style={{
                                ...glassSurface({
                                  padding: "6px 12px",
                                  borderRadius: theme.borderRadius.sm,
                                  backgroundColor: getRecommendationColor(
                                    aiAnalysisMap[position.symbol].recommendation
                                  ).bg,
                                  border: `1px solid ${
                                    getRecommendationColor(
                                      aiAnalysisMap[position.symbol].recommendation
                                    ).border
                                  }`,
                                }),
                                fontSize: "13px",
                                fontWeight: "700",
                                color: getRecommendationColor(
                                  aiAnalysisMap[position.symbol].recommendation
                                ).text,
                                whiteSpace: "nowrap",
                              }}
                            >
                              {aiAnalysisMap[position.symbol].recommendation}
                            </div>
                          </div>

                          {/* Metrics Grid */}
                          <div
                            style={{
                              display: "grid",
                              gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
                              gap: theme.spacing.sm,
                              marginBottom: theme.spacing.md,
                            }}
                          >
                            {/* Confidence Score */}
                            <div
                              style={glassSurface({
                                padding: theme.spacing.sm,
                                borderRadius: theme.borderRadius.sm,
                              })}
                            >
                              <div
                                style={{
                                  fontSize: "11px",
                                  color: theme.colors.textMuted,
                                  marginBottom: "4px",
                                }}
                              >
                                Confidence Score
                              </div>
                              <div
                                style={{
                                  fontSize: "16px",
                                  fontWeight: "600",
                                  color: theme.colors.primary,
                                }}
                              >
                                {aiAnalysisMap[position.symbol].confidence.toFixed(1)}%
                              </div>
                            </div>

                            {/* Risk Score */}
                            <div
                              style={glassSurface({
                                padding: theme.spacing.sm,
                                borderRadius: theme.borderRadius.sm,
                              })}
                            >
                              <div
                                style={{
                                  fontSize: "11px",
                                  color: theme.colors.textMuted,
                                  marginBottom: "4px",
                                }}
                              >
                                Risk Level
                              </div>
                              <div
                                style={{
                                  ...glassSurface({
                                    padding: "4px 8px",
                                    borderRadius: theme.borderRadius.sm,
                                    backgroundColor: getRiskColor(
                                      aiAnalysisMap[position.symbol].riskScore
                                    ).bg,
                                    border: `1px solid ${
                                      getRiskColor(aiAnalysisMap[position.symbol].riskScore).border
                                    }`,
                                  }),
                                  fontSize: "14px",
                                  fontWeight: "600",
                                  color: getRiskColor(aiAnalysisMap[position.symbol].riskScore)
                                    .text,
                                  display: "inline-block",
                                }}
                              >
                                {aiAnalysisMap[position.symbol].riskScore}
                              </div>
                            </div>
                          </div>

                          {/* Sentiment */}
                          <div
                            style={{
                              ...glassSurface({
                                padding: theme.spacing.md,
                                borderRadius: theme.borderRadius.sm,
                              }),
                              marginBottom: theme.spacing.md,
                              borderLeft: `4px solid ${theme.colors.primary}`,
                            }}
                          >
                            <div
                              style={{
                                fontSize: "13px",
                                color: theme.colors.text,
                                lineHeight: "1.5",
                              }}
                            >
                              <strong style={{ color: theme.colors.primary }}>Sentiment:</strong>{" "}
                              {aiAnalysisMap[position.symbol].sentiment}
                            </div>
                          </div>

                          {/* Suggested Action */}
                          <div
                            style={{
                              ...glassSurface({
                                padding: theme.spacing.md,
                                borderRadius: theme.borderRadius.sm,
                                backgroundColor: theme.background.card,
                              }),
                              fontSize: "12px",
                              color: theme.colors.textMuted,
                              lineHeight: "1.6",
                              borderLeft: `3px solid ${theme.colors.primary}`,
                              marginBottom: aiAnalysisMap[position.symbol].exitStrategy
                                ? theme.spacing.md
                                : 0,
                            }}
                          >
                            <div
                              style={{
                                fontWeight: "600",
                                color: theme.colors.text,
                                marginBottom: "8px",
                              }}
                            >
                              💡 AI Suggestion
                            </div>
                            <div>{aiAnalysisMap[position.symbol].suggestedAction}</div>
                          </div>

                          {/* Exit Strategy */}
                          {aiAnalysisMap[position.symbol].exitStrategy && (
                            <div
                              style={glassSurface({
                                padding: theme.spacing.md,
                                borderRadius: theme.borderRadius.sm,
                              })}
                            >
                              <div
                                style={{
                                  fontSize: "12px",
                                  fontWeight: "600",
                                  color: theme.colors.textMuted,
                                  marginBottom: theme.spacing.sm,
                                }}
                              >
                                Exit Strategy
                              </div>
                              <div
                                style={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  gap: theme.spacing.md,
                                }}
                              >
                                <div>
                                  <div
                                    style={{
                                      fontSize: "11px",
                                      color: theme.colors.textMuted,
                                    }}
                                  >
                                    Profit Target
                                  </div>
                                  <div
                                    style={{
                                      fontSize: "15px",
                                      fontWeight: "600",
                                      color: theme.colors.primary,
                                    }}
                                  >
                                    $
                                    {aiAnalysisMap[
                                      position.symbol
                                    ].exitStrategy!.profitTarget.toFixed(2)}
                                  </div>
                                </div>
                                <div>
                                  <div
                                    style={{
                                      fontSize: "11px",
                                      color: theme.colors.textMuted,
                                    }}
                                  >
                                    Stop Loss
                                  </div>
                                  <div
                                    style={{
                                      fontSize: "15px",
                                      fontWeight: "600",
                                      color: theme.colors.danger,
                                    }}
                                  >
                                    $
                                    {aiAnalysisMap[position.symbol].exitStrategy!.stopLoss.toFixed(
                                      2
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  <Button
                    variant="danger"
                    size="sm"
                    style={{ marginTop: theme.spacing.md, width: "100%" }}
                    onClick={async () => {
                      if (confirm(`Close entire position in ${position.symbol}?`)) {
                        try {
                          await alpaca.closePosition(position.symbol);
                          // Refresh positions after close
                          await loadPositions();
                        } catch (error) {
                          logger.error(`Failed to close position ${position.symbol}`, error);
                          alert(`Failed to close position: ${error}`);
                        }
                      }
                    }}
                  >
                    Close Position
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  subValue,
  valueColor,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  subValue?: string;
  valueColor?: string;
}) {
  return (
    <Card>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: theme.spacing.xs,
          marginBottom: theme.spacing.xs,
        }}
      >
        {icon}
        <p style={{ fontSize: "14px", color: theme.colors.textMuted, margin: 0 }}>{label}</p>
      </div>
      <p
        style={{
          fontSize: "24px",
          fontWeight: "bold",
          color: valueColor || theme.colors.text,
          margin: 0,
        }}
      >
        {value}
      </p>
      {subValue && (
        <p
          style={{
            fontSize: "14px",
            color: theme.colors.textMuted,
            margin: `${theme.spacing.xs} 0 0 0`,
          }}
        >
          {subValue}
        </p>
      )}
    </Card>
  );
}
