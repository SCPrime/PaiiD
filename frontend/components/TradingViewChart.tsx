import { useCallback, useEffect, useId, useRef, useState } from "react";
import { Activity, BarChart3, RefreshCw, TrendingUp } from "lucide-react";
import { theme } from "../styles/theme";

interface TradingViewChartProps {
  symbol?: string;
  autoHeight?: boolean;
  height?: number;
  /**
   * Control the current interval externally. When provided, the component will
   * use this value instead of its internal state.
   */
  interval?: string;
  /**
   * Default interval used when the chart first mounts. Ignored when the
   * `interval` prop is supplied.
   */
  defaultInterval?: string;
  /**
   * Callback fired whenever the interval changes due to user interaction.
   */
  onIntervalChange?: (value: string) => void;
  /**
   * Hide the built-in controls so the chart can be embedded inside custom
   * dashboards without duplicated UI.
   */
  showControls?: boolean;
  /**
   * Toggle the indicator buttons inside the controls header.
   */
  showIndicatorToggles?: boolean;
}

interface TradingViewGlobal {
  widget: (options: Record<string, unknown>) => unknown;
}

declare global {
  interface Window {
    TradingView?: TradingViewGlobal;
  }
}

export default function TradingViewChart({
  symbol = "$DJI.IX",
  autoHeight = false,
  height = 500,
  interval,
  defaultInterval = "D",
  onIntervalChange,
  showControls = true,
  showIndicatorToggles = true,
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentSymbol, setCurrentSymbol] = useState(symbol);
  const [internalInterval, setInternalInterval] = useState<string>(interval ?? defaultInterval);
  const [showIndicators, setShowIndicators] = useState({
    sma: true,
    rsi: false,
    macd: false,
  });
  const widgetRef = useRef<unknown>(null);
  const containerId = useId();

  useEffect(() => {
    setCurrentSymbol(symbol);
  }, [symbol]);

  useEffect(() => {
    if (interval) {
      setInternalInterval(interval);
    }
  }, [interval]);

  const timeframes = [
    { label: "1D", value: "D", name: "1 Day" },
    { label: "1W", value: "W", name: "1 Week" },
    { label: "1M", value: "M", name: "1 Month" },
    { label: "3M", value: "3M", name: "3 Months" },
    { label: "1Y", value: "12M", name: "1 Year" },
  ];

  const indicators = [
    { key: "sma", label: "SMA", icon: TrendingUp, name: "Simple Moving Average" },
    { key: "rsi", label: "RSI", icon: Activity, name: "Relative Strength Index" },
    { key: "macd", label: "MACD", icon: BarChart3, name: "Moving Average Convergence Divergence" },
  ];

  // Load TradingView script
  const initWidget = useCallback(() => {
    const target = containerRef.current;
    const tradingView = window.TradingView;
    if (!target || !tradingView || typeof tradingView.widget !== "function") {
      return;
    }

    // Clear existing widget
    target.innerHTML = "";

    // Build studies array based on selected indicators
    const studies: string[] = [];
    if (showIndicators.sma) {
      studies.push("MASimple@tv-basicstudies");
    }
    if (showIndicators.rsi) {
      studies.push("RSI@tv-basicstudies");
    }
    if (showIndicators.macd) {
      studies.push("MACD@tv-basicstudies");
    }

    // Create new widget
    widgetRef.current = tradingView.widget({
      autosize: true,
      symbol: currentSymbol,
      interval: internalInterval,
      timezone: "America/New_York",
      theme: "dark",
      style: "1",
      locale: "en",
      toolbar_bg: "#0f172a",
      enable_publishing: false,
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: false,
      container_id: containerId,
      studies: studies,
      backgroundColor: "#0f172a",
      gridColor: "#1e293b",
      height: autoHeight ? "100%" : height,
      width: "100%",
    });
  }, [
    autoHeight,
    containerId,
    currentSymbol,
    height,
    internalInterval,
    showIndicators.macd,
    showIndicators.rsi,
    showIndicators.sma,
  ]);

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;
    script.onload = () => {
      initWidget();
    };
    document.body.appendChild(script);

    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, [initWidget]);

  useEffect(() => {
    initWidget();
  }, [initWidget]);

  const handleSymbolChange = (newSymbol: string) => {
    setCurrentSymbol(newSymbol.toUpperCase());
  };

  const toggleIndicator = (key: "sma" | "rsi" | "macd") => {
    setShowIndicators((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const updateInterval = (value: string) => {
    if (!interval) {
      setInternalInterval(value);
    }
    onIntervalChange?.(value);
  };

  return (
    <div
      style={{
        background: theme.background.card,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.lg,
        padding: theme.spacing.lg,
      }}
    >
      {showControls && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: theme.spacing.lg,
            flexWrap: "wrap",
            gap: theme.spacing.md,
          }}
        >
          {/* Symbol Input */}
          <div style={{ display: "flex", alignItems: "center", gap: theme.spacing.sm }}>
            <label
              htmlFor={`${containerId}-symbol`}
              style={{
                position: "absolute",
                width: 1,
                height: 1,
                padding: 0,
                margin: -1,
                overflow: "hidden",
                clip: "rect(0, 0, 0, 0)",
                whiteSpace: "nowrap",
                border: 0,
              }}
            >
              Symbol
            </label>
            <input
              id={`${containerId}-symbol`}
              type="text"
              value={currentSymbol}
              onChange={(e) => handleSymbolChange(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSymbolChange(currentSymbol)}
              placeholder="Symbol (e.g., $DJI.IX, AAPL)"
              style={{
                padding: "8px 12px",
                background: theme.background.input,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.sm,
                color: theme.colors.text,
                fontSize: "14px",
                fontWeight: "600",
                width: "120px",
                textTransform: "uppercase",
              }}
            />
            <button
              onClick={() => setCurrentSymbol(symbol)}
              style={{
                padding: "8px",
                background: theme.background.input,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.sm,
                color: theme.colors.textMuted,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transition: theme.transitions.normal,
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = theme.colors.primary;
                e.currentTarget.style.color = theme.colors.primary;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = theme.colors.border;
                e.currentTarget.style.color = theme.colors.textMuted;
              }}
              title="Reset to default symbol"
            >
              <RefreshCw size={16} />
            </button>
          </div>

          {/* Timeframe Selector */}
          <div
            style={{
              display: "flex",
              gap: theme.spacing.xs,
              background: theme.background.input,
              padding: "4px",
              borderRadius: theme.borderRadius.sm,
              border: `1px solid ${theme.colors.border}`,
            }}
          >
            {timeframes.map((tf) => (
              <button
                key={tf.value}
                onClick={() => updateInterval(tf.value)}
                style={{
                  padding: "6px 12px",
                  background:
                    internalInterval === tf.value ? theme.colors.primary : "transparent",
                  border: "none",
                  borderRadius: theme.borderRadius.sm,
                  color: internalInterval === tf.value ? "#ffffff" : theme.colors.textMuted,
                  fontSize: "13px",
                  fontWeight: "600",
                  cursor: "pointer",
                  transition: theme.transitions.fast,
                }}
                onMouseEnter={(e) => {
                  if (internalInterval !== tf.value) {
                    e.currentTarget.style.background = "rgba(16, 185, 129, 0.1)";
                    e.currentTarget.style.color = theme.colors.primary;
                  }
                }}
                onMouseLeave={(e) => {
                  if (internalInterval !== tf.value) {
                    e.currentTarget.style.background = "transparent";
                    e.currentTarget.style.color = theme.colors.textMuted;
                  }
                }}
                title={tf.name}
              >
                {tf.label}
              </button>
            ))}
          </div>

          {/* Indicator Toggles */}
          {showIndicatorToggles && (
            <div
              style={{
                display: "flex",
                gap: theme.spacing.xs,
              }}
            >
              {indicators.map((ind) => {
                const Icon = ind.icon;
                const isActive = showIndicators[ind.key as "sma" | "rsi" | "macd"];
                return (
                  <button
                    key={ind.key}
                    onClick={() => toggleIndicator(ind.key as "sma" | "rsi" | "macd")}
                    style={{
                      padding: "6px 10px",
                      background: isActive
                        ? "rgba(16, 185, 129, 0.2)"
                        : theme.background.input,
                      border: `1px solid ${
                        isActive ? theme.colors.primary : theme.colors.border
                      }`,
                      borderRadius: theme.borderRadius.sm,
                      color: isActive ? theme.colors.primary : theme.colors.textMuted,
                      fontSize: "12px",
                      fontWeight: "600",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px",
                      transition: theme.transitions.normal,
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.borderColor = theme.colors.primary;
                        e.currentTarget.style.color = theme.colors.primary;
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.borderColor = theme.colors.border;
                        e.currentTarget.style.color = theme.colors.textMuted;
                      }
                    }}
                    title={ind.name}
                  >
                    <Icon size={14} />
                    {ind.label}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* TradingView Widget Container */}
      <div
        id={containerId}
        ref={containerRef}
        style={{
          height: autoHeight ? "100%" : `${height}px`,
          width: "100%",
          background: theme.background.input,
          borderRadius: theme.borderRadius.md,
          overflow: "hidden",
        }}
      />

      {/* Attribution */}
      <div
        style={{
          marginTop: theme.spacing.sm,
          padding: theme.spacing.sm,
          textAlign: "center",
          fontSize: "11px",
          color: theme.colors.textMuted,
        }}
      >
        Powered by{" "}
        <a
          href="https://www.tradingview.com/"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            color: theme.colors.primary,
            textDecoration: "none",
          }}
        >
          TradingView
        </a>
      </div>
    </div>
  );
}
