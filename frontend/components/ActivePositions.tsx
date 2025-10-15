"use client";
import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Percent, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { Card, Button } from './ui';
import { theme } from '../styles/theme';
import { alpaca, formatPosition } from '../lib/alpaca';
import { useIsMobile } from '../hooks/useBreakpoint';
import { usePositionUpdates } from '../hooks/usePositionUpdates';

interface Position {
  symbol: string;
  qty: number;
  avgEntryPrice: number;
  currentPrice: number;
  marketValue: number;
  unrealizedPL: number;
  unrealizedPLPercent: number;
  side: 'long' | 'short';
  dayChange: number;
  dayChangePercent: number;
}

interface PortfolioMetrics {
  totalValue: number;
  buyingPower: number;
  totalPL: number;
  totalPLPercent: number;
  dayPL: number;
  dayPLPercent: number;
  positionCount: number;
}

export default function ActivePositions() {
  const isMobile = useIsMobile();
  const [positions, setPositions] = useState<Position[]>([]);
  const [metrics, setMetrics] = useState<PortfolioMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'symbol' | 'pl' | 'plPercent' | 'value'>('symbol');

  // Real-time position updates via SSE
  const { positions: streamedPositions, connected, connecting, error: streamError, reconnect } = usePositionUpdates({
    autoReconnect: true,
    maxReconnectAttempts: 5,
    debug: false,
  });

  // Use streamed positions when available
  useEffect(() => {
    if (streamedPositions.length > 0) {
      setPositions(streamedPositions);
      calculateMetrics(streamedPositions);
    }
  }, [streamedPositions]);

  // Initial load and fallback polling (only if SSE not connected)
  useEffect(() => {
    loadPositions();
    // Only poll if SSE is not connected
    if (!connected && !connecting) {
      const interval = setInterval(loadPositions, 10000); // Slower polling as fallback
      return () => clearInterval(interval);
    }
  }, [connected, connecting]);

  // Calculate portfolio metrics from positions
  const calculateMetrics = async (positionsList: Position[]) => {
    try {
      // Fetch account data for buying power
      const account = await alpaca.getAccount();

      const totalValue = positionsList.reduce((sum, p) => sum + p.marketValue, 0);
      const totalPL = positionsList.reduce((sum, p) => sum + p.unrealizedPL, 0);
      const totalCost = positionsList.reduce((sum, p) => sum + (p.avgEntryPrice * p.qty), 0);
      const dayPL = positionsList.reduce((sum, p) => sum + (p.dayChange * p.qty), 0);

      const calculatedMetrics: PortfolioMetrics = {
        totalValue,
        buyingPower: parseFloat(account.buying_power),
        totalPL,
        totalPLPercent: totalCost > 0 ? (totalPL / totalCost) * 100 : 0,
        dayPL,
        dayPLPercent: (totalValue - dayPL) > 0 ? (dayPL / (totalValue - dayPL)) * 100 : 0,
        positionCount: positionsList.length,
      };

      setMetrics(calculatedMetrics);
    } catch (error) {
      console.error('Failed to calculate metrics:', error);
    }
  };

  const loadPositions = async () => {
    setLoading(true);

    try {
      // Fetch positions from Alpaca
      const alpacaPositions = await alpaca.getPositions();

      // Format positions for UI
      const formattedPositions: Position[] = alpacaPositions.map(formatPosition);

      setPositions(formattedPositions);
      await calculateMetrics(formattedPositions);
    } catch (error) {
      console.error('Failed to load positions:', error);
      // Keep existing data if refresh fails
    } finally {
      setLoading(false);
    }
  };

  const sortPositions = (positions: Position[]) => {
    return [...positions].sort((a, b) => {
      switch (sortBy) {
        case 'symbol':
          return a.symbol.localeCompare(b.symbol);
        case 'pl':
          return b.unrealizedPL - a.unrealizedPL;
        case 'plPercent':
          return b.unrealizedPLPercent - a.unrealizedPLPercent;
        case 'value':
          return b.marketValue - a.marketValue;
        default:
          return 0;
      }
    });
  };

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      {/* Header with PaiiD Logo */}
      <div style={{
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        alignItems: isMobile ? 'flex-start' : 'center',
        justifyContent: 'space-between',
        gap: isMobile ? theme.spacing.sm : 0,
        marginBottom: theme.spacing.lg
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: isMobile ? theme.spacing.sm : theme.spacing.md }}>
          {/* PaiiD Logo */}
          <div style={{ fontSize: isMobile ? '28px' : '42px', fontWeight: '900', lineHeight: '1' }}>
            <span style={{
              background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              filter: 'drop-shadow(0 3px 8px rgba(26, 117, 96, 0.4))'
            }}>P</span>
            <span style={{
              background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textShadow: '0 0 18px rgba(69, 240, 192, 0.8), 0 0 36px rgba(69, 240, 192, 0.4)',
              animation: 'glow-ai 3s ease-in-out infinite'
            }}>aii</span>
            <span style={{
              background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              filter: 'drop-shadow(0 3px 8px rgba(26, 117, 96, 0.4))'
            }}>D</span>
          </div>

          <TrendingUp size={isMobile ? 24 : 32} color={theme.colors.primary} />
          <h1 style={{
            margin: 0,
            fontSize: isMobile ? '24px' : '32px',
            fontWeight: '700',
            color: theme.colors.text,
            textShadow: theme.glow.green,
          }}>
            Active Positions
          </h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm, width: isMobile ? '100%' : 'auto' }}>
          {/* Connection Status Indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.xs,
            padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
            background: connected ? 'rgba(16, 185, 129, 0.1)' : connecting ? 'rgba(251, 191, 36, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            border: `1px solid ${connected ? 'rgba(16, 185, 129, 0.3)' : connecting ? 'rgba(251, 191, 36, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            borderRadius: theme.borderRadius.sm,
          }}>
            {connected ? (
              <Wifi size={14} color={theme.colors.primary} />
            ) : (
              <WifiOff size={14} color={theme.colors.danger} />
            )}
            <span style={{ fontSize: '12px', color: theme.colors.textMuted }}>
              {connecting ? 'Connecting...' : connected ? 'Live' : 'Offline'}
            </span>
          </div>

          <Button variant="secondary" size="sm" onClick={loadPositions} style={{ flex: isMobile ? '1' : 'none' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.xs }}>
              <RefreshCw size={16} />
              {!isMobile && 'Refresh'}
            </div>
          </Button>
        </div>
      </div>

      {loading ? (
        <Card>
          <div style={{ textAlign: 'center', padding: theme.spacing.xl, color: theme.colors.textMuted }}>
            Loading positions...
          </div>
        </Card>
      ) : (
        <>
          {/* Portfolio Metrics */}
          {metrics && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: isMobile ? '1fr' : 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: theme.spacing.md,
              marginBottom: theme.spacing.lg,
            }}>
              <MetricCard
                icon={<DollarSign size={20} color={theme.colors.secondary} />}
                label="Total Value"
                value={`$${metrics.totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              />
              <MetricCard
                icon={<DollarSign size={20} color={theme.colors.info} />}
                label="Buying Power"
                value={`$${metrics.buyingPower.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              />
              <MetricCard
                icon={metrics.totalPL >= 0 ? <TrendingUp size={20} color={theme.colors.primary} /> : <TrendingDown size={20} color={theme.colors.danger} />}
                label="Total P&L"
                value={`${metrics.totalPL >= 0 ? '+' : ''}$${Math.abs(metrics.totalPL).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                subValue={`${metrics.totalPLPercent >= 0 ? '+' : ''}${metrics.totalPLPercent.toFixed(2)}%`}
                valueColor={metrics.totalPL >= 0 ? theme.colors.primary : theme.colors.danger}
              />
              <MetricCard
                icon={metrics.dayPL >= 0 ? <TrendingUp size={20} color={theme.colors.primary} /> : <TrendingDown size={20} color={theme.colors.danger} />}
                label="Today's P&L"
                value={`${metrics.dayPL >= 0 ? '+' : ''}$${Math.abs(metrics.dayPL).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                subValue={`${metrics.dayPLPercent >= 0 ? '+' : ''}${metrics.dayPLPercent.toFixed(2)}%`}
                valueColor={metrics.dayPL >= 0 ? theme.colors.primary : theme.colors.danger}
              />
            </div>
          )}

          {/* Sort Controls */}
          <Card style={{ marginBottom: theme.spacing.md, padding: theme.spacing.md }}>
            <div style={{
              display: 'flex',
              flexDirection: isMobile ? 'column' : 'row',
              alignItems: isMobile ? 'flex-start' : 'center',
              gap: theme.spacing.sm
            }}>
              <span style={{ color: theme.colors.textMuted, fontSize: '14px' }}>Sort by:</span>
              <div style={{ display: 'flex', gap: theme.spacing.sm, flexWrap: 'wrap' }}>
                {(['symbol', 'pl', 'plPercent', 'value'] as const).map((sort) => (
                  <button
                    key={sort}
                    onClick={() => setSortBy(sort)}
                    style={{
                      padding: `${theme.spacing.xs} ${theme.spacing.md}`,
                      background: sortBy === sort ? theme.colors.primary : theme.background.input,
                      color: sortBy === sort ? '#fff' : theme.colors.text,
                      borderRadius: theme.borderRadius.sm,
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: sortBy === sort ? '600' : '400',
                      transition: theme.transitions.fast,
                    }}
                  >
                    {sort === 'pl' ? 'P&L' : sort === 'plPercent' ? 'P&L %' : sort.charAt(0).toUpperCase() + sort.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </Card>

          {/* Positions List */}
          {positions.length === 0 ? (
            <Card>
              <div style={{ textAlign: 'center', padding: theme.spacing.xl, color: theme.colors.textMuted }}>
                No active positions
              </div>
            </Card>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
              {sortPositions(positions).map((position) => (
                <Card key={position.symbol} glow={position.unrealizedPL >= 0 ? 'green' : undefined}>
                  <div style={{
                    display: 'flex',
                    flexDirection: isMobile ? 'column' : 'row',
                    justifyContent: 'space-between',
                    gap: isMobile ? theme.spacing.sm : 0,
                    marginBottom: theme.spacing.md
                  }}>
                    <div>
                      <h3 style={{
                        margin: 0,
                        fontSize: isMobile ? '20px' : '24px',
                        fontWeight: '700',
                        color: theme.colors.text
                      }}>
                        {position.symbol}
                      </h3>
                      <p style={{ margin: `${theme.spacing.xs} 0 0 0`, color: theme.colors.textMuted, fontSize: '14px' }}>
                        {position.qty} shares @ ${position.avgEntryPrice.toFixed(2)}
                      </p>
                    </div>
                    <div style={{ textAlign: isMobile ? 'left' : 'right' }}>
                      <p style={{ margin: 0, fontSize: isMobile ? '20px' : '24px', fontWeight: '700', color: theme.colors.text }}>
                        ${position.currentPrice.toFixed(2)}
                      </p>
                      <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.xs, justifyContent: 'flex-end' }}>
                        {position.dayChange >= 0 ? (
                          <TrendingUp size={16} color={theme.colors.primary} />
                        ) : (
                          <TrendingDown size={16} color={theme.colors.danger} />
                        )}
                        <span style={{
                          fontSize: '14px',
                          fontWeight: '500',
                          color: position.dayChange >= 0 ? theme.colors.primary : theme.colors.danger,
                        }}>
                          {position.dayChange >= 0 ? '+' : ''}{position.dayChange.toFixed(2)} ({position.dayChangePercent >= 0 ? '+' : ''}{position.dayChangePercent.toFixed(2)}%)
                        </span>
                      </div>
                    </div>
                  </div>

                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)',
                    gap: theme.spacing.md,
                    paddingTop: theme.spacing.md,
                    borderTop: `1px solid ${theme.colors.border}`,
                  }}>
                    <div>
                      <p style={{ fontSize: '12px', color: theme.colors.textMuted, margin: 0 }}>Market Value</p>
                      <p style={{ fontSize: '18px', fontWeight: '600', color: theme.colors.text, margin: `${theme.spacing.xs} 0 0 0` }}>
                        ${position.marketValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </p>
                    </div>
                    <div>
                      <p style={{ fontSize: '12px', color: theme.colors.textMuted, margin: 0 }}>Unrealized P&L</p>
                      <p style={{
                        fontSize: '18px',
                        fontWeight: '600',
                        color: position.unrealizedPL >= 0 ? theme.colors.primary : theme.colors.danger,
                        margin: `${theme.spacing.xs} 0 0 0`,
                      }}>
                        {position.unrealizedPL >= 0 ? '+' : ''}${Math.abs(position.unrealizedPL).toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p style={{ fontSize: '12px', color: theme.colors.textMuted, margin: 0 }}>Return</p>
                      <p style={{
                        fontSize: '18px',
                        fontWeight: '600',
                        color: position.unrealizedPLPercent >= 0 ? theme.colors.primary : theme.colors.danger,
                        margin: `${theme.spacing.xs} 0 0 0`,
                      }}>
                        {position.unrealizedPLPercent >= 0 ? '+' : ''}{position.unrealizedPLPercent.toFixed(2)}%
                      </p>
                    </div>
                  </div>

                  <Button
                    variant="danger"
                    size="sm"
                    style={{ marginTop: theme.spacing.md, width: '100%' }}
                    onClick={async () => {
                      if (confirm(`Close entire position in ${position.symbol}?`)) {
                        try {
                          await alpaca.closePosition(position.symbol);
                          // Refresh positions after close
                          await loadPositions();
                        } catch (error) {
                          console.error(`Failed to close position ${position.symbol}:`, error);
                          alert(`Failed to close position: ${error}`);
                        }
                      }
                    }}
                  >
                    Close Position
                  </Button>
                </Card>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function MetricCard({ icon, label, value, subValue, valueColor }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  subValue?: string;
  valueColor?: string;
}) {
  return (
    <Card>
      <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.xs, marginBottom: theme.spacing.xs }}>
        {icon}
        <p style={{ fontSize: '14px', color: theme.colors.textMuted, margin: 0 }}>{label}</p>
      </div>
      <p style={{
        fontSize: '24px',
        fontWeight: 'bold',
        color: valueColor || theme.colors.text,
        margin: 0
      }}>
        {value}
      </p>
      {subValue && (
        <p style={{ fontSize: '14px', color: theme.colors.textMuted, margin: `${theme.spacing.xs} 0 0 0` }}>
          {subValue}
        </p>
      )}
    </Card>
  );
}
