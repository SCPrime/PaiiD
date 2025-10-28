import React from "react";
import CompletePaiiDLogo from "../CompletePaiiDLogo";

interface PaiiDInlineProps {
  size?: number;
}

export default function PaiiDInline({ size = 16 }: PaiiDInlineProps) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", verticalAlign: "middle" }}>
      <CompletePaiiDLogo size={size} />
      <span className="sr-only">PaiiD</span>
    </span>
  );
}


