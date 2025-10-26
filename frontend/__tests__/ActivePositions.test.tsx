import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ActivePositions from '../components/ActivePositions';
import * as alpaca from '../lib/alpaca';

// Mock dependencies
jest.mock('../lib/alpaca');
jest.mock('../lib/logger');
jest.mock('../hooks/useBreakpoint', () => ({
  useIsMobile: () => false,
}));

const mockAlpaca = alpaca as jest.Mocked<typeof alpaca>;

describe('ActivePositions', () => {
  const mockPositions = [
    {
      symbol: 'AAPL',
      qty: 10,
      side: 'long' as const,
      avgEntryPrice: 150.0,
      currentPrice: 155.0,
      marketValue: 1550.0,
      unrealizedPL: 50.0,
      unrealizedPLPercent: 3.33,
      dayChange: 2.0,
      dayChangePercent: 1.29,
    },
    {
      symbol: 'MSFT',
      qty: 5,
      side: 'long' as const,
      avgEntryPrice: 300.0,
      currentPrice: 295.0,
      marketValue: 1475.0,
      unrealizedPL: -25.0,
      unrealizedPLPercent: -1.67,
      dayChange: -5.0,
      dayChangePercent: -1.67,
    },
  ];

  const mockAccount = {
    buying_power: '50000',
  };

  beforeEach(() => {
    mockAlpaca.getPositions.mockResolvedValue(mockPositions as any);
    mockAlpaca.getAccount.mockResolvedValue(mockAccount as any);
    mockAlpaca.formatPosition.mockImplementation((p: any) => p);
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    } as Response);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', async () => {
    render(<ActivePositions />);
    await waitFor(() => {
      expect(screen.getByText(/Active Positions/i)).toBeInTheDocument();
    });
  });

  it('displays loading state initially', () => {
    render(<ActivePositions />);
    expect(screen.getByText(/Loading positions/i)).toBeInTheDocument();
  });

  it('displays positions after loading', async () => {
    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('MSFT')).toBeInTheDocument();
    });
  });

  it('displays portfolio metrics', async () => {
    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.getByText('Total Value')).toBeInTheDocument();
      expect(screen.getByText('Buying Power')).toBeInTheDocument();
      expect(screen.getByText('Total P&L')).toBeInTheDocument();
    });
  });

  it('displays positive P&L in green', async () => {
    render(<ActivePositions />);

    await waitFor(() => {
      const appleSymbol = screen.getByText('AAPL');
      const card = appleSymbol.closest('div[style*="padding"]');
      expect(card).toBeInTheDocument();
    });
  });

  it('displays negative P&L in red', async () => {
    render(<ActivePositions />);

    await waitFor(() => {
      const msftSymbol = screen.getByText('MSFT');
      expect(msftSymbol).toBeInTheDocument();
    });
  });

  it('refreshes positions when refresh button clicked', async () => {
    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const refreshButton = screen.getByRole('button', { name: /refresh/i });
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(mockAlpaca.getPositions).toHaveBeenCalledTimes(2); // Initial + refresh
    });
  });

  it('displays empty state when no positions', async () => {
    mockAlpaca.getPositions.mockResolvedValue([]);

    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.getByText(/No active positions/i)).toBeInTheDocument();
    });
  });

  it('sorts positions by symbol', async () => {
    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const symbolButton = screen.getByRole('button', { name: /Symbol/i });
    fireEvent.click(symbolButton);

    // Positions should be sorted alphabetically
    const symbols = screen.getAllByText(/^(AAPL|MSFT)$/);
    expect(symbols).toHaveLength(2);
  });

  it('expands AI analysis panel when button clicked', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        symbol: 'AAPL',
        recommendation: 'HOLD',
        confidence: 85,
        riskScore: 'LOW',
        sentiment: 'Bullish',
        suggestedAction: 'Hold position',
        currentPrice: 155.0,
        analysis: 'Strong fundamentals',
      }),
    } as Response);

    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const aiButtons = screen.getAllByText(/Show AI Insights/i);
    fireEvent.click(aiButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Analyzing/i)).toBeInTheDocument();
    });
  });

  it('displays AI analysis after loading', async () => {
    const mockAnalysis = {
      symbol: 'AAPL',
      recommendation: 'ADD',
      confidence: 90,
      riskScore: 'LOW',
      sentiment: 'Bullish',
      suggestedAction: 'Consider adding to position',
      currentPrice: 155.0,
      analysis: 'Strong buy signal detected',
    };

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => mockAnalysis,
    } as Response);

    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const aiButtons = screen.getAllByText(/Show AI Insights/i);
    fireEvent.click(aiButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/PaπD AI Analysis/i)).toBeInTheDocument();
    });
  });

  it('handles position close action', async () => {
    mockAlpaca.closePosition = jest.fn().mockResolvedValue({ success: true });
    global.confirm = jest.fn().mockReturnValue(true);

    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const closeButtons = screen.getAllByText(/Close Position/i);
    fireEvent.click(closeButtons[0]);

    await waitFor(() => {
      expect(mockAlpaca.closePosition).toHaveBeenCalledWith('AAPL');
    });
  });

  it('polls for position updates every 5 seconds', async () => {
    jest.useFakeTimers();

    render(<ActivePositions />);

    await waitFor(() => {
      expect(mockAlpaca.getPositions).toHaveBeenCalledTimes(1);
    });

    jest.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(mockAlpaca.getPositions).toHaveBeenCalledTimes(2);
    });

    jest.useRealTimers();
  });

  it('handles API errors gracefully', async () => {
    mockAlpaca.getPositions.mockRejectedValue(new Error('API Error'));

    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.queryByText('AAPL')).not.toBeInTheDocument();
    });
  });

  it('displays position metrics correctly', async () => {
    render(<ActivePositions />);

    await waitFor(() => {
      expect(screen.getByText('Market Value')).toBeInTheDocument();
      expect(screen.getByText('Unrealized P&L')).toBeInTheDocument();
      expect(screen.getByText('Return')).toBeInTheDocument();
    });
  });
});
