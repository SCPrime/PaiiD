import React from "react";
import { useIsMobile } from "../hooks/useBreakpoint";

interface CompanyHeaderProps {
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  marketCap?: number;
  pe_ratio?: number;
  week52High?: number;
  week52Low?: number;
  avgVolume?: number;
  dividend_yield?: number;
}

const CompanyHeader: React.FC<CompanyHeaderProps> = ({
  symbol,
  name,
  currentPrice,
  change,
  changePercent,
  marketCap,
  pe_ratio,
  week52High,
  week52Low,
  avgVolume,
  dividend_yield,
}) => {
  const isMobile = useIsMobile();

  const theme = {
    bg: "rgba(15, 23, 42, 0.7)",
    text: "#e2e8f0",
    textMuted: "#94a3b8",
    primary: "#10b981",
    danger: "#ef4444",
    border: "rgba(148, 163, 184, 0.2)",
  };

  const formatMarketCap = (value: number | undefined): string => {
    if (!value) return "N/A";
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  const formatVolume = (value: number | undefined): string => {
    if (!value) return "N/A";
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value.toString();
  };

  return (
    <div
      style={{
        padding: isMobile ? "16px" : "24px",
        background: theme.bg,
        borderRadius: "12px",
        border: `1px solid ${theme.border}`,
      }}
    >
      {/* Header Row */}
      <div
        style={{
          display: "flex",
          flexDirection: isMobile ? "column" : "row",
          justifyContent: "space-between",
          alignItems: isMobile ? "flex-start" : "center",
          gap: "12px",
          marginBottom: "16px",
        }}
      >
        <div>
          <h2
            style={{
              fontSize: isMobile ? "24px" : "28px",
              fontWeight: 700,
              color: theme.text,
              margin: 0,
            }}
          >
            {symbol}
          </h2>
          <p
            style={{
              fontSize: "14px",
              color: theme.textMuted,
              margin: "4px 0 0 0",
            }}
          >
            {name}
          </p>
        </div>
        <div style={{ textAlign: isMobile ? "left" : "right" }}>
          <div
            style={{
              fontSize: isMobile ? "28px" : "32px",
              fontWeight: 700,
              color: theme.text,
            }}
          >
            ${currentPrice.toFixed(2)}
          </div>
          <div
            style={{
              fontSize: "16px",
              color: change >= 0 ? theme.primary : theme.danger,
              fontWeight: 600,
            }}
          >
            {change >= 0 ? "+" : ""}
            {change.toFixed(2)}({changePercent >= 0 ? "+" : ""}
            {changePercent.toFixed(2)}%)
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: isMobile ? "1fr 1fr" : "repeat(auto-fit, minmax(120px, 1fr))",
          gap: "16px",
          paddingTop: "16px",
          borderTop: `1px solid ${theme.border}`,
        }}
      >
        {marketCap && (
          <div>
            <div style={{ fontSize: "12px", color: theme.textMuted }}>Market Cap</div>
            <div style={{ fontSize: "16px", color: theme.text, fontWeight: 600 }}>
              {formatMarketCap(marketCap)}
            </div>
          </div>
        )}
        {pe_ratio && (
          <div>
            <div style={{ fontSize: "12px", color: theme.textMuted }}>P/E Ratio</div>
            <div style={{ fontSize: "16px", color: theme.text, fontWeight: 600 }}>
              {pe_ratio.toFixed(2)}
            </div>
          </div>
        )}
        {week52High !== undefined && (
          <div>
            <div style={{ fontSize: "12px", color: theme.textMuted }}>52W High</div>
            <div style={{ fontSize: "16px", color: theme.text, fontWeight: 600 }}>
              ${week52High.toFixed(2)}
            </div>
          </div>
        )}
        {week52Low !== undefined && (
          <div>
            <div style={{ fontSize: "12px", color: theme.textMuted }}>52W Low</div>
            <div style={{ fontSize: "16px", color: theme.text, fontWeight: 600 }}>
              ${week52Low.toFixed(2)}
            </div>
          </div>
        )}
        {avgVolume && (
          <div>
            <div style={{ fontSize: "12px", color: theme.textMuted }}>Avg Volume</div>
            <div style={{ fontSize: "16px", color: theme.text, fontWeight: 600 }}>
              {formatVolume(avgVolume)}
            </div>
          </div>
        )}
        {dividend_yield && (
          <div>
            <div style={{ fontSize: "12px", color: theme.textMuted }}>Dividend Yield</div>
            <div style={{ fontSize: "16px", color: theme.text, fontWeight: 600 }}>
              {(dividend_yield * 100).toFixed(2)}%
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompanyHeader;
