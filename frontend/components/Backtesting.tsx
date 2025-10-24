"use client";

import { useState, useMemo, ReactNode } from "react";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Activity,
  DollarSign,
  Percent,
  Play,
} from "lucide-react";

import { Card, Button, Input, Select } from "./ui";
import { theme } from "../styles/theme";
import { useIsMobile } from "../hooks/useBreakpoint";

interface BacktestConfig {
  symbol: string;
  startDate: string;
  endDate: string;
  initialCapital: string;
  strategyName: StrategyKey;
}

interface BacktestResults {
  performance: {
    total_return: number;
    total_return_percent: number;
    annualized_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    max_drawdown_percent: number;
  };
  statistics: {
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    avg_win: number;
    avg_loss: number;
    profit_factor: number;
  };
  capital: {
    initial: number;
    final: number;
  };
  config: {
    symbol: string;
    start_date: string;
    end_date: string;
  };
  equityCurve: { date: string; value: number; drawdown?: number }[];
  tradeHistory: {
    date: string;
    type: "buy" | "sell";
    price: number;
    quantity: number;
    pnl: number;
    entryDate: string;
    exitDate: string | null;
  }[];
}

type StrategyKey = "rsi" | "ma" | "breakout";

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);

const STRATEGY_TEMPLATES: Record<StrategyKey, { entry_rules: any[]; exit_rules: any[] }> = {
  rsi: {
    entry_rules: [{ indicator: "RSI", operator: "<", value: 30 }],
    exit_rules: [
      { indicator: "RSI", operator: ">", value: 55 },
      { type: "take_profit", value: 5 },
      { type: "stop_loss", value: 2 },
    ],
  },
  ma: {
    entry_rules: [
      { indicator: "SMA", operator: ">", period: 50, compared_to: { indicator: "SMA", period: 200 } },
    ],
    exit_rules: [
      { indicator: "SMA", operator: "<", period: 50, compared_to: { indicator: "SMA", period: 200 } },
      { type: "stop_loss", value: 3 },
    ],
  },
  breakout: {
    entry_rules: [
      { indicator: "PRICE", operator: ">", value: "recent_high", lookback: 20 },
      { indicator: "VOLUME", operator: ">", multiplier: 1.3, compared_to: "average" },
    ],
    exit_rules: [
      { type: "trailing_stop", value: 4 },
      { type: "take_profit", value: 8 },
    ],
  },
};

const STRATEGY_OPTIONS = [
  { value: "rsi", label: "RSI Reversal" },
  { value: "ma", label: "Moving Average Crossover" },
  { value: "breakout", label: "Breakout Momentum" },
];

export default function Backtesting() {
  const isMobile = useIsMobile();
  const [config, setConfig] = useState<BacktestConfig>({
    symbol: "SPY",
    startDate: "2024-01-01",
    endDate: "2024-12-31",
    initialCapital: "10000",
    strategyName: "rsi",
  });
  const [results, setResults] = useState<BacktestResults | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const equityBounds = useMemo(() => {
    if (!results || results.equityCurve.length === 0) {
      return { min: 0, max: 0 };
    }
    const values = results.equityCurve.map((point) => point.value);
    return {
      min: Math.min(...values),
      max: Math.max(...values),
    };
  }, [results]);

  const runBacktest = async () => {
    if (!config.symbol.trim()) {
      setError("Please enter a symbol to backtest.");
      return;
    }

    setIsRunning(true);
    setError(null);

    try {
      const strategyTemplate = STRATEGY_TEMPLATES[config.strategyName];
      if (!strategyTemplate) {
        throw new Error("Selected strategy is not supported");
      }

      const initialCapital = Number(config.initialCapital);
      if (!Number.isFinite(initialCapital) || initialCapital <= 0) {
        throw new Error("Initial capital must be a positive number");
      }

      const payload = {
        symbol: config.symbol.trim().toUpperCase(),
        start_date: config.startDate,
        end_date: config.endDate,
        initial_capital: initialCapital,
        entry_rules: strategyTemplate.entry_rules,
        exit_rules: strategyTemplate.exit_rules,
        position_size_percent: 10,
        max_positions: 1,
      };

      const response = await fetch("/api/proxy/backtesting/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail ?? `Backtest failed with status ${response.status}`);
      }

      if (!data?.success) {
        throw new Error(data?.error ?? "Backtest failed");
      }

      const resultPayload = data.result;
      const transformed: BacktestResults = {
        performance: {
          total_return: Number(resultPayload.performance?.total_return ?? 0),
          total_return_percent: Number(resultPayload.performance?.total_return_percent ?? 0),
          annualized_return: Number(resultPayload.performance?.annualized_return ?? 0),
          sharpe_ratio: Number(resultPayload.performance?.sharpe_ratio ?? 0),
          max_drawdown: Number(resultPayload.performance?.max_drawdown ?? 0),
          max_drawdown_percent: Number(
            resultPayload.performance?.max_drawdown_percent ?? 0,
          ),
        },
        statistics: {
          total_trades: Number(resultPayload.statistics?.total_trades ?? 0),
          winning_trades: Number(resultPayload.statistics?.winning_trades ?? 0),
          losing_trades: Number(resultPayload.statistics?.losing_trades ?? 0),
          win_rate: Number(resultPayload.statistics?.win_rate ?? 0),
          avg_win: Number(resultPayload.statistics?.avg_win ?? 0),
          avg_loss: Number(resultPayload.statistics?.avg_loss ?? 0),
          profit_factor: Number(resultPayload.statistics?.profit_factor ?? 0),
        },
        capital: {
          initial: Number(resultPayload.capital?.initial ?? initialCapital),
          final: Number(resultPayload.capital?.final ?? initialCapital),
        },
        config: {
          symbol: String(resultPayload.config?.symbol ?? payload.symbol),
          start_date: String(resultPayload.config?.start_date ?? payload.start_date),
          end_date: String(resultPayload.config?.end_date ?? payload.end_date),
        },
        equityCurve: Array.isArray(resultPayload.equity_curve)
          ? resultPayload.equity_curve.map((point: any) => ({
              date: String(point?.date ?? ""),
              value: Number(point?.value ?? 0),
              drawdown: Number(point?.drawdown ?? 0),
            }))
          : [],
        tradeHistory: Array.isArray(resultPayload.trade_history)
          ? resultPayload.trade_history.map((trade: any) => ({
              date: String(trade?.exit_date ?? trade?.entry_date ?? ""),
              type: String(trade?.side ?? "buy").toLowerCase() === "sell" ? "sell" : "buy",
              price: Number(trade?.exit_price ?? trade?.entry_price ?? 0),
              quantity: Number(trade?.quantity ?? 0),
              pnl: Number(trade?.pnl ?? 0),
              entryDate: String(trade?.entry_date ?? ""),
              exitDate: trade?.exit_date ? String(trade.exit_date) : null,
            }))
          : [],
      };

      setResults(transformed);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Backtest failed";
      setError(message);
      setResults(null);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: isMobile ? theme.spacing.sm : theme.spacing.md,
          marginBottom: theme.spacing.lg,
          flexWrap: "wrap",
        }}
      >
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
          Backtesting
        </h1>
      </div>

      <Card glow="teal" style={{ marginBottom: theme.spacing.lg }}>
        <h3
          style={{
            margin: `0 0 ${theme.spacing.md} 0`,
            color: theme.colors.text,
            fontSize: "18px",
          }}
        >
          Configuration
        </h3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "repeat(auto-fit, minmax(200px, 1fr))",
            gap: theme.spacing.md,
            marginBottom: theme.spacing.md,
          }}
        >
          <Select
            label="Strategy"
            options={STRATEGY_OPTIONS.map((option) => ({ value: option.value, label: option.label }))}
            value={config.strategyName}
            onChange={(e) => setConfig({ ...config, strategyName: e.target.value as StrategyKey })}
          />
          <Input
            label="Symbol"
            value={config.symbol}
            onChange={(e) => setConfig({ ...config, symbol: e.target.value.toUpperCase() })}
          />
          <Input
            label="Start Date"
            type="date"
            value={config.startDate}
            onChange={(e) => setConfig({ ...config, startDate: e.target.value })}
          />
          <Input
            label="End Date"
            type="date"
            value={config.endDate}
            onChange={(e) => setConfig({ ...config, endDate: e.target.value })}
          />
          <Input
            label="Initial Capital"
            type="number"
            value={config.initialCapital}
            onChange={(e) => setConfig({ ...config, initialCapital: e.target.value })}
          />
        </div>
        <Button
          variant="primary"
          size="md"
          loading={isRunning}
          onClick={runBacktest}
          style={{
            margin: isMobile ? 0 : "0 auto",
            display: "block",
            width: isMobile ? "100%" : "auto",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.xs }}>
            <Play size={20} />
            {isRunning ? "Running..." : "Run Backtest"}
          </div>
        </Button>
      </Card>

      {error && (
        <Card glow="red" style={{ marginBottom: theme.spacing.lg }}>
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
            <Button variant="secondary" size="sm" onClick={runBacktest}>
              Retry
            </Button>
          </div>
        </Card>
      )}

      {results && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: isMobile ? "1fr" : "repeat(auto-fit, minmax(200px, 1fr))",
              gap: theme.spacing.md,
              marginBottom: theme.spacing.lg,
            }}
          >
            <MetricCard
              icon={
                <DollarSign
                  size={20}
                  color={
                    results.performance.total_return >= 0
                      ? theme.colors.primary
                      : theme.colors.danger
                  }
                />
              }
              label="Total Return"
              value={`${results.performance.total_return.toLocaleString("en-US", {
                minimumFractionDigits: 2,
              })}`}
              subValue={`${
                results.performance.total_return_percent >= 0 ? "+" : ""
              }${results.performance.total_return_percent.toFixed(2)}%`}
              valueColor={
                results.performance.total_return >= 0
                  ? theme.colors.primary
                  : theme.colors.danger
              }
            />
            <MetricCard
              icon={<TrendingUp size={20} color={theme.colors.primary} />}
              label="Annualized Return"
              value={`${
                results.performance.annualized_return >= 0 ? "+" : ""
              }${results.performance.annualized_return.toFixed(2)}%`}
              valueColor={
                results.performance.annualized_return >= 0
                  ? theme.colors.primary
                  : theme.colors.danger
              }
            />
            <MetricCard
              icon={<Activity size={20} color={theme.colors.info} />}
              label="Sharpe Ratio"
              value={results.performance.sharpe_ratio.toFixed(2)}
            />
            <MetricCard
              icon={<TrendingDown size={20} color={theme.colors.danger} />}
              label="Max Drawdown"
              value={`${results.performance.max_drawdown_percent.toFixed(2)}%`}
              subValue={`${formatCurrency(results.performance.max_drawdown)} drawdown`}
              valueColor={theme.colors.danger}
            />
            <MetricCard
              icon={<Percent size={20} color={theme.colors.secondary} />}
              label="Win Rate"
              value={`${results.statistics.win_rate.toFixed(1)}%`}
            />
            <MetricCard
              icon={<BarChart3 size={20} color={theme.colors.primary} />}
              label="Profit Factor"
              value={results.statistics.profit_factor.toFixed(2)}
              valueColor={
                results.statistics.profit_factor > 1
                  ? theme.colors.primary
                  : theme.colors.danger
              }
            />
          </div>

          <Card style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                margin: `0 0 ${theme.spacing.md} 0`,
                color: theme.colors.text,
                fontSize: "18px",
              }}
            >
              Equity Curve
            </h3>
            <div
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
              {results.equityCurve.length === 0 ? (
                <p style={{ color: theme.colors.textMuted }}>No equity data available</p>
              ) : (
                results.equityCurve
                  .filter((_, index) => index % 5 === 0)
                  .map((point, index) => {
                    const { min, max } = equityBounds;
                    const range = max - min || 1;
                    const relativeHeight = ((point.value - min) / range) * 100;
                    return (
                      <div
                        key={`${point.date}-${index}`}
                        style={{
                          flex: 1,
                          height: `${relativeHeight}%`,
                          background:
                            point.value >= results.capital.initial
                              ? theme.colors.primary
                              : theme.colors.danger,
                          borderRadius: "2px 2px 0 0",
                          transition: theme.transitions.fast,
                        }}
                        title={`${point.date}: ${point.value.toFixed(2)}`}
                      />
                    );
                  })
              )}
            </div>
          </Card>

          <Card style={{ marginBottom: theme.spacing.lg }}>
            <h3
              style={{
                margin: `0 0 ${theme.spacing.md} 0`,
                color: theme.colors.text,
                fontSize: "18px",
              }}
            >
              Trade Statistics
            </h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: isMobile
                  ? "repeat(2, 1fr)"
                  : "repeat(auto-fit, minmax(150px, 1fr))",
                gap: theme.spacing.md,
              }}
            >
              <StatItem label="Total Trades" value={results.statistics.total_trades.toString()} />
              <StatItem
                label="Winning"
                value={results.statistics.winning_trades.toString()}
                color={theme.colors.primary}
              />
              <StatItem
                label="Losing"
                value={results.statistics.losing_trades.toString()}
                color={theme.colors.danger}
              />
              <StatItem
                label="Avg Win"
                value={`${results.statistics.avg_win.toFixed(2)}`}
                color={theme.colors.primary}
              />
              <StatItem
                label="Avg Loss"
                value={`${Math.abs(results.statistics.avg_loss).toFixed(2)}`}
                color={theme.colors.danger}
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
              Recent Trades
            </h3>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ borderBottom: `1px solid ${theme.colors.border}` }}>
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "left",
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                      }}
                    >
                      Entry Date
                    </th>
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "left",
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                      }}
                    >
                      Exit Date
                    </th>
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "left",
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                      }}
                    >
                      Type
                    </th>
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "right",
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                      }}
                    >
                      Exit Price
                    </th>
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "right",
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                      }}
                    >
                      Qty
                    </th>
                    <th
                      style={{
                        padding: theme.spacing.sm,
                        textAlign: "right",
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                      }}
                    >
                      P&L
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {results.tradeHistory.map((trade, index) => (
                    <tr key={`${trade.date}-${index}`} style={{ borderBottom: `1px solid ${theme.colors.border}40` }}>
                      <td
                        style={{
                          padding: theme.spacing.sm,
                          fontSize: "14px",
                          color: theme.colors.text,
                        }}
                      >
                        {trade.entryDate || "-"}
                      </td>
                      <td
                        style={{
                          padding: theme.spacing.sm,
                          fontSize: "14px",
                          color: theme.colors.text,
                        }}
                      >
                        {trade.exitDate || "Open"}
                      </td>
                      <td style={{ padding: theme.spacing.sm }}>
                        <span
                          style={{
                            padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
                            borderRadius: theme.borderRadius.sm,
                            fontSize: "12px",
                            fontWeight: "600",
                            background:
                              trade.type === "buy"
                                ? `${theme.colors.primary}20`
                                : `${theme.colors.danger}20`,
                            color: trade.type === "buy" ? theme.colors.primary : theme.colors.danger,
                          }}
                        >
                          {trade.type.toUpperCase()}
                        </span>
                      </td>
                      <td
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "right",
                          fontSize: "14px",
                          color: theme.colors.text,
                        }}
                      >
                        {formatCurrency(trade.price)}
                      </td>
                      <td
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "right",
                          fontSize: "14px",
                          color: theme.colors.text,
                        }}
                      >
                        {trade.quantity}
                      </td>
                      <td
                        style={{
                          padding: theme.spacing.sm,
                          textAlign: "right",
                          fontSize: "14px",
                          fontWeight: "600",
                          color: trade.pnl >= 0 ? theme.colors.primary : theme.colors.danger,
                        }}
                      >
                        {trade.pnl >= 0 ? "+" : ""}{trade.pnl.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}

      <style jsx>{`
        @keyframes glow-ai {
          0%,
          100% {
            filter: drop-shadow(0 0 8px rgba(69, 240, 192, 0.6));
          }
          50% {
            filter: drop-shadow(0 0 16px rgba(69, 240, 192, 0.9));
          }
        }
      `}</style>
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
  icon: ReactNode;
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

function StatItem({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div>
      <p style={{ fontSize: "12px", color: theme.colors.textMuted, margin: 0 }}>{label}</p>
      <p
        style={{
          fontSize: "18px",
          fontWeight: "600",
          color: color || theme.colors.text,
          margin: `${theme.spacing.xs} 0 0 0`,
        }}
      >
        {value}
      </p>
    </div>
  );
}
