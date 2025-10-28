import React from "react";
import CompletePaiiDLogo from "../CompletePaiiDLogo";

interface AppHeaderProps {
  onLogoClick?: () => void;
}

export default function AppHeader({ onLogoClick }: AppHeaderProps) {
  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 1000,
        width: "100%",
        background: "rgba(15, 23, 42, 0.85)",
        backdropFilter: "blur(10px)",
        borderBottom: "1px solid rgba(148, 163, 184, 0.2)",
      }}
      aria-label="PaiiD header"
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          margin: "0 auto",
          padding: "8px 16px",
          maxWidth: 1400,
        }}
      >
        <button
          onClick={onLogoClick}
          aria-label="PaiiD"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            background: "transparent",
            border: "none",
            padding: 0,
            cursor: onLogoClick ? "pointer" : "default",
          }}
        >
          <CompletePaiiDLogo size={36} enableModal={true} />
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {/* Right side actions could go here if needed */}
        </div>
      </div>
    </header>
  );
}


