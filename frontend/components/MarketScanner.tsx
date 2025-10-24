"use client";

import { useState, useEffect, useMemo } from "react";
import { Search, RefreshCw } from "lucide-react";

import { Card, Button, Input, Select } from "./ui";
import { theme } from "../styles/theme";
import { useIsMobile } from "../hooks/useBreakpoint";
import StockLookup from "./StockLookup";

export type OpportunityType = "stock" | "option" | "multileg";
export type SignalStrength =
  | "strong_buy"
  | "buy"
  | "neutral"
  | "sell"
  | "strong_sell";

interface ScanResult {
  symbol: string;
  type: OpportunityType;
  strategy: string;
  reason: string;
  currentPrice: number;
  targetPrice: number | null;
  confidence: number;
  risk: "low" | "medium" | "high";
  signal: SignalStrength;
}

interface ScanFilter {
  minPrice: number;
  maxPrice: number;
  minConfidence: number;
  signalType: "all" | "buy" | "sell";
}

const DEFAULT_FILTER: ScanFilter = {
  minPrice: 1,
  maxPrice: 1000,
  minConfidence: 65,
  signalType: "all",
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);

const getSignalColor = (signal: SignalStrength) => {
  switch (signal) {
    case "strong_buy":
      return theme.colors.primary;
    case "buy":
      return theme.colors.secondary;
    case "neutral":
      return theme.colors.textMuted;
    case "sell":
      return theme.colors.warning;
    case "strong_sell":
      return theme.colors.danger;
  }
};

const getSignalLabel = (signal: SignalStrength) =>
  signal
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

const deriveSignal = (confidence: number, risk: ScanResult["risk"]): SignalStrength => {
  const riskAdjustment = risk === "high" ? -8 : risk === "low" ? 6 : 0;
  const score = confidence + riskAdjustment;

  if (score >= 85) return "strong_buy";
  if (score >= 72) return "buy";
  if (score <= 45) return "strong_sell";
  if (score <= 60) return "sell";
  return "neutral";
};

const getConfidenceLabel = (confidence: number) => {
  if (confidence >= 85) return "High conviction";
  if (confidence >= 70) return "Moderate conviction";
  return "Developing setup";
};

const getRiskBadge = (risk: ScanResult["risk"]) => {
  switch (risk) {
    case "low":
      return {
        color: theme.colors.success,
        description: "Tighter risk parameters",
      };
    case "medium":
      return {
        color: theme.colors.warning,
        description: "Balanced risk/reward",
      };
    case "high":
      return {
        color: theme.colors.danger,
        description: "Requires active management",
      };
  }
};

export default function MarketScanner() {
  const isMobile = useIsMobile();
  const [results, setResults] = useState<ScanResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<ScanFilter>(DEFAULT_FILTER);
  const [scanType, setScanType] = useState<"momentum" | "breakout" | "reversal" | "custom">(
    "momentum",
  );
  const [selectedSymbol, setSelectedSymbol] = useState<string>("");
  const [showResearch, setShowResearch] = useState(false);

  useEffect(() => {
    runScan();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scanType]);

  const maxPriceParam = useMemo(() => {
    if (!Number.isFinite(filter.maxPrice) || filter.maxPrice <= 0) {
      return undefined;
    }
    return filter.maxPrice;
  }, [filter.maxPrice]);

  const runScan = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (maxPriceParam) {
        params.set("max_price", maxPriceParam.toString());
      }
      params.set("scan_type", scanType);

      const query = params.toString();
      const response = await fetch(
        `/api/proxy/screening/opportunities${query ? `?${query}` : ""}`,
        { cache: "no-store" },
      );

      if (!response.ok) {
        throw new Error(`Market scan failed with status ${response.status}`);
      }

      const data = await response.json();
      const opportunities: any[] = Array.isArray(data?.opportunities)
        ? data.opportunities
        : [];

      const normalized = opportunities
        .map((raw) => {
          const currentPrice = Number(raw?.currentPrice ?? raw?.price ?? 0);
          if (!Number.isFinite(currentPrice)) {
            return null;
          }
          const target = raw?.targetPrice != null ? Number(raw.targetPrice) : null;
          const confidence = Number(raw?.confidence ?? 0);
          const risk = (raw?.risk ?? "medium") as ScanResult["risk"];

          return {
            symbol: String(raw?.symbol ?? "").toUpperCase(),
            type: (raw?.type ?? "stock") as OpportunityType,
            strategy: String(raw?.strategy ?? "Unknown strategy"),
            reason: String(raw?.reason ?? ""),
            currentPrice,
            targetPrice: Number.isFinite(target) ? target : null,
            confidence,
            risk,
            signal: deriveSignal(confidence, risk),
          } satisfies ScanResult;
        })
        .filter((result): result is ScanResult => Boolean(result));

      let filteredResults = normalized.filter(
        (opportunity) =>
          opportunity.currentPrice >= filter.minPrice &&
          opportunity.currentPrice <= filter.maxPrice &&
          opportunity.confidence >= filter.minConfidence,
      );

      if (filter.signalType !== "all") {
        const desiredSignals =
          filter.signalType === "buy"
            ? ["buy", "strong_buy"]
            : ["sell", "strong_sell"];
        filteredResults = filteredResults.filter((result) =>
          desiredSignals.includes(result.signal),
        );
      }

      setResults(filteredResults);
    } catch (fetchError) {
      const message =
        fetchError instanceof Error
          ? fetchError.message
          : "Unable to load market scanner results";
      setError(message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleConfidenceChange = (value: string) => {
    const numeric = Number(value);
    setFilter((prev) => ({ ...prev, minConfidence: Number.isFinite(numeric) ? numeric : prev.minConfidence }));
  };

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      {/* Header */}
      <div
        style={{
          display: "flex",
          flexDirection: isMobile ? "column" : "row",
          alignItems: isMobile ? "stretch" : "center",
          justifyContent: "space-between",
          gap: isMobile ? theme.spacing.sm : 0,
          marginBottom: theme.spacing.lg,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}>
          <Search size={isMobile ? 24 : 32} color={theme.colors.info} />
          <h1
            style={{
              margin: 0,
              fontSize: isMobile ? "24px" : "32px",
              fontWeight: "700",
              color: theme.colors.text,
              textShadow: `0 0 20px ${theme.colors.info}40`,
            }}
          >
            Market Scanner
          </h1>
        </div>
        <Button
          variant="primary"
          size="md"
          onClick={runScan}
          loading={loading}
          style={{ width: isMobile ? "100%" : "auto" }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.xs }}>
            <RefreshCw size={20} />
            Scan Market
          </div>
        </Button>
      </div>

      {/* Direct Symbol Search */}
      <Card style={{ marginBottom: theme.spacing.md, padding: theme.spacing.md }}>
        <div style={{ marginBottom: theme.spacing.xs }}>
          <p
            style={{
              fontSize: "14px",
              fontWeight: "600",
              color: theme.colors.textMuted,
              margin: `0 0 ${theme.spacing.sm} 0`,
            }}
          >
            Search Stock Symbol
          </p>
          <div style={{ display: "flex", gap: theme.spacing.sm }}>
            <Input
              type="text"
              placeholder="Enter symbol (e.g., AAPL, TSLA, SPY)"
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
              onKeyDown={(e) => {
                if (e.key === "Enter" && selectedSymbol.trim()) {
                  setShowResearch(true);
                }
              }}
              style={{ flex: 1 }}
            />
            <Button
              variant="primary"
              size="md"
              onClick={() => {
                if (selectedSymbol.trim()) {
                  setShowResearch(true);
                }
              }}
              disabled={!selectedSymbol.trim()}
              style={{ width: isMobile ? "120px" : "auto" }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.xs }}>
                <Search size={18} />
                Research
              </div>
            </Button>
          </div>
          <p
            style={{ fontSize: "12px", color: theme.colors.textMuted, marginTop: theme.spacing.xs }}
          >
            Research any stock with detailed analysis, charts, and AI insights
          </p>
        </div>
      </Card>

      {/* Scan Type & Filters */}
      <Card style={{ marginBottom: theme.spacing.md, padding: theme.spacing.md }}>
        <div style={{ marginBottom: theme.spacing.md }}>
          <p
            style={{
              fontSize: "14px",
              fontWeight: "600",
              color: theme.colors.textMuted,
              margin: `0 0 ${theme.spacing.sm} 0`,
            }}
          >
            Scan Type
          </p>
          <div style={{ display: "flex", gap: theme.spacing.xs, flexWrap: "wrap" }}>
            {(["momentum", "breakout", "reversal", "custom"] as const).map((type) => (
              <Button
                key={type}
                variant={scanType === type ? "primary" : "secondary"}
                size="sm"
                onClick={() => setScanType(type)}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </Button>
            ))}
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "repeat(auto-fit, minmax(200px, 1fr))",
            gap: theme.spacing.md,
          }}
        >
          <Input
            label="Min Price"
            type="number"
            value={filter.minPrice.toString()}
            onChange={(e) =>
              setFilter({
                ...filter,
                minPrice: Number.isFinite(Number(e.target.value))
                  ? Number(e.target.value)
                  : filter.minPrice,
              })
            }
          />
          <Input
            label="Max Price"
            type="number"
            value={filter.maxPrice.toString()}
            onChange={(e) =>
              setFilter({
                ...filter,
                maxPrice: Number.isFinite(Number(e.target.value))
                  ? Number(e.target.value)
                  : filter.maxPrice,
              })
            }
          />
          <Input
            label="Min Confidence (%)"
            type="number"
            value={filter.minConfidence.toString()}
            onChange={(e) => handleConfidenceChange(e.target.value)}
          />
          <Select
            label="Signal Bias"
            options={[
              { value: "all", label: "All" },
              { value: "buy", label: "Bullish" },
              { value: "sell", label: "Bearish" },
            ]}
            value={filter.signalType}
            onChange={(e) =>
              setFilter({ ...filter, signalType: e.target.value as ScanFilter["signalType"] })
            }
          />
        </div>
      </Card>

      {error && (
        <Card glow="red" style={{ marginBottom: theme.spacing.md }}>
          <div
            style={{
              color: theme.colors.danger,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: theme.spacing.sm,
            }}
          >
            <span>{error}</span>
            <Button size="sm" variant="secondary" onClick={runScan}>
              Retry
            </Button>
          </div>
        </Card>
      )}

      {/* Results */}
      {loading ? (
        <Card>
          <div
            style={{
              textAlign: "center",
              padding: theme.spacing.xl,
              color: theme.colors.textMuted,
            }}
          >
            <RefreshCw size={32} style={{ animation: "spin 1s linear infinite" }} />
            <p style={{ marginTop: theme.spacing.md }}>Scanning market...</p>
          </div>
        </Card>
      ) : results.length === 0 ? (
        <Card>
          <div
            style={{
              textAlign: "center",
              padding: theme.spacing.xl,
              color: theme.colors.textMuted,
            }}
          >
            No opportunities found matching your criteria. Try adjusting the filters.
          </div>
        </Card>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.md }}>
          {results.map((result) => {
            const riskBadge = getRiskBadge(result.risk);
            return (
              <Card
                key={`${result.symbol}-${result.strategy}`}
                glow={
                  result.signal.includes("buy")
                    ? "green"
                    : result.signal.includes("sell")
                    ? "red"
                    : undefined
                }
              >
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
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: theme.spacing.sm,
                        marginBottom: theme.spacing.xs,
                        flexWrap: "wrap",
                      }}
                    >
                      <h3
                        style={{
                          margin: 0,
                          fontSize: isMobile ? "20px" : "24px",
                          fontWeight: "700",
                          color: theme.colors.text,
                        }}
                      >
                        {result.symbol}
                      </h3>
                      <span
                        style={{
                          padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                          borderRadius: theme.borderRadius.sm,
                          fontSize: "12px",
                          fontWeight: "600",
                          background: `${getSignalColor(result.signal)}20`,
                          color: getSignalColor(result.signal),
                        }}
                      >
                        {getSignalLabel(result.signal)}
                      </span>
                      <span
                        style={{
                          padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                          borderRadius: theme.borderRadius.sm,
                          fontSize: "12px",
                          fontWeight: "600",
                          background: `${riskBadge.color}20`,
                          color: riskBadge.color,
                        }}
                      >
                        {result.risk.charAt(0).toUpperCase() + result.risk.slice(1)} risk
                      </span>
                    </div>
                    <p style={{ margin: 0, fontSize: "14px", color: theme.colors.textMuted }}>
                      {formatCurrency(result.currentPrice)}
                      {result.targetPrice
                        ? ` · Target ${formatCurrency(result.targetPrice)}`
                        : ""}
                    </p>
                  </div>
                  <div
                    style={{
                      display: "flex",
                      flexDirection: isMobile ? "column" : "row",
                      gap: theme.spacing.xs,
                      width: isMobile ? "100%" : "auto",
                    }}
                  >
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setSelectedSymbol(result.symbol);
                        setShowResearch(true);
                      }}
                      style={{ width: isMobile ? "100%" : "auto" }}
                    >
                      Research
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        setSelectedSymbol(result.symbol);
                        setShowResearch(true);
                      }}
                      style={{ width: isMobile ? "100%" : "auto" }}
                    >
                      Prepare Trade
                    </Button>
                  </div>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: isMobile
                      ? "repeat(2, 1fr)"
                      : "repeat(auto-fit, minmax(160px, 1fr))",
                    gap: theme.spacing.md,
                    marginBottom: theme.spacing.md,
                    padding: theme.spacing.md,
                    background: theme.background.input,
                    borderRadius: theme.borderRadius.md,
                  }}
                >
                  <Indicator label="Strategy" value={result.strategy} />
                  <Indicator
                    label="Opportunity Type"
                    value={result.type.charAt(0).toUpperCase() + result.type.slice(1)}
                  />
                  <Indicator
                    label="Confidence"
                    value={`${result.confidence.toFixed(0)}%`}
                    subValue={getConfidenceLabel(result.confidence)}
                  />
                  <Indicator label="Risk Guidance" value={riskBadge.description} />
                  <Indicator
                    label="Target"
                    value={
                      result.targetPrice ? formatCurrency(result.targetPrice) : "Not specified"
                    }
                  />
                </div>

                <div
                  style={{
                    padding: theme.spacing.md,
                    background: `${getSignalColor(result.signal)}10`,
                    borderLeft: `4px solid ${getSignalColor(result.signal)}`,
                    borderRadius: theme.borderRadius.sm,
                  }}
                >
                  <p style={{ margin: 0, fontSize: "14px", color: theme.colors.text }}>
                    <strong>Analysis:</strong> {result.reason}
                  </p>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Stock Research Section */}
      {showResearch && (
        <div style={{ marginTop: theme.spacing.lg }}>
          <Card>
            <div
              style={{
                display: "flex",
                flexDirection: isMobile ? "column" : "row",
                justifyContent: "space-between",
                alignItems: isMobile ? "flex-start" : "center",
                gap: isMobile ? theme.spacing.sm : 0,
                marginBottom: theme.spacing.md,
                paddingBottom: theme.spacing.md,
                borderBottom: `1px solid ${theme.background.input}`,
              }}
            >
              <h2
                style={{
                  margin: 0,
                  fontSize: isMobile ? "20px" : "24px",
                  fontWeight: "700",
                  color: theme.colors.text,
                }}
              >
                Detailed Research
              </h2>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowResearch(false)}
                style={{ width: isMobile ? "100%" : "auto" }}
              >
                Close
              </Button>
            </div>
            <StockLookup
              initialSymbol={selectedSymbol}
              showChart={true}
              showIndicators={true}
              showCompanyInfo={true}
              showNews={false}
              enableAIAnalysis={true}
              onSymbolSelect={(sym) => setSelectedSymbol(sym)}
            />
          </Card>
        </div>
      )}

      <style jsx>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
}

function Indicator({
  label,
  value,
  subValue,
}: {
  label: string;
  value: string;
  subValue?: string;
}) {
  return (
    <div>
      <p
        style={{
          fontSize: "12px",
          color: theme.colors.textMuted,
          margin: `0 0 ${theme.spacing.xs} 0`,
        }}
      >
        {label}
      </p>
      <p style={{ fontSize: "16px", fontWeight: "600", color: theme.colors.text, margin: 0 }}>
        {value}
      </p>
      {subValue && (
        <p
          style={{
            fontSize: "12px",
            color: theme.colors.textMuted,
            margin: `${theme.spacing.xs} 0 0 0`,
          }}
        >
          {subValue}
        </p>
      )}
    </div>
  );
}
