"use client";
import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import type { UTCTimestamp } from "lightweight-charts";
import {
  BarChart3,
  TrendingDown,
  DollarSign,
  Percent,
  Target,
  Award,
  Download,
} from "lucide-react";
import { Card, Button } from "./ui";
import { theme } from "../styles/theme";
import { useIsMobile } from "../hooks/useBreakpoint";
import html2canvas from "html2canvas";
import {
  MarketChart,
  PositionAllocationChart,
  GreeksHeatmap,
  CandlestickViews,
  type PositionSlice,
  type OptionGreekSnapshot,
  type CandleDatum,
} from "@/src/features/analytics";

interface PerformanceMetrics {
  totalReturn: number;
  totalReturnPercent: number;
  winRate: number;
  profitFactor: number;
  sharpeRatio: number;
  maxDrawdown: number;
  avgWin: number;
  avgLoss: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
}

interface DailyPerformance {
  date: string;
  pnl: number;
  portfolioValue: number;
  trades: number;
}

interface MonthlyStats {
  month: string;
  profit: number;
  trades: number;
  winRate: number;
}

interface PortfolioSummary {
  total_value: number;
  cash: number;
  buying_power: number;
  total_pl: number;
  total_pl_percent: number;
  day_pl: number;
  day_pl_percent: number;
  num_positions: number;
  num_winning: number;
  num_losing: number;
  largest_winner?: { symbol: string; pl: number; pl_percent: number };
  largest_loser?: { symbol: string; pl: number; pl_percent: number };
}

interface AiAnalysisResult {
  health_score: number;
  risk_level: string;
  diversification_score: number;
  ai_summary: string;
  recommendations: string[];
  risk_factors: string[];
  opportunities: string[];
}

const MARKET_SYMBOL_FALLBACKS = [
  { label: "S&P 500", value: "SPX" },
  { label: "NASDAQ 100", value: "NDX" },
  { label: "Dow Jones", value: "$DJI.IX" },
  { label: "Gold", value: "GC1!" },
  { label: "BTC/USD", value: "BTCUSD" },
];

const CANDLE_INTERVALS = ["1D", "5D", "1M", "3M"] as const;

const FALLBACK_POSITION_SLICES: PositionSlice[] = [
  { symbol: "AAPL", allocation: 42000, marketValue: 42000, dayPnl: 560 },
  { symbol: "MSFT", allocation: 36000, marketValue: 36000, dayPnl: 320 },
  { symbol: "NVDA", allocation: 28000, marketValue: 28000, dayPnl: -440 },
  { symbol: "SPY", allocation: 25000, marketValue: 25000, dayPnl: 210 },
  { symbol: "TSLA", allocation: 18000, marketValue: 18000, dayPnl: -380 },
];

const DEFAULT_AI_ANALYSIS: AiAnalysisResult = {
  health_score: 0,
  risk_level: "Unknown",
  diversification_score: 0,
  ai_summary: "No analysis available.",
  recommendations: [],
  risk_factors: [],
  opportunities: [],
};

function parseNumeric(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string") {
    const parsed = parseFloat(value);
    return Number.isFinite(parsed) ? parsed : 0;
  }
  return 0;
}

function parseOptionalNumeric(value: unknown): number | undefined {
  if (value === null || value === undefined) {
    return undefined;
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return undefined;
}

function toUtcTimestamp(value: unknown): UTCTimestamp {
  if (typeof value === "number" && Number.isFinite(value)) {
    const milliseconds = value > 1_000_000_000_000 ? value : value * 1000;
    return Math.floor(milliseconds / 1000) as UTCTimestamp;
  }

  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Date.parse(value);
    if (!Number.isNaN(parsed)) {
      return Math.floor(parsed / 1000) as UTCTimestamp;
    }
  }

  return Math.floor(Date.now() / 1000) as UTCTimestamp;
}

function sanitizeSymbol(symbol?: string | null): string {
  if (!symbol) {
    return "";
  }
  return symbol.replace(/[^A-Za-z0-9]/g, "").toUpperCase();
}

function generateMockCandlesForInterval(interval: string, length = 80): CandleDatum[] {
  const now = Date.now();
  const stepMap: Record<string, number> = {
    "1D": 30 * 60 * 1000,
    "5D": 2 * 60 * 60 * 1000,
    "1M": 24 * 60 * 60 * 1000,
    "3M": 3 * 24 * 60 * 60 * 1000,
  };
  const step = stepMap[interval] ?? 24 * 60 * 60 * 1000;
  let base = 150 + Math.random() * 10;

  return Array.from({ length }, (_, index) => {
    const timestamp = Math.floor(
      new Date(now - (length - index) * step).getTime() / 1000
    ) as UTCTimestamp;
    const oscillation = Math.sin(index / 6) * 2.4;
    const drift = index * 0.05;
    const open = base + oscillation + drift;
    const close = open + Math.sin(index / 4) * 1.2;
    const high = Math.max(open, close) + Math.random() * 1.5;
    const low = Math.min(open, close) - Math.random() * 1.5;
    base = close;

    return {
      time: timestamp,
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      volume: Math.floor(400000 + Math.random() * 800000),
    };
  });
}

function generateMockCandlesSet(intervals: readonly string[]): Record<string, CandleDatum[]> {
  return intervals.reduce<Record<string, CandleDatum[]>>((acc, interval) => {
    acc[interval] = generateMockCandlesForInterval(interval);
    return acc;
  }, {});
}

function buildFallbackGreeks(positions: PositionSlice[]): OptionGreekSnapshot[] {
  const sourcePositions = positions.length ? positions : FALLBACK_POSITION_SLICES;
  const baseSymbols = sourcePositions.map((position) => position.symbol);

  return baseSymbols.slice(0, 5).map((symbol, index) => {
    const weight = sourcePositions[index]?.allocation ?? 20;
    const expiryDate = new Date(Date.now() + (index + 1) * 30 * 24 * 60 * 60 * 1000)
      .toISOString()
      .split("T")[0];
    const rawDelta = 0.2 + weight / 200 - index * 0.08;

    return {
      symbol,
      expiry: expiryDate,
      delta: parseFloat(Math.max(-0.9, Math.min(0.9, rawDelta)).toFixed(3)),
      gamma: parseFloat((0.012 + index * 0.004).toFixed(3)),
      theta: parseFloat((-0.055 + index * 0.006).toFixed(3)),
      vega: parseFloat((0.08 + index * 0.012).toFixed(3)),
      rho: parseFloat((0.02 + index * 0.0035).toFixed(3)),
    };
  });
}

async function fetchCandlestickSeries(
  symbol: string,
  intervals: readonly string[]
): Promise<Record<string, CandleDatum[]>> {
  const results = await Promise.all(
    intervals.map(async (interval) => {
      const response = await fetch(
        `/api/market/historical?symbol=${encodeURIComponent(symbol)}&timeframe=${interval}`
      );

      if (!response.ok) {
        throw new Error(`Failed to load ${symbol} historical data for ${interval}`);
      }

      const payload = await response.json();
      const bars = Array.isArray(payload?.bars) ? (payload.bars as unknown[]) : [];

      const normalized = bars.map((bar: unknown): CandleDatum => {
        if (!bar || typeof bar !== "object") {
          return generateMockCandlesForInterval(interval, 1)[0];
        }

        const entry = bar as Record<string, unknown>;
        const volumeSource = entry.volume ?? entry.v ?? entry.vol;

        return {
          time: toUtcTimestamp(entry.time ?? entry.t),
          open: parseNumeric(entry.open ?? entry.o),
          high: parseNumeric(entry.high ?? entry.h),
          low: parseNumeric(entry.low ?? entry.l),
          close: parseNumeric(entry.close ?? entry.c),
          ...(volumeSource !== undefined ? { volume: parseNumeric(volumeSource) } : {}),
        } satisfies CandleDatum;
      });

      return [interval, normalized] as const;
    })
  );

  return Object.fromEntries(results);
}

function extractPositionsPayload(payload: unknown): unknown[] {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (payload && typeof payload === "object") {
    const record = payload as Record<string, unknown>;
    const nested = record.positions ?? record.data;

    if (Array.isArray(nested)) {
      return nested;
    }
  }

  return [];
}

function normalizeAiAnalysis(payload: unknown): AiAnalysisResult {
  if (!payload || typeof payload !== "object") {
    return DEFAULT_AI_ANALYSIS;
  }

  const record = payload as Record<string, unknown>;
  const toStringArray = (value: unknown): string[] =>
    Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];

  return {
    health_score: Number(record.health_score ?? DEFAULT_AI_ANALYSIS.health_score),
    risk_level:
      typeof record.risk_level === "string" ? record.risk_level : DEFAULT_AI_ANALYSIS.risk_level,
    diversification_score: Number(
      record.diversification_score ?? DEFAULT_AI_ANALYSIS.diversification_score
    ),
    ai_summary:
      typeof record.ai_summary === "string" ? record.ai_summary : DEFAULT_AI_ANALYSIS.ai_summary,
    recommendations: toStringArray(record.recommendations),
    risk_factors: toStringArray(record.risk_factors),
    opportunities: toStringArray(record.opportunities),
  };
}

function PortfolioSummaryCard() {
  const isMobile = useIsMobile();
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
    // Refresh every 30 seconds
    const interval = setInterval(loadSummary, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSummary = async () => {
    try {
      const response = await fetch("/api/proxy/portfolio/summary");
      const data = await response.json();
      setSummary(data);
      setLoading(false);
    } catch (error) {
      console.error("Failed to load portfolio summary:", error);
      setLoading(false);
    }
  };

  if (loading || !summary) {
    return null;
  }

  return (
    <Card style={{ marginBottom: theme.spacing.lg }} glow="teal">
      <h3
        style={{ margin: `0 0 ${theme.spacing.md} 0`, color: theme.colors.text, fontSize: "18px" }}
      >
        Portfolio Summary
      </h3>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
          gap: theme.spacing.md,
        }}
      >
        {/* Total Value */}
        <div>
          <p
            style={{
              fontSize: "12px",
              color: theme.colors.textMuted,
              margin: `0 0 ${theme.spacing.xs} 0`,
            }}
          >
            Total Value
          </p>
          <p style={{ fontSize: "24px", fontWeight: "bold", color: theme.colors.text, margin: 0 }}>
            ${summary.total_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </p>
        </div>

        {/* Total P&L */}
        <div>
          <p
            style={{
              fontSize: "12px",
              color: theme.colors.textMuted,
              margin: `0 0 ${theme.spacing.xs} 0`,
            }}
          >
            Total P&L
          </p>
          <p
            style={{
              fontSize: "24px",
              fontWeight: "bold",
              color: summary.total_pl >= 0 ? theme.colors.primary : theme.colors.danger,
              margin: 0,
            }}
          >
            {summary.total_pl >= 0 ? "+" : ""}$
            {summary.total_pl.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            <span style={{ fontSize: "16px", marginLeft: theme.spacing.xs }}>
              ({summary.total_pl_percent >= 0 ? "+" : ""}
              {summary.total_pl_percent.toFixed(2)}%)
            </span>
          </p>
        </div>

        {/* Day P&L */}
        <div>
          <p
            style={{
              fontSize: "12px",
              color: theme.colors.textMuted,
              margin: `0 0 ${theme.spacing.xs} 0`,
            }}
          >
            Today&apos;s P&L
          </p>
          <p
            style={{
              fontSize: "24px",
              fontWeight: "bold",
              color: summary.day_pl >= 0 ? theme.colors.primary : theme.colors.danger,
              margin: 0,
            }}
          >
            {summary.day_pl >= 0 ? "+" : ""}$
            {summary.day_pl.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            <span style={{ fontSize: "16px", marginLeft: theme.spacing.xs }}>
              ({summary.day_pl_percent >= 0 ? "+" : ""}
              {summary.day_pl_percent.toFixed(2)}%)
            </span>
          </p>
        </div>

        {/* Positions */}
        <div>
          <p
            style={{
              fontSize: "12px",
              color: theme.colors.textMuted,
              margin: `0 0 ${theme.spacing.xs} 0`,
            }}
          >
            Positions
          </p>
          <p style={{ fontSize: "24px", fontWeight: "bold", color: theme.colors.text, margin: 0 }}>
            {summary.num_positions}
            <span
              style={{
                fontSize: "16px",
                marginLeft: theme.spacing.xs,
                color: theme.colors.textMuted,
              }}
            >
              ({summary.num_winning}W / {summary.num_losing}L)
            </span>
          </p>
        </div>
      </div>

      {/* Largest Winner/Loser */}
      {(summary.largest_winner || summary.largest_loser) && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
            gap: theme.spacing.md,
            marginTop: theme.spacing.md,
            paddingTop: theme.spacing.md,
            borderTop: `1px solid ${theme.colors.border}`,
          }}
        >
          {summary.largest_winner && (
            <div>
              <p
                style={{
                  fontSize: "12px",
                  color: theme.colors.textMuted,
                  margin: `0 0 ${theme.spacing.xs} 0`,
                }}
              >
                Largest Winner
              </p>
              <p
                style={{
                  fontSize: "18px",
                  fontWeight: "bold",
                  color: theme.colors.text,
                  margin: 0,
                }}
              >
                {summary.largest_winner.symbol}
              </p>
              <p
                style={{
                  fontSize: "16px",
                  color: theme.colors.primary,
                  margin: `${theme.spacing.xs} 0 0 0`,
                }}
              >
                +${summary.largest_winner.pl.toFixed(2)} (+
                {summary.largest_winner.pl_percent.toFixed(2)}%)
              </p>
            </div>
          )}

          {summary.largest_loser && (
            <div>
              <p
                style={{
                  fontSize: "12px",
                  color: theme.colors.textMuted,
                  margin: `0 0 ${theme.spacing.xs} 0`,
                }}
              >
                Largest Loser
              </p>
              <p
                style={{
                  fontSize: "18px",
                  fontWeight: "bold",
                  color: theme.colors.text,
                  margin: 0,
                }}
              >
                {summary.largest_loser.symbol}
              </p>
              <p
                style={{
                  fontSize: "16px",
                  color: theme.colors.danger,
                  margin: `${theme.spacing.xs} 0 0 0`,
                }}
              >
                ${summary.largest_loser.pl.toFixed(2)} (
                {summary.largest_loser.pl_percent.toFixed(2)}%)
              </p>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

export default function Analytics() {
  const [timeframe, setTimeframe] = useState<"1W" | "1M" | "3M" | "1Y" | "ALL">("1M");
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [dailyPerformance, setDailyPerformance] = useState<DailyPerformance[]>([]);
  const [monthlyStats, setMonthlyStats] = useState<MonthlyStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [positionSlices, setPositionSlices] = useState<PositionSlice[]>(FALLBACK_POSITION_SLICES);
  const [greeksHeatmapData, setGreeksHeatmapData] = useState<OptionGreekSnapshot[]>(
    buildFallbackGreeks(FALLBACK_POSITION_SLICES)
  );
  const [candlestickData, setCandlestickData] = useState<Record<string, CandleDatum[]>>(
    generateMockCandlesSet(CANDLE_INTERVALS)
  );
  const [candlestickSymbol, setCandlestickSymbol] = useState<string>(
    sanitizeSymbol(FALLBACK_POSITION_SLICES[0]?.symbol) || "AAPL"
  );
  const [supplementaryLoading, setSupplementaryLoading] = useState(false);

  // AI Portfolio Analysis state
  const [aiAnalysis, setAiAnalysis] = useState<AiAnalysisResult | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [showAiPanel, setShowAiPanel] = useState(false);

  // Mobile responsiveness
  const isMobile = useIsMobile();

  // Chart refs for export functionality
  const equityChartRef = useRef<HTMLDivElement>(null);
  const pnlChartRef = useRef<HTMLDivElement>(null);

  // Export chart as PNG
  const exportChartAsPNG = async (chartRef: React.RefObject<HTMLDivElement>, chartName: string) => {
    if (!chartRef.current) return;

    try {
      const canvas = await html2canvas(chartRef.current, {
        backgroundColor: theme.background.card,
        scale: 2, // Higher quality
      });

      const link = document.createElement("a");
      link.download = `PaiiD_${chartName}_${new Date().toISOString().split("T")[0]}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
    } catch (error) {
      console.error("Failed to export chart:", error);
    }
  };

  // Fetch AI Portfolio Analysis
  const fetchAIPortfolioAnalysis = async () => {
    setAiLoading(true);
    setAiError(null);

    try {
      const response = await fetch("/api/proxy/api/ai/analyze-portfolio", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setAiAnalysis(normalizeAiAnalysis(data));
      setShowAiPanel(true);
    } catch (error: unknown) {
      console.error("AI Portfolio Analysis error:", error);
      setAiError(error instanceof Error ? error.message : "Failed to fetch AI analysis");
    } finally {
      setAiLoading(false);
    }
  };

  const loadSupplementaryData = useCallback(async () => {
    setSupplementaryLoading(true);

    try {
      const response = await fetch("/api/proxy/api/portfolio/positions");
      let positions: PositionSlice[] = [];

      if (response.ok) {
        const payload = await response.json();
        const rawPositions = extractPositionsPayload(payload);

        const normalizedPositions: Array<PositionSlice | null> = rawPositions.map(
          (item): PositionSlice | null => {
            if (!item || typeof item !== "object") {
              return null;
            }

            const record = item as Record<string, unknown>;
            const rawSymbol = record.symbol ?? record.ticker;
            if (typeof rawSymbol !== "string") {
              return null;
            }

            const marketValueSource = record["market_value"] ?? record["marketValue"];
            const costBasisSource = record["cost_basis"] ?? record["costBasis"];
            const dayPnlSource =
              record["day_pl"] ??
              record["dayPnL"] ??
              record["unrealized_intraday_pl"] ??
              record["today_pl"] ??
              record["pnl_day"];
            const quantitySource = record["quantity"] ?? record["qty"] ?? record["shares"];

            const marketValue = parseOptionalNumeric(marketValueSource);
            const costBasis = parseOptionalNumeric(costBasisSource);
            const dayPnl = parseOptionalNumeric(dayPnlSource);
            const allocationBase =
              marketValue ?? parseOptionalNumeric(quantitySource) ?? parseNumeric(quantitySource);

            const position: PositionSlice = {
              symbol: rawSymbol.trim().toUpperCase(),
              allocation: allocationBase,
              ...(marketValue !== undefined ? { marketValue } : {}),
              ...(costBasis !== undefined ? { costBasis } : {}),
              ...(dayPnl !== undefined ? { dayPnl } : {}),
            };

            return position;
          }
        );

        positions = normalizedPositions.filter((value): value is PositionSlice => value !== null);

        positions.sort((a, b) => (b.marketValue ?? 0) - (a.marketValue ?? 0));
      }

      if (!positions.length) {
        positions = FALLBACK_POSITION_SLICES.map((slice) => ({ ...slice }));
      }

      setPositionSlices(positions);

      const focusSymbol = positions[0]?.symbol ?? "AAPL";
      const sanitizedFocus = sanitizeSymbol(focusSymbol) || focusSymbol.toUpperCase() || "AAPL";
      setCandlestickSymbol(sanitizedFocus);

      try {
        const fetchedCandles = await fetchCandlestickSeries(sanitizedFocus, CANDLE_INTERVALS);
        setCandlestickData(fetchedCandles);
      } catch (error) {
        console.error("Candlestick data load failed, using mock data:", error);
        setCandlestickData(generateMockCandlesSet(CANDLE_INTERVALS));
      }

      setGreeksHeatmapData(buildFallbackGreeks(positions));
    } catch (error: unknown) {
      console.error("Supplementary analytics load failed:", error);
      setPositionSlices(FALLBACK_POSITION_SLICES.map((slice) => ({ ...slice })));
      setCandlestickSymbol(sanitizeSymbol(FALLBACK_POSITION_SLICES[0]?.symbol) || "AAPL");
      setCandlestickData(generateMockCandlesSet(CANDLE_INTERVALS));
      setGreeksHeatmapData(buildFallbackGreeks(FALLBACK_POSITION_SLICES));
    } finally {
      setSupplementaryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAnalytics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeframe]);

  useEffect(() => {
    loadSupplementaryData();
  }, [loadSupplementaryData]);

  const marketSymbols = useMemo(() => {
    const dynamicSymbols = positionSlices
      .map((position) => position.symbol?.trim().toUpperCase())
      .filter((symbol): symbol is string => Boolean(symbol))
      .map((symbol) => ({ label: symbol, value: symbol }));

    const combined = [...dynamicSymbols, ...MARKET_SYMBOL_FALLBACKS];
    const seen = new Set<string>();

    return combined.filter((option) => {
      const key = option.value.toUpperCase();
      if (!key || seen.has(key)) {
        return false;
      }
      seen.add(key);
      return true;
    });
  }, [positionSlices]);

  const loadAnalytics = async () => {
    setLoading(true);

    try {
      // Fetch performance metrics from new analytics backend
      const perfResponse = await fetch(`/api/proxy/analytics/performance?period=${timeframe}`);
      const perfData = await perfResponse.json();

      // Fetch portfolio history
      const historyResponse = await fetch(`/api/proxy/portfolio/history?period=${timeframe}`);
      const historyData = await historyResponse.json();

      // Transform backend data to match component interface
      const metricsData: PerformanceMetrics = {
        totalReturn: perfData.total_return,
        totalReturnPercent: perfData.total_return_percent,
        winRate: perfData.win_rate,
        profitFactor: perfData.profit_factor,
        sharpeRatio: perfData.sharpe_ratio,
        maxDrawdown: perfData.max_drawdown_percent,
        avgWin: perfData.avg_win,
        avgLoss: Math.abs(perfData.avg_loss),
        totalTrades: perfData.num_trades,
        winningTrades: perfData.num_wins,
        losingTrades: perfData.num_losses,
      };

      // Transform equity history to daily performance format
      const dailyPerf: DailyPerformance[] = historyData.data.map(
        (point: { timestamp: string; equity: number }) => ({
          date: point.timestamp.split("T")[0],
          pnl: 0, // Calculate from equity changes
          portfolioValue: point.equity,
          trades: 0,
        })
      );

      // Calculate daily P&L from equity changes
      for (let i = 1; i < dailyPerf.length; i++) {
        dailyPerf[i].pnl = dailyPerf[i].portfolioValue - dailyPerf[i - 1].portfolioValue;
      }

      const monthlyData = generateMonthlyStats(); // Keep this for now

      setMetrics(metricsData);
      setDailyPerformance(dailyPerf);
      setMonthlyStats(monthlyData);
    } catch (error) {
      console.error("Failed to load analytics:", error);

      // Fallback to generating DEMO data if API fails
      setIsDemoMode(true);

      const mockMetrics: PerformanceMetrics = {
        totalReturn: 2500,
        totalReturnPercent: 2.5,
        winRate: 58.5,
        profitFactor: 2.13,
        sharpeRatio: 1.42,
        maxDrawdown: -12.3,
        avgWin: 142.5,
        avgLoss: 87.3,
        totalTrades: 47,
        winningTrades: 27,
        losingTrades: 20,
      };

      const mockDaily = generateDailyPerformance(timeframe);
      const mockMonthly = generateMonthlyStats();

      setMetrics(mockMetrics);
      setDailyPerformance(mockDaily);
      setMonthlyStats(mockMonthly);
    } finally {
      setLoading(false);
    }
  };

  const generateDailyPerformance = (tf: string): DailyPerformance[] => {
    const days = tf === "1W" ? 7 : tf === "1M" ? 30 : tf === "3M" ? 90 : tf === "1Y" ? 365 : 365;
    const data: DailyPerformance[] = [];
    let portfolioValue = 100000;

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const pnl = (Math.random() - 0.45) * 500;
      portfolioValue += pnl;
      data.push({
        date: date.toISOString().split("T")[0],
        pnl,
        portfolioValue,
        trades: Math.floor(Math.random() * 5),
      });
    }
    return data;
  };

  const generateMonthlyStats = (): MonthlyStats[] => {
    const months = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];
    const currentMonth = new Date().getMonth();
    const stats: MonthlyStats[] = [];

    for (let i = 0; i < 6; i++) {
      const monthIndex = (currentMonth - i + 12) % 12;
      stats.unshift({
        month: months[monthIndex],
        profit: (Math.random() - 0.3) * 5000,
        trades: Math.floor(Math.random() * 50) + 20,
        winRate: 50 + Math.random() * 20,
      });
    }
    return stats;
  };

  if (loading) {
    return (
      <div style={{ padding: theme.spacing.lg }}>
        <Card>
          <div
            style={{
              textAlign: "center",
              padding: theme.spacing.xl,
              color: theme.colors.textMuted,
            }}
          >
            Loading analytics...
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      {/* DEMO MODE Banner */}
      {isDemoMode && (
        <div
          style={{
            background: "rgba(251, 191, 36, 0.1)",
            border: "2px solid rgba(251, 191, 36, 0.5)",
            borderRadius: theme.borderRadius.lg,
            padding: theme.spacing.md,
            marginBottom: theme.spacing.lg,
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.md,
          }}
        >
          <div
            style={{
              background: "rgba(251, 191, 36, 0.2)",
              borderRadius: "50%",
              padding: theme.spacing.sm,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span style={{ fontSize: "24px" }}>⚠️</span>
          </div>
          <div>
            <h3
              style={{
                margin: 0,
                color: "#fbbf24",
                fontSize: "16px",
                fontWeight: "700",
              }}
            >
              DEMO MODE
            </h3>
            <p
              style={{
                margin: `${theme.spacing.xs} 0 0 0`,
                color: theme.colors.textMuted,
                fontSize: "14px",
              }}
            >
              Using sample data - API unavailable. This is demonstration data only.
            </p>
          </div>
        </div>
      )}

      {/* Header with PaiiD Logo */}
      <div
        style={{
          display: "flex",
          alignItems: isMobile ? "flex-start" : "center",
          justifyContent: "space-between",
          marginBottom: theme.spacing.lg,
          flexDirection: isMobile ? "column" : "row",
          gap: isMobile ? theme.spacing.md : "0",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.md }}>
          {/* PaiiD Logo */}
          <div style={{ fontSize: isMobile ? "28px" : "42px", fontWeight: "900", lineHeight: "1" }}>
            <span
              style={{
                background: "linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                filter: "drop-shadow(0 3px 8px rgba(26, 117, 96, 0.4))",
              }}
            >
              P
            </span>
            <span
              style={{
                background: "linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                textShadow: "0 0 18px rgba(69, 240, 192, 0.8), 0 0 36px rgba(69, 240, 192, 0.4)",
                animation: "glow-ai 3s ease-in-out infinite",
              }}
            >
              aii
            </span>
            <span
              style={{
                background: "linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                filter: "drop-shadow(0 3px 8px rgba(26, 117, 96, 0.4))",
              }}
            >
              D
            </span>
          </div>

          <BarChart3 size={isMobile ? 24 : 32} color={theme.colors.info} />
          <h1
            style={{
              margin: 0,
              fontSize: isMobile ? "24px" : "32px",
              fontWeight: "700",
              color: theme.colors.text,
              textShadow: `0 0 20px ${theme.colors.info}40`,
            }}
          >
            Analytics Dashboard
          </h1>
        </div>

        {/* Timeframe Selector */}
        <div
          style={{
            display: "flex",
            gap: theme.spacing.xs,
            flexWrap: "wrap",
            width: isMobile ? "100%" : "auto",
          }}
        >
          {(["1W", "1M", "3M", "1Y", "ALL"] as const).map((tf) => (
            <Button
              key={tf}
              variant={timeframe === tf ? "primary" : "secondary"}
              size="sm"
              onClick={() => setTimeframe(tf)}
              style={{ flex: isMobile ? "1" : "none", minWidth: isMobile ? "0" : "auto" }}
            >
              {tf}
            </Button>
          ))}
        </div>
      </div>

      {/* Portfolio Summary Card */}
      <PortfolioSummaryCard />

      {/* AI Portfolio Health Check Button */}
      <div style={{ marginBottom: theme.spacing.lg }}>
        <button
          onClick={fetchAIPortfolioAnalysis}
          disabled={aiLoading}
          style={{
            padding: "12px 24px",
            backgroundColor: aiLoading ? "#4B5563" : "#8B5CF6",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: aiLoading ? "not-allowed" : "pointer",
            fontSize: "16px",
            fontWeight: "600",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            transition: "all 0.2s",
          }}
        >
          <span style={{ fontSize: "20px" }}>🤖</span>
          {aiLoading ? "Analyzing Portfolio..." : "AI Portfolio Health Check"}
        </button>

        {/* AI Analysis Panel */}
        {showAiPanel && aiAnalysis && (
          <div
            style={{
              marginTop: "24px",
              padding: "24px",
              background:
                "linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1))",
              border: "1px solid rgba(139, 92, 246, 0.3)",
              borderRadius: "12px",
              backdropFilter: "blur(10px)",
            }}
          >
            {/* Header */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "20px",
              }}
            >
              <h3 style={{ fontSize: "24px", fontWeight: "bold", color: "#E2E8F0" }}>
                🤖 AI Portfolio Health Analysis
              </h3>
              <button
                onClick={() => setShowAiPanel(false)}
                style={{
                  background: "none",
                  border: "none",
                  color: "#94A3B8",
                  cursor: "pointer",
                  fontSize: "24px",
                }}
              >
                ×
              </button>
            </div>

            {/* Health Score */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                gap: "16px",
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  padding: "16px",
                  background: "rgba(15, 23, 42, 0.6)",
                  borderRadius: "8px",
                  border: "1px solid rgba(148, 163, 184, 0.2)",
                }}
              >
                <div style={{ fontSize: "14px", color: "#94A3B8", marginBottom: "8px" }}>
                  Health Score
                </div>
                <div style={{ fontSize: "32px", fontWeight: "bold", color: "#10B981" }}>
                  {aiAnalysis.health_score}/100
                </div>
              </div>

              <div
                style={{
                  padding: "16px",
                  background: "rgba(15, 23, 42, 0.6)",
                  borderRadius: "8px",
                  border: "1px solid rgba(148, 163, 184, 0.2)",
                }}
              >
                <div style={{ fontSize: "14px", color: "#94A3B8", marginBottom: "8px" }}>
                  Risk Level
                </div>
                <div
                  style={{
                    fontSize: "24px",
                    fontWeight: "bold",
                    color:
                      aiAnalysis.risk_level === "Low"
                        ? "#10B981"
                        : aiAnalysis.risk_level === "Medium"
                          ? "#F59E0B"
                          : "#EF4444",
                  }}
                >
                  {aiAnalysis.risk_level}
                </div>
              </div>

              <div
                style={{
                  padding: "16px",
                  background: "rgba(15, 23, 42, 0.6)",
                  borderRadius: "8px",
                  border: "1px solid rgba(148, 163, 184, 0.2)",
                }}
              >
                <div style={{ fontSize: "14px", color: "#94A3B8", marginBottom: "8px" }}>
                  Diversification
                </div>
                <div style={{ fontSize: "32px", fontWeight: "bold", color: "#3B82F6" }}>
                  {aiAnalysis.diversification_score}/100
                </div>
              </div>
            </div>

            {/* AI Summary */}
            <div
              style={{
                padding: "16px",
                background: "rgba(15, 23, 42, 0.6)",
                borderRadius: "8px",
                border: "1px solid rgba(148, 163, 184, 0.2)",
                marginBottom: "16px",
              }}
            >
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: "bold",
                  color: "#E2E8F0",
                  marginBottom: "8px",
                }}
              >
                📊 AI Summary
              </div>
              <div style={{ fontSize: "14px", color: "#CBD5E1", lineHeight: "1.6" }}>
                {aiAnalysis.ai_summary}
              </div>
            </div>

            {/* Recommendations */}
            <div
              style={{
                padding: "16px",
                background: "rgba(15, 23, 42, 0.6)",
                borderRadius: "8px",
                border: "1px solid rgba(148, 163, 184, 0.2)",
                marginBottom: "16px",
              }}
            >
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: "bold",
                  color: "#E2E8F0",
                  marginBottom: "12px",
                }}
              >
                💡 AI Recommendations
              </div>
              <ul style={{ margin: 0, paddingLeft: "20px" }}>
                {aiAnalysis.recommendations.map((rec: string, idx: number) => (
                  <li
                    key={idx}
                    style={{
                      fontSize: "14px",
                      color: "#CBD5E1",
                      marginBottom: "8px",
                      lineHeight: "1.6",
                    }}
                  >
                    {rec}
                  </li>
                ))}
              </ul>
            </div>

            {/* Risk Factors */}
            {aiAnalysis.risk_factors.length > 0 && (
              <div
                style={{
                  padding: "16px",
                  background: "rgba(15, 23, 42, 0.6)",
                  borderRadius: "8px",
                  border: "1px solid rgba(239, 68, 68, 0.3)",
                  marginBottom: "16px",
                }}
              >
                <div
                  style={{
                    fontSize: "16px",
                    fontWeight: "bold",
                    color: "#EF4444",
                    marginBottom: "12px",
                  }}
                >
                  ⚠️ Risk Factors
                </div>
                <ul style={{ margin: 0, paddingLeft: "20px" }}>
                  {aiAnalysis.risk_factors.map((risk: string, idx: number) => (
                    <li
                      key={idx}
                      style={{
                        fontSize: "14px",
                        color: "#FCA5A5",
                        marginBottom: "8px",
                        lineHeight: "1.6",
                      }}
                    >
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Opportunities */}
            {aiAnalysis.opportunities.length > 0 && (
              <div
                style={{
                  padding: "16px",
                  background: "rgba(15, 23, 42, 0.6)",
                  borderRadius: "8px",
                  border: "1px solid rgba(16, 185, 129, 0.3)",
                }}
              >
                <div
                  style={{
                    fontSize: "16px",
                    fontWeight: "bold",
                    color: "#10B981",
                    marginBottom: "12px",
                  }}
                >
                  🎯 Opportunities
                </div>
                <ul style={{ margin: 0, paddingLeft: "20px" }}>
                  {aiAnalysis.opportunities.map((opp: string, idx: number) => (
                    <li
                      key={idx}
                      style={{
                        fontSize: "14px",
                        color: "#6EE7B7",
                        marginBottom: "8px",
                        lineHeight: "1.6",
                      }}
                    >
                      {opp}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {aiError && (
          <div
            style={{
              marginTop: "16px",
              padding: "16px",
              background: "rgba(239, 68, 68, 0.1)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              borderRadius: "8px",
              color: "#FCA5A5",
            }}
          >
            ⚠️ {aiError}
          </div>
        )}
      </div>

      {/* Performance Metrics */}
      {metrics && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: theme.spacing.md,
              marginBottom: theme.spacing.lg,
            }}
          >
            <MetricCard
              icon={
                <DollarSign
                  size={20}
                  color={metrics.totalReturn >= 0 ? theme.colors.primary : theme.colors.danger}
                />
              }
              label="Total Return"
              value={`$${Math.abs(metrics.totalReturn).toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
              subValue={`${metrics.totalReturnPercent >= 0 ? "+" : ""}${metrics.totalReturnPercent.toFixed(2)}%`}
              valueColor={metrics.totalReturn >= 0 ? theme.colors.primary : theme.colors.danger}
            />
            <MetricCard
              icon={<Percent size={20} color={theme.colors.secondary} />}
              label="Win Rate"
              value={`${metrics.winRate.toFixed(1)}%`}
              subValue={`${metrics.winningTrades}W / ${metrics.losingTrades}L`}
            />
            <MetricCard
              icon={<Target size={20} color={theme.colors.primary} />}
              label="Profit Factor"
              value={metrics.profitFactor.toFixed(2)}
              valueColor={metrics.profitFactor > 1 ? theme.colors.primary : theme.colors.danger}
            />
            <MetricCard
              icon={<Award size={20} color={theme.colors.info} />}
              label="Sharpe Ratio"
              value={metrics.sharpeRatio.toFixed(2)}
              valueColor={metrics.sharpeRatio > 1 ? theme.colors.primary : theme.colors.warning}
            />
            <MetricCard
              icon={<TrendingDown size={20} color={theme.colors.danger} />}
              label="Max Drawdown"
              value={`${metrics.maxDrawdown.toFixed(2)}%`}
              valueColor={theme.colors.danger}
            />
            <MetricCard
              icon={<BarChart3 size={20} color={theme.colors.secondary} />}
              label="Total Trades"
              value={metrics.totalTrades.toString()}
            />
          </div>

          {/* Equity Curve */}
          <Card style={{ marginBottom: theme.spacing.lg }} glow="teal">
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: theme.spacing.md,
              }}
            >
              <h3 style={{ margin: 0, color: theme.colors.text, fontSize: "18px" }}>
                Portfolio Value Over Time
              </h3>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => exportChartAsPNG(equityChartRef, "Equity_Curve")}
                style={{ display: "flex", alignItems: "center", gap: theme.spacing.xs }}
              >
                <Download size={16} />
                {!isMobile && "Export"}
              </Button>
            </div>
            <div
              ref={equityChartRef}
              style={{
                height: isMobile ? "200px" : "300px",
                display: "flex",
                alignItems: "flex-end",
                gap: "2px",
                padding: theme.spacing.md,
                background: theme.background.input,
                borderRadius: theme.borderRadius.sm,
              }}
            >
              {dailyPerformance
                .filter((_, i) => {
                  // Sample data based on timeframe
                  const sampleRate =
                    timeframe === "1W" ? 1 : timeframe === "1M" ? 1 : timeframe === "3M" ? 3 : 7;
                  return i % sampleRate === 0;
                })
                .map((point, index) => {
                  const minValue = Math.min(...dailyPerformance.map((d) => d.portfolioValue));
                  const maxValue = Math.max(...dailyPerformance.map((d) => d.portfolioValue));
                  const range = maxValue - minValue;
                  const height = range > 0 ? ((point.portfolioValue - minValue) / range) * 100 : 50;

                  return (
                    <div
                      key={index}
                      style={{
                        flex: 1,
                        height: `${Math.max(height, 5)}%`,
                        background:
                          point.portfolioValue > 100000
                            ? theme.colors.primary
                            : theme.colors.danger,
                        borderRadius: "2px 2px 0 0",
                        transition: theme.transitions.fast,
                      }}
                      title={`${point.date}: $${point.portfolioValue.toFixed(2)}`}
                    />
                  );
                })}
            </div>
          </Card>

          {/* Daily P&L Chart */}
          <Card style={{ marginBottom: theme.spacing.lg }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: theme.spacing.md,
              }}
            >
              <h3 style={{ margin: 0, color: theme.colors.text, fontSize: "18px" }}>Daily P&L</h3>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => exportChartAsPNG(pnlChartRef, "Daily_PnL")}
                style={{ display: "flex", alignItems: "center", gap: theme.spacing.xs }}
              >
                <Download size={16} />
                {!isMobile && "Export"}
              </Button>
            </div>
            <div
              ref={pnlChartRef}
              style={{
                height: isMobile ? "150px" : "200px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "2px",
                padding: theme.spacing.md,
                background: theme.background.input,
                borderRadius: theme.borderRadius.sm,
              }}
            >
              {dailyPerformance
                .filter((_, i) => {
                  const sampleRate =
                    timeframe === "1W" ? 1 : timeframe === "1M" ? 1 : timeframe === "3M" ? 3 : 7;
                  return i % sampleRate === 0;
                })
                .map((point, index) => {
                  const maxPnl = Math.max(...dailyPerformance.map((d) => Math.abs(d.pnl)));
                  const height = maxPnl > 0 ? (Math.abs(point.pnl) / maxPnl) * 90 : 10;

                  return (
                    <div
                      key={index}
                      style={{
                        flex: 1,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: point.pnl >= 0 ? "flex-end" : "flex-start",
                        height: "100%",
                      }}
                    >
                      <div
                        style={{
                          width: "100%",
                          height: `${height}%`,
                          background: point.pnl >= 0 ? theme.colors.primary : theme.colors.danger,
                          borderRadius: "2px",
                          transition: theme.transitions.fast,
                        }}
                        title={`${point.date}: ${point.pnl >= 0 ? "+" : ""}$${point.pnl.toFixed(2)}`}
                      />
                    </div>
                  );
                })}
            </div>
          </Card>

          {/* Monthly Performance */}
          <Card style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                margin: `0 0 ${theme.spacing.md} 0`,
                color: theme.colors.text,
                fontSize: "18px",
              }}
            >
              Monthly Performance
            </h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
                gap: theme.spacing.md,
              }}
            >
              {monthlyStats.map((stat, index) => (
                <div
                  key={index}
                  style={{
                    padding: theme.spacing.md,
                    background: theme.background.input,
                    borderRadius: theme.borderRadius.md,
                    borderLeft: `4px solid ${stat.profit >= 0 ? theme.colors.primary : theme.colors.danger}`,
                  }}
                >
                  <p style={{ margin: 0, fontSize: "12px", color: theme.colors.textMuted }}>
                    {stat.month}
                  </p>
                  <p
                    style={{
                      margin: `${theme.spacing.xs} 0`,
                      fontSize: "20px",
                      fontWeight: "700",
                      color: stat.profit >= 0 ? theme.colors.primary : theme.colors.danger,
                    }}
                  >
                    {stat.profit >= 0 ? "+" : ""}${stat.profit.toFixed(0)}
                  </p>
                  <p style={{ margin: 0, fontSize: "12px", color: theme.colors.textMuted }}>
                    {stat.trades} trades · {stat.winRate.toFixed(0)}% win
                  </p>
                </div>
              ))}
            </div>
          </Card>

          {/* Market Intelligence */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: isMobile ? "1fr" : "repeat(2, minmax(320px, 1fr))",
              gap: theme.spacing.lg,
              marginBottom: theme.spacing.lg,
            }}
          >
            <MarketChart symbols={marketSymbols} height={isMobile ? 360 : 420} />
            <CandlestickViews
              candlesByTimeframe={candlestickData}
              defaultTimeframe="1D"
              title={`Price Action · ${candlestickSymbol}`}
              description={
                supplementaryLoading
                  ? "Loading candlestick data…"
                  : "Multi-interval perspective for your top holding."
              }
              height={isMobile ? 320 : 360}
            />
          </div>

          {/* Portfolio Composition & Risk */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: isMobile ? "1fr" : "repeat(2, minmax(320px, 1fr))",
              gap: theme.spacing.lg,
              marginBottom: theme.spacing.lg,
            }}
          >
            <PositionAllocationChart
              positions={positionSlices}
              description={
                supplementaryLoading
                  ? "Refreshing portfolio allocation…"
                  : "Share of total capital across open positions."
              }
            />
            <GreeksHeatmap
              data={greeksHeatmapData}
              title="Portfolio Greeks Exposure"
              description={
                supplementaryLoading
                  ? "Refreshing Greeks exposure…"
                  : "Sensitivity snapshot across key Greeks."
              }
            />
          </div>

          {/* Trade Statistics */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
              gap: theme.spacing.md,
            }}
          >
            <Card>
              <h3
                style={{
                  margin: `0 0 ${theme.spacing.md} 0`,
                  color: theme.colors.text,
                  fontSize: "18px",
                }}
              >
                Win/Loss Analysis
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.sm }}>
                <StatRow
                  label="Average Win"
                  value={`$${metrics.avgWin.toFixed(2)}`}
                  color={theme.colors.primary}
                />
                <StatRow
                  label="Average Loss"
                  value={`$${Math.abs(metrics.avgLoss).toFixed(2)}`}
                  color={theme.colors.danger}
                />
                <StatRow
                  label="Win/Loss Ratio"
                  value={(metrics.avgWin / Math.abs(metrics.avgLoss)).toFixed(2)}
                />
              </div>
            </Card>

            <Card>
              <h3
                style={{
                  margin: `0 0 ${theme.spacing.md} 0`,
                  color: theme.colors.text,
                  fontSize: "18px",
                }}
              >
                Risk Metrics
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.sm }}>
                <StatRow label="Sharpe Ratio" value={metrics.sharpeRatio.toFixed(2)} />
                <StatRow label="Profit Factor" value={metrics.profitFactor.toFixed(2)} />
                <StatRow
                  label="Max Drawdown"
                  value={`${metrics.maxDrawdown.toFixed(2)}%`}
                  color={theme.colors.danger}
                />
              </div>
            </Card>
          </div>
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

function StatRow({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <span style={{ fontSize: "14px", color: theme.colors.textMuted }}>{label}</span>
      <span style={{ fontSize: "16px", fontWeight: "600", color: color || theme.colors.text }}>
        {value}
      </span>
    </div>
  );
}
