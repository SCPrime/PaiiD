"use client";

import { useId, useMemo } from "react";
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { TooltipProps } from "recharts";
import { Card } from "@/components/ui";
import { theme } from "@/styles/theme";
import type { PositionSlice } from "./types";

interface PositionAllocationChartProps {
  positions: PositionSlice[];
  title?: string;
  description?: string;
}

const COLORS = [
  theme.colors.primary,
  theme.workflow.activePositions,
  theme.workflow.strategyBuilder,
  theme.workflow.backtesting,
  theme.workflow.execute,
  theme.workflow.newsReview,
  theme.workflow.research,
];

export function PositionAllocationChart({
  positions,
  title = "Position Allocation",
  description = "Portfolio weights across active positions.",
}: PositionAllocationChartProps) {
  const titleId = useId();
  const descriptionId = useId();

  const normalizedPositions = useMemo(() => {
    const total = positions.reduce((acc, item) => acc + Math.max(item.allocation, 0), 0);
    if (!total) {
      return positions.map((item) => ({
        ...item,
        percentage: 0,
      }));
    }

    return positions.map((item) => ({
      ...item,
      percentage: (Math.max(item.allocation, 0) / total) * 100,
    }));
  }, [positions]);

  const renderTooltip = ({ active, payload }: TooltipProps<number, string>) => {
    if (!active || !payload?.length) return null;
    const data = payload[0];
    const slice = data.payload as PositionSlice & { percentage: number };

    return (
      <div
        role="presentation"
        style={{
          background: theme.background.card,
          border: `1px solid ${theme.colors.border}`,
          borderRadius: theme.borderRadius.sm,
          padding: theme.spacing.sm,
          color: theme.colors.text,
          fontSize: "13px",
        }}
      >
        <div style={{ fontWeight: 600 }}>{slice.symbol}</div>
        <div style={{ color: theme.colors.textMuted }}>
          {slice.percentage.toFixed(2)}% allocation
        </div>
        {typeof slice.marketValue === "number" && (
          <div style={{ color: theme.colors.textMuted }}>
            Value: ${slice.marketValue.toLocaleString("en-US", { minimumFractionDigits: 2 })}
          </div>
        )}
        {typeof slice.dayPnl === "number" && (
          <div
            style={{
              marginTop: 4,
              color: slice.dayPnl >= 0 ? theme.colors.success : theme.colors.danger,
            }}
          >
            Day P&L: {slice.dayPnl >= 0 ? "+" : "-"}${Math.abs(slice.dayPnl).toLocaleString("en-US")}
          </div>
        )}
      </div>
    );
  };

  return (
    <Card
      glow="teal"
      style={{
        minHeight: 360,
      }}
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: theme.spacing.sm,
          marginBottom: theme.spacing.md,
        }}
      >
        <h2
          id={titleId}
          style={{
            margin: 0,
            color: theme.colors.text,
            fontSize: "18px",
          }}
        >
          {title}
        </h2>
        <p
          id={descriptionId}
          style={{
            margin: 0,
            color: theme.colors.textMuted,
            fontSize: "13px",
          }}
        >
          {description}
        </p>
      </div>

      {positions.length === 0 ? (
        <p style={{ color: theme.colors.textMuted, fontSize: "13px" }}>
          No open positions to visualise.
        </p>
      ) : (
        <div
          role="img"
          aria-labelledby={titleId}
          style={{ width: "100%", height: 240 }}
        >
          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={normalizedPositions}
                dataKey="percentage"
                nameKey="symbol"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={4}
              >
                {normalizedPositions.map((entry, index) => (
                  <Cell key={entry.symbol} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={renderTooltip} />
              <Legend
                verticalAlign="bottom"
                iconType="circle"
                wrapperStyle={{
                  color: theme.colors.textMuted,
                  fontSize: "12px",
                  paddingTop: theme.spacing.sm,
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
