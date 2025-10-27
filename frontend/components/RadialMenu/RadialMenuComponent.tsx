import * as d3 from "d3";
import { memo, useEffect, useMemo, useRef, useState } from "react";
import { useIsMobile, useWindowDimensions } from "../../hooks/useBreakpoint";
import { useMarketData } from "../../hooks/useMarketData";
import { useRadialMenuD3, updateSelectedWorkflowAria } from "../../hooks/useRadialMenuD3";
import { logger } from "../../lib/logger";
import { LOGO_ANIMATION_KEYFRAME } from "../../styles/logoConstants";
import {
  calculateFontSizes,
  calculateMenuSize,
} from "../../utils/radialMenuHelpers";
import CompletePaiiDLogo from "../CompletePaiiDLogo";
import { Workflow, workflows } from "./workflows";
import MarketStatusBadge from "./MarketStatusBadge";

export interface RadialMenuProps {
  onWorkflowSelect: (workflowId: string) => void;
  onWorkflowHover?: (workflow: Workflow | null) => void;
  selectedWorkflow?: string;
  compact?: boolean;
}

// Memoized logo component - prevents re-renders from parent state changes
const MemoizedCenterLogo = memo(({ isMobile }: { isMobile: boolean }) => (
  <CompletePaiiDLogo size={isMobile ? 38 : 58} enableModal={true} />
));
MemoizedCenterLogo.displayName = "MemoizedCenterLogo";

const MemoizedHeaderLogo = memo(
  ({ isMobile, setShowAIChat }: { isMobile: boolean; setShowAIChat: (val: boolean) => void }) => (
    <div onClick={() => setShowAIChat(true)} style={{ cursor: "pointer" }}>
      <CompletePaiiDLogo size={isMobile ? 64 : 96} />
    </div>
  )
);
MemoizedHeaderLogo.displayName = "MemoizedHeaderLogo";

function RadialMenuComponent({
  onWorkflowSelect,
  onWorkflowHover,
  selectedWorkflow,
  compact,
}: RadialMenuProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const [_hoveredWorkflow, _setHoveredWorkflow] = useState<Workflow | null>(null);
  const [_showAIChat, _setShowAIChat] = useState(false);
  const [announcement, setAnnouncement] = useState<string>("");

  // Use custom hooks for market data and responsive sizing
  const {
    marketData,
    forceFieldConfidence,
    isMarketDataLoading,
    sseConnected: _sseConnected,
    sseRetryCount: _sseRetryCount,
    marketStatus,
    setMarketStatus: _setMarketStatus,
  } = useMarketData();

  // Responsive sizing
  const { width: viewportWidth } = useWindowDimensions();
  const isMobile = useIsMobile();

  // Memoize responsive menu size - only recalculate when dependencies change
  const menuSize = useMemo(
    () => calculateMenuSize(isMobile, viewportWidth),
    [isMobile, viewportWidth]
  );

  // Memoize responsive font sizes - only recalculate when isMobile changes
  const fontSizes = useMemo(() => calculateFontSizes(isMobile), [isMobile]);

  // Use D3.js rendering hook
  useRadialMenuD3({
    svgRef,
    workflows,
    menuSize,
    fontSizes,
    onWorkflowSelect,
    onWorkflowHover,
    setHoveredWorkflow,
    isMarketDataLoading,
    marketData,
    forceFieldConfidence,
  });

  // Debug logging for Fast Refresh loop detection
  useEffect(() => {
    logger.info("RadialMenu rendered with selectedWorkflow", { selectedWorkflow });
  }, [selectedWorkflow]);

  // Announce workflow changes for screen readers
  useEffect(() => {
    if (selectedWorkflow) {
      const workflow = workflows.find((w) => w.id === selectedWorkflow);
      if (workflow) {
        setAnnouncement(`${workflow.name.replace("\n", " ")} workflow selected`);
      }
    } else {
      setAnnouncement("");
    }
  }, [selectedWorkflow]);

  // Separate effect for selectedWorkflow updates - only update selected wedge styling
  useEffect(() => {
    if (!svgRef.current || !selectedWorkflow) return;

    // Update only the selected wedge styling without full re-render
    d3.select(svgRef.current)
      .selectAll(".segment path")
      .style("filter", function (this: SVGPathElement, d: { data: { id: string } }) {
        return d.data.id === selectedWorkflow ? "url(#clickGlow)" : "url(#normalShadow)";
      });

    // Update aria-current attribute for accessibility
    updateSelectedWorkflowAria(svgRef.current, selectedWorkflow);
  }, [selectedWorkflow]);

  return (
    <div
      ref={containerRef}
      role="navigation"
      aria-label="Trading workflow navigation menu"
      style={{
        width: "100%",
        height: "100%",
        background: "linear-gradient(135deg, #0f1828 0%, #1a2a3f 100%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0",
      }}
    >
      {/* Title Header - only show in full screen mode */}
      {!compact && (
        <div style={{ textAlign: "center", marginBottom: "10px" }}>
          <MemoizedHeaderLogo isMobile={isMobile} setShowAIChat={setShowAIChat} />
        </div>
      )}

      {/* SVG Radial Menu */}
      <div style={{ position: "relative" }}>
        <svg ref={svgRef} className="drop-shadow-2xl" />

        {/* Center Logo Overlay - perfectly centered in circle */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            pointerEvents: "auto",
          }}
        >
          <MemoizedCenterLogo isMobile={isMobile} />
        </div>

        {/* Market Status Badge */}
        <MarketStatusBadge marketStatus={marketStatus} menuSize={menuSize} isMobile={isMobile} />
      </div>

      {/* Screen reader announcements */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        style={{
          position: "absolute",
          left: "-10000px",
          width: "1px",
          height: "1px",
          overflow: "hidden",
        }}
      >
        {announcement}
      </div>

      {/* CSS Animations */}
      <style jsx>{`
        ${LOGO_ANIMATION_KEYFRAME}

        @keyframes pulse-open {
          0%,
          100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.7;
            transform: scale(1.2);
          }
        }
      `}</style>
    </div>
  );
}

// Export memoized component - prevents unnecessary re-renders when props haven't changed
export default memo(RadialMenuComponent, (prevProps, nextProps) => {
  // Custom comparison: only re-render if these props actually changed
  return (
    prevProps.selectedWorkflow === nextProps.selectedWorkflow &&
    prevProps.compact === nextProps.compact &&
    prevProps.onWorkflowSelect === nextProps.onWorkflowSelect &&
    prevProps.onWorkflowHover === nextProps.onWorkflowHover
  );
});
