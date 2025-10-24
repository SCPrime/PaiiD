"use client";

import React, { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { Activity, LineChart as LineChartIcon } from "lucide-react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Button, Card } from "@/components/ui";
import { theme } from "@/styles/theme";

import { usePortfolioHistory } from "../hooks/usePortfolioHistory";
import { EquityHistoryPoint } from "../types";

const TradingViewChart = dynamic(() => import("@/components/TradingViewChart"), {
  ssr: false,
  loading: () => (
    <div
      style={{
        height: 320,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: theme.colors.textMuted,
      }}
    >
      Loading live market chart…
    </div>
  ),
});

const PERIODS: { label: string; value: string }[] = [
  { label: "1W", value: "1W" },
  { label: "1M", value: "1M" },
  { label: "3M", value: "3M" },
  { label: "1Y", value: "1Y" },
];

function formatCurrency(value: number) {
  return value.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  });
}

function transformHistory(points: EquityHistoryPoint[]) {
  return points.map((point) => ({
    date: new Date(point.timestamp).toLocaleDateString(),
    equity: point.equity,
    cash: point.cash,
  }));
}

export function PortfolioPerformancePanel() {
  const [period, setPeriod] = useState<string>("1M");
  const { data, isLoading, error, refresh } = usePortfolioHistory(period);

  const history = useMemo(() => transformHistory(data?.data ?? []), [data]);

  return (
    <Card style={{ display: "grid", gap: theme.spacing.lg }}>
      <header
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          justifyContent: "space-between",
          gap: theme.spacing.md,
        }}
      >
        <div>
          <h3 style={{ margin: 0, color: theme.colors.text }}>Performance &amp; Exposure</h3>
          <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "14px" }}>
            Track equity curve trends alongside live market context.
          </p>
        </div>
        <div style={{ display: "flex", gap: theme.spacing.sm, flexWrap: "wrap" }}>
          {PERIODS.map((option) => (
            <Button
              key={option.value}
              variant={period === option.value ? "primary" : "secondary"}
              size="sm"
              onClick={() => setPeriod(option.value)}
            >
              {option.label}
            </Button>
          ))}
          <Button
            variant="secondary"
            size="sm"
            onClick={() => refresh()}
            aria-label="Refresh equity history"
            style={{ display: "flex", alignItems: "center", gap: theme.spacing.xs }}
          >
            <Activity size={14} /> Sync
          </Button>
        </div>
      </header>

      <section style={{ minHeight: 240 }}>
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={history}>
            <defs>
              <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={theme.colors.primary} stopOpacity={0.8} />
                <stop offset="95%" stopColor={theme.colors.primary} stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <XAxis dataKey="date" stroke={theme.colors.textMuted} hide={history.length > 30} />
            <YAxis
              stroke={theme.colors.textMuted}
              tickFormatter={(value) => formatCurrency(value).replace("$", "")}
            />
            <Tooltip
              cursor={{ stroke: theme.colors.primary, strokeWidth: 1 }}
              contentStyle={{
                background: theme.background.surface,
                borderRadius: theme.borderRadius.sm,
                borderColor: theme.colors.border,
                color: theme.colors.text,
              }}
              formatter={(value: number) => formatCurrency(value)}
            />
            <Area
              type="monotone"
              dataKey="equity"
              stroke={theme.colors.primary}
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#equityGradient)"
              isAnimationActive={!isLoading}
              name="Equity"
            />
          </AreaChart>
        </ResponsiveContainer>
      </section>

      {error && (
        <span style={{ color: theme.colors.danger, fontSize: "12px" }}>
          Unable to load historical equity data right now.
        </span>
      )}

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: theme.spacing.md,
        }}
      >
        <Card
          style={{
            background: theme.background.surface,
            border: `1px solid ${theme.colors.border}`,
            boxShadow: theme.glow.blue,
            display: "flex",
            flexDirection: "column",
            gap: theme.spacing.md,
          }}
        >
          <h4 style={{ margin: 0, display: "flex", alignItems: "center", gap: theme.spacing.xs }}>
            <LineChartIcon size={16} /> Market Context
          </h4>
          <TradingViewChart symbol="SPY" autoHeight height={320} />
        </Card>

        <div
          style={{
            display: "grid",
            alignContent: "start",
            gap: theme.spacing.md,
            background: theme.background.surface,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.lg,
            padding: theme.spacing.lg,
          }}
        >
          <h4 style={{ margin: 0 }}>Latest Snapshot</h4>
          <div style={{ display: "grid", gap: theme.spacing.sm }}>
            <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "12px" }}>
              Last updated: {data ? new Date(data.end_date).toLocaleString() : "—"}
            </p>
            <p style={{ margin: 0 }}>
              Equity: <strong>{history.length ? formatCurrency(history.at(-1)!.equity) : "—"}</strong>
            </p>
            <p style={{ margin: 0 }}>
              Cash: <strong>{history.length ? formatCurrency(history.at(-1)!.cash) : "—"}</strong>
            </p>
            {data?.is_simulated && (
              <p style={{ margin: 0, color: theme.colors.warning }}>
                Historical data is still warming up. Keep the dashboard open to accumulate history.
              </p>
            )}
          </div>
        </div>
      </section>
    </Card>
  );
}

export default PortfolioPerformancePanel;
