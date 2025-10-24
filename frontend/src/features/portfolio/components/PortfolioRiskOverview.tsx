"use client";

import React, { useMemo } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Button, Card } from "@/components/ui";
import { theme } from "@/styles/theme";

import { usePortfolioGreeks } from "../hooks/usePortfolioGreeks";
import { PortfolioGreekAnalytics } from "../types";

const GREEK_KEYS = ["delta", "gamma", "theta", "vega", "rho"] as const;

function formatNumber(value: number, fractionDigits = 2) {
  return value.toLocaleString("en-US", {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  });
}

function buildChartData(data?: PortfolioGreekAnalytics) {
  if (!data) {
    return [];
  }

  return GREEK_KEYS.map((key) => ({
    name: key.toUpperCase(),
    exposure: data.totals[key],
  }));
}

export function PortfolioRiskOverview() {
  const { data, isLoading, error, refresh } = usePortfolioGreeks();

  const chartData = useMemo(() => buildChartData(data), [data]);

  const totals = data?.totals;

  return (
    <Card style={{ display: "flex", flexDirection: "column", gap: theme.spacing.lg }}>
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: theme.spacing.md,
          flexWrap: "wrap",
        }}
      >
        <div>
          <h3 style={{ margin: 0, color: theme.colors.text }}>Portfolio Risk Overview</h3>
          <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "14px" }}>
            Live option Greeks aggregated across your holdings. Refreshes every 30 seconds.
          </p>
        </div>
        <Button
          onClick={() => refresh()}
          style={{ display: "flex", alignItems: "center", gap: theme.spacing.xs }}
          aria-label="Refresh portfolio risk metrics"
        >
          <RefreshCw size={16} /> Refresh
        </Button>
      </header>

      {error && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: theme.spacing.sm,
            padding: theme.spacing.md,
            border: `1px solid ${theme.colors.danger}60`,
            borderRadius: theme.borderRadius.md,
            background: `${theme.colors.danger}10`,
            color: theme.colors.danger,
          }}
          role="alert"
        >
          <AlertTriangle size={18} />
          <span>Unable to load portfolio Greeks. Please retry.</span>
        </div>
      )}

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
          gap: theme.spacing.md,
        }}
      >
        {GREEK_KEYS.map((key) => (
          <div
            key={key}
            style={{
              background: theme.background.surface,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.md,
              padding: theme.spacing.md,
            }}
          >
            <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "12px" }}>
              Net {key.toUpperCase()}
            </p>
            <p
              data-testid={`greek-total-${key}`}
              style={{
                margin: 0,
                fontWeight: 600,
                fontSize: "20px",
                color: theme.colors.text,
              }}
            >
              {totals ? formatNumber(totals[key]) : "—"}
            </p>
          </div>
        ))}
      </section>

      <div style={{ height: 260 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke={theme.colors.border} />
            <XAxis dataKey="name" stroke={theme.colors.textMuted} />
            <YAxis stroke={theme.colors.textMuted} />
            <Tooltip
              cursor={{ fill: `${theme.colors.primary}10` }}
              contentStyle={{
                background: theme.background.surface,
                borderRadius: theme.borderRadius.sm,
                borderColor: theme.colors.border,
                color: theme.colors.text,
              }}
              formatter={(value: number) => formatNumber(value)}
            />
            <Bar dataKey="exposure" fill={theme.colors.primary} radius={[6, 6, 0, 0]} isAnimationActive={!isLoading} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <footer style={{ color: theme.colors.textMuted, fontSize: "12px" }}>
        Data updates automatically while you keep the dashboard open.
      </footer>
    </Card>
  );
}

export default PortfolioRiskOverview;
