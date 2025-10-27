import { getConfidenceColor } from "../utils/radialMenuHelpers";

interface ForceFieldIndicatorProps {
  confidence: number;
  size?: "small" | "medium" | "large";
}

/**
 * ForceFieldIndicator - Displays market data confidence level
 *
 * Confidence calculation based on:
 * - Data freshness (40%): How recently market data was received
 * - Market stability (40%): Lower volatility = higher confidence
 * - Connection quality (20%): SSE connection retry attempts
 *
 * Color coding:
 * - Green (≥80%): Excellent confidence
 * - Amber (≥60%): Good confidence
 * - Orange (≥40%): Fair confidence
 * - Red (<40%): Low confidence
 */
export default function ForceFieldIndicator({
  confidence,
  size = "medium"
}: ForceFieldIndicatorProps) {
  const color = getConfidenceColor(confidence);

  // Size configurations
  const sizeConfig = {
    small: {
      fontSize: "16px",
      labelSize: "12px",
      padding: "8px 12px",
    },
    medium: {
      fontSize: "24px",
      labelSize: "14px",
      padding: "12px 16px",
    },
    large: {
      fontSize: "32px",
      labelSize: "16px",
      padding: "16px 20px",
    },
  };

  const config = sizeConfig[size];

  return (
    <div
      style={{
        display: "inline-flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "4px",
        padding: config.padding,
        background: "rgba(15, 23, 42, 0.6)",
        backdropFilter: "blur(10px)",
        border: `2px solid ${color}`,
        borderRadius: "8px",
        boxShadow: `0 0 20px ${color}40`,
      }}
    >
      <div
        style={{
          fontSize: config.labelSize,
          fontWeight: 600,
          color: "#94a3b8",
          letterSpacing: "0.05em",
        }}
      >
        FORCE FIELD
      </div>
      <div
        style={{
          fontSize: config.fontSize,
          fontWeight: 700,
          color: color,
          textShadow: `0 0 10px ${color}80`,
        }}
      >
        {confidence}%
      </div>
    </div>
  );
}
