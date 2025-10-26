"use client";

import { createContext, ReactNode, useContext, useEffect, useState } from "react";
import { logger } from "../lib/logger";

type GlowStyle = "radial" | "halo";

interface GlowStyleContextType {
  glowStyle: GlowStyle;
  setGlowStyle: (style: GlowStyle) => void;
}

const GlowStyleContext = createContext<GlowStyleContextType | undefined>(undefined);

export function GlowStyleProvider({ children }: { children: ReactNode }) {
  const [glowStyle, setGlowStyle] = useState<GlowStyle>("radial");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const glow = params.get("glow");
      if (glow === "halo") {
        setGlowStyle("halo");
        logger.info("[GlowStyle] 🎨 Using HALO glow");
      } else {
        setGlowStyle("radial");
        logger.info("[GlowStyle] 🎨 Using RADIAL glow (default)");
      }
    }
  }, []);

  return (
    <GlowStyleContext.Provider value={{ glowStyle, setGlowStyle }}>
      {children}
    </GlowStyleContext.Provider>
  );
}

export function useGlowStyle() {
  const context = useContext(GlowStyleContext);
  if (context === undefined) {
    throw new Error("useGlowStyle must be used within GlowStyleProvider");
  }
  return context;
}
