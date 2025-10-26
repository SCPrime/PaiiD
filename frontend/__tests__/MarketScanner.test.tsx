import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MarketScanner from '../components/MarketScanner';

// Mock dependencies
jest.mock('../lib/logger');
jest.mock('../lib/api');
jest.mock('../hooks/useBreakpoint', () => ({
  useIsMobile: () => false,
}));

// Mock dynamic import for StockLookup
jest.mock('next/dynamic', () => () => {
  const DynamicComponent = () => <div>StockLookup Component</div>;
  DynamicComponent.displayName = 'StockLookup';
  return DynamicComponent;
});

describe('MarketScanner', () => {
  const mockScanResults = [
    {
      symbol: 'AAPL',
      price: 150.0,
      change: 2.5,
      changePercent: 1.69,
      volume: 50000000,
      avgVolume: 48000000,
      signal: 'buy' as const,
      indicators: {
        rsi: 62.5,
        macd: 'bullish' as const,
        movingAverage: '50_above' as const,
        volumeProfile: 'high' as const,
      },
      pattern: 'Bull Flag',
      reason: 'Breaking above 20-day MA with strong volume',
    },
    {
      symbol: 'TSLA',
      price: 240.0,
      change: -5.0,
      changePercent: -2.04,
      volume: 120000000,
      avgVolume: 90000000,
      signal: 'sell' as const,
      indicators: {
        rsi: 32.8,
        macd: 'bearish' as const,
        movingAverage: '50_below' as const,
        volumeProfile: 'high' as const,
      },
      pattern: 'Head and Shoulders',
      reason: 'Breaking down from support',
    },
  ];

  beforeEach(() => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ results: mockScanResults }),
    } as Response);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<MarketScanner />);
    expect(screen.getByText(/Market Scanner/i)).toBeInTheDocument();
  });

  it('displays scan type buttons', () => {
    render(<MarketScanner />);

    expect(screen.getByText('Momentum')).toBeInTheDocument();
    expect(screen.getByText('Breakout')).toBeInTheDocument();
    expect(screen.getByText('Reversal')).toBeInTheDocument();
    expect(screen.getByText('Custom')).toBeInTheDocument();
  });

  it('displays filter inputs', () => {
    render(<MarketScanner />);

    expect(screen.getByLabelText(/Min Price/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Max Price/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Min Volume/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Signal Type/i)).toBeInTheDocument();
  });

  it('loads scan results on mount', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('TSLA')).toBeInTheDocument();
    });
  });

  it('displays loading state', async () => {
    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ ok: true, json: async () => ({ results: [] }) }), 100))
    );

    render(<MarketScanner />);

    // Initial loading state is shown
    expect(screen.getByText(/Market Scanner/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  it('displays scan results after loading', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText(/Bull Flag/i)).toBeInTheDocument();
    });
  });

  it('shows signal badges', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText('Buy')).toBeInTheDocument();
      expect(screen.getByText('Sell')).toBeInTheDocument();
    });
  });

  it('displays technical indicators', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText('RSI')).toBeInTheDocument();
      expect(screen.getByText('MACD')).toBeInTheDocument();
      expect(screen.getByText('Volume')).toBeInTheDocument();
    });
  });

  it('changes scan type when button clicked', async () => {
    render(<MarketScanner />);

    const breakoutButton = screen.getByText('Breakout');
    fireEvent.click(breakoutButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('scanType=breakout'),
        expect.any(Object)
      );
    });
  });

  it('updates filters', async () => {
    render(<MarketScanner />);

    const minPriceInput = screen.getByLabelText(/Min Price/i) as HTMLInputElement;
    fireEvent.change(minPriceInput, { target: { value: '50' } });

    expect(minPriceInput.value).toBe('50');
  });

  it('refreshes scan when button clicked', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const scanButton = screen.getByText(/Scan Market/i);
    fireEvent.click(scanButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2); // Initial + manual scan
    });
  });

  it('displays empty state when no results', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ results: [] }),
    });

    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText(/No opportunities found/i)).toBeInTheDocument();
    });
  });

  it('opens research panel when research button clicked', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const researchButtons = screen.getAllByText('Research');
    fireEvent.click(researchButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Detailed Research/i)).toBeInTheDocument();
    });
  });

  it('allows direct symbol search', () => {
    render(<MarketScanner />);

    const searchInput = screen.getByPlaceholderText(/Enter symbol/i) as HTMLInputElement;
    fireEvent.change(searchInput, { target: { value: 'AAPL' } });

    expect(searchInput.value).toBe('AAPL');
  });

  it('opens research on symbol search', async () => {
    render(<MarketScanner />);

    const searchInput = screen.getByPlaceholderText(/Enter symbol/i);
    fireEvent.change(searchInput, { target: { value: 'AAPL' } });

    const searchButton = screen.getAllByText(/Research/i)[0];
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText(/Detailed Research/i)).toBeInTheDocument();
    });
  });

  it('closes research panel when close button clicked', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const researchButtons = screen.getAllByText('Research');
    fireEvent.click(researchButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Detailed Research/i)).toBeInTheDocument();
    });

    const closeButton = screen.getByText(/Close/i);
    fireEvent.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText(/Detailed Research/i)).not.toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText(/No opportunities found/i)).toBeInTheDocument();
    });
  });

  it('displays pattern information', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText('Bull Flag')).toBeInTheDocument();
      expect(screen.getByText('Head and Shoulders')).toBeInTheDocument();
    });
  });

  it('shows analysis reason', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText(/Breaking above 20-day MA/i)).toBeInTheDocument();
    });
  });

  it('formats volume correctly', async () => {
    render(<MarketScanner />);

    await waitFor(() => {
      expect(screen.getByText(/50.0M/i)).toBeInTheDocument();
    });
  });

  it('allows filtering by signal type', async () => {
    render(<MarketScanner />);

    const signalTypeSelect = screen.getByLabelText(/Signal Type/i) as HTMLSelectElement;
    fireEvent.change(signalTypeSelect, { target: { value: 'buy' } });

    expect(signalTypeSelect.value).toBe('buy');
  });
});
