import * as d3 from "d3";
import React, { useEffect, useRef, useState } from "react";
import { useIsMobile } from "../hooks/useBreakpoint";
import EnhancedCard from "./ui/EnhancedCard";
import StatusIndicator from "./ui/StatusIndicator";

export interface Workflow {
  id: string;
  name: string;
  color: string;
  icon: string;
  description: string;
  status?: "active" | "inactive" | "loading";
}

interface EnhancedRadialMenuProps {
  onWorkflowSelect: (workflowId: string) => void;
  onWorkflowHover?: (workflow: Workflow | null) => void;
  selectedWorkflow?: string;
  compact?: boolean;
}

export const enhancedWorkflows: Workflow[] = [
  {
    id: "morning-routine",
    name: "MORNING\nROUTINE",
    color: "#00ACC1",
    icon: "🌅",
    description: "Start your day with market analysis, portfolio review, and trading alerts.",
    status: "active",
  },
  {
    id: "news-review",
    name: "NEWS\nREVIEW",
    color: "#7E57C2",
    icon: "📰",
    description: "Real-time market news aggregation with AI-powered sentiment analysis.",
    status: "active",
  },
  {
    id: "proposals",
    name: "AI\nRECS",
    color: "#0097A7",
    icon: "🤖",
    description: "Review AI-generated trading recommendations and strategy proposals.",
    status: "loading",
  },
  {
    id: "active-positions",
    name: "ACTIVE\nPOSITIONS",
    color: "#00C851",
    icon: "📊",
    description: "Monitor your current positions, P&L, and portfolio performance in real-time.",
    status: "active",
  },
  {
    id: "execute",
    name: "EXECUTE\nTRADE",
    color: "#FF6B35",
    icon: "⚡",
    description: "Execute trades with advanced order types and risk management.",
    status: "active",
  },
  {
    id: "proposal-review",
    name: "RISK\nCALC",
    color: "#FF3D71",
    icon: "🛡️",
    description: "Calculate risk metrics and review trading proposals before execution.",
    status: "inactive",
  },
  {
    id: "research",
    name: "RESEARCH",
    color: "#9C27B0",
    icon: "🔍",
    description: "Deep dive into market research, technical analysis, and fundamental data.",
    status: "active",
  },
  {
    id: "settings",
    name: "SETTINGS",
    color: "#607D8B",
    icon: "⚙️",
    description: "Configure your trading preferences, API keys, and system settings.",
    status: "active",
  },
];

const EnhancedRadialMenu: React.FC<EnhancedRadialMenuProps> = ({
  onWorkflowSelect,
  onWorkflowHover,
  selectedWorkflow,
  compact = false,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const isMobile = useIsMobile();
  const [dimensions, setDimensions] = useState({ width: 400, height: 400 });
  const [hoveredWorkflow, setHoveredWorkflow] = useState<Workflow | null>(null);

  // Responsive sizing
  useEffect(() => {
    const updateDimensions = () => {
      const size = isMobile ? 300 : compact ? 350 : 400;
      setDimensions({ width: size, height: size });
    };

    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, [isMobile, compact]);

  // Create radial menu with enhanced animations
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const { width, height } = dimensions;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.35;
    const segmentAngle = (2 * Math.PI) / enhancedWorkflows.length;

    // Create gradient definitions
    const defs = svg.append("defs");

    enhancedWorkflows.forEach((workflow, _index) => {
      const gradient = defs
        .append("linearGradient")
        .attr("id", `gradient-${workflow.id}`)
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "100%")
        .attr("y2", "100%");

      gradient
        .append("stop")
        .attr("offset", "0%")
        .attr("stop-color", workflow.color)
        .attr("stop-opacity", 0.8);

      gradient
        .append("stop")
        .attr("offset", "100%")
        .attr("stop-color", workflow.color)
        .attr("stop-opacity", 0.4);
    });

    // Create segments
    const segments = svg.append("g").attr("class", "segments");

    enhancedWorkflows.forEach((workflow, index) => {
      const startAngle = index * segmentAngle - Math.PI / 2;
      const endAngle = startAngle + segmentAngle;

      const isSelected = selectedWorkflow === workflow.id;
      const isHovered = hoveredWorkflow?.id === workflow.id;

      const segmentRadius = isSelected ? radius + 20 : isHovered ? radius + 10 : radius;
      const opacity = isSelected ? 0.9 : isHovered ? 0.7 : 0.5;

      // Create arc path
      const arc = d3
        .arc<d3.DefaultArcObject>()
        .innerRadius(radius * 0.3)
        .outerRadius(segmentRadius)
        .startAngle(startAngle)
        .endAngle(endAngle);

      const segment = segments
        .append("g")
        .attr("class", `segment segment-${workflow.id}`)
        .attr("transform", `translate(${centerX}, ${centerY})`);

      // Background arc
      segment
        .append("path")
        .attr("d", arc({}))
        .attr("fill", `url(#gradient-${workflow.id})`)
        .attr("opacity", opacity)
        .attr("stroke", workflow.color)
        .attr("stroke-width", isSelected ? 3 : 1)
        .attr("stroke-opacity", 0.8)
        .style("cursor", "pointer")
        .style("filter", isSelected ? "drop-shadow(0 0 10px rgba(255,255,255,0.3))" : "none")
        .on("click", () => onWorkflowSelect(workflow.id))
        .on("mouseenter", () => {
          setHoveredWorkflow(workflow);
          onWorkflowHover?.(workflow);
        })
        .on("mouseleave", () => {
          setHoveredWorkflow(null);
          onWorkflowHover?.(null);
        });

      // Icon
      const iconAngle = startAngle + segmentAngle / 2;
      const iconRadius = radius * 0.65;
      const iconX = Math.cos(iconAngle) * iconRadius;
      const iconY = Math.sin(iconAngle) * iconRadius;

      segment
        .append("text")
        .attr("x", iconX)
        .attr("y", iconY)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("font-size", "24px")
        .attr("font-family", "system-ui")
        .text(workflow.icon)
        .style("pointer-events", "none")
        .style("filter", isSelected ? "drop-shadow(0 0 5px rgba(255,255,255,0.5))" : "none");

      // Label
      const labelAngle = startAngle + segmentAngle / 2;
      const labelRadius = radius * 0.85;
      const labelX = Math.cos(labelAngle) * labelRadius;
      const labelY = Math.sin(labelAngle) * labelRadius;

      segment
        .append("text")
        .attr("x", labelX)
        .attr("y", labelY)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("font-size", "10px")
        .attr("font-weight", "bold")
        .attr("font-family", "system-ui")
        .attr("fill", "white")
        .text(workflow.name)
        .style("pointer-events", "none")
        .style("filter", isSelected ? "drop-shadow(0 0 3px rgba(0,0,0,0.8))" : "none");

      // Status indicator
      if (workflow.status === "loading") {
        const statusAngle = startAngle + segmentAngle / 2;
        const statusRadius = radius * 0.45;
        const statusX = Math.cos(statusAngle) * statusRadius;
        const statusY = Math.sin(statusAngle) * statusRadius;

        segment
          .append("circle")
          .attr("cx", statusX)
          .attr("cy", statusY)
          .attr("r", 4)
          .attr("fill", "#3B82F6")
          .attr("opacity", 0.8)
          .style("animation", "pulse 2s infinite");
      }
    });

    // Center circle
    const centerCircle = svg
      .append("g")
      .attr("class", "center")
      .attr("transform", `translate(${centerX}, ${centerY})`);

    centerCircle
      .append("circle")
      .attr("r", radius * 0.25)
      .attr("fill", "rgba(30, 41, 59, 0.8)")
      .attr("stroke", "rgba(148, 163, 184, 0.3)")
      .attr("stroke-width", 1);

    centerCircle
      .append("text")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .attr("font-family", "system-ui")
      .attr("fill", "white")
      .text("PaiiD")
      .style("filter", "drop-shadow(0 0 3px rgba(0,0,0,0.8))");
  }, [
    dimensions,
    selectedWorkflow,
    hoveredWorkflow,
    onWorkflowSelect,
    onWorkflowHover,
    isMobile,
    compact,
  ]);

  return (
    <div className="relative">
      <svg
        ref={svgRef}
        width={dimensions.width}
        height={dimensions.height}
        className="transition-all duration-300 ease-in-out"
        style={{ filter: "drop-shadow(0 4px 20px rgba(0,0,0,0.3))" }}
      />

      {/* Status overlay */}
      {hoveredWorkflow && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <EnhancedCard variant="glass" size="sm" className="opacity-90">
            <div className="flex items-center gap-2">
              <StatusIndicator
                status={hoveredWorkflow.status === "loading" ? "loading" : "online"}
                size="sm"
              />
              <span className="text-xs text-slate-300">
                {hoveredWorkflow.status === "loading" ? "Loading..." : "Ready"}
              </span>
            </div>
          </EnhancedCard>
        </div>
      )}
    </div>
  );
};

export default EnhancedRadialMenu;
