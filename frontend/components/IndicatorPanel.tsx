import React from "react";
import { useIsMobile } from "../hooks/useBreakpoint";

interface TechnicalIndicators {
  rsi?: number;
  macd?: {
    macd: number;
    signal: number;
    histogram: number;
  };
  bollingerBands?: {
    upper: number;
    middle: number;
    lower: number;
    currentPrice: number;
  };
  sma?: {
    sma20: number;
    sma50: number;
    sma200: number;
    currentPrice: number;
  };
  ema?: {
    ema12: number;
    ema26: number;
  };
  atr?: number;
}

interface IndicatorPanelProps {
  symbol: string;
  indicators?: TechnicalIndicators;
  loading?: boolean;
}

const IndicatorPanel: React.FC<IndicatorPanelProps> = ({ symbol, indicators, loading = false }) => {
  const isMobile = useIsMobile();

  const theme = {
    bg: "rgba(15, 23, 42, 0.7)",
    bgLight: "rgba(30, 41, 59, 0.8)",
    text: "#e2e8f0",
    textMuted: "#94a3b8",
    primary: "#10b981",
    warning: "#eab308",
    danger: "#ef4444",
    border: "rgba(148, 163, 184, 0.2)",
  };

  const getRSISignal = (rsi: number | undefined): { color: string; signal: string } => {
    if (!rsi) return { color: theme.textMuted, signal: "N/A" };
    if (rsi > 70) return { color: theme.danger, signal: "Overbought" };
    if (rsi < 30) return { color: theme.primary, signal: "Oversold" };
    return { color: theme.warning, signal: "Neutral" };
  };

  const getMACDSignal = (macd: TechnicalIndicators["macd"]): { color: string; signal: string } => {
    if (!macd) return { color: theme.textMuted, signal: "N/A" };
    if (macd.histogram > 0) return { color: theme.primary, signal: "Bullish" };
    if (macd.histogram < 0) return { color: theme.danger, signal: "Bearish" };
    return { color: theme.warning, signal: "Neutral" };
  };

  const getBBSignal = (
    bb: TechnicalIndicators["bollingerBands"]
  ): { color: string; signal: string } => {
    if (!bb) return { color: theme.textMuted, signal: "N/A" };
    const { currentPrice, upper, lower, middle: _middle } = bb;
    if (currentPrice >= upper) return { color: theme.danger, signal: "Overbought" };
    if (currentPrice <= lower) return { color: theme.primary, signal: "Oversold" };
    return { color: theme.warning, signal: "Neutral" };
  };

  const getSMASignal = (sma: TechnicalIndicators["sma"]): { color: string; signal: string } => {
    if (!sma) return { color: theme.textMuted, signal: "N/A" };
    const { currentPrice, sma20, sma50, sma200 } = sma;
    if (currentPrice > sma20 && currentPrice > sma50 && currentPrice > sma200) {
      return { color: theme.primary, signal: "Strong Uptrend" };
    }
    if (currentPrice < sma20 && currentPrice < sma50 && currentPrice < sma200) {
      return { color: theme.danger, signal: "Strong Downtrend" };
    }
    if (currentPrice > sma20 && currentPrice > sma50) {
      return { color: theme.primary, signal: "Uptrend" };
    }
    return { color: theme.warning, signal: "Mixed" };
  };

  const rsiSignal = getRSISignal(indicators?.rsi);
  const macdSignal = getMACDSignal(indicators?.macd);
  const bbSignal = getBBSignal(indicators?.bollingerBands);
  const smaSignal = getSMASignal(indicators?.sma);

  return (
    <div
      style={{
        padding: isMobile ? "16px" : "24px",
        background: theme.bg,
        borderRadius: "12px",
        border: `1px solid ${theme.border}`,
      }}
    >
      <h3
        style={{
          fontSize: "18px",
          fontWeight: 600,
          color: theme.text,
          margin: "0 0 16px 0",
        }}
      >
        Technical Indicators - {symbol}
      </h3>

      {loading ? (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            color: theme.textMuted,
            fontSize: "14px",
          }}
        >
          Calculating indicators...
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: isMobile ? "1fr" : "repeat(2, 1fr)",
            gap: "12px",
          }}
        >
          {/* RSI */}
          <div
            style={{
              padding: "16px",
              background: theme.bgLight,
              borderRadius: "8px",
              borderLeft: `4px solid ${rsiSignal.color}`,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <div style={{ fontSize: "14px", color: theme.textMuted, fontWeight: 600 }}>
                RSI (14)
              </div>
              <div style={{ fontSize: "12px", color: rsiSignal.color, fontWeight: 600 }}>
                {rsiSignal.signal}
              </div>
            </div>
            <div style={{ fontSize: "24px", color: theme.text, fontWeight: 700 }}>
              {indicators?.rsi ? indicators.rsi.toFixed(2) : "N/A"}
            </div>
            <div style={{ fontSize: "11px", color: theme.textMuted, marginTop: "4px" }}>
              &lt;30 Oversold | &gt;70 Overbought
            </div>
          </div>

          {/* MACD */}
          <div
            style={{
              padding: "16px",
              background: theme.bgLight,
              borderRadius: "8px",
              borderLeft: `4px solid ${macdSignal.color}`,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <div style={{ fontSize: "14px", color: theme.textMuted, fontWeight: 600 }}>
                MACD (12,26,9)
              </div>
              <div style={{ fontSize: "12px", color: macdSignal.color, fontWeight: 600 }}>
                {macdSignal.signal}
              </div>
            </div>
            <div style={{ fontSize: "20px", color: theme.text, fontWeight: 700 }}>
              {indicators?.macd ? indicators.macd.histogram.toFixed(4) : "N/A"}
            </div>
            <div style={{ fontSize: "11px", color: theme.textMuted, marginTop: "4px" }}>
              {indicators?.macd
                ? `MACD: ${indicators.macd.macd.toFixed(4)} | Signal: ${indicators.macd.signal.toFixed(4)}`
                : "Histogram value"}
            </div>
          </div>

          {/* Bollinger Bands */}
          <div
            style={{
              padding: "16px",
              background: theme.bgLight,
              borderRadius: "8px",
              borderLeft: `4px solid ${bbSignal.color}`,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <div style={{ fontSize: "14px", color: theme.textMuted, fontWeight: 600 }}>
                Bollinger Bands (20,2)
              </div>
              <div style={{ fontSize: "12px", color: bbSignal.color, fontWeight: 600 }}>
                {bbSignal.signal}
              </div>
            </div>
            <div style={{ fontSize: "14px", color: theme.text }}>
              {indicators?.bollingerBands ? (
                <>
                  <div>Upper: ${indicators.bollingerBands.upper.toFixed(2)}</div>
                  <div style={{ fontWeight: 700 }}>
                    Mid: ${indicators.bollingerBands.middle.toFixed(2)}
                  </div>
                  <div>Lower: ${indicators.bollingerBands.lower.toFixed(2)}</div>
                </>
              ) : (
                "N/A"
              )}
            </div>
          </div>

          {/* SMA */}
          <div
            style={{
              padding: "16px",
              background: theme.bgLight,
              borderRadius: "8px",
              borderLeft: `4px solid ${smaSignal.color}`,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <div style={{ fontSize: "14px", color: theme.textMuted, fontWeight: 600 }}>
                Simple Moving Averages
              </div>
              <div style={{ fontSize: "12px", color: smaSignal.color, fontWeight: 600 }}>
                {smaSignal.signal}
              </div>
            </div>
            <div style={{ fontSize: "14px", color: theme.text }}>
              {indicators?.sma ? (
                <>
                  <div>SMA 20: ${indicators.sma.sma20.toFixed(2)}</div>
                  <div>SMA 50: ${indicators.sma.sma50.toFixed(2)}</div>
                  <div>SMA 200: ${indicators.sma.sma200.toFixed(2)}</div>
                </>
              ) : (
                "N/A"
              )}
            </div>
          </div>
        </div>
      )}

      <p
        style={{
          fontSize: "12px",
          color: theme.textMuted,
          marginTop: "16px",
          textAlign: "center",
          borderTop: `1px solid ${theme.border}`,
          paddingTop: "12px",
        }}
      >
        Indicators calculated from Tradier historical data
      </p>
    </div>
  );
};

export default IndicatorPanel;
