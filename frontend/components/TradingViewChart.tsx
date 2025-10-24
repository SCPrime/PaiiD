import { Activity, BarChart3, RefreshCw, TrendingUp } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { theme } from "../styles/theme";

interface TradingViewChartProps {
  symbol?: string;
  autoHeight?: boolean;
  height?: number;
}

declare global {
  interface Window {
    TradingView?: {
      widget: (options: {
        container_id: string;
        symbol: string;
        interval: string;
        autosize: boolean;
        height: number;
        theme: string;
        style: string;
        locale: string;
        toolbar_bg: string;
        enable_publishing: boolean;
        hide_top_toolbar: boolean;
        hide_legend: boolean;
        save_image: boolean;
        studies: string[];
        overrides: Record<string, unknown>;
      }) => unknown;
    };
  }
}

export default function TradingViewChart({
  symbol = "$DJI.IX",
  autoHeight = false,
  height = 500,
}: TradingViewChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentSymbol, setCurrentSymbol] = useState(symbol);
  const [interval, setInterval] = useState<string>("D");
  const [showIndicators, setShowIndicators] = useState({
    sma: true,
    rsi: false,
    macd: false,
  });
  const widgetRef = useRef<{
    remove: () => void;
    onChartReady: (callback: () => void) => void;
  } | null>(null);

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
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;
    script.onload = () => {
      if (containerRef.current) {
        initWidget();
      }
    };
    document.body.appendChild(script);

    return () => {
      // Cleanup
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, [initWidget]);

  // Reinitialize widget when symbol, interval, or indicators change
  useEffect(() => {
    if (window.TradingView && containerRef.current) {
      initWidget();
    }
  }, [initWidget]);

  const initWidget = useCallback(() => {
    if (!containerRef.current || !window.TradingView) return;

    // Clear existing widget
    containerRef.current.innerHTML = "";

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
    widgetRef.current = new window.TradingView.widget({
      autosize: true,
      symbol: currentSymbol,
      interval: interval,
      timezone: "America/New_York",
      theme: "dark",
      style: "1",
      locale: "en",
      toolbar_bg: "#0f172a",
      enable_publishing: false,
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: false,
      container_id: containerRef.current.id,
      studies: studies,
      backgroundColor: "#0f172a",
      gridColor: "#1e293b",
      height: autoHeight ? "100%" : height,
      width: "100%",
    });
  }, [showIndicators, currentSymbol, interval, autoHeight, height]);

  const handleSymbolChange = (newSymbol: string) => {
    setCurrentSymbol(newSymbol.toUpperCase());
  };

  const toggleIndicator = (key: "sma" | "rsi" | "macd") => {
    setShowIndicators((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
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
      {/* Header with Controls */}
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
          <input
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
              onClick={() => setInterval(tf.value)}
              style={{
                padding: "6px 12px",
                background: interval === tf.value ? theme.colors.primary : "transparent",
                border: "none",
                borderRadius: theme.borderRadius.sm,
                color: interval === tf.value ? "#ffffff" : theme.colors.textMuted,
                fontSize: "13px",
                fontWeight: "600",
                cursor: "pointer",
                transition: theme.transitions.fast,
              }}
              onMouseEnter={(e) => {
                if (interval !== tf.value) {
                  e.currentTarget.style.background = "rgba(16, 185, 129, 0.1)";
                  e.currentTarget.style.color = theme.colors.primary;
                }
              }}
              onMouseLeave={(e) => {
                if (interval !== tf.value) {
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
                  background: isActive ? "rgba(16, 185, 129, 0.2)" : theme.background.input,
                  border: `1px solid ${isActive ? theme.colors.primary : theme.colors.border}`,
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
      </div>

      {/* TradingView Widget Container */}
      <div
        id="tradingview_widget"
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
