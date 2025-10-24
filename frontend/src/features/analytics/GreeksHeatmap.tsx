"use client";

import { useId } from "react";
import { Card } from "@/components/ui";
import { theme } from "@/styles/theme";
import type { OptionGreekSnapshot } from "./types";

interface GreeksHeatmapProps {
  data: OptionGreekSnapshot[];
  title?: string;
  description?: string;
}

const greekKeys: Array<keyof OptionGreekSnapshot> = [
  "delta",
  "gamma",
  "theta",
  "vega",
  "rho",
];

const greekLabels: Record<keyof OptionGreekSnapshot, string> = {
  symbol: "Symbol",
  expiry: "Expiry",
  delta: "Δ",
  gamma: "Γ",
  theta: "Θ",
  vega: "V",
  rho: "ρ",
};

function getHeatmapColor(value: number | undefined) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return theme.background.input;
  }
  const clamped = Math.max(-1, Math.min(1, value));
  if (clamped >= 0) {
    const intensity = Math.round(clamped * 80) + 20;
    return `rgba(22, 163, 148, ${intensity / 100})`;
  }
  const intensity = Math.round(Math.abs(clamped) * 60) + 20;
  return `rgba(255, 68, 68, ${intensity / 100})`;
}

export function GreeksHeatmap({
  data,
  title = "Options Greeks Heatmap",
  description = "Quickly compare portfolio sensitivity across strikes and expirations.",
}: GreeksHeatmapProps) {
  const titleId = useId();
  const descriptionId = useId();
  const hasRho = data.some((row) => typeof row.rho === "number");

  const columns = hasRho ? greekKeys : greekKeys.filter((key) => key !== "rho");

  return (
    <Card
      glow="purple"
      style={{
        overflowX: "auto",
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
          style={{ margin: 0, color: theme.colors.text, fontSize: "18px" }}
        >
          {title}
        </h2>
        <p
          id={descriptionId}
          style={{ margin: 0, color: theme.colors.textMuted, fontSize: "13px" }}
        >
          {description}
        </p>
      </div>

      {data.length === 0 ? (
        <p style={{ color: theme.colors.textMuted, fontSize: "13px" }}>
          Greeks data unavailable.
        </p>
      ) : (
        <table
          role="grid"
          aria-describedby={descriptionId}
          style={{
            width: "100%",
            borderCollapse: "separate",
            borderSpacing: 0,
            borderRadius: theme.borderRadius.md,
            overflow: "hidden",
          }}
        >
          <thead>
            <tr>
              <th
                scope="col"
                style={{
                  padding: "12px 16px",
                  textAlign: "left",
                  background: theme.background.input,
                  color: theme.colors.text,
                  borderBottom: `1px solid ${theme.colors.border}`,
                  position: "sticky",
                  left: 0,
                  zIndex: 1,
                }}
              >
                Symbol
              </th>
              {columns.map((key) => (
                <th
                  key={key}
                  scope="col"
                  style={{
                    padding: "12px 16px",
                    textAlign: "center",
                    background: theme.background.input,
                    color: theme.colors.text,
                    borderBottom: `1px solid ${theme.colors.border}`,
                  }}
                >
                  {greekLabels[key]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={`${row.symbol}-${row.expiry ?? "na"}`}>
                <th
                  scope="row"
                  style={{
                    padding: "12px 16px",
                    textAlign: "left",
                    background: theme.background.input,
                    color: theme.colors.text,
                    borderBottom: `1px solid ${theme.colors.border}`,
                    position: "sticky",
                    left: 0,
                  }}
                >
                  <div style={{ display: "flex", flexDirection: "column" }}>
                    <span style={{ fontWeight: 600 }}>{row.symbol}</span>
                    {row.expiry && (
                      <span style={{ color: theme.colors.textMuted, fontSize: "12px" }}>
                        {row.expiry}
                      </span>
                    )}
                  </div>
                </th>
                {columns.map((key) => {
                  if (key === "symbol" || key === "expiry") return null;
                  const value = row[key as keyof OptionGreekSnapshot];
                  const background = getHeatmapColor(typeof value === "number" ? value : undefined);
                  return (
                    <td
                      key={key}
                      style={{
                        padding: "12px 16px",
                        textAlign: "center",
                        borderBottom: `1px solid ${theme.colors.border}`,
                        background,
                        color: theme.colors.text,
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {typeof value === "number" && !Number.isNaN(value)
                        ? value.toFixed(3)
                        : "—"}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Card>
  );
}
