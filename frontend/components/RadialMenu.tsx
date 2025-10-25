/* eslint-disable no-console */
import * as d3 from "d3";
import { throttle } from "lodash";
import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useIsMobile, useWindowDimensions } from "../hooks/useBreakpoint";
import { LOGO_ANIMATION_KEYFRAME } from "../styles/logoConstants";
import CompletePaiiDLogo from "./CompletePaiiDLogo";

export interface Workflow {
  id: string;
  name: string;
  color: string;
  icon: string;
  description: string;
}

interface RadialMenuProps {
  onWorkflowSelect: (workflowId: string) => void;
  onWorkflowHover?: (workflow: Workflow | null) => void;
  selectedWorkflow?: string;
  compact?: boolean;
}

export const workflows: Workflow[] = [
  {
    id: "morning-routine",
    name: "MORNING\nROUTINE",
    color: "#00ACC1",
    icon: "🌅",
    description: "Start your day with market analysis, portfolio review, and trading alerts.",
  },
  {
    id: "news-review",
    name: "NEWS\nREVIEW",
    color: "#7E57C2",
    icon: "📰",
    description: "Real-time market news aggregation with AI-powered sentiment analysis.",
  },
  {
    id: "proposals",
    name: "AI\nRECS",
    color: "#0097A7",
    icon: "🤖",
    description: "Review AI-generated trading recommendations and strategy proposals.",
  },
  {
    id: "active-positions",
    name: "ACTIVE\nPOSITIONS",
    color: "#00C851",
    icon: "📊",
    description: "Monitor and manage your current open positions and orders.",
  },
  {
    id: "pnl-dashboard",
    name: "P&L\nDASHBOARD",
    color: "#FF8800",
    icon: "💰",
    description: "Analytics, performance metrics, equity curves, and trading statistics.",
  },
  {
    id: "strategy-builder",
    name: "STRATEGY\nBUILDER",
    color: "#5E35B1",
    icon: "🎯",
    description: "Design and test custom trading strategies with drag-and-drop rules.",
  },
  {
    id: "backtesting",
    name: "BACK\nTESTING",
    color: "#00BCD4",
    icon: "📈",
    description: "Test strategies against historical data to validate performance.",
  },
  {
    id: "execute",
    name: "EXECUTE",
    color: "#FF4444",
    icon: "⚡",
    description: "Execute trades with pre-filled orders and real-time confirmation.",
  },
  {
    id: "options-trading",
    name: "OPTIONS\nTRADING",
    color: "#8B5CF6",
    icon: "📈",
    description: "Options chain viewer with Greeks, multi-leg strategies, and execution.",
  },
  {
    id: "monitor",
    name: "REPO\nMONITOR",
    color: "#10B981",
    icon: "🔍",
    description: "GitHub repository monitoring with real-time activity tracking and metrics.",
  },
  {
    id: "ml-intelligence",
    name: "ML\nINTELLIGENCE",
    color: "#8B5CF6",
    icon: "🧠",
    description: "AI-powered market analysis, pattern recognition, and personal trading insights.",
  },
  {
    id: "settings",
    name: "SETTINGS",
    color: "#64748b",
    icon: "⚙️",
    description: "Trading journal, risk control, and system configuration.",
  },
];

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
  const [_hoveredWorkflow, setHoveredWorkflow] = useState<Workflow | null>(null);
  const [_showAIChat, setShowAIChat] = useState(false);
  const [marketData, setMarketData] = useState({
    dow: { value: 0, change: 0, symbol: "DJI" },
    nasdaq: { value: 0, change: 0, symbol: "COMP" },
    lastUpdate: 0,
  });
  const [forceFieldConfidence, setForceFieldConfidence] = useState(0);
  const [isMarketDataLoading, setIsMarketDataLoading] = useState(true);
  const [_sseConnected, setSseConnected] = useState(false);
  const [_sseRetryCount, setSseRetryCount] = useState(0);
  const [marketStatus, _setMarketStatus] = useState<{
    is_open: boolean;
    state: string;
    description: string;
  } | null>(null);

  // Responsive sizing
  const { width: viewportWidth } = useWindowDimensions();
  const isMobile = useIsMobile();

  // Memoize responsive menu size - only recalculate when dependencies change
  const menuSize = useMemo(() => {
    if (isMobile) {
      // Mobile: 90% of viewport width, max 675px (35% increase from 500)
      return Math.min(viewportWidth * 0.9, 675);
    }

    // Desktop: Responsive to viewport width for split-screen mode
    // When viewport < 1900px (typical split screen), scale down proportionally
    if (viewportWidth < 1900) {
      return Math.min(viewportWidth * 0.85, 945);
    }

    // Desktop full screen: Standard 945px (35% increase from 700)
    return 945;
  }, [isMobile, viewportWidth]);

  // Memoize responsive font sizes - only recalculate when isMobile changes
  const fontSizes = useMemo(() => {
    if (isMobile) {
      return {
        headerLogo: "65px", // 48 × 1.35
        headerSubtitle1: "22px", // 16 × 1.35
        headerSubtitle2: "19px", // 14 × 1.35
        segmentText: "22px", // 16 × 1.35
        centerLogo: "27px", // 20 × 1.35
        marketLabel: "9px", // 7 × 1.35 ≈ 9
        marketValue: "16px", // 12 × 1.35 ≈ 16
        marketChange: "11px", // 8 × 1.35 ≈ 11
      };
    }
    // Desktop sizes - scaled up 35% for better readability
    return {
      headerLogo: "130px", // 96 × 1.35
      headerSubtitle1: "30px", // 22 × 1.35
      headerSubtitle2: "24px", // 18 × 1.35
      segmentText: "30px", // 22 × 1.35
      centerLogo: "43px", // 32 × 1.35
      marketLabel: "12px", // 9 × 1.35
      marketValue: "22px", // 16 × 1.35
      marketChange: "14px", // 10 × 1.35
    };
  }, [isMobile]);

  // Throttled market data update - prevents animation interruptions
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const throttledSetMarketData = useCallback(
    throttle((newData: typeof marketData) => {
      setMarketData(newData);
      console.info("[RadialMenu] 🎯 Market data updated (throttled)");
    }, 10000), // Update max once per 10 seconds
    []
  );

  // ⚡ REAL-TIME STREAMING: SSE for market data with auto-reconnection
  useEffect(() => {
    let eventSource: EventSource | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    let isUnmounted = false;

    // Load cached market data on mount
    const loadCachedData = () => {
      try {
        const cached = localStorage.getItem("paiid-market-data");
        if (cached) {
          const parsed = JSON.parse(cached);
          // Only use cache if it's less than 24 hours old
          if (parsed.timestamp && Date.now() - parsed.timestamp < 24 * 60 * 60 * 1000) {
            console.info("[RadialMenu] 💾 Loading cached market data from localStorage");
            setMarketData(parsed.data);
            setIsMarketDataLoading(false);
          }
        }
      } catch (error) {
        console.error("[RadialMenu] ❌ Failed to load cached market data:", error);
      }
    };

    // SSE connection with exponential backoff retry
    const connectSSE = (retryAttempt = 0) => {
      if (isUnmounted) return;

      const maxRetries = 10;
      const baseDelay = 2000; // 2 seconds

      if (retryAttempt >= maxRetries) {
        console.error("[RadialMenu] 🚨 Max SSE retry attempts reached. Giving up.");
        setIsMarketDataLoading(false);
        return;
      }

      console.info(
        `[RadialMenu] 📡 Connecting to SSE stream (attempt ${retryAttempt + 1}/${maxRetries})...`
      );
      setSseRetryCount(retryAttempt);

      try {
        eventSource = new EventSource("/api/proxy/stream/market-indices");

        eventSource.addEventListener("indices_update", (e) => {
          const data = JSON.parse(e.data);
          console.debug("[RadialMenu] 📊 Received live market data:", data);

          const now = Date.now();
          const newData = {
            dow: {
              value: data.dow?.last || 0,
              change: data.dow?.changePercent || 0,
              symbol: "DJI",
            },
            nasdaq: {
              value: data.nasdaq?.last || 0,
              change: data.nasdaq?.changePercent || 0,
              symbol: "COMP",
            },
            lastUpdate: now,
          };

          // Calculate Force Field Confidence (0-100%)
          // Based on: data freshness, market stability, and connection quality
          const dataFreshness = 100; // Fresh data just received
          const marketVolatility = Math.abs(newData.dow.change) + Math.abs(newData.nasdaq.change);
          const stabilityScore = Math.max(0, 100 - marketVolatility * 10); // Lower volatility = higher confidence
          const connectionScore = retryAttempt === 0 ? 100 : Math.max(0, 100 - retryAttempt * 10);

          const confidence = Math.round(
            dataFreshness * 0.4 + stabilityScore * 0.4 + connectionScore * 0.2
          );
          setForceFieldConfidence(Math.min(100, Math.max(0, confidence)));

          // Use throttled update to prevent logo animation interruptions
          throttledSetMarketData(newData);

          // Mark as connected and loading complete
          setSseConnected(true);
          setIsMarketDataLoading(false);
          setSseRetryCount(0); // Reset retry count on success

          // Cache the data in localStorage (immediate, not throttled)
          try {
            localStorage.setItem(
              "paiid-market-data",
              JSON.stringify({
                data: newData,
                timestamp: Date.now(),
              })
            );
          } catch (error) {
            console.error("[RadialMenu] ❌ Failed to cache market data:", error);
          }
        });

        eventSource.addEventListener("heartbeat", (e) => {
          const data = JSON.parse(e.data);
          console.debug("[RadialMenu] 💓 SSE heartbeat received:", data.timestamp);
        });

        eventSource.addEventListener("error", (e) => {
          console.error("[RadialMenu] ❌ SSE connection error:", e);
          setSseConnected(false);

          if (eventSource) {
            eventSource.close();
            eventSource = null;
          }

          // Exponential backoff: 2s, 4s, 8s, 16s, 32s, 64s, 128s (max ~2min)
          const delay = Math.min(baseDelay * Math.pow(2, retryAttempt), 128000);
          console.warn(
            `[RadialMenu] ⚠️ SSE disconnected. Retrying in ${delay / 1000}s... (attempt ${retryAttempt + 1}/${maxRetries})`
          );

          reconnectTimeout = setTimeout(() => {
            connectSSE(retryAttempt + 1);
          }, delay);
        });

        eventSource.addEventListener("open", () => {
          console.info("[RadialMenu] ✅ SSE connection established");
          setSseConnected(true);
        });
      } catch (error) {
        console.error("[RadialMenu] ❌ Failed to create EventSource:", error);
        setSseConnected(false);

        // Retry with exponential backoff
        const delay = Math.min(baseDelay * Math.pow(2, retryAttempt), 128000);
        reconnectTimeout = setTimeout(() => {
          connectSSE(retryAttempt + 1);
        }, delay);
      }
    };

    // Initialize
    loadCachedData();
    connectSSE(0);

    // Cleanup: close SSE connection on unmount
    return () => {
      isUnmounted = true;
      console.info("[RadialMenu] 🔌 Closing SSE connection");

      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }

      if (eventSource) {
        eventSource.close();
      }
    };
  }, [throttledSetMarketData]);

  // Debug logging for Fast Refresh loop detection
  useEffect(() => {
    console.info("RadialMenu rendered with selectedWorkflow:", selectedWorkflow);
  }, [selectedWorkflow]);

  useEffect(() => {
    if (!svgRef.current) return;

    // ✅ EXTENSION VERIFICATION: D3.js
    console.info("[Extension Verification] ✅ D3.js loaded successfully:", {
      version: d3.version,
      modules: ["select", "pie", "arc", "selectAll"],
      status: "FUNCTIONAL",
    });

    const width = menuSize;
    const height = menuSize;
    const radius = Math.min(width, height) / 2;
    const innerRadius = radius * 0.3;
    const outerRadius = radius * 0.9;

    // Calculate responsive center content positions based on innerRadius
    // This ensures proper spacing regardless of menu size (500px mobile → 700px desktop)
    const centerContentSpacing = {
      logoOffset: -(innerRadius * 0.55), // Logo at top of circle (reduced from 0.65 to stay within bounds)
      dowOffset: -(innerRadius * 0.25), // DOW below logo (increased from 0.15 to move up more)
      nasdaqOffset: innerRadius * 0.45, // NASDAQ below DOW (increased from 0.30 for more spacing)
      statusBadgeOffset: innerRadius * 0.7, // Status badge at bottom
    };

    // Debug log positioning
    console.info("[RadialMenu] Center positioning:", {
      innerRadius,
      menuSize,
      centerContentSpacing,
    });

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const defs = svg.append("defs");

    // ====== SVG FILTERS ======

    // PREMIUM GLASS: Enhanced shadow filter (3-layer depth system)
    const normalShadow = defs
      .append("filter")
      .attr("id", "normalShadow")
      .attr("height", "200%")
      .attr("width", "200%")
      .attr("x", "-50%")
      .attr("y", "-50%");
    normalShadow.append("feGaussianBlur").attr("in", "SourceAlpha").attr("stdDeviation", "4").attr("result", "blur1");
    normalShadow.append("feOffset").attr("in", "blur1").attr("dx", "0").attr("dy", "3").attr("result", "dropShadow");
    normalShadow.append("feFlood").attr("flood-color", "#000000").attr("flood-opacity", "0.3").attr("result", "dropColor");
    normalShadow.append("feComposite").attr("in", "dropColor").attr("in2", "dropShadow").attr("operator", "in").attr("result", "shadow1");
    normalShadow.append("feGaussianBlur").attr("in", "SourceAlpha").attr("stdDeviation", "8").attr("result", "blur2");
    normalShadow.append("feFlood").attr("flood-color", "#000000").attr("flood-opacity", "0.15").attr("result", "ambientColor");
    normalShadow.append("feComposite").attr("in", "ambientColor").attr("in2", "blur2").attr("operator", "in").attr("result", "shadow2");
    normalShadow.append("feGaussianBlur").attr("in", "SourceAlpha").attr("stdDeviation", "1").attr("result", "edgeBlur");
    normalShadow.append("feFlood").attr("flood-color", "#ffffff").attr("flood-opacity", "0.08").attr("result", "edgeColor");
    normalShadow.append("feComposite").attr("in", "edgeColor").attr("in2", "edgeBlur").attr("operator", "in").attr("result", "edgeHighlight");
    const normalMerge = normalShadow.append("feMerge");
    normalMerge.append("feMergeNode").attr("in", "shadow2");
    normalMerge.append("feMergeNode").attr("in", "shadow1");
    normalMerge.append("feMergeNode").attr("in", "SourceGraphic");
    normalMerge.append("feMergeNode").attr("in", "edgeHighlight");

    // Hover glow filter
    const hoverGlow = defs
      .append("filter")
      .attr("id", "hoverGlow")
      .attr("height", "200%")
      .attr("width", "200%")
      .attr("x", "-50%")
      .attr("y", "-50%");
    hoverGlow
      .append("feGaussianBlur")
      .attr("in", "SourceAlpha")
      .attr("stdDeviation", "8")
      .attr("result", "blur");
    hoverGlow.append("feFlood").attr("flood-color", "#00ffff").attr("flood-opacity", "0.6");
    hoverGlow
      .append("feComposite")
      .attr("in2", "blur")
      .attr("operator", "in")
      .attr("result", "glow");
    const hoverMerge = hoverGlow.append("feMerge");
    hoverMerge.append("feMergeNode").attr("in", "glow");
    hoverMerge.append("feMergeNode").attr("in", "glow");
    hoverMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Click glow filter
    const clickGlow = defs
      .append("filter")
      .attr("id", "clickGlow")
      .attr("height", "300%")
      .attr("width", "300%")
      .attr("x", "-100%")
      .attr("y", "-100%");
    clickGlow
      .append("feGaussianBlur")
      .attr("in", "SourceAlpha")
      .attr("stdDeviation", "12")
      .attr("result", "blur");
    clickGlow.append("feFlood").attr("flood-color", "#ffffff").attr("flood-opacity", "0.8");
    clickGlow
      .append("feComposite")
      .attr("in2", "blur")
      .attr("operator", "in")
      .attr("result", "glow");
    const clickMerge = clickGlow.append("feMerge");
    clickMerge.append("feMergeNode").attr("in", "glow");
    clickMerge.append("feMergeNode").attr("in", "glow");
    clickMerge.append("feMergeNode").attr("in", "glow");
    clickMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Inner shadow filter
    const innerShadow = defs.append("filter").attr("id", "innerShadow");
    innerShadow
      .append("feGaussianBlur")
      .attr("in", "SourceAlpha")
      .attr("stdDeviation", "3")
      .attr("result", "blur");
    innerShadow
      .append("feOffset")
      .attr("in", "blur")
      .attr("dx", "0")
      .attr("dy", "2")
      .attr("result", "offsetBlur");
    innerShadow
      .append("feFlood")
      .attr("flood-color", "#000000")
      .attr("flood-opacity", "0.5")
      .attr("result", "color");
    innerShadow
      .append("feComposite")
      .attr("in", "color")
      .attr("in2", "offsetBlur")
      .attr("operator", "in")
      .attr("result", "shadow");
    innerShadow
      .append("feComposite")
      .attr("in", "shadow")
      .attr("in2", "SourceAlpha")
      .attr("operator", "in");
    const innerMerge = innerShadow.append("feMerge");
    innerMerge.append("feMergeNode");
    innerMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Sparkles filter
    const sparkles = defs
      .append("filter")
      .attr("id", "sparkles")
      .attr("x", "-50%")
      .attr("y", "-50%")
      .attr("width", "200%")
      .attr("height", "200%");
    sparkles
      .append("feGaussianBlur")
      .attr("in", "SourceAlpha")
      .attr("stdDeviation", "2")
      .attr("result", "blur");
    sparkles
      .append("feSpecularLighting")
      .attr("in", "blur")
      .attr("surfaceScale", "5")
      .attr("specularConstant", "0.75")
      .attr("specularExponent", "20")
      .attr("lighting-color", "#ffffff")
      .attr("result", "spec")
      .append("fePointLight")
      .attr("x", "0")
      .attr("y", "0")
      .attr("z", "100");
    sparkles
      .append("feComposite")
      .attr("in", "spec")
      .attr("in2", "SourceAlpha")
      .attr("operator", "in")
      .attr("result", "specOut");
    const sparkleMerge = sparkles.append("feMerge");
    sparkleMerge.append("feMergeNode").attr("in", "SourceGraphic");
    sparkleMerge.append("feMergeNode").attr("in", "specOut");

    // AI Glow filter for center logo
    const aiGlow = defs
      .append("filter")
      .attr("id", "aiGlow")
      .attr("x", "-50%")
      .attr("y", "-50%")
      .attr("width", "200%")
      .attr("height", "200%");
    aiGlow.append("feGaussianBlur").attr("stdDeviation", "4").attr("result", "coloredBlur");
    const aiMerge = aiGlow.append("feMerge");
    aiMerge.append("feMergeNode").attr("in", "coloredBlur");
    aiMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // ====== GRADIENTS ======

    // Center gradient
    const centerGradient = defs.append("radialGradient").attr("id", "centerGradient");
    centerGradient.append("stop").attr("offset", "0%").attr("stop-color", "#0f172a");
    centerGradient.append("stop").attr("offset", "100%").attr("stop-color", "#1e293b");

    // PREMIUM GLASS: 4-stop depth gradients with subtle shimmer
    workflows.forEach((workflow, i) => {
      const wedgeGradient = defs
        .append("radialGradient")
        .attr("id", `wedgeGradient${i}`)
        .attr("cx", "50%")
        .attr("cy", "50%")
        .attr("r", "50%");

      // 4-stop gradient for depth perception
      const stop1 = wedgeGradient
        .append("stop")
        .attr("offset", "0%")
        .attr("stop-color", workflow.color)
        .attr("stop-opacity", "1");

      wedgeGradient
        .append("stop")
        .attr("offset", "35%")
        .attr("stop-color", workflow.color)
        .attr("stop-opacity", "1");

      wedgeGradient
        .append("stop")
        .attr("offset", "70%")
        .attr("stop-color", workflow.color)
        .attr("stop-opacity", "0.92");

      wedgeGradient
        .append("stop")
        .attr("offset", "100%")
        .attr("stop-color", workflow.color)
        .attr("stop-opacity", "0.85");

      // SUBTLE SHIMMER: 4x slower, smaller range, staggered
      stop1
        .append("animate")
        .attr("attributeName", "stop-opacity")
        .attr("values", "0.92;1.0;0.92")
        .attr("dur", "12s")
        .attr("begin", `${i * 0.8}s`)
        .attr("repeatCount", "indefinite");
    });

    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    const pie = d3
      .pie<Workflow>()
      .value(1)
      .sort(null)
      .startAngle(-Math.PI / 2)
      .padAngle(0.008);

    const arc = d3
      .arc<d3.PieArcDatum<Workflow>>()
      .innerRadius(innerRadius)
      .outerRadius(outerRadius)
      .cornerRadius(3);

    const hoverArc = d3
      .arc<d3.PieArcDatum<Workflow>>()
      .innerRadius(innerRadius)
      .outerRadius(outerRadius + 15)
      .cornerRadius(3);

    const segments = g
      .selectAll(".segment")
      .data(pie(workflows))
      .enter()
      .append("g")
      .attr("class", "segment")
      .style("cursor", "pointer");

    segments
      .append("path")
      .attr("d", arc)
      .attr("fill", (_d, i) => `url(#wedgeGradient${i})`)
      .attr("stroke", "rgba(255, 255, 255, 0.15)")
      .attr("stroke-width", 1.5)
      .style("filter", "url(#normalShadow)")
      .on("mouseenter", function (_event, d) {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("d", hoverArc as (d: unknown) => string)
          .style("filter", "url(#hoverGlow)");
        setHoveredWorkflow(d.data);
        if (onWorkflowHover) onWorkflowHover(d.data);
      })
      .on("mouseleave", function () {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("d", arc as (d: unknown) => string)
          .style("filter", "url(#normalShadow)");
        setHoveredWorkflow(null);
        if (onWorkflowHover) onWorkflowHover(null);
      })
      .on("mousedown", function () {
        d3.select(this).style("filter", "url(#clickGlow)");
      })
      .on("mouseup", function () {
        d3.select(this).style("filter", "url(#hoverGlow)");
      })
      .on("click", (_event, d) => {
        console.info("RadialMenu: Workflow clicked:", d.data.id);
        onWorkflowSelect(d.data.id);
      });

    segments
      .append("text")
      .attr("transform", (d) => {
        const [x, y] = arc.centroid(d);
        return `translate(${x}, ${y})`;
      })
      .attr("text-anchor", "middle")
      .attr("font-size", fontSizes.segmentText)
      .attr("font-weight", "900")
      .attr("font-style", "italic")
      .attr("fill", "white")
      .attr("letter-spacing", "1px")
      .style("text-shadow", "0 4px 12px rgba(0, 0, 0, 0.9), 0 2px 4px rgba(0, 0, 0, 0.8)")
      .style("pointer-events", "none")
      .style("filter", "url(#sparkles)")
      .each(function (d) {
        const lines = d.data.name.split("\n");
        const text = d3.select(this);

        lines.forEach((line, i) => {
          text
            .append("tspan")
            .attr("x", 0)
            .attr("dy", i === 0 ? "-0.5em" : "1.3em")
            .text(line);
        });
      });

    // ====== CENTER CIRCLE ======
    const centerGroup = g
      .append("g")
      .style("cursor", "pointer")
      .on("click", () => onWorkflowSelect(""));

    centerGroup
      .append("circle")
      .attr("r", innerRadius - 15)
      .attr("fill", "url(#centerGradient)")
      .attr("stroke", "#45f0c0")
      .attr("stroke-width", 3)
      .style("filter", "url(#innerShadow)");

    // Animated ring around center
    centerGroup
      .append("circle")
      .attr("r", innerRadius - 15)
      .attr("fill", "none")
      .attr("stroke", "#45f0c0")
      .attr("stroke-width", 2)
      .attr("opacity", 0.3)
      .append("animate")
      .attr("attributeName", "opacity")
      .attr("values", "0.3;0.8;0.3")
      .attr("dur", "2s")
      .attr("repeatCount", "indefinite");

    // ====== CENTER LOGO (PaiiD) ======
    // Note: Logo rendered as HTML overlay for CSS animation compatibility

    // ====== MARKET DATA ======
    const dow = centerGroup
      .append("g")
      .attr("transform", `translate(0, ${centerContentSpacing.dowOffset})`);

    dow
      .append("text")
      .attr("text-anchor", "middle")
      .attr("font-size", fontSizes.marketLabel)
      .attr("font-weight", "800")
      .attr("fill", "#cbd5e1")
      .attr("letter-spacing", "2px")
      .style("pointer-events", "none")
      .text("DOW JONES INDUSTRIAL");

    dow
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "14") // Reduced from 20 for tighter spacing
      .attr("font-size", fontSizes.marketValue)
      .attr("font-weight", "900")
      .attr("fill", "#f1f5f9")
      .style("text-shadow", "0 2px 6px rgba(0, 0, 0, 0.6)")
      .style("pointer-events", "none")
      .text(
        isMarketDataLoading && marketData.dow.value === 0
          ? "Loading..."
          : marketData.dow.value.toLocaleString("en-US", { minimumFractionDigits: 2 })
      );

    const dowChange = dow
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "26") // Reduced from 38 for tighter spacing
      .attr("font-size", fontSizes.marketChange)
      .attr("font-weight", "800")
      .attr("fill", marketData.dow.change >= 0 ? "#45f0c0" : "#ef4444")
      .style(
        "text-shadow",
        "0 0 10px " +
          (marketData.dow.change >= 0 ? "rgba(69, 240, 192, 0.5)" : "rgba(239, 68, 68, 0.5)")
      )
      .style("pointer-events", "none")
      .text(
        `${marketData.dow.change >= 0 ? "▲" : "▼"} ${Math.abs(marketData.dow.change).toFixed(2)}%`
      );

    // Animate market data
    dowChange
      .transition()
      .duration(1000)
      .style("opacity", 0.7)
      .transition()
      .duration(1000)
      .style("opacity", 1)
      .on("end", function repeat() {
        d3.select(this)
          .transition()
          .duration(1000)
          .style("opacity", 0.7)
          .transition()
          .duration(1000)
          .style("opacity", 1)
          .on("end", repeat);
      });

    const nasdaqGroup = centerGroup
      .append("g")
      .attr("transform", `translate(0, ${centerContentSpacing.nasdaqOffset})`);

    nasdaqGroup
      .append("text")
      .attr("text-anchor", "middle")
      .attr("font-size", fontSizes.marketLabel)
      .attr("font-weight", "800")
      .attr("fill", "#cbd5e1")
      .attr("letter-spacing", "2px")
      .style("pointer-events", "none")
      .text("NASDAQ COMPOSITE");

    nasdaqGroup
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "14") // Reduced from 20 for tighter spacing
      .attr("font-size", fontSizes.marketValue)
      .attr("font-weight", "900")
      .attr("fill", "#f1f5f9")
      .style("text-shadow", "0 2px 6px rgba(0, 0, 0, 0.6)")
      .style("pointer-events", "none")
      .text(
        isMarketDataLoading && marketData.nasdaq.value === 0
          ? "Loading..."
          : marketData.nasdaq.value.toLocaleString("en-US", { minimumFractionDigits: 2 })
      );

    const nasdaqChange = nasdaqGroup
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "26") // Reduced from 38 for tighter spacing
      .attr("font-size", fontSizes.marketChange)
      .attr("font-weight", "800")
      .attr("fill", marketData.nasdaq.change >= 0 ? "#45f0c0" : "#ef4444")
      .style(
        "text-shadow",
        "0 0 10px " +
          (marketData.nasdaq.change >= 0 ? "rgba(69, 240, 192, 0.5)" : "rgba(239, 68, 68, 0.5)")
      )
      .style("pointer-events", "none")
      .text(
        `${marketData.nasdaq.change >= 0 ? "▲" : "▼"} ${Math.abs(marketData.nasdaq.change).toFixed(2)}%`
      );

    // Animate market data
    nasdaqChange
      .transition()
      .duration(1000)
      .delay(500)
      .style("opacity", 0.7)
      .transition()
      .duration(1000)
      .style("opacity", 1)
      .on("end", function repeat() {
        d3.select(this)
          .transition()
          .duration(1000)
          .style("opacity", 0.7)
          .transition()
          .duration(1000)
          .style("opacity", 1)
          .on("end", repeat);
      });

    // ====== FORCE FIELD CONFIDENCE ======
    const forceFieldGroup = centerGroup
      .append("g")
      .attr("transform", `translate(0, ${-centerContentSpacing.dowOffset - 35})`);

    forceFieldGroup
      .append("text")
      .attr("text-anchor", "middle")
      .attr("font-size", fontSizes.marketLabel)
      .attr("font-weight", "800")
      .attr("fill", "#cbd5e1")
      .attr("letter-spacing", "1.5px")
      .style("pointer-events", "none")
      .text("FORCE FIELD");

    const confidenceColor =
      forceFieldConfidence >= 80
        ? "#45f0c0"
        : forceFieldConfidence >= 60
          ? "#fbbf24"
          : forceFieldConfidence >= 40
            ? "#fb923c"
            : "#ef4444";

    forceFieldGroup
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dy", "14")
      .attr("font-size", `${parseInt(fontSizes.marketValue) * 1.3}px`)
      .attr("font-weight", "900")
      .attr("fill", confidenceColor)
      .style("text-shadow", `0 0 15px ${confidenceColor}80, 0 2px 8px rgba(0, 0, 0, 0.8)`)
      .style("pointer-events", "none")
      .text(`${forceFieldConfidence}%`);
  }, [
    menuSize,
    fontSizes,
    onWorkflowSelect,
    onWorkflowHover,
    isMarketDataLoading,
    marketData.dow.value,
    marketData.dow.change,
    marketData.nasdaq.value,
    marketData.nasdaq.change,
    forceFieldConfidence,
    centerContentSpacing,
  ]); // Re-render when menu size or loading state changes

  // Separate effect for market data updates - only update text when data changes
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);

    // Update DOW value
    svg
      .selectAll("text")
      .filter(function () {
        return (
          d3
            .select(this as SVGTextElement)
            .text()
            .includes(".") && d3.select(this as SVGTextElement).attr("dy") === "20"
        );
      })
      .each(function () {
        const element = this as SVGTextElement;
        const text = d3.select(element);
        const parentNode = element.parentNode as SVGGElement;
        const transform = d3.select(parentNode).attr("transform");
        if (transform && transform.includes("-15")) {
          // This is the DOW value text
          text.text(marketData.dow.value.toLocaleString("en-US", { minimumFractionDigits: 2 }));
        } else if (transform && transform.includes("45")) {
          // This is the NASDAQ value text
          text.text(marketData.nasdaq.value.toLocaleString("en-US", { minimumFractionDigits: 2 }));
        }
      });

    // Update change percentages
    svg
      .selectAll("text")
      .filter(function () {
        return d3.select(this as SVGTextElement).attr("dy") === "38";
      })
      .each(function () {
        const element = this as SVGTextElement;
        const text = d3.select(element);
        const parentNode = element.parentNode as SVGGElement;
        const transform = d3.select(parentNode).attr("transform");
        if (transform && transform.includes("-15")) {
          // DOW change
          text
            .attr("fill", marketData.dow.change >= 0 ? "#45f0c0" : "#ef4444")
            .style(
              "text-shadow",
              "0 0 10px " +
                (marketData.dow.change >= 0 ? "rgba(69, 240, 192, 0.5)" : "rgba(239, 68, 68, 0.5)")
            )
            .text(
              `${marketData.dow.change >= 0 ? "▲" : "▼"} ${Math.abs(marketData.dow.change).toFixed(2)}%`
            );
        } else if (transform && transform.includes("45")) {
          // NASDAQ change
          text
            .attr("fill", marketData.nasdaq.change >= 0 ? "#45f0c0" : "#ef4444")
            .style(
              "text-shadow",
              "0 0 10px " +
                (marketData.nasdaq.change >= 0
                  ? "rgba(69, 240, 192, 0.5)"
                  : "rgba(239, 68, 68, 0.5)")
            )
            .text(
              `${marketData.nasdaq.change >= 0 ? "▲" : "▼"} ${Math.abs(marketData.nasdaq.change).toFixed(2)}%`
            );
        }
      });
  }, [marketData]);

  // Separate effect for selectedWorkflow updates - only update selected wedge styling
  useEffect(() => {
    if (!svgRef.current || !selectedWorkflow) return;

    // Update only the selected wedge styling without full re-render
    d3.select(svgRef.current)
      .selectAll(".segment path")
      .style("filter", function (this: SVGPathElement, d: { data: { id: string } }) {
        return d.data.id === selectedWorkflow ? "url(#clickGlow)" : "url(#normalShadow)";
      });
  }, [selectedWorkflow]);

  return (
    <div
      ref={containerRef}
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
        {marketStatus && (
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
        )}
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
