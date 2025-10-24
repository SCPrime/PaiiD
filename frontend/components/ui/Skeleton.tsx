"use client";

import { theme } from "../../styles/theme";

export function Skeleton({
  width = "100%",
  height = 16,
  radius = 8,
}: {
  width?: string | number;
  height?: number;
  radius?: number;
}) {
  return (
    <div
      style={{
        width,
        height,
        borderRadius: radius,
        background: theme.background.input,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(90deg, transparent, ${theme.colors.textMuted}20, transparent)`,
          animation: "skeleton-shimmer 1.2s infinite",
        }}
      />
      <style jsx>{`
        @keyframes skeleton-shimmer {
          0% {
            transform: translateX(-100%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </div>
  );
}
