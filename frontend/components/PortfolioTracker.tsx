import React, { useEffect, useState } from "react";
import { PositionUpdate, useWebSocket } from "../hooks/useWebSocket";
import AnimatedCounter from "./ui/AnimatedCounter";
import EnhancedCard from "./ui/EnhancedCard";
import StatusIndicator from "./ui/StatusIndicator";

interface PortfolioTrackerProps {
  userId: string;
  className?: string;
  showPositions?: boolean;
  compact?: boolean;
}

interface PositionItemProps {
  position: PositionUpdate;
  compact?: boolean;
}

const PositionItem: React.FC<PositionItemProps> = ({ position, compact = false }) => {
  const isPositive = position.unrealized_pnl >= 0;
  const pnlColor = isPositive ? "positive" : "negative";

  if (compact) {
    return (
      <div className="flex items-center justify-between p-2 bg-slate-800/50 rounded-lg">
        <div className="flex items-center gap-2">
          <span className="font-mono font-semibold text-white text-sm">{position.symbol}</span>
          <span className="text-slate-400 text-xs">{position.quantity} shares</span>
        </div>
        <div className="flex items-center gap-2">
          <AnimatedCounter
            value={position.market_value}
            prefix="$"
            decimals={2}
            color="neutral"
            className="text-sm"
          />
          <AnimatedCounter
            value={position.unrealized_pnl}
            prefix={isPositive ? "+" : ""}
            decimals={2}
            color={pnlColor}
            className="text-sm"
          />
        </div>
      </div>
    );
  }

  return (
    <EnhancedCard variant="glass" size="sm" className="hover:scale-105 transition-transform">
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="font-mono font-bold text-white text-lg">{position.symbol}</span>
          <span className="text-slate-400 text-sm">{position.quantity} shares</span>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">Current Price</span>
            <AnimatedCounter
              value={position.current_price}
              prefix="$"
              decimals={2}
              color="neutral"
              className="text-sm"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">Market Value</span>
            <AnimatedCounter
              value={position.market_value}
              prefix="$"
              decimals={2}
              color="neutral"
              className="text-sm font-semibold"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">Unrealized P&L</span>
            <div className="flex items-center gap-2">
              <AnimatedCounter
                value={position.unrealized_pnl}
                prefix={isPositive ? "+" : ""}
                decimals={2}
                color={pnlColor}
                className="text-sm font-semibold"
              />
              <AnimatedCounter
                value={position.unrealized_pnl_percent}
                prefix={isPositive ? "+" : ""}
                suffix="%"
                decimals={2}
                color={pnlColor}
                className="text-sm"
              />
            </div>
          </div>
        </div>

        <div className="text-xs text-slate-500">
          Updated: {new Date(position.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </EnhancedCard>
  );
};

const PortfolioTracker: React.FC<PortfolioTrackerProps> = ({
  userId,
  className,
  showPositions = true,
  compact = false,
}) => {
  const [isSubscribed, setIsSubscribed] = useState(false);

  const { isConnected, isConnecting, error, portfolioUpdate, positionUpdates } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws",
    userId,
    autoConnect: true,
  });

  // Subscribe to portfolio updates when connected
  useEffect(() => {
    if (isConnected && !isSubscribed) {
      // Send subscription message for portfolio updates
      // This would be handled by the WebSocket service
      setIsSubscribed(true);
    }
  }, [isConnected, isSubscribed]);

  if (error) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-red-400">
          <StatusIndicator status="error" size="sm" />
          <p className="mt-2">Portfolio Error: {error}</p>
        </div>
      </EnhancedCard>
    );
  }

  if (isConnecting) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center">
          <StatusIndicator status="loading" size="sm" />
          <p className="mt-2 text-slate-400">Loading portfolio data...</p>
        </div>
      </EnhancedCard>
    );
  }

  if (!isConnected) {
    return (
      <EnhancedCard variant="default" className={className}>
        <div className="text-center text-yellow-400">
          <StatusIndicator status="warning" size="sm" />
          <p className="mt-2">Disconnected from portfolio data</p>
        </div>
      </EnhancedCard>
    );
  }

  const isPositive = portfolioUpdate?.total_change && portfolioUpdate.total_change >= 0;
  const totalColor = isPositive ? "positive" : "negative";

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Portfolio Summary */}
      {portfolioUpdate && (
        <EnhancedCard variant="gradient" size="lg" className="text-center">
          <div className="space-y-4">
            <div className="flex items-center justify-center gap-2">
              <h3 className="text-white font-bold text-xl">Portfolio Value</h3>
              <StatusIndicator status="online" size="sm" />
            </div>

            <div className="space-y-2">
              <AnimatedCounter
                value={portfolioUpdate.total_value}
                prefix="$"
                decimals={2}
                color={totalColor}
                className="text-3xl font-bold"
              />

              <div className="flex items-center justify-center gap-4">
                <AnimatedCounter
                  value={portfolioUpdate.total_change}
                  prefix={isPositive ? "+" : ""}
                  decimals={2}
                  color={totalColor}
                  className="text-lg"
                />
                <AnimatedCounter
                  value={portfolioUpdate.total_change_percent}
                  prefix={isPositive ? "+" : ""}
                  suffix="%"
                  decimals={2}
                  color={totalColor}
                  className="text-lg"
                />
              </div>
            </div>
          </div>
        </EnhancedCard>
      )}

      {/* Positions */}
      {showPositions && positionUpdates.size > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-white font-semibold">Positions</h4>
            <span className="text-slate-400 text-sm">
              {positionUpdates.size} position{positionUpdates.size !== 1 ? "s" : ""}
            </span>
          </div>

          {compact ? (
            <div className="space-y-2">
              {Array.from(positionUpdates.values()).map((position) => (
                <PositionItem key={position.symbol} position={position} compact={compact} />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from(positionUpdates.values()).map((position) => (
                <PositionItem key={position.symbol} position={position} compact={compact} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* No positions message */}
      {showPositions && positionUpdates.size === 0 && (
        <EnhancedCard variant="default" className="text-center">
          <div className="text-slate-400">
            <StatusIndicator status="offline" size="sm" />
            <p className="mt-2">No positions found</p>
          </div>
        </EnhancedCard>
      )}
    </div>
  );
};

export default PortfolioTracker;
