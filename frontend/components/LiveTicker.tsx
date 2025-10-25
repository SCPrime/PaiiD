import React, { useEffect, useState } from "react";
import { MarketData, useWebSocket } from "../hooks/useWebSocket";
import AnimatedCounter from "./ui/AnimatedCounter";
import EnhancedCard from "./ui/EnhancedCard";
import StatusIndicator from "./ui/StatusIndicator";

interface LiveTickerProps {
  symbols: string[];
  userId: string;
  className?: string;
  showVolume?: boolean;
  showChange?: boolean;
  compact?: boolean;
}

interface TickerItemProps {
  symbol: string;
  data: MarketData;
  showVolume?: boolean;
  showChange?: boolean;
  compact?: boolean;
}

const TickerItem: React.FC<TickerItemProps> = ({
  symbol,
  data,
  showVolume = true,
  showChange = true,
  compact = false,
}) => {
  const isPositive = data.change >= 0;
  const changeColor = isPositive ? "positive" : "negative";

  if (compact) {
    return (
      <div className="flex items-center justify-between p-2 bg-slate-800/50 rounded-lg">
        <div className="flex items-center gap-2">
          <span className="font-mono font-semibold text-white text-sm">{symbol}</span>
          <AnimatedCounter
            value={data.price}
            prefix="$"
            decimals={2}
            color={changeColor}
            className="text-sm"
          />
        </div>
        {showChange && (
          <div className="flex items-center gap-1">
            <AnimatedCounter
              value={data.change}
              prefix={isPositive ? "+" : ""}
              decimals={2}
              color={changeColor}
              className="text-xs"
            />
            <AnimatedCounter
              value={data.change_percent}
              suffix="%"
              decimals={2}
              color={changeColor}
              className="text-xs"
            />
          </div>
        )}
      </div>
    );
  }

  return (
    <EnhancedCard variant="glass" size="sm" className="hover:scale-105 transition-transform">
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="font-mono font-bold text-white">{symbol}</span>
          <StatusIndicator status="online" size="sm" label={data.source} />
        </div>

        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">Price</span>
            <AnimatedCounter
              value={data.price}
              prefix="$"
              decimals={2}
              color={changeColor}
              className="text-lg font-semibold"
            />
          </div>

          {showChange && (
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">Change</span>
              <div className="flex items-center gap-2">
                <AnimatedCounter
                  value={data.change}
                  prefix={isPositive ? "+" : ""}
                  decimals={2}
                  color={changeColor}
                  className="text-sm"
                />
                <AnimatedCounter
                  value={data.change_percent}
                  suffix="%"
                  decimals={2}
                  color={changeColor}
                  className="text-sm"
                />
              </div>
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">High</span>
            <span className="text-white text-sm">${data.high.toFixed(2)}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">Low</span>
            <span className="text-white text-sm">${data.low.toFixed(2)}</span>
          </div>

          {showVolume && (
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">Volume</span>
              <span className="text-white text-sm">{data.volume.toLocaleString()}</span>
            </div>
          )}
        </div>

        <div className="text-xs text-slate-500">
          Updated: {new Date(data.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </EnhancedCard>
  );
};

const LiveTicker: React.FC<LiveTickerProps> = ({
  symbols,
  userId,
  className,
  showVolume = true,
  showChange = true,
  compact = false,
}) => {
  const [isSubscribed, setIsSubscribed] = useState(false);

  const { isConnected, isConnecting, error, marketData, subscribe, unsubscribe } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    userId,
    autoConnect: true,
  });

  // Subscribe to symbols when connected
  useEffect(() => {
    if (isConnected && !isSubscribed && symbols.length > 0) {
      subscribe(symbols);
      setIsSubscribed(true);
    }
  }, [isConnected, symbols, subscribe, isSubscribed]);

  // Unsubscribe on unmount
  useEffect(() => {
    return () => {
      if (isSubscribed) {
        unsubscribe(symbols);
      }
    };
  }, [isSubscribed, symbols, unsubscribe]);

  if (error) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-red-400">
          <StatusIndicator status="error" size="sm" />
          <p className="mt-2">Connection Error: {error}</p>
        </div>
      </EnhancedCard>
    );
  }

  if (isConnecting) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Connecting to market data...</p>
        </div>
      </EnhancedCard>
    );
  }

  if (!isConnected) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-yellow-400">
          <StatusIndicator status="warning" size="sm" />
          <p className="mt-2">Disconnected from market data</p>
        </div>
      </EnhancedCard>
    );
  }

  const availableData = symbols.filter((symbol) => marketData.has(symbol));

  if (availableData.length === 0) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-slate-400">
          <StatusIndicator status="offline" size="sm" />
          <p className="mt-2">No market data available</p>
        </div>
      </EnhancedCard>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold">Live Market Data</h3>
        <div className="flex items-center gap-2">
          <StatusIndicator status="online" size="sm" />
          <span className="text-xs text-slate-400">
            {availableData.length}/{symbols.length} symbols
          </span>
        </div>
      </div>

      {compact ? (
        <div className="grid grid-cols-1 gap-2">
          {availableData.map((symbol) => (
            <TickerItem
              key={symbol}
              symbol={symbol}
              data={marketData.get(symbol)!}
              showVolume={showVolume}
              showChange={showChange}
              compact={compact}
            />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {availableData.map((symbol) => (
            <TickerItem
              key={symbol}
              symbol={symbol}
              data={marketData.get(symbol)!}
              showVolume={showVolume}
              showChange={showChange}
              compact={compact}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default LiveTicker;
