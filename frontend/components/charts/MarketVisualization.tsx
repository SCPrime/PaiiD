import * as d3 from "d3";
import React, { useEffect, useRef, useState } from "react";
import { useWebSocket } from "../../hooks/useWebSocket";
import AnimatedCounter from "../ui/AnimatedCounter";
import EnhancedCard from "../ui/EnhancedCard";
import StatusIndicator from "../ui/StatusIndicator";

interface MarketVisualizationProps {
  userId: string;
  className?: string;
  visualizationType?: "treemap" | "bubble" | "sector" | "correlation";
  symbols?: string[];
  showLegend?: boolean;
  showControls?: boolean;
}

interface MarketData {
  symbol: string;
  value: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  sector: string;
  color: string;
}

const MarketVisualization: React.FC<MarketVisualizationProps> = ({
  userId,
  className,
  visualizationType = "treemap",
  symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX", "AMD", "INTC"],
  showLegend = true,
  showControls = true,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [_isLoading, _setIsLoading] = useState(false);
  const [_error, _setError] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState(visualizationType);

  const { isConnected } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    userId,
    autoConnect: true,
  });

  // Generate mock market data
  useEffect(() => {
    const generateMockData = (): MarketData[] => {
      const sectors = [
        { name: "Technology", color: "#3b82f6" },
        { name: "Healthcare", color: "#10b981" },
        { name: "Finance", color: "#f59e0b" },
        { name: "Energy", color: "#ef4444" },
        { name: "Consumer", color: "#8b5cf6" },
        { name: "Industrial", color: "#06b6d4" },
      ];

      return symbols.map((symbol) => {
        const change = (Math.random() - 0.5) * 20;
        const baseValue = 50 + Math.random() * 300;
        const volume = Math.floor(Math.random() * 50000000) + 1000000;
        const marketCap = Math.floor(Math.random() * 2000000000000) + 10000000000;
        const sector = sectors[Math.floor(Math.random() * sectors.length)];

        return {
          symbol,
          value: Number(baseValue.toFixed(2)),
          change: Number(change.toFixed(2)),
          changePercent: Number(((change / baseValue) * 100).toFixed(2)),
          volume,
          marketCap,
          sector: sector.name,
          color: sector.color,
        };
      });
    };

    setMarketData(generateMockData());
  }, [symbols]);

  // Render treemap visualization
  const renderTreemap = () => {
    if (!svgRef.current || marketData.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 20, bottom: 20, left: 20 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const g = svg
      .attr("width", 800)
      .attr("height", 400)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create treemap layout
    const treemap = d3.treemap<MarketData>().size([width, height]).padding(2).round(true);

    const root = d3
      .hierarchy({ children: marketData })
      .sum((d) => d.marketCap)
      .sort((a, b) => (b.value || 0) - (a.value || 0));

    treemap(root);

    // Create cells
    const cells = g
      .selectAll(".treemap-cell")
      .data(root.leaves())
      .enter()
      .append("g")
      .attr("class", "treemap-cell")
      .attr("transform", (d) => `translate(${d.x0},${d.y0})`);

    // Add rectangles
    cells
      .append("rect")
      .attr("width", (d) => d.x1 - d.x0)
      .attr("height", (d) => d.y1 - d.y0)
      .attr("fill", (d) => d.data.color)
      .attr("stroke", "#374151")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")
      .on("mouseover", function () {
        d3.select(this).attr("stroke", "#60a5fa").attr("stroke-width", 2);
      })
      .on("mouseout", function () {
        d3.select(this).attr("stroke", "#374151").attr("stroke-width", 1);
      });

    // Add text labels
    cells
      .append("text")
      .attr("x", (d) => (d.x1 - d.x0) / 2)
      .attr("y", (d) => (d.y1 - d.y0) / 2 - 5)
      .attr("text-anchor", "middle")
      .attr("font-size", (d) => Math.min(12, (d.x1 - d.x0) / 6))
      .attr("font-weight", "bold")
      .attr("fill", "white")
      .text((d) => d.data.symbol);

    cells
      .append("text")
      .attr("x", (d) => (d.x1 - d.x0) / 2)
      .attr("y", (d) => (d.y1 - d.y0) / 2 + 10)
      .attr("text-anchor", "middle")
      .attr("font-size", (d) => Math.min(10, (d.x1 - d.x0) / 8))
      .attr("fill", "white")
      .text((d) => `${d.data.changePercent >= 0 ? "+" : ""}${d.data.changePercent.toFixed(1)}%`);
  };

  // Render bubble chart
  const renderBubbleChart = () => {
    if (!svgRef.current || marketData.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 20, bottom: 40, left: 60 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const g = svg
      .attr("width", 800)
      .attr("height", 400)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const xScale = d3
      .scaleLinear()
      .domain(d3.extent(marketData, (d) => d.changePercent) as [number, number])
      .range([0, width]);

    const yScale = d3
      .scaleLinear()
      .domain(d3.extent(marketData, (d) => d.volume) as [number, number])
      .range([height, 0]);

    const rScale = d3
      .scaleSqrt()
      .domain(d3.extent(marketData, (d) => d.marketCap) as [number, number])
      .range([5, 30]);

    // Add bubbles
    g.selectAll(".bubble")
      .data(marketData)
      .enter()
      .append("circle")
      .attr("class", "bubble")
      .attr("cx", (d) => xScale(d.changePercent))
      .attr("cy", (d) => yScale(d.volume))
      .attr("r", (d) => rScale(d.marketCap))
      .attr("fill", (d) => d.color)
      .attr("stroke", "#374151")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")
      .on("mouseover", function () {
        d3.select(this).attr("stroke", "#60a5fa").attr("stroke-width", 2);
      })
      .on("mouseout", function () {
        d3.select(this).attr("stroke", "#374151").attr("stroke-width", 1);
      });

    // Add labels
    g.selectAll(".bubble-label")
      .data(marketData)
      .enter()
      .append("text")
      .attr("class", "bubble-label")
      .attr("x", (d) => xScale(d.changePercent))
      .attr("y", (d) => yScale(d.volume))
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-size", "10px")
      .attr("font-weight", "bold")
      .attr("fill", "white")
      .text((d) => d.symbol);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat(d3.format(".1f")));

    g.append("g").call(d3.axisLeft(yScale).tickFormat(d3.format(".0s")));

    // Add axis labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - height / 2)
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .attr("fill", "white")
      .text("Volume");

    g.append("text")
      .attr("transform", `translate(${width / 2}, ${height + margin.bottom - 5})`)
      .style("text-anchor", "middle")
      .attr("fill", "white")
      .text("Change %");
  };

  // Render visualization based on type
  useEffect(() => {
    if (selectedType === "treemap") {
      renderTreemap();
    } else if (selectedType === "bubble") {
      renderBubbleChart();
    }
  }, [marketData, selectedType]);

  const getPerformanceColor = (change: number) => {
    if (change > 5) return "text-green-400";
    if (change > 0) return "text-green-300";
    if (change > -5) return "text-yellow-400";
    return "text-red-400";
  };

  if (error) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-red-400">
          <StatusIndicator status="error" size="sm" />
          <p className="mt-2">Visualization Error: {error}</p>
        </div>
      </EnhancedCard>
    );
  }

  if (isLoading) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Loading market data...</p>
        </div>
      </EnhancedCard>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-white font-bold text-xl">Market Visualization</h3>
          <StatusIndicator status={isConnected ? "online" : "offline"} size="sm" />
        </div>

        {showControls && (
          <div className="flex items-center gap-2">
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as typeof visualizationType)}
              className="bg-slate-700 text-white border border-slate-600 rounded-lg px-3 py-1 text-sm"
            >
              <option value="treemap">Treemap</option>
              <option value="bubble">Bubble Chart</option>
            </select>
          </div>
        )}
      </div>

      {/* Market Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <EnhancedCard variant="glass" size="sm">
          <div className="text-center">
            <div className="text-slate-400 text-sm">Total Market Cap</div>
            <AnimatedCounter
              value={marketData.reduce((sum, d) => sum + d.marketCap, 0) / 1000000000}
              prefix="$"
              suffix="B"
              decimals={1}
              color="neutral"
              className="text-lg font-semibold"
            />
          </div>
        </EnhancedCard>

        <EnhancedCard variant="glass" size="sm">
          <div className="text-center">
            <div className="text-slate-400 text-sm">Best Performer</div>
            <div className="text-green-400 font-semibold">
              {
                marketData.reduce((best, current) =>
                  current.changePercent > best.changePercent ? current : best
                ).symbol
              }
            </div>
          </div>
        </EnhancedCard>

        <EnhancedCard variant="glass" size="sm">
          <div className="text-center">
            <div className="text-slate-400 text-sm">Worst Performer</div>
            <div className="text-red-400 font-semibold">
              {
                marketData.reduce((worst, current) =>
                  current.changePercent < worst.changePercent ? current : worst
                ).symbol
              }
            </div>
          </div>
        </EnhancedCard>

        <EnhancedCard variant="glass" size="sm">
          <div className="text-center">
            <div className="text-slate-400 text-sm">Avg Change</div>
            <AnimatedCounter
              value={marketData.reduce((sum, d) => sum + d.changePercent, 0) / marketData.length}
              prefix=""
              suffix="%"
              decimals={2}
              color={
                marketData.reduce((sum, d) => sum + d.changePercent, 0) / marketData.length >= 0
                  ? "positive"
                  : "negative"
              }
              className="text-lg font-semibold"
            />
          </div>
        </EnhancedCard>
      </div>

      {/* Visualization Chart */}
      <EnhancedCard variant="glass" size="lg">
        <div className="w-full h-full">
          <svg ref={svgRef} className="w-full h-full" style={{ minHeight: "400px" }} />
        </div>
      </EnhancedCard>

      {/* Legend */}
      {showLegend && (
        <EnhancedCard variant="default" size="sm">
          <div className="space-y-3">
            <h4 className="text-white font-semibold">Sector Legend</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {Array.from(new Set(marketData.map((d) => d.sector))).map((sector) => {
                const sectorData = marketData.find((d) => d.sector === sector);
                return (
                  <div key={sector} className="flex items-center gap-2">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: sectorData?.color }}
                    />
                    <span className="text-slate-300 text-sm">{sector}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </EnhancedCard>
      )}

      {/* Detailed List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {marketData.map((item, index) => (
          <EnhancedCard
            key={index}
            variant="glass"
            size="sm"
            className="hover:scale-105 transition-transform"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono font-bold text-white">{item.symbol}</span>
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
              </div>

              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 text-sm">Price</span>
                  <span className="text-white font-semibold">${item.value.toFixed(2)}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-400 text-sm">Change</span>
                  <div className="flex items-center gap-2">
                    <AnimatedCounter
                      value={item.change}
                      prefix={item.change >= 0 ? "+" : ""}
                      decimals={2}
                      color={item.change >= 0 ? "positive" : "negative"}
                      className="text-sm font-semibold"
                    />
                    <span
                      className={`text-sm font-semibold ${getPerformanceColor(item.changePercent)}`}
                    >
                      {item.changePercent >= 0 ? "+" : ""}
                      {item.changePercent.toFixed(2)}%
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-400 text-sm">Sector</span>
                  <span className="text-white text-sm">{item.sector}</span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-400 text-sm">Market Cap</span>
                  <span className="text-white text-sm">
                    ${(item.marketCap / 1000000000).toFixed(1)}B
                  </span>
                </div>
              </div>
            </div>
          </EnhancedCard>
        ))}
      </div>
    </div>
  );
};

export default MarketVisualization;
