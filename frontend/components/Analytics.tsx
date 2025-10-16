"use client";
import { useState, useEffect, useRef } from 'react';
import { BarChart3, TrendingDown, DollarSign, Percent, Target, Award, Download } from 'lucide-react';
import { Card, Button } from './ui';
import { theme } from '../styles/theme';
import TradingViewChart from './TradingViewChart';
import { useIsMobile } from '../hooks/useBreakpoint';
import html2canvas from 'html2canvas';

interface PerformanceMetrics {
  totalReturn: number;
  totalReturnPercent: number;
  winRate: number;
  profitFactor: number;
  sharpeRatio: number;
  maxDrawdown: number;
  avgWin: number;
  avgLoss: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
}

interface DailyPerformance {
  date: string;
  pnl: number;
  portfolioValue: number;
  trades: number;
}

interface MonthlyStats {
  month: string;
  profit: number;
  trades: number;
  winRate: number;
}

interface PortfolioSummary {
  total_value: number;
  cash: number;
  buying_power: number;
  total_pl: number;
  total_pl_percent: number;
  day_pl: number;
  day_pl_percent: number;
  num_positions: number;
  num_winning: number;
  num_losing: number;
  largest_winner?: { symbol: string; pl: number; pl_percent: number };
  largest_loser?: { symbol: string; pl: number; pl_percent: number };
}

function PortfolioSummaryCard() {
  const isMobile = useIsMobile();
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSummary();
    // Refresh every 30 seconds
    const interval = setInterval(loadSummary, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSummary = async () => {
    try {
      const response = await fetch('/api/proxy/portfolio/summary');
      const data = await response.json();
      setSummary(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load portfolio summary:', error);
      setLoading(false);
    }
  };

  if (loading || !summary) {
    return null;
  }

  return (
    <Card style={{ marginBottom: theme.spacing.lg }} glow="teal">
      <h3 style={{ margin: `0 0 ${theme.spacing.md} 0`, color: theme.colors.text, fontSize: '18px' }}>
        Portfolio Summary
      </h3>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: theme.spacing.md,
      }}>
        {/* Total Value */}
        <div>
          <p style={{ fontSize: '12px', color: theme.colors.textMuted, margin: `0 0 ${theme.spacing.xs} 0` }}>
            Total Value
          </p>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: theme.colors.text, margin: 0 }}>
            ${summary.total_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </p>
        </div>

        {/* Total P&L */}
        <div>
          <p style={{ fontSize: '12px', color: theme.colors.textMuted, margin: `0 0 ${theme.spacing.xs} 0` }}>
            Total P&L
          </p>
          <p style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: summary.total_pl >= 0 ? theme.colors.primary : theme.colors.danger,
            margin: 0
          }}>
            {summary.total_pl >= 0 ? '+' : ''}${summary.total_pl.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            <span style={{ fontSize: '16px', marginLeft: theme.spacing.xs }}>
              ({summary.total_pl_percent >= 0 ? '+' : ''}{summary.total_pl_percent.toFixed(2)}%)
            </span>
          </p>
        </div>

        {/* Day P&L */}
        <div>
          <p style={{ fontSize: '12px', color: theme.colors.textMuted, margin: `0 0 ${theme.spacing.xs} 0` }}>
            Today&apos;s P&L
          </p>
          <p style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: summary.day_pl >= 0 ? theme.colors.primary : theme.colors.danger,
            margin: 0
          }}>
            {summary.day_pl >= 0 ? '+' : ''}${summary.day_pl.toLocaleString('en-US', { minimumFractionDigits: 2 })}
            <span style={{ fontSize: '16px', marginLeft: theme.spacing.xs }}>
              ({summary.day_pl_percent >= 0 ? '+' : ''}{summary.day_pl_percent.toFixed(2)}%)
            </span>
          </p>
        </div>

        {/* Positions */}
        <div>
          <p style={{ fontSize: '12px', color: theme.colors.textMuted, margin: `0 0 ${theme.spacing.xs} 0` }}>
            Positions
          </p>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: theme.colors.text, margin: 0 }}>
            {summary.num_positions}
            <span style={{ fontSize: '16px', marginLeft: theme.spacing.xs, color: theme.colors.textMuted }}>
              ({summary.num_winning}W / {summary.num_losing}L)
            </span>
          </p>
        </div>
      </div>

      {/* Largest Winner/Loser */}
      {(summary.largest_winner || summary.largest_loser) && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
          gap: theme.spacing.md,
          marginTop: theme.spacing.md,
          paddingTop: theme.spacing.md,
          borderTop: `1px solid ${theme.colors.border}`,
        }}>
          {summary.largest_winner && (
            <div>
              <p style={{ fontSize: '12px', color: theme.colors.textMuted, margin: `0 0 ${theme.spacing.xs} 0` }}>
                Largest Winner
              </p>
              <p style={{ fontSize: '18px', fontWeight: 'bold', color: theme.colors.text, margin: 0 }}>
                {summary.largest_winner.symbol}
              </p>
              <p style={{ fontSize: '16px', color: theme.colors.primary, margin: `${theme.spacing.xs} 0 0 0` }}>
                +${summary.largest_winner.pl.toFixed(2)} (+{summary.largest_winner.pl_percent.toFixed(2)}%)
              </p>
            </div>
          )}

          {summary.largest_loser && (
            <div>
              <p style={{ fontSize: '12px', color: theme.colors.textMuted, margin: `0 0 ${theme.spacing.xs} 0` }}>
                Largest Loser
              </p>
              <p style={{ fontSize: '18px', fontWeight: 'bold', color: theme.colors.text, margin: 0 }}>
                {summary.largest_loser.symbol}
              </p>
              <p style={{ fontSize: '16px', color: theme.colors.danger, margin: `${theme.spacing.xs} 0 0 0` }}>
                ${summary.largest_loser.pl.toFixed(2)} ({summary.largest_loser.pl_percent.toFixed(2)}%)
              </p>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

export default function Analytics() {
  const [timeframe, setTimeframe] = useState<'1W' | '1M' | '3M' | '1Y' | 'ALL'>('1M');
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [dailyPerformance, setDailyPerformance] = useState<DailyPerformance[]>([]);
  const [monthlyStats, setMonthlyStats] = useState<MonthlyStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);

  // Mobile responsiveness
  const isMobile = useIsMobile();

  // Chart refs for export functionality
  const equityChartRef = useRef<HTMLDivElement>(null);
  const pnlChartRef = useRef<HTMLDivElement>(null);

  // Export chart as PNG
  const exportChartAsPNG = async (chartRef: React.RefObject<HTMLDivElement>, chartName: string) => {
    if (!chartRef.current) return;

    try {
      const canvas = await html2canvas(chartRef.current, {
        backgroundColor: theme.background.card,
        scale: 2, // Higher quality
      });

      const link = document.createElement('a');
      link.download = `PaiiD_${chartName}_${new Date().toISOString().split('T')[0]}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    } catch (error) {
      console.error('Failed to export chart:', error);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [timeframe]);

  const loadAnalytics = async () => {
    setLoading(true);

    try {
      // Fetch performance metrics from new analytics backend
      const perfResponse = await fetch(`/api/proxy/analytics/performance?period=${timeframe}`);
      const perfData = await perfResponse.json();

      // Fetch portfolio history
      const historyResponse = await fetch(`/api/proxy/portfolio/history?period=${timeframe}`);
      const historyData = await historyResponse.json();

      // Transform backend data to match component interface
      const metricsData: PerformanceMetrics = {
        totalReturn: perfData.total_return,
        totalReturnPercent: perfData.total_return_percent,
        winRate: perfData.win_rate,
        profitFactor: perfData.profit_factor,
        sharpeRatio: perfData.sharpe_ratio,
        maxDrawdown: perfData.max_drawdown_percent,
        avgWin: perfData.avg_win,
        avgLoss: Math.abs(perfData.avg_loss),
        totalTrades: perfData.num_trades,
        winningTrades: perfData.num_wins,
        losingTrades: perfData.num_losses,
      };

      // Transform equity history to daily performance format
      const dailyPerf: DailyPerformance[] = historyData.data.map((point: any) => ({
        date: point.timestamp.split('T')[0],
        pnl: 0, // Calculate from equity changes
        portfolioValue: point.equity,
        trades: 0,
      }));

      // Calculate daily P&L from equity changes
      for (let i = 1; i < dailyPerf.length; i++) {
        dailyPerf[i].pnl = dailyPerf[i].portfolioValue - dailyPerf[i - 1].portfolioValue;
      }

      const monthlyData = generateMonthlyStats(); // Keep this for now

      setMetrics(metricsData);
      setDailyPerformance(dailyPerf);
      setMonthlyStats(monthlyData);
    } catch (error) {
      console.error('Failed to load analytics:', error);

      // Fallback to generating DEMO data if API fails
      setIsDemoMode(true);

      const mockMetrics: PerformanceMetrics = {
        totalReturn: 2500,
        totalReturnPercent: 2.5,
        winRate: 58.5,
        profitFactor: 2.13,
        sharpeRatio: 1.42,
        maxDrawdown: -12.3,
        avgWin: 142.50,
        avgLoss: 87.30,
        totalTrades: 47,
        winningTrades: 27,
        losingTrades: 20,
      };

      const mockDaily = generateDailyPerformance(timeframe);
      const mockMonthly = generateMonthlyStats();

      setMetrics(mockMetrics);
      setDailyPerformance(mockDaily);
      setMonthlyStats(mockMonthly);
    } finally {
      setLoading(false);
    }
  };

  const generateDailyPerformance = (tf: string): DailyPerformance[] => {
    const days = tf === '1W' ? 7 : tf === '1M' ? 30 : tf === '3M' ? 90 : tf === '1Y' ? 365 : 365;
    const data: DailyPerformance[] = [];
    let portfolioValue = 100000;

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const pnl = (Math.random() - 0.45) * 500;
      portfolioValue += pnl;
      data.push({
        date: date.toISOString().split('T')[0],
        pnl,
        portfolioValue,
        trades: Math.floor(Math.random() * 5),
      });
    }
    return data;
  };

  const generateMonthlyStats = (): MonthlyStats[] => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const currentMonth = new Date().getMonth();
    const stats: MonthlyStats[] = [];

    for (let i = 0; i < 6; i++) {
      const monthIndex = (currentMonth - i + 12) % 12;
      stats.unshift({
        month: months[monthIndex],
        profit: (Math.random() - 0.3) * 5000,
        trades: Math.floor(Math.random() * 50) + 20,
        winRate: 50 + Math.random() * 20,
      });
    }
    return stats;
  };

  if (loading) {
    return (
      <div style={{ padding: theme.spacing.lg }}>
        <Card>
          <div style={{ textAlign: 'center', padding: theme.spacing.xl, color: theme.colors.textMuted }}>
            Loading analytics...
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: isMobile ? theme.spacing.md : theme.spacing.lg }}>
      {/* DEMO MODE Banner */}
      {isDemoMode && (
        <div style={{
          background: 'rgba(251, 191, 36, 0.1)',
          border: '2px solid rgba(251, 191, 36, 0.5)',
          borderRadius: theme.borderRadius.lg,
          padding: theme.spacing.md,
          marginBottom: theme.spacing.lg,
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing.md,
        }}>
          <div style={{
            background: 'rgba(251, 191, 36, 0.2)',
            borderRadius: '50%',
            padding: theme.spacing.sm,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <span style={{ fontSize: '24px' }}>⚠️</span>
          </div>
          <div>
            <h3 style={{
              margin: 0,
              color: '#fbbf24',
              fontSize: '16px',
              fontWeight: '700',
            }}>
              DEMO MODE
            </h3>
            <p style={{
              margin: `${theme.spacing.xs} 0 0 0`,
              color: theme.colors.textMuted,
              fontSize: '14px',
            }}>
              Using sample data - API unavailable. This is demonstration data only.
            </p>
          </div>
        </div>
      )}

      {/* Header with PaiiD Logo */}
      <div style={{
        display: 'flex',
        alignItems: isMobile ? 'flex-start' : 'center',
        justifyContent: 'space-between',
        marginBottom: theme.spacing.lg,
        flexDirection: isMobile ? 'column' : 'row',
        gap: isMobile ? theme.spacing.md : '0'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.md }}>
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

          <BarChart3 size={isMobile ? 24 : 32} color={theme.colors.info} />
          <h1 style={{
            margin: 0,
            fontSize: isMobile ? '24px' : '32px',
            fontWeight: '700',
            color: theme.colors.text,
            textShadow: `0 0 20px ${theme.colors.info}40`,
          }}>
            Analytics Dashboard
          </h1>
        </div>

        {/* Timeframe Selector */}
        <div style={{
          display: 'flex',
          gap: theme.spacing.xs,
          flexWrap: 'wrap',
          width: isMobile ? '100%' : 'auto'
        }}>
          {(['1W', '1M', '3M', '1Y', 'ALL'] as const).map((tf) => (
            <Button
              key={tf}
              variant={timeframe === tf ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setTimeframe(tf)}
              style={{ flex: isMobile ? '1' : 'none', minWidth: isMobile ? '0' : 'auto' }}
            >
              {tf}
            </Button>
          ))}
        </div>
      </div>

      {/* Portfolio Summary Card */}
      <PortfolioSummaryCard />

      {/* Performance Metrics */}
      {metrics && (
        <>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: theme.spacing.md,
            marginBottom: theme.spacing.lg,
          }}>
            <MetricCard
              icon={<DollarSign size={20} color={metrics.totalReturn >= 0 ? theme.colors.primary : theme.colors.danger} />}
              label="Total Return"
              value={`$${Math.abs(metrics.totalReturn).toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
              subValue={`${metrics.totalReturnPercent >= 0 ? '+' : ''}${metrics.totalReturnPercent.toFixed(2)}%`}
              valueColor={metrics.totalReturn >= 0 ? theme.colors.primary : theme.colors.danger}
            />
            <MetricCard
              icon={<Percent size={20} color={theme.colors.secondary} />}
              label="Win Rate"
              value={`${metrics.winRate.toFixed(1)}%`}
              subValue={`${metrics.winningTrades}W / ${metrics.losingTrades}L`}
            />
            <MetricCard
              icon={<Target size={20} color={theme.colors.primary} />}
              label="Profit Factor"
              value={metrics.profitFactor.toFixed(2)}
              valueColor={metrics.profitFactor > 1 ? theme.colors.primary : theme.colors.danger}
            />
            <MetricCard
              icon={<Award size={20} color={theme.colors.info} />}
              label="Sharpe Ratio"
              value={metrics.sharpeRatio.toFixed(2)}
              valueColor={metrics.sharpeRatio > 1 ? theme.colors.primary : theme.colors.warning}
            />
            <MetricCard
              icon={<TrendingDown size={20} color={theme.colors.danger} />}
              label="Max Drawdown"
              value={`${metrics.maxDrawdown.toFixed(2)}%`}
              valueColor={theme.colors.danger}
            />
            <MetricCard
              icon={<BarChart3 size={20} color={theme.colors.secondary} />}
              label="Total Trades"
              value={metrics.totalTrades.toString()}
            />
          </div>

          {/* Equity Curve */}
          <Card style={{ marginBottom: theme.spacing.lg }} glow="teal">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.md }}>
              <h3 style={{ margin: 0, color: theme.colors.text, fontSize: '18px' }}>
                Portfolio Value Over Time
              </h3>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => exportChartAsPNG(equityChartRef, 'Equity_Curve')}
                style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.xs }}
              >
                <Download size={16} />
                {!isMobile && 'Export'}
              </Button>
            </div>
            <div
              ref={equityChartRef}
              style={{
                height: isMobile ? '200px' : '300px',
                display: 'flex',
                alignItems: 'flex-end',
                gap: '2px',
                padding: theme.spacing.md,
                background: theme.background.input,
                borderRadius: theme.borderRadius.sm,
              }}
            >
              {dailyPerformance.filter((_, i) => {
                // Sample data based on timeframe
                const sampleRate = timeframe === '1W' ? 1 : timeframe === '1M' ? 1 : timeframe === '3M' ? 3 : 7;
                return i % sampleRate === 0;
              }).map((point, index) => {
                const minValue = Math.min(...dailyPerformance.map(d => d.portfolioValue));
                const maxValue = Math.max(...dailyPerformance.map(d => d.portfolioValue));
                const range = maxValue - minValue;
                const height = range > 0 ? ((point.portfolioValue - minValue) / range) * 100 : 50;

                return (
                  <div
                    key={index}
                    style={{
                      flex: 1,
                      height: `${Math.max(height, 5)}%`,
                      background: point.portfolioValue > 100000 ? theme.colors.primary : theme.colors.danger,
                      borderRadius: '2px 2px 0 0',
                      transition: theme.transitions.fast,
                    }}
                    title={`${point.date}: $${point.portfolioValue.toFixed(2)}`}
                  />
                );
              })}
            </div>
          </Card>

          {/* Daily P&L Chart */}
          <Card style={{ marginBottom: theme.spacing.lg }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: theme.spacing.md }}>
              <h3 style={{ margin: 0, color: theme.colors.text, fontSize: '18px' }}>
                Daily P&L
              </h3>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => exportChartAsPNG(pnlChartRef, 'Daily_PnL')}
                style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.xs }}
              >
                <Download size={16} />
                {!isMobile && 'Export'}
              </Button>
            </div>
            <div
              ref={pnlChartRef}
              style={{
                height: isMobile ? '150px' : '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '2px',
                padding: theme.spacing.md,
                background: theme.background.input,
                borderRadius: theme.borderRadius.sm,
              }}
            >
              {dailyPerformance.filter((_, i) => {
                const sampleRate = timeframe === '1W' ? 1 : timeframe === '1M' ? 1 : timeframe === '3M' ? 3 : 7;
                return i % sampleRate === 0;
              }).map((point, index) => {
                const maxPnl = Math.max(...dailyPerformance.map(d => Math.abs(d.pnl)));
                const height = maxPnl > 0 ? (Math.abs(point.pnl) / maxPnl) * 90 : 10;

                return (
                  <div
                    key={index}
                    style={{
                      flex: 1,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: point.pnl >= 0 ? 'flex-end' : 'flex-start',
                      height: '100%',
                    }}
                  >
                    <div
                      style={{
                        width: '100%',
                        height: `${height}%`,
                        background: point.pnl >= 0 ? theme.colors.primary : theme.colors.danger,
                        borderRadius: '2px',
                        transition: theme.transitions.fast,
                      }}
                      title={`${point.date}: ${point.pnl >= 0 ? '+' : ''}$${point.pnl.toFixed(2)}`}
                    />
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Monthly Performance */}
          <Card style={{ marginBottom: theme.spacing.lg }}>
            <h3 style={{ margin: `0 0 ${theme.spacing.md} 0`, color: theme.colors.text, fontSize: '18px' }}>
              Monthly Performance
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: theme.spacing.md }}>
              {monthlyStats.map((stat, index) => (
                <div key={index} style={{
                  padding: theme.spacing.md,
                  background: theme.background.input,
                  borderRadius: theme.borderRadius.md,
                  borderLeft: `4px solid ${stat.profit >= 0 ? theme.colors.primary : theme.colors.danger}`,
                }}>
                  <p style={{ margin: 0, fontSize: '12px', color: theme.colors.textMuted }}>{stat.month}</p>
                  <p style={{
                    margin: `${theme.spacing.xs} 0`,
                    fontSize: '20px',
                    fontWeight: '700',
                    color: stat.profit >= 0 ? theme.colors.primary : theme.colors.danger,
                  }}>
                    {stat.profit >= 0 ? '+' : ''}${stat.profit.toFixed(0)}
                  </p>
                  <p style={{ margin: 0, fontSize: '12px', color: theme.colors.textMuted }}>
                    {stat.trades} trades · {stat.winRate.toFixed(0)}% win
                  </p>
                </div>
              ))}
            </div>
          </Card>

          {/* TradingView Chart */}
          <div style={{ marginBottom: theme.spacing.lg }}>
            <TradingViewChart symbol="$DJI.IX" height={isMobile ? 400 : 600} />
          </div>

          {/* Trade Statistics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: theme.spacing.md }}>
            <Card>
              <h3 style={{ margin: `0 0 ${theme.spacing.md} 0`, color: theme.colors.text, fontSize: '18px' }}>
                Win/Loss Analysis
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.sm }}>
                <StatRow label="Average Win" value={`$${metrics.avgWin.toFixed(2)}`} color={theme.colors.primary} />
                <StatRow label="Average Loss" value={`$${Math.abs(metrics.avgLoss).toFixed(2)}`} color={theme.colors.danger} />
                <StatRow label="Win/Loss Ratio" value={(metrics.avgWin / Math.abs(metrics.avgLoss)).toFixed(2)} />
              </div>
            </Card>

            <Card>
              <h3 style={{ margin: `0 0 ${theme.spacing.md} 0`, color: theme.colors.text, fontSize: '18px' }}>
                Risk Metrics
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.sm }}>
                <StatRow label="Sharpe Ratio" value={metrics.sharpeRatio.toFixed(2)} />
                <StatRow label="Profit Factor" value={metrics.profitFactor.toFixed(2)} />
                <StatRow label="Max Drawdown" value={`${metrics.maxDrawdown.toFixed(2)}%`} color={theme.colors.danger} />
              </div>
            </Card>
          </div>
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
        margin: 0,
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

function StatRow({ label, value, color }: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ fontSize: '14px', color: theme.colors.textMuted }}>{label}</span>
      <span style={{ fontSize: '16px', fontWeight: '600', color: color || theme.colors.text }}>{value}</span>
    </div>
  );
}
