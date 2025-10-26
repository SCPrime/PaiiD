import { MarketStatus } from "../../hooks/useMarketData";

interface MarketStatusBadgeProps {
  marketStatus: MarketStatus | null;
  menuSize: number;
  isMobile: boolean;
}

export default function MarketStatusBadge({
  marketStatus,
  menuSize,
  isMobile,
}: MarketStatusBadgeProps) {
  if (!marketStatus) return null;

  return (
    <div
      style={{
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        marginTop: `${(menuSize / 2) * 0.3 * 0.75}px`, // Responsive: matches centerContentSpacing.statusBadgeOffset
        pointerEvents: "none",
        textAlign: "center",
      }}
    >
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          padding: isMobile ? "4px 10px" : "6px 14px",
          background: marketStatus.is_open
            ? "rgba(69, 240, 192, 0.15)"
            : "rgba(239, 68, 68, 0.15)",
          border: `1px solid ${marketStatus.is_open ? "rgba(69, 240, 192, 0.4)" : "rgba(239, 68, 68, 0.4)"}`,
          borderRadius: "20px",
          backdropFilter: "blur(10px)",
          boxShadow: marketStatus.is_open
            ? "0 0 15px rgba(69, 240, 192, 0.2)"
            : "0 0 15px rgba(239, 68, 68, 0.2)",
        }}
      >
        <div
          style={{
            width: isMobile ? "6px" : "8px",
            height: isMobile ? "6px" : "8px",
            borderRadius: "50%",
            background: marketStatus.is_open ? "#45f0c0" : "#ef4444",
            boxShadow: `0 0 8px ${marketStatus.is_open ? "rgba(69, 240, 192, 0.6)" : "rgba(239, 68, 68, 0.6)"}`,
            animation: marketStatus.is_open ? "pulse-open 2s ease-in-out infinite" : "none",
          }}
        />
        <div
          style={{
            fontSize: isMobile ? "9px" : "11px",
            fontWeight: "800",
            letterSpacing: "1px",
            textTransform: "uppercase",
            color: marketStatus.is_open ? "#45f0c0" : "#ef4444",
          }}
        >
          {marketStatus.state === "open" && "Market Open"}
          {marketStatus.state === "premarket" && "Pre-Market"}
          {marketStatus.state === "postmarket" && "After Hours"}
          {marketStatus.state === "closed" && "Market Closed"}
        </div>
      </div>
    </div>
  );
}
