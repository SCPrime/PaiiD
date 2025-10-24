import React, { memo } from "react";

import { Button, Card } from "@/components/ui";
import { theme } from "@/styles/theme";

import { Recommendation } from "./types";

interface RecommendationTableProps {
  recommendations: Recommendation[];
  onResearch?(symbol: string): void;
  onExecute?(recommendation: Recommendation): void;
}

const badgeStyle = (color: string) => ({
  display: "inline-flex",
  alignItems: "center",
  padding: "4px 10px",
  borderRadius: "9999px",
  fontSize: "12px",
  fontWeight: 600,
  color,
  border: `1px solid ${color}`,
  background: `${color}15`,
});

export const RecommendationTable = memo(
  ({ recommendations, onResearch, onExecute }: RecommendationTableProps) => {
    if (!recommendations.length) {
      return null;
    }

    return (
      <Card
        glow="purple"
        style={{
          marginBottom: theme.spacing.lg,
          overflowX: "auto",
        }}
      >
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: "13px",
          }}
        >
          <thead>
            <tr style={{ textAlign: "left", color: theme.colors.textMuted }}>
              <th style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>Symbol</th>
              <th style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>Action</th>
              <th style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>Confidence</th>
              <th style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>Risk</th>
              <th style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>Volatility</th>
              <th style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>Momentum</th>
              <th style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>Score</th>
              <th style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {recommendations.map((rec) => {
              const riskColor =
                rec.risk === "Low"
                  ? theme.colors.primary
                  : rec.risk === "High"
                    ? theme.colors.danger
                    : theme.colors.warning;
              const volColor = (() => {
                switch (rec.volatility?.volatility_class) {
                  case "Low":
                    return theme.colors.primary;
                  case "High":
                    return theme.colors.danger;
                  case "Medium":
                  default:
                    return theme.colors.warning;
                }
              })();
              const momentum = rec.momentum?.trend_alignment ?? "Neutral";
              const momentumColor = momentum.toLowerCase().includes("bull")
                ? theme.colors.primary
                : momentum.toLowerCase().includes("bear")
                  ? theme.colors.danger
                  : theme.colors.secondary;

              return (
                <tr
                  key={`${rec.symbol}-${rec.action}`}
                  style={{ borderTop: `1px solid ${theme.colors.border}` }}
                >
                  <td
                    style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}`, fontWeight: 600 }}
                  >
                    {rec.symbol}
                  </td>
                  <td style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>
                    {rec.action}
                  </td>
                  <td style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>
                    {rec.confidence.toFixed(1)}%
                  </td>
                  <td style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>
                    <span style={badgeStyle(riskColor)}>{rec.risk ?? "--"}</span>
                  </td>
                  <td style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>
                    <span style={badgeStyle(volColor)}>
                      {rec.volatility?.volatility_class ?? "--"}
                    </span>
                  </td>
                  <td style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>
                    <span style={badgeStyle(momentumColor)}>{momentum}</span>
                  </td>
                  <td style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>
                    {rec.score.toFixed(1)}
                  </td>
                  <td style={{ padding: `${theme.spacing.sm} ${theme.spacing.md}` }}>
                    <div style={{ display: "flex", gap: theme.spacing.xs }}>
                      {onResearch && (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => onResearch(rec.symbol)}
                        >
                          Research
                        </Button>
                      )}
                      {onExecute && (
                        <Button size="sm" onClick={() => onExecute(rec)}>
                          Execute
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    );
  }
);

RecommendationTable.displayName = "RecommendationTable";
