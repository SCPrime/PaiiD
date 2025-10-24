"use client";

import dynamic from "next/dynamic";
import { useId, useMemo, useState } from "react";
import { Card, Select } from "@/components/ui";
import { theme } from "@/styles/theme";
import type { TimeframeOption } from "./types";

const TradingViewChart = dynamic(() => import("@/components/TradingViewChart"), {
  ssr: false,
});

const DEFAULT_SYMBOLS = [
  { label: "S&P 500", value: "SPX" },
  { label: "NASDAQ 100", value: "NDX" },
  { label: "Dow Jones", value: "$DJI.IX" },
  { label: "Gold", value: "GC1!" },
  { label: "BTC/USD", value: "BTCUSD" },
];

const DEFAULT_TIMEFRAMES: TimeframeOption[] = [
  { id: "1d", label: "1 Day", interval: "D" },
  { id: "1w", label: "1 Week", interval: "W" },
  { id: "1m", label: "1 Month", interval: "M" },
  { id: "3m", label: "3 Months", interval: "3M" },
  { id: "1y", label: "1 Year", interval: "12M" },
];

interface MarketChartProps {
  symbols?: Array<{ label: string; value: string }>;
  timeframes?: TimeframeOption[];
  height?: number;
}

export function MarketChart({
  symbols = DEFAULT_SYMBOLS,
  timeframes = DEFAULT_TIMEFRAMES,
  height = 420,
}: MarketChartProps) {
  const [selectedSymbol, setSelectedSymbol] = useState(symbols[0]?.value ?? "SPX");
  const [selectedTimeframe, setSelectedTimeframe] = useState(timeframes[0]?.interval ?? "D");

  const titleId = useId();
  const descriptionId = useId();

  const timeframeOptions = useMemo(
    () =>
      timeframes.map((timeframe) => ({
        value: timeframe.interval,
        label: timeframe.label,
      })),
    [timeframes],
  );

  return (
    <Card
      glow="teal"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: theme.spacing.md,
        minHeight: height + 120,
      }}
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
    >
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          gap: theme.spacing.md,
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.xs }}>
          <h2
            id={titleId}
            style={{
              margin: 0,
              fontSize: "18px",
              color: theme.colors.text,
            }}
          >
            Market Overview
          </h2>
          <p
            id={descriptionId}
            style={{
              margin: 0,
              fontSize: "13px",
              color: theme.colors.textMuted,
              maxWidth: "520px",
            }}
          >
            Interactive TradingView charts let you monitor key indices and instruments with your
            preferred timeframe.
          </p>
        </div>
        <div
          style={{
            display: "flex",
            gap: theme.spacing.md,
            minWidth: "260px",
          }}
        >
          <Select
            aria-label="Select market symbol"
            value={selectedSymbol}
            onChange={(event) => setSelectedSymbol(event.target.value)}
            options={symbols}
          />
          <Select
            aria-label="Select chart timeframe"
            value={selectedTimeframe}
            onChange={(event) => setSelectedTimeframe(event.target.value)}
            options={timeframeOptions}
          />
        </div>
      </div>

      <div
        style={{
          flex: 1,
          minHeight: height,
        }}
      >
        <TradingViewChart
          symbol={selectedSymbol}
          height={height}
          interval={selectedTimeframe}
          showControls={false}
          showIndicatorToggles={false}
        />
      </div>
    </Card>
  );
}
