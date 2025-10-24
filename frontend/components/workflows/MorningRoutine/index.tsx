import React, { useMemo } from "react";
import { paidTheme } from "../../../styles/paiid-theme";
import { MarketStatus } from "./MarketStatus";
import { PortfolioSummary } from "./PortfolioSummary";
import { TodaySchedule } from "./TodaySchedule";
import { MarketAlerts } from "./MarketAlerts";
import { PreMarketMovers } from "./PreMarketMovers";
import { useIsMobile, useIsTablet } from "@/hooks/useBreakpoint";

export const MorningRoutine: React.FC = () => {
  const isMobile = useIsMobile();
  const isTablet = useIsTablet();

  const layoutColumns = useMemo(() => {
    if (isMobile) return "repeat(1, minmax(0, 1fr))";
    if (isTablet) return "repeat(8, minmax(0, 1fr))";
    return "repeat(12, minmax(0, 1fr))";
  }, [isMobile, isTablet]);

  const leftColumnSpan = useMemo(() => {
    if (isMobile) return "span 1";
    if (isTablet) return "span 3";
    return "span 3";
  }, [isMobile, isTablet]);

  const middleColumnSpan = useMemo(() => {
    if (isMobile) return "span 1";
    if (isTablet) return "span 5";
    return "span 6";
  }, [isMobile, isTablet]);

  const rightColumnSpan = useMemo(() => {
    if (isMobile) return "span 1";
    if (isTablet) return "span 8";
    return "span 3";
  }, [isMobile, isTablet]);

  const containerPadding = isMobile ? paidTheme.spacing.md : paidTheme.spacing.xl;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: paidTheme.colors.background,
        color: paidTheme.colors.text,
        fontFamily: paidTheme.typography.fontFamily.main,
        padding: containerPadding,
        paddingTop: isMobile ? paidTheme.spacing.lg : paidTheme.spacing.xl,
      }}
    >
      {/* Header */}
      <div
        style={{
          marginBottom: isMobile ? paidTheme.spacing.lg : paidTheme.spacing.xl,
          paddingBottom: isMobile ? paidTheme.spacing.md : paidTheme.spacing.lg,
          borderBottom: `1px solid ${paidTheme.colors.glassBorder}`,
          display: "flex",
          flexDirection: "column",
          gap: isMobile ? paidTheme.spacing.xs : paidTheme.spacing.sm,
        }}
      >
        <h1
          style={{
            fontSize: isMobile
              ? paidTheme.typography.fontSize["xl"]
              : paidTheme.typography.fontSize["3xl"],
            fontWeight: 700,
            margin: 0,
            marginBottom: paidTheme.spacing.xs,
            background: `linear-gradient(135deg, ${paidTheme.colors.text}, ${paidTheme.colors.accent})`,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          Morning Routine
        </h1>
        <p
          style={{
            fontSize: isMobile
              ? paidTheme.typography.fontSize.sm
              : paidTheme.typography.fontSize.base,
            color: paidTheme.colors.textMuted,
            margin: 0,
          }}
        >
          Your daily market briefing and portfolio overview
        </p>
      </div>

      {/* Main Grid Layout */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: layoutColumns,
          gap: isMobile ? paidTheme.spacing.md : paidTheme.spacing.lg,
        }}
      >
        {/* Left Column - Market Status + Alerts */}
        <div
          style={{
            gridColumn: leftColumnSpan,
            display: "flex",
            flexDirection: "column",
            gap: paidTheme.spacing.md,
          }}
        >
          <MarketStatus />
          <MarketAlerts />
        </div>

        {/* Middle Column - Portfolio + Schedule */}
        <div
          style={{
            gridColumn: middleColumnSpan,
            display: "flex",
            flexDirection: "column",
            gap: paidTheme.spacing.md,
          }}
        >
          <PortfolioSummary />
          <TodaySchedule />
        </div>

        {/* Right Column - Pre-Market Movers */}
        <div
          style={{
            gridColumn: rightColumnSpan,
          }}
        >
          <PreMarketMovers />
        </div>
      </div>

      {/* Quick Actions Footer */}
      <div
        style={{
          marginTop: isMobile ? paidTheme.spacing.lg : paidTheme.spacing.xl,
          display: "flex",
          flexWrap: "wrap",
          gap: paidTheme.spacing.sm,
          justifyContent: "center",
        }}
      >
        {[
          { label: "View Full Portfolio", icon: "📊" },
          { label: "Trading Dashboard", icon: "📈" },
          { label: "Research Tools", icon: "🔍" },
          { label: "Settings", icon: "⚙️" },
        ].map((action) => (
          <button
            key={action.label}
            style={{
              background: paidTheme.colors.glass,
              border: `1px solid ${paidTheme.colors.glassBorder}`,
              borderRadius: paidTheme.borderRadius.md,
              padding: `${paidTheme.spacing.xs} ${paidTheme.spacing.md}`,
              color: paidTheme.colors.text,
              fontSize: paidTheme.typography.fontSize.sm,
              fontWeight: 500,
              cursor: "pointer",
              transition: `all ${paidTheme.animation.duration.normal}`,
              display: "flex",
              alignItems: "center",
              gap: paidTheme.spacing.sm,
              width: isMobile ? "100%" : "auto",
              justifyContent: "center",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = paidTheme.colors.glassHover;
              e.currentTarget.style.borderColor = paidTheme.colors.accent + "60";
              e.currentTarget.style.transform = "translateY(-2px)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = paidTheme.colors.glass;
              e.currentTarget.style.borderColor = paidTheme.colors.glassBorder;
              e.currentTarget.style.transform = "translateY(0)";
            }}
          >
            <span>{action.icon}</span>
            <span>{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default MorningRoutine;
