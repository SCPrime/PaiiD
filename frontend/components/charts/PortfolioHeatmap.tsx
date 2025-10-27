import * as d3 from "d3";
import React, { useEffect, useRef, useState } from "react";
import { useWebSocket } from "../../hooks/useWebSocket";
import AnimatedCounter from "../ui/AnimatedCounter";
import EnhancedCard from "../ui/EnhancedCard";
import StatusIndicator from "../ui/StatusIndicator";

interface PortfolioHeatmapProps {
  userId: string;
  className?: string;
  symbols?: string[];
  showVolume?: boolean;
  showPerformance?: boolean;
}

interface HeatmapData {
  symbol: string;
  value: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  sector: string;
}

const PortfolioHeatmap: React.FC<PortfolioHeatmapProps> = ({
  userId,
  className,
  symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX"],
  showVolume = true,
  showPerformance: _showPerformance = true,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
  const [_isLoading, _setIsLoading] = useState(false);
  const [_error, _setError] = useState<string | null>(null);
  const [selectedMetric, setSelectedMetric] = useState<"change" | "volume" | "marketCap">("change");

  const { isConnected, marketData: _marketData } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    userId,
    autoConnect: true,
  });

  // Fetch real portfolio positions for heatmap
  useEffect(() => {
    const fetchHeatmapData = async () => {
      _setIsLoading(true);
      _setError(null);
      try {
        const response = await fetch(
          `/api/proxy/api/portfolio/positions`,
          {
            headers: {
              'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch positions: ${response.statusText}`);
        }

        const data = await response.json();

        // Transform positions to heatmap format
        const heatmap: HeatmapData[] = (data.positions || []).map((pos: any) => ({
          symbol: pos.symbol,
          value: pos.current_price || 0,
          change: pos.unrealized_pl || 0,
          changePercent: pos.unrealized_plpc || 0,
          volume: pos.qty || 0,
          marketCap: pos.market_value || 0,
          sector: pos.sector || 'Unknown',
        }));

        setHeatmapData(heatmap);
      } catch (error) {
        logger.error('Failed to fetch heatmap data', error);
        _setError('Failed to load portfolio heatmap');
        setHeatmapData([]);
      } finally {
        _setIsLoading(false);
      }
    };

    fetchHeatmapData();
  }, [symbols]);

  // Render heatmap
  useEffect(() => {
    if (!svgRef.current || heatmapData.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const margin = { top: 20, right: 20, bottom: 40, left: 100 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const g = svg
      .attr("width", 800)
      .attr("height", 400)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Calculate grid dimensions
    const cols = Math.ceil(Math.sqrt(heatmapData.length));
    const rows = Math.ceil(heatmapData.length / cols);
    const cellWidth = width / cols;
    const cellHeight = height / rows;

    // Color scale based on selected metric
    let colorScale: d3.ScaleLinear<string, string>;

    if (selectedMetric === "change") {
      const extent = d3.extent(heatmapData, (d) => d.changePercent) as [number, number];
      colorScale = d3
        .scaleLinear<string, string>()
        .domain([extent[0], 0, extent[1]])
        .range(["#dc2626", "#6b7280", "#16a34a"]);
    } else if (selectedMetric === "volume") {
      const extent = d3.extent(heatmapData, (d) => d.volume) as [number, number];
      colorScale = d3.scaleLinear<string, string>().domain(extent).range(["#1e293b", "#3b82f6"]);
    } else {
      const extent = d3.extent(heatmapData, (d) => d.marketCap) as [number, number];
      colorScale = d3.scaleLinear<string, string>().domain(extent).range(["#1e293b", "#8b5cf6"]);
    }

    // Create heatmap cells
    const cells = g
      .selectAll(".heatmap-cell")
      .data(heatmapData)
      .enter()
      .append("g")
      .attr("class", "heatmap-cell")
      .attr("transform", (_d, i) => {
        const row = Math.floor(i / cols);
        const col = i % cols;
        return `translate(${col * cellWidth},${row * cellHeight})`;
      });

    // Cell rectangles
    cells
      .append("rect")
      .attr("width", cellWidth - 2)
      .attr("height", cellHeight - 2)
      .attr("rx", 4)
      .attr("fill", (d) => {
        if (selectedMetric === "change") return colorScale(d.changePercent);
        if (selectedMetric === "volume") return colorScale(d.volume);
        return colorScale(d.marketCap);
      })
      .attr("stroke", "#374151")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")
      .on("mouseover", function () {
        // Highlight on hover
        d3.select(this).attr("stroke", "#60a5fa").attr("stroke-width", 2);
      })
      .on("mouseout", function () {
        // Remove highlight
        d3.select(this).attr("stroke", "#374151").attr("stroke-width", 1);
      });

    // Symbol labels
    cells
      .append("text")
      .attr("x", cellWidth / 2)
      .attr("y", cellHeight / 2 - 8)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .attr("fill", "white")
      .text((d) => d.symbol);

    // Value labels
    cells
      .append("text")
      .attr("x", cellWidth / 2)
      .attr("y", cellHeight / 2 + 8)
      .attr("text-anchor", "middle")
      .attr("font-size", "10px")
      .attr("fill", "white")
      .text((d) => {
        if (selectedMetric === "change")
          return `${d.changePercent >= 0 ? "+" : ""}${d.changePercent.toFixed(1)}%`;
        if (selectedMetric === "volume") return `${(d.volume / 1000000).toFixed(1)}M`;
        return `$${(d.marketCap / 1000000000).toFixed(1)}B`;
      });

    // Legend
    const legend = g
      .append("g")
      .attr("class", "legend")
      .attr("transform", `translate(${width - 150}, 20)`);

    legend
      .append("text")
      .attr("x", 0)
      .attr("y", 0)
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .attr("fill", "white")
      .text(
        `Showing: ${selectedMetric === "change" ? "Performance" : selectedMetric === "volume" ? "Volume" : "Market Cap"}`
      );
  }, [heatmapData, selectedMetric]);

  const getPerformanceColor = (change: number) => {
    if (change > 5) return "text-green-400";
    if (change > 0) return "text-green-300";
    if (change > -5) return "text-yellow-400";
    return "text-red-400";
  };

  if (_error) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-red-400">
          <StatusIndicator status="error" size="sm" />
          <p className="mt-2">Heatmap Error: {_error}</p>
        </div>
      </EnhancedCard>
    );
  }

  if (_isLoading) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Loading heatmap data...</p>
        </div>
      </EnhancedCard>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-white font-bold text-xl">Portfolio Heatmap</h3>
          <StatusIndicator status={isConnected ? "online" : "offline"} size="sm" />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value as "change" | "volume" | "marketCap")}
            className="bg-slate-700 text-white border border-slate-600 rounded-lg px-3 py-1 text-sm"
          >
            <option value="change">Performance</option>
            <option value="volume">Volume</option>
            <option value="marketCap">Market Cap</option>
          </select>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <EnhancedCard variant="glass" size="sm">
          <div className="text-center">
            <div className="text-slate-400 text-sm">Total Value</div>
            <AnimatedCounter
              value={heatmapData.reduce((sum, d) => sum + d.value, 0)}
              prefix="$"
              decimals={0}
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
                heatmapData.reduce((best, current) =>
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
                heatmapData.reduce((worst, current) =>
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
              value={heatmapData.reduce((sum, d) => sum + d.changePercent, 0) / heatmapData.length}
              prefix=""
              suffix="%"
              decimals={2}
              color={
                heatmapData.reduce((sum, d) => sum + d.changePercent, 0) / heatmapData.length >= 0
                  ? "positive"
                  : "negative"
              }
              className="text-lg font-semibold"
            />
          </div>
        </EnhancedCard>
      </div>

      {/* Heatmap Chart */}
      <EnhancedCard variant="glass" size="lg">
        <div className="w-full h-full">
          <svg ref={svgRef} className="w-full h-full" style={{ minHeight: "400px" }} />
        </div>
      </EnhancedCard>

      {/* Detailed List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {heatmapData.map((item, index) => (
          <EnhancedCard
            key={index}
            variant="glass"
            size="sm"
            className="hover:scale-105 transition-transform"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-mono font-bold text-white">{item.symbol}</span>
                <span className="text-slate-400 text-sm">{item.sector}</span>
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

                {showVolume && (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 text-sm">Volume</span>
                    <span className="text-white text-sm">
                      {(item.volume / 1000000).toFixed(1)}M
                    </span>
                  </div>
                )}
              </div>
            </div>
          </EnhancedCard>
        ))}
      </div>
    </div>
  );
};

export default PortfolioHeatmap;
