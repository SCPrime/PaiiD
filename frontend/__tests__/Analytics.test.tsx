import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Analytics from '../components/Analytics';

// Mock dependencies
jest.mock('../lib/logger');
jest.mock('../hooks/useBreakpoint', () => ({
  useIsMobile: () => false,
}));
jest.mock('react-hot-toast');

// Mock TradingViewChart component
jest.mock('../components/TradingViewChart', () => {
  return function MockTradingViewChart() {
    return <div>TradingView Chart</div>;
  };
});

// Mock html2canvas
jest.mock('html2canvas', () => {
  return jest.fn(() => Promise.resolve({
    toBlob: (callback: (blob: Blob) => void) => {
      callback(new Blob(['mock'], { type: 'image/png' }));
    },
  }));
});

describe('Analytics', () => {
  const mockPerformanceData = {
    total_return: 2500,
    total_return_percent: 2.5,
    win_rate: 58.5,
    profit_factor: 2.13,
    sharpe_ratio: 1.42,
    max_drawdown_percent: -12.3,
    avg_win: 142.5,
    avg_loss: -87.3,
    num_trades: 47,
    num_wins: 27,
    num_losses: 20,
  };

  const mockHistoryData = {
    data: [
      { timestamp: '2024-01-01T00:00:00Z', equity: 100000 },
      { timestamp: '2024-01-02T00:00:00Z', equity: 101000 },
      { timestamp: '2024-01-03T00:00:00Z', equity: 102000 },
    ],
  };

  const mockSummaryData = {
    total_value: 102500,
    cash: 50000,
    buying_power: 100000,
    total_pl: 2500,
    total_pl_percent: 2.5,
    day_pl: 500,
    day_pl_percent: 0.49,
    num_positions: 5,
    num_winning: 3,
    num_losing: 2,
  };

  beforeEach(() => {
    global.fetch = jest.fn((url: string | URL | Request) => {
      const urlString = typeof url === 'string' ? url : url.toString();
      if (urlString.includes('/analytics/performance')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockPerformanceData,
        } as Response);
      } else if (urlString.includes('/portfolio/history')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockHistoryData,
        } as Response);
      } else if (urlString.includes('/portfolio/summary')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockSummaryData,
        } as Response);
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<Analytics />);
    expect(screen.getByText(/Analytics Dashboard/i)).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    render(<Analytics />);
    expect(screen.getByText(/Loading analytics/i)).toBeInTheDocument();
  });

  it('loads analytics data on mount', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/analytics/performance'),
        undefined
      );
    });
  });

  it('displays performance metrics after loading', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText('Total Return')).toBeInTheDocument();
      expect(screen.getByText('Win Rate')).toBeInTheDocument();
      expect(screen.getByText('Profit Factor')).toBeInTheDocument();
      expect(screen.getByText('Sharpe Ratio')).toBeInTheDocument();
    });
  });

  it('displays timeframe selector', () => {
    render(<Analytics />);

    expect(screen.getByText('1W')).toBeInTheDocument();
    expect(screen.getByText('1M')).toBeInTheDocument();
    expect(screen.getByText('3M')).toBeInTheDocument();
    expect(screen.getByText('1Y')).toBeInTheDocument();
    expect(screen.getByText('ALL')).toBeInTheDocument();
  });

  it('changes timeframe when button clicked', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/Analytics Dashboard/i)).toBeInTheDocument();
    });

    const timeframeButton = screen.getByText('3M');
    fireEvent.click(timeframeButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('period=3M'),
        undefined
      );
    });
  });

  it('displays portfolio summary card', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText('Portfolio Summary')).toBeInTheDocument();
    });
  });

  it('displays equity curve chart', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/Portfolio Value Over Time/i)).toBeInTheDocument();
    });
  });

  it('displays daily P&L chart', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/Daily P&L/i)).toBeInTheDocument();
    });
  });

  it('displays monthly performance', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/Monthly Performance/i)).toBeInTheDocument();
    });
  });

  it('displays TradingView chart', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText('TradingView Chart')).toBeInTheDocument();
    });
  });

  it('exports equity chart as PNG', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/Portfolio Value Over Time/i)).toBeInTheDocument();
    });

    const exportButtons = screen.getAllByText(/Export/i);
    fireEvent.click(exportButtons[0]);

    await waitFor(() => {
      // html2canvas should have been called
      const html2canvas = require('html2canvas');
      expect(html2canvas).toHaveBeenCalled();
    });
  });

  it('displays AI portfolio analysis button', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/AI Portfolio Health Check/i)).toBeInTheDocument();
    });
  });

  it('fetches AI analysis when button clicked', async () => {
    const mockAIAnalysis = {
      health_score: 85,
      risk_level: 'Medium',
      diversification_score: 75,
      ai_summary: 'Portfolio is well-balanced',
      recommendations: ['Consider rebalancing', 'Reduce tech exposure'],
      risk_factors: ['High concentration in tech'],
      opportunities: ['Add defensive stocks'],
    };

    global.fetch = jest.fn((url: string | URL | Request) => {
      const urlString = typeof url === 'string' ? url : url.toString();
      if (urlString.includes('/ai/analyze-portfolio')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockAIAnalysis,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        json: async () => ({}),
      } as Response);
    });

    render(<Analytics />);

    await waitFor(() => {
      const aiButton = screen.getByText(/AI Portfolio Health Check/i);
      fireEvent.click(aiButton);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/ai/analyze-portfolio'),
        expect.any(Object)
      );
    });
  });

  it('displays AI analysis results', async () => {
    const mockAIAnalysis = {
      health_score: 85,
      risk_level: 'Medium',
      diversification_score: 75,
      ai_summary: 'Portfolio is well-balanced',
      recommendations: ['Consider rebalancing', 'Reduce tech exposure'],
    };

    global.fetch = jest.fn((url: string | URL | Request) => {
      const urlString = typeof url === 'string' ? url : url.toString();
      if (urlString.includes('/ai/analyze-portfolio')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockAIAnalysis,
        } as Response);
      }
      return Promise.resolve({
        ok: true,
        json: async () => ({}),
      } as Response);
    });

    render(<Analytics />);

    await waitFor(() => {
      const aiButton = screen.getByText(/AI Portfolio Health Check/i);
      fireEvent.click(aiButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/85\/100/i)).toBeInTheDocument();
      expect(screen.getByText(/Portfolio is well-balanced/i)).toBeInTheDocument();
    });
  });

  it('displays demo mode banner when API fails', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('API Error'));

    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/DEMO MODE/i)).toBeInTheDocument();
    });
  });

  it('displays win/loss analysis', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/Win\/Loss Analysis/i)).toBeInTheDocument();
      expect(screen.getByText('Average Win')).toBeInTheDocument();
      expect(screen.getByText('Average Loss')).toBeInTheDocument();
    });
  });

  it('displays risk metrics', async () => {
    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/Risk Metrics/i)).toBeInTheDocument();
      expect(screen.getByText('Max Drawdown')).toBeInTheDocument();
    });
  });

  it('handles chart export errors gracefully', async () => {
    const html2canvas = require('html2canvas');
    html2canvas.mockRejectedValueOnce(new Error('Export failed'));

    render(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/Portfolio Value Over Time/i)).toBeInTheDocument();
    });

    const exportButtons = screen.getAllByText(/Export/i);
    fireEvent.click(exportButtons[0]);

    await waitFor(() => {
      expect(html2canvas).toHaveBeenCalled();
    });
  });
});
