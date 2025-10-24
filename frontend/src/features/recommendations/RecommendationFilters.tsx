import React, { memo } from "react";

import { Button, Card, Input, Select } from "@/components/ui";
import { theme } from "@/styles/theme";

import {
  RecommendationAction,
  RecommendationFilterState,
  RecommendationRiskLevel,
  RecommendationSortKey,
  RecommendationVolatilityClass,
  SortDirection,
} from "./types";

interface RecommendationFiltersProps {
  filters: RecommendationFilterState;
  onSearchChange(value: string): void;
  onConfidenceChange(value: number): void;
  onToggleAction(action: RecommendationAction): void;
  onToggleRisk(level: RecommendationRiskLevel): void;
  onVolatilityChange(value: RecommendationVolatilityClass | "All"): void;
  onMomentumChange(value: string | "All"): void;
  onSortChange(sortBy: RecommendationSortKey, direction: SortDirection): void;
  onReset(): void;
  onExport(): void;
}

const actionLabels: Record<RecommendationAction, string> = {
  BUY: "Buy",
  SELL: "Sell",
  HOLD: "Hold",
};

const riskLevels: RecommendationRiskLevel[] = ["Low", "Medium", "High"];

const sortOptions = [
  { value: "confidence", label: "Confidence" },
  { value: "score", label: "AI Score" },
  { value: "volatility", label: "Volatility" },
  { value: "momentum", label: "Momentum" },
  { value: "risk", label: "Risk" },
  { value: "symbol", label: "Symbol" },
];

const volatilityOptions: Array<{ value: RecommendationVolatilityClass | "All"; label: string }> = [
  { value: "All", label: "All volatility" },
  { value: "Low", label: "Low volatility" },
  { value: "Medium", label: "Medium volatility" },
  { value: "High", label: "High volatility" },
];

const momentumOptions = [
  { value: "All", label: "All trends" },
  { value: "bullish", label: "Bullish" },
  { value: "bearish", label: "Bearish" },
  { value: "mixed", label: "Mixed" },
];

export const RecommendationFilters = memo(
  ({
    filters,
    onSearchChange,
    onConfidenceChange,
    onToggleAction,
    onToggleRisk,
    onVolatilityChange,
    onMomentumChange,
    onSortChange,
    onReset,
    onExport,
  }: RecommendationFiltersProps) => {
    return (
      <Card
        glow="cyan"
        style={{
          marginBottom: theme.spacing.lg,
          padding: theme.spacing.lg,
        }}
      >
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: theme.spacing.lg,
            alignItems: "center",
            marginBottom: theme.spacing.lg,
          }}
        >
          <div style={{ flex: 1, minWidth: 220 }}>
            <Input
              placeholder="Search symbol, sector, or reason"
              value={filters.search}
              onChange={(event) => onSearchChange(event.target.value)}
            />
          </div>

          <div style={{ minWidth: 200 }}>
            <label
              htmlFor="confidence-slider"
              style={{
                display: "block",
                fontSize: "12px",
                fontWeight: 600,
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.xs,
              }}
            >
              Minimum confidence ({filters.minConfidence}%)
            </label>
            <input
              type="range"
              min={0}
              max={100}
              value={filters.minConfidence}
              id="confidence-slider"
              onChange={(event) => onConfidenceChange(Number(event.target.value))}
              style={{ width: "100%" }}
            />
          </div>

          <Select
            options={sortOptions}
            value={filters.sortBy}
            onChange={(event) =>
              onSortChange(event.target.value as RecommendationSortKey, filters.sortDirection)
            }
          />

          <Select
            options={[
              { value: "desc", label: "High → Low" },
              { value: "asc", label: "Low → High" },
            ]}
            value={filters.sortDirection}
            onChange={(event) => onSortChange(filters.sortBy, event.target.value as SortDirection)}
          />
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: theme.spacing.lg,
          }}
        >
          <div>
            <div
              style={{
                fontSize: "12px",
                fontWeight: 600,
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.sm,
              }}
            >
              Actions
            </div>
            <div style={{ display: "flex", gap: theme.spacing.sm }}>
              {Object.keys(actionLabels).map((action) => {
                const typed = action as RecommendationAction;
                const isActive = filters.actions.includes(typed);
                return (
                  <Button
                    key={action}
                    variant={isActive ? "primary" : "secondary"}
                    size="sm"
                    onClick={() => onToggleAction(typed)}
                  >
                    {actionLabels[typed]}
                  </Button>
                );
              })}
            </div>
          </div>

          <div>
            <div
              style={{
                fontSize: "12px",
                fontWeight: 600,
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.sm,
              }}
            >
              Risk level
            </div>
            <div style={{ display: "flex", gap: theme.spacing.sm }}>
              {riskLevels.map((risk) => {
                const isActive = filters.riskLevels.includes(risk);
                return (
                  <Button
                    key={risk}
                    variant={isActive ? "primary" : "secondary"}
                    size="sm"
                    onClick={() => onToggleRisk(risk)}
                  >
                    {risk}
                  </Button>
                );
              })}
            </div>
          </div>

          <div>
            <div
              style={{
                fontSize: "12px",
                fontWeight: 600,
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.sm,
              }}
            >
              Volatility
            </div>
            <Select
              options={volatilityOptions.map((option) => ({
                value: option.value,
                label: option.label,
              }))}
              value={filters.volatilityClass}
              onChange={(event) =>
                onVolatilityChange(event.target.value as RecommendationVolatilityClass | "All")
              }
            />
          </div>

          <div>
            <div
              style={{
                fontSize: "12px",
                fontWeight: 600,
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.sm,
              }}
            >
              Momentum trend
            </div>
            <Select
              options={momentumOptions}
              value={filters.momentumTrend}
              onChange={(event) => onMomentumChange(event.target.value)}
            />
          </div>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: theme.spacing.sm,
            marginTop: theme.spacing.lg,
          }}
        >
          <Button variant="secondary" onClick={onReset}>
            Reset filters
          </Button>
          <Button variant="secondary" onClick={onExport}>
            Export CSV
          </Button>
        </div>
      </Card>
    );
  }
);

RecommendationFilters.displayName = "RecommendationFilters";
