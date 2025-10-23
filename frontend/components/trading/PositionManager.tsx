'use client';

import { useState, useEffect } from 'react';

interface PositionGreeks {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
}

interface Position {
  id: string;
  symbol: string;
  option_symbol: string;
  qty: number;
  avg_entry_price: number;
  current_price: number;
  unrealized_pl: number;
  unrealized_pl_percent: number;
  market_value: number;
  cost_basis: number;
  greeks: PositionGreeks;
  expiration: string;
  days_to_expiry: number;
  status: string;
}

interface PortfolioGreeks {
  total_delta: number;
  total_gamma: number;
  total_theta: number;
  total_vega: number;
  position_count: number;
}

export default function PositionManager() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [portfolioGreeks, setPortfolioGreeks] = useState<PortfolioGreeks | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(10000); // 10 seconds

  useEffect(() => {
    fetchPositions();
    fetchPortfolioGreeks();
    
    const interval = setInterval(() => {
      fetchPositions();
      fetchPortfolioGreeks();
    }, refreshInterval);
    
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const fetchPositions = async () => {
    try {
      const res = await fetch('/api/proxy/positions');
      const data = await res.json();
      setPositions(data);
    } catch (error) {
      console.error('Failed to fetch positions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPortfolioGreeks = async () => {
    try {
      const res = await fetch('/api/proxy/positions/greeks');
      const data = await res.json();
      setPortfolioGreeks(data);
    } catch (error) {
      console.error('Failed to fetch portfolio Greeks:', error);
    }
  };

  const handleClosePosition = async (positionId: string) => {
    if (!confirm('Are you sure you want to close this position?')) return;
    
    try {
      await fetch(`/api/proxy/positions/${positionId}/close`, {
        method: 'POST'
      });
      fetchPositions();
    } catch (error) {
      console.error('Failed to close position:', error);
      alert('Failed to close position');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading) {
    return <div className="p-6">Loading positions...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Position Manager</h2>
        <select
          value={refreshInterval}
          onChange={(e) => setRefreshInterval(Number(e.target.value))}
          className="px-3 py-1 bg-gray-800 border border-gray-700 rounded"
          title="Select refresh interval"
        >
          <option value={5000}>Refresh: 5s</option>
          <option value={10000}>Refresh: 10s</option>
          <option value={30000}>Refresh: 30s</option>
          <option value={60000}>Refresh: 1m</option>
        </select>
      </div>

      {/* Portfolio Greeks Summary */}
      {portfolioGreeks && (
        <div className="grid grid-cols-5 gap-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400">Positions</div>
            <div className="text-2xl font-bold">{portfolioGreeks.position_count}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400">Portfolio Delta</div>
            <div className="text-2xl font-bold">{portfolioGreeks.total_delta.toFixed(2)}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400">Portfolio Gamma</div>
            <div className="text-2xl font-bold">{portfolioGreeks.total_gamma.toFixed(3)}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400">Portfolio Theta</div>
            <div className="text-2xl font-bold">{portfolioGreeks.total_theta.toFixed(2)}</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <div className="text-sm text-gray-400">Portfolio Vega</div>
            <div className="text-2xl font-bold">{portfolioGreeks.total_vega.toFixed(2)}</div>
          </div>
        </div>
      )}

      {/* Positions Table */}
      {positions.length === 0 ? (
        <div className="text-center text-gray-400 py-12">
          No open positions
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left p-3">Symbol</th>
                <th className="text-right p-3">Qty</th>
                <th className="text-right p-3">Entry</th>
                <th className="text-right p-3">Current</th>
                <th className="text-right p-3">P&L</th>
                <th className="text-right p-3">Delta</th>
                <th className="text-right p-3">Theta</th>
                <th className="text-right p-3">DTE</th>
                <th className="text-right p-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((position) => (
                <tr key={position.id} className="border-b border-gray-800 hover:bg-gray-800/50">
                  <td className="p-3">
                    <div className="font-semibold">{position.symbol}</div>
                    <div className="text-xs text-gray-400">{position.option_symbol}</div>
                  </td>
                  <td className="text-right p-3">{position.qty}</td>
                  <td className="text-right p-3">{formatCurrency(position.avg_entry_price)}</td>
                  <td className="text-right p-3">{formatCurrency(position.current_price)}</td>
                  <td className={`text-right p-3 font-semibold ${position.unrealized_pl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    <div>{formatCurrency(position.unrealized_pl)}</div>
                    <div className="text-xs">{formatPercent(position.unrealized_pl_percent)}</div>
                  </td>
                  <td className="text-right p-3">{position.greeks.delta.toFixed(3)}</td>
                  <td className="text-right p-3">{position.greeks.theta.toFixed(2)}</td>
                  <td className="text-right p-3">
                    <span className={position.days_to_expiry < 7 ? 'text-red-400 font-semibold' : ''}>
                      {position.days_to_expiry}d
                    </span>
                  </td>
                  <td className="text-right p-3">
                    <button
                      onClick={() => handleClosePosition(position.id)}
                      className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
                    >
                      Close
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
