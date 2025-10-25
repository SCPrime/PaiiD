import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { useWebSocket, MarketData } from "../../hooks/useWebSocket";
import EnhancedCard from "../ui/EnhancedCard";
import StatusIndicator from "../ui/StatusIndicator";

interface AdvancedChartProps {
  symbol: string;
  userId: string;
  className?: string;
  chartType?: "candlestick" | "line" | "volume" | "heatmap";
  timeFrame?: "1m" | "5m" | "15m" | "1h" | "1d";
  showIndicators?: boolean;
  showAI?: boolean;
}

interface ChartData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TechnicalIndicator {
  name: string;
  value: number;
  signal: "buy" | "sell" | "hold";
  color: string;
}

const AdvancedChart: React.FC<AdvancedChartProps> = ({
  symbol,
  userId,
  className,
  chartType = "candlestick",
  timeFrame = "1d",
  showIndicators = true,
  showAI = true,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [indicators, setIndicators] = useState<TechnicalIndicator[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { isConnected, marketData } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    userId,
    autoConnect: true,
  });

  // Generate mock chart data
  useEffect(() => {
    const generateMockData = () => {
      const data: ChartData[] = [];
      const now = new Date();
      
      for (let i = 100; i >= 0; i--) {
        const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
        const basePrice = 150 + Math.sin(i * 0.1) * 20;
        const volatility = 2 + Math.random() * 3;
        
        const open = basePrice + (Math.random() - 0.5) * volatility;
        const close = open + (Math.random() - 0.5) * volatility * 2;
        const high = Math.max(open, close) + Math.random() * volatility;
        const low = Math.min(open, close) - Math.random() * volatility;
        const volume = Math.floor(Math.random() * 1000000) + 100000;
        
        data.push({
          timestamp: date.toISOString(),
          open: Number(open.toFixed(2)),
          high: Number(high.toFixed(2)),
          low: Number(low.toFixed(2)),
          close: Number(close.toFixed(2)),
          volume,
        });
      }
      
      return data;
    };

    setChartData(generateMockData());
  }, [symbol]);

  // Calculate technical indicators
  useEffect(() => {
    if (chartData.length === 0) return;

    const calculateRSI = (prices: number[], period: number = 14): number => {
      if (prices.length < period + 1) return 50;
      
      const gains: number[] = [];
      const losses: number[] = [];
      
      for (let i = 1; i < prices.length; i++) {
        const change = prices[i] - prices[i - 1];
        gains.push(change > 0 ? change : 0);
        losses.push(change < 0 ? Math.abs(change) : 0);
      }
      
      const avgGain = gains.slice(-period).reduce((a, b) => a + b, 0) / period;
      const avgLoss = losses.slice(-period).reduce((a, b) => a + b, 0) / period;
      
      if (avgLoss === 0) return 100;
      const rs = avgGain / avgLoss;
      return 100 - (100 / (1 + rs));
    };

    const calculateMACD = (prices: number[]): { macd: number; signal: number; histogram: number } => {
      if (prices.length < 26) return { macd: 0, signal: 0, histogram: 0 };
      
      const ema12 = prices.slice(-12).reduce((a, b) => a + b, 0) / 12;
      const ema26 = prices.slice(-26).reduce((a, b) => a + b, 0) / 26;
      const macd = ema12 - ema26;
      const signal = macd * 0.9; // Simplified signal line
      const histogram = macd - signal;
      
      return { macd, signal, histogram };
    };

    const prices = chartData.map(d => d.close);
    const rsi = calculateRSI(prices);
    const macd = calculateMACD(prices);
    
    const newIndicators: TechnicalIndicator[] = [
      {
        name: "RSI",
        value: rsi,
        signal: rsi > 70 ? "sell" : rsi < 30 ? "buy" : "hold",
        color: rsi > 70 ? "#ef4444" : rsi < 30 ? "#22c55e" : "#6b7280",
      },
      {
        name: "MACD",
        value: macd.macd,
        signal: macd.macd > macd.signal ? "buy" : "sell",
        color: macd.macd > macd.signal ? "#22c55e" : "#ef4444",
      },
    ];
    
    setIndicators(newIndicators);
  }, [chartData]);

  // Render candlestick chart
  useEffect(() => {
    if (!svgRef.current || chartData.length === 0) return;

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
      .scaleTime()
      .domain(d3.extent(chartData, d => new Date(d.timestamp)) as [Date, Date])
      .range([0, width]);

    const yScale = d3
      .scaleLinear()
      .domain(d3.extent(chartData, d => [d.low, d.high]).flat() as [number, number])
      .range([height, 0]);

    // Candlestick rectangles
    g.selectAll(".candlestick")
      .data(chartData)
      .enter()
      .append("rect")
      .attr("class", "candlestick")
      .attr("x", d => xScale(new Date(d.timestamp)) - 2)
      .attr("y", d => yScale(Math.max(d.open, d.close)))
      .attr("width", 4)
      .attr("height", d => Math.abs(yScale(d.close) - yScale(d.open)))
      .attr("fill", d => d.close >= d.open ? "#22c55e" : "#ef4444")
      .attr("stroke", d => d.close >= d.open ? "#16a34a" : "#dc2626");

    // High-low lines
    g.selectAll(".wick")
      .data(chartData)
      .enter()
      .append("line")
      .attr("class", "wick")
      .attr("x1", d => xScale(new Date(d.timestamp)))
      .attr("x2", d => xScale(new Date(d.timestamp)))
      .attr("y1", d => yScale(d.high))
      .attr("y2", d => yScale(d.low))
      .attr("stroke", d => d.close >= d.open ? "#16a34a" : "#dc2626")
      .attr("stroke-width", 1);

    // Moving average line
    const ma20 = chartData.map((d, i) => {
      if (i < 19) return null;
      const slice = chartData.slice(i - 19, i + 1);
      const avg = slice.reduce((sum, item) => sum + item.close, 0) / slice.length;
      return { timestamp: d.timestamp, value: avg };
    }).filter(d => d !== null);

    const line = d3
      .line<{ timestamp: string; value: number }>()
      .x(d => xScale(new Date(d.timestamp)))
      .y(d => yScale(d.value));

    g.append("path")
      .datum(ma20)
      .attr("fill", "none")
      .attr("stroke", "#3b82f6")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat("%m/%d")));

    g.append("g")
      .call(d3.axisLeft(yScale).tickFormat(d3.format("$.2f")));

    // Grid lines
    g.append("g")
      .attr("class", "grid")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickSize(-height).tickFormat(() => ""))
      .style("stroke-dasharray", "3,3")
      .style("opacity", 0.3);

    g.append("g")
      .attr("class", "grid")
      .call(d3.axisLeft(yScale).tickSize(-width).tickFormat(() => ""))
      .style("stroke-dasharray", "3,3")
      .style("opacity", 0.3);

  }, [chartData, chartType]);

  if (error) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-red-400">
          <StatusIndicator status="error" size="sm" />
          <p className="mt-2">Chart Error: {error}</p>
        </div>
      </EnhancedCard>
    );
  }

  if (isLoading) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Loading chart data...</p>
        </div>
      </EnhancedCard>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Chart Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-white font-bold text-xl">{symbol} Chart</h3>
          <StatusIndicator status={isConnected ? "online" : "offline"} size="sm" />
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-sm capitalize">{chartType}</span>
          <span className="text-slate-400 text-sm">{timeFrame}</span>
        </div>
      </div>

      {/* Technical Indicators */}
      {showIndicators && indicators.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {indicators.map((indicator, index) => (
            <EnhancedCard key={index} variant="glass" size="sm">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 text-sm">{indicator.name}</span>
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: indicator.color }}
                  />
                </div>
                <div className="text-white font-semibold">
                  {indicator.value.toFixed(2)}
                </div>
                <div className="text-xs text-slate-400 capitalize">
                  {indicator.signal}
                </div>
              </div>
            </EnhancedCard>
          ))}
        </div>
      )}

      {/* Chart Container */}
      <EnhancedCard variant="glass" size="lg">
        <div className="w-full h-full">
          <svg
            ref={svgRef}
            className="w-full h-full"
            style={{ minHeight: "400px" }}
          />
        </div>
      </EnhancedCard>

      {/* AI Insights */}
      {showAI && (
        <EnhancedCard variant="gradient" size="md">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🤖</span>
              <h4 className="text-white font-semibold">AI Chart Analysis</h4>
            </div>
            <div className="text-slate-300 text-sm">
              <p>• Trend: {chartData[chartData.length - 1]?.close > chartData[chartData.length - 2]?.close ? "Bullish" : "Bearish"}</p>
              <p>• Support: ${Math.min(...chartData.map(d => d.low)).toFixed(2)}</p>
              <p>• Resistance: ${Math.max(...chartData.map(d => d.high)).toFixed(2)}</p>
              <p>• Volume: {chartData[chartData.length - 1]?.volume.toLocaleString()}</p>
            </div>
          </div>
        </EnhancedCard>
      )}
    </div>
  );
};

export default AdvancedChart;
