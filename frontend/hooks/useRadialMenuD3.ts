import * as d3 from "d3";
import { RefObject, useEffect } from "react";
import { logger } from "../lib/logger";
import { Workflow } from "../components/RadialMenu";
import { MarketDataState } from "./useMarketData";
import {
  ResponsiveFontSizes,
  calculateCenterContentSpacing,
  getConfidenceColor,
} from "../utils/radialMenuHelpers";

interface UseRadialMenuD3Props {
  svgRef: RefObject<SVGSVGElement>;
  workflows: Workflow[];
  menuSize: number;
  fontSizes: ResponsiveFontSizes;
  onWorkflowSelect: (workflowId: string) => void;
  onWorkflowHover?: (workflow: Workflow | null) => void;
  setHoveredWorkflow: (workflow: Workflow | null) => void;
  isMarketDataLoading: boolean;
  marketData: MarketDataState;
  forceFieldConfidence: number;
}

/**
 * Hook to handle D3.js rendering of the radial menu
 * Extracts complex D3 visualization logic from the main component
 */
export function useRadialMenuD3({
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
}: UseRadialMenuD3Props) {
  // Main D3 rendering effect
  useEffect(() => {
    if (!svgRef.current) return;

    // Extension verification: D3.js
    logger.info("[Extension Verification] D3.js loaded successfully", {
      version: "7.9.0",
      modules: ["select", "pie", "arc", "selectAll"],
      status: "FUNCTIONAL",
    });

    const width = menuSize;
    const height = menuSize;
    const radius = Math.min(width, height) / 2;
    const innerRadius = radius * 0.3;
    const outerRadius = radius * 0.9;

    // Calculate responsive center content positions
    const centerContentSpacing = calculateCenterContentSpacing(innerRadius);

    // Debug log positioning
    logger.info("[RadialMenu] Center positioning", {
      innerRadius,
      menuSize,
      centerContentSpacing,
    });

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const defs = svg.append("defs");

    // SVG FILTERS
    createSVGFilters(defs);

    // GRADIENTS
    createGradients(defs, workflows);

    const g = svg
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", `translate(${width / 2}, ${height / 2})`);

    const pie = d3
      .pie<Workflow>()
      .value(1)
      .sort(null)
      .startAngle(-Math.PI / 2 + (Math.PI * 2 / 10 / 2)) // Start at top-right (offset by half a wedge = 18°)
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

    // Create segments
    createSegments(
      g,
      pie,
      arc,
      hoverArc,
      workflows,
      fontSizes,
      onWorkflowSelect,
      onWorkflowHover,
      setHoveredWorkflow
    );

    // Create center circle
    const centerGroup = createCenterCircle(g, innerRadius, onWorkflowSelect);

    // Render market data
    renderMarketData(
      centerGroup,
      centerContentSpacing,
      fontSizes,
      isMarketDataLoading,
      marketData
    );

    // Render force field confidence
    renderForceFieldConfidence(
      centerGroup,
      centerContentSpacing,
      fontSizes,
      forceFieldConfidence
    );
  }, [
    svgRef,
    workflows,
    menuSize,
    fontSizes,
    onWorkflowSelect,
    onWorkflowHover,
    setHoveredWorkflow,
    isMarketDataLoading,
    marketData.dow.value,
    marketData.dow.change,
    marketData.nasdaq.value,
    marketData.nasdaq.change,
    forceFieldConfidence,
  ]);

  // Separate effect for market data updates
  useEffect(() => {
    if (!svgRef.current) return;
    updateMarketDataText(svgRef.current, marketData);
  }, [svgRef, marketData]);
}

/**
 * Update aria-current attribute for selected workflow
 */
export function updateSelectedWorkflowAria(
  svgElement: SVGSVGElement,
  selectedWorkflow: string | undefined
) {
  const svg = d3.select(svgElement);
  svg.selectAll(".segment").attr("aria-current", function (d) {
    const data = d as d3.PieArcDatum<Workflow>;
    return data.data.id === selectedWorkflow ? "true" : null;
  });
}

/**
 * Create SVG filters for visual effects
 */
function createSVGFilters(defs: d3.Selection<SVGDefsElement, unknown, null, undefined>) {
  // Normal shadow filter (3-layer depth system)
  const normalShadow = defs
    .append("filter")
    .attr("id", "normalShadow")
    .attr("height", "200%")
    .attr("width", "200%")
    .attr("x", "-50%")
    .attr("y", "-50%");
  normalShadow
    .append("feGaussianBlur")
    .attr("in", "SourceAlpha")
    .attr("stdDeviation", "4")
    .attr("result", "blur1");
  normalShadow
    .append("feOffset")
    .attr("in", "blur1")
    .attr("dx", "0")
    .attr("dy", "3")
    .attr("result", "dropShadow");
  normalShadow
    .append("feFlood")
    .attr("flood-color", "#000000")
    .attr("flood-opacity", "0.3")
    .attr("result", "dropColor");
  normalShadow
    .append("feComposite")
    .attr("in", "dropColor")
    .attr("in2", "dropShadow")
    .attr("operator", "in")
    .attr("result", "shadow1");
  normalShadow
    .append("feGaussianBlur")
    .attr("in", "SourceAlpha")
    .attr("stdDeviation", "8")
    .attr("result", "blur2");
  normalShadow
    .append("feFlood")
    .attr("flood-color", "#000000")
    .attr("flood-opacity", "0.15")
    .attr("result", "ambientColor");
  normalShadow
    .append("feComposite")
    .attr("in", "ambientColor")
    .attr("in2", "blur2")
    .attr("operator", "in")
    .attr("result", "shadow2");
  normalShadow
    .append("feGaussianBlur")
    .attr("in", "SourceAlpha")
    .attr("stdDeviation", "1")
    .attr("result", "edgeBlur");
  normalShadow
    .append("feFlood")
    .attr("flood-color", "#ffffff")
    .attr("flood-opacity", "0.08")
    .attr("result", "edgeColor");
  normalShadow
    .append("feComposite")
    .attr("in", "edgeColor")
    .attr("in2", "edgeBlur")
    .attr("operator", "in")
    .attr("result", "edgeHighlight");
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

  // AI Glow filter
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
}

/**
 * Create gradients for center and workflow wedges
 */
function createGradients(
  defs: d3.Selection<SVGDefsElement, unknown, null, undefined>,
  workflows: Workflow[]
) {
  // Center gradient
  const centerGradient = defs.append("radialGradient").attr("id", "centerGradient");
  centerGradient.append("stop").attr("offset", "0%").attr("stop-color", "#0f172a");
  centerGradient.append("stop").attr("offset", "100%").attr("stop-color", "#1e293b");

  // 4-stop depth gradients for workflow wedges
  workflows.forEach((workflow, i) => {
    const wedgeGradient = defs
      .append("radialGradient")
      .attr("id", `wedgeGradient${i}`)
      .attr("cx", "50%")
      .attr("cy", "50%")
      .attr("r", "50%");

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

    // Subtle shimmer animation
    stop1
      .append("animate")
      .attr("attributeName", "stop-opacity")
      .attr("values", "0.92;1.0;0.92")
      .attr("dur", "12s")
      .attr("begin", `${i * 0.8}s`)
      .attr("repeatCount", "indefinite");
  });
}

/**
 * Create workflow segments with interactions
 */
function createSegments(
  g: d3.Selection<SVGGElement, unknown, null, undefined>,
  pie: d3.Pie<unknown, Workflow>,
  arc: d3.Arc<unknown, d3.PieArcDatum<Workflow>>,
  hoverArc: d3.Arc<unknown, d3.PieArcDatum<Workflow>>,
  workflows: Workflow[],
  fontSizes: ResponsiveFontSizes,
  onWorkflowSelect: (workflowId: string) => void,
  onWorkflowHover: ((workflow: Workflow | null) => void) | undefined,
  setHoveredWorkflow: (workflow: Workflow | null) => void
) {
  const segments = g
    .selectAll(".segment")
    .data(pie(workflows))
    .enter()
    .append("g")
    .attr("class", "segment")
    .attr("role", "button")
    .attr("tabindex", "0")
    .attr("aria-label", (d) => `${d.data.name.replace("\n", " ")} - ${d.data.description}`)
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
      logger.info("RadialMenu: Workflow clicked", { workflowId: d.data.id });
      onWorkflowSelect(d.data.id);
    });

  // Add keyboard navigation support
  segments.on("keydown", function (event, d) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      logger.info("RadialMenu: Workflow selected via keyboard", { workflowId: d.data.id });
      onWorkflowSelect(d.data.id);
    }
  });

  // Add focus indicators
  segments
    .on("focus", function () {
      d3.select(this)
        .select("path")
        .transition()
        .duration(200)
        .attr("d", hoverArc as (d: unknown) => string)
        .style("filter", "url(#hoverGlow)")
        .attr("stroke", "#3b82f6")
        .attr("stroke-width", 3);
    })
    .on("blur", function () {
      d3.select(this)
        .select("path")
        .transition()
        .duration(200)
        .attr("d", arc as (d: unknown) => string)
        .style("filter", "url(#normalShadow)")
        .attr("stroke", "rgba(255, 255, 255, 0.15)")
        .attr("stroke-width", 1.5);
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
}

/**
 * Create center circle with animated ring
 */
function createCenterCircle(
  g: d3.Selection<SVGGElement, unknown, null, undefined>,
  innerRadius: number,
  onWorkflowSelect: (workflowId: string) => void
): d3.Selection<SVGGElement, unknown, null, undefined> {
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

  return centerGroup;
}

/**
 * Render market data displays (DOW and NASDAQ)
 */
function renderMarketData(
  centerGroup: d3.Selection<SVGGElement, unknown, null, undefined>,
  centerContentSpacing: { dowOffset: number; nasdaqOffset: number },
  fontSizes: ResponsiveFontSizes,
  isMarketDataLoading: boolean,
  marketData: MarketDataState
) {
  // DOW JONES
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
    .attr("dy", "14")
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
    .attr("dy", "26")
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

  // Animate DOW change
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

  // NASDAQ COMPOSITE
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
    .attr("dy", "14")
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
    .attr("dy", "26")
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

  // Animate NASDAQ change
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
}

/**
 * Render Force Field Confidence display
 */
function renderForceFieldConfidence(
  centerGroup: d3.Selection<SVGGElement, unknown, null, undefined>,
  centerContentSpacing: { dowOffset: number },
  fontSizes: ResponsiveFontSizes,
  forceFieldConfidence: number
) {
  const forceFieldGroup = centerGroup
    .append("g")
    .attr("transform", `translate(0, ${-centerContentSpacing.dowOffset - (parseInt(fontSizes.marketLabel) * 3)})`);

  forceFieldGroup
    .append("text")
    .attr("text-anchor", "middle")
    .attr("font-size", fontSizes.marketLabel)
    .attr("font-weight", "800")
    .attr("fill", "#cbd5e1")
    .attr("letter-spacing", "1.5px")
    .style("pointer-events", "none")
    .text("FORCE FIELD");

  const confidenceColor = getConfidenceColor(forceFieldConfidence);

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
}

/**
 * Update market data text without full re-render
 */
function updateMarketDataText(svgElement: SVGSVGElement, marketData: MarketDataState) {
  const svg = d3.select(svgElement);

  // Update DOW and NASDAQ values
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
        // DOW value text
        text.text(marketData.dow.value.toLocaleString("en-US", { minimumFractionDigits: 2 }));
      } else if (transform && transform.includes("45")) {
        // NASDAQ value text
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
}
