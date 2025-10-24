"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import {
  createChart,
  ColorType,
  type CandlestickData,
  type IChartApi,
  type ISeriesApi,
  type Time,
} from "lightweight-charts";
import { Card, Select } from "@/components/ui";
import { theme } from "@/styles/theme";
import type { CandleDatum, TimeframeOption } from "./types";

interface CandlestickViewsProps {
  candlesByTimeframe: Record<string, CandleDatum[]>;
  timeframes?: TimeframeOption[];
  defaultTimeframe?: string;
  title?: string;
  description?: string;
  height?: number;
}

const DEFAULT_TIMEFRAMES: TimeframeOption[] = [
  { id: "1D", label: "1 Day", interval: "1D" },
  { id: "5D", label: "5 Days", interval: "5D" },
  { id: "1M", label: "1 Month", interval: "1M" },
  { id: "3M", label: "3 Months", interval: "3M" },
];

export function CandlestickViews({
  candlesByTimeframe,
  timeframes = DEFAULT_TIMEFRAMES,
  defaultTimeframe,
  title = "Price Action",
  description = "Multi-timeframe candlestick analysis powered by Lightweight Charts.",
  height = 360,
}: CandlestickViewsProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>(
    defaultTimeframe ?? timeframes[0]?.interval ?? "1D"
  );

  const titleId = useId();
  const descriptionId = useId();

  const timeframeOptions = useMemo(
    () =>
      timeframes.map((tf) => ({
        value: tf.interval,
        label: tf.label,
      })),
    [timeframes]
  );

  useEffect(() => {
    if (!chartContainerRef.current) {
      return;
    }

    chartRef.current = createChart(chartContainerRef.current, {
      height,
      layout: {
        background: {
          type: ColorType.Solid,
          color: "transparent",
        },
        textColor: theme.colors.textMuted,
      },
      grid: {
        vertLines: {
          color: "rgba(148, 163, 184, 0.2)",
        },
        horzLines: {
          color: "rgba(148, 163, 184, 0.2)",
        },
      },
      crosshair: {
        mode: 1,
      },
      timeScale: {
        borderColor: theme.colors.border,
      },
      rightPriceScale: {
        borderColor: theme.colors.border,
      },
    });

    seriesRef.current = chartRef.current.addCandlestickSeries({
      upColor: theme.colors.success,
      downColor: theme.colors.danger,
      wickUpColor: theme.colors.success,
      wickDownColor: theme.colors.danger,
      borderVisible: false,
    });

    const observer = new ResizeObserver((entries) => {
      if (!chartRef.current || !entries.length) return;
      const { width, height: nextHeight } = entries[0].contentRect;
      chartRef.current.resize(width, nextHeight);
    });
    observer.observe(chartContainerRef.current);

    return () => {
      observer.disconnect();
      chartRef.current?.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, [height]);

  useEffect(() => {
    if (!seriesRef.current) {
      return;
    }
    const candles = candlesByTimeframe[selectedTimeframe] ?? [];
    const sanitized = candles.map((candle) => ({
      time: candle.time,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
    })) as CandlestickData<Time>[];

    seriesRef.current.setData(sanitized);
    chartRef.current?.timeScale().fitContent();
  }, [candlesByTimeframe, selectedTimeframe]);

  useEffect(() => {
    if (defaultTimeframe) {
      setSelectedTimeframe(defaultTimeframe);
    }
  }, [defaultTimeframe]);

  useEffect(() => {
    if (!timeframes.some((tf) => tf.interval === selectedTimeframe)) {
      const fallback = defaultTimeframe ?? timeframes[0]?.interval;
      if (fallback) {
        setSelectedTimeframe(fallback);
      }
    }
  }, [timeframes, selectedTimeframe, defaultTimeframe]);

  return (
    <Card
      glow="cyan"
      style={{ display: "flex", flexDirection: "column", gap: theme.spacing.md }}
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
    >
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-between",
          gap: theme.spacing.md,
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.xs }}>
          <h2 id={titleId} style={{ margin: 0, color: theme.colors.text, fontSize: "18px" }}>
            {title}
          </h2>
          <p
            id={descriptionId}
            style={{ margin: 0, color: theme.colors.textMuted, fontSize: "13px" }}
          >
            {description}
          </p>
        </div>
        <div style={{ minWidth: "180px" }}>
          <Select
            aria-label="Select candlestick timeframe"
            value={selectedTimeframe}
            onChange={(event) => setSelectedTimeframe(event.target.value)}
            options={timeframeOptions}
          />
        </div>
      </div>

      <div
        ref={chartContainerRef}
        style={{
          width: "100%",
          minHeight: height,
          background: theme.background.input,
          borderRadius: theme.borderRadius.md,
          border: `1px solid ${theme.colors.border}`,
        }}
        role="img"
        aria-labelledby={titleId}
      />
    </Card>
  );
}
