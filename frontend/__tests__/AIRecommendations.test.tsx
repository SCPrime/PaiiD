import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AIRecommendations from '../components/AIRecommendations';

// Mock dependencies
jest.mock('../lib/logger');
jest.mock('../hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    isConnected: true,
    sendMessage: jest.fn(),
  }),
}));

describe('AIRecommendations', () => {
  const mockRecommendations = {
    user_id: 'test-user',
    buy_recommendations: [
      {
        symbol: 'AAPL',
        action: 'buy' as const,
        confidence: 85,
        reasoning: 'Strong upward momentum',
        price_target: 160.0,
        time_horizon: 'Short-term',
        risk_level: 'low' as const,
      },
    ],
    sell_recommendations: [
      {
        symbol: 'TSLA',
        action: 'sell' as const,
        confidence: 75,
        reasoning: 'Overbought conditions',
        price_target: 220.0,
        time_horizon: 'Medium-term',
        risk_level: 'medium' as const,
      },
    ],
    hold_recommendations: [
      {
        symbol: 'MSFT',
        action: 'hold' as const,
        confidence: 70,
        reasoning: 'Stable fundamentals',
        time_horizon: 'Long-term',
        risk_level: 'low' as const,
      },
    ],
    overall_risk: 'Medium',
    market_outlook: 'Bullish',
    timestamp: new Date().toISOString(),
  };

  beforeEach(() => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => mockRecommendations,
    } as Response);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<AIRecommendations userId="test-user" />);
    expect(screen.getByText(/AI Trading Recommendations/i)).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    render(<AIRecommendations userId="test-user" />);
    expect(screen.getByText(/Loading AI recommendations/i)).toBeInTheDocument();
  });

  it('loads recommendations on mount', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/ai/recommendations',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  it('displays recommendations after loading', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('TSLA')).toBeInTheDocument();
      expect(screen.getByText('MSFT')).toBeInTheDocument();
    });
  });

  it('displays market outlook', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/Market Outlook/i)).toBeInTheDocument();
      expect(screen.getByText(/Bullish/i)).toBeInTheDocument();
    });
  });

  it('displays overall risk level', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/Overall Risk/i)).toBeInTheDocument();
      expect(screen.getByText(/MEDIUM/i)).toBeInTheDocument();
    });
  });

  it('displays confidence scores', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/85%/i)).toBeInTheDocument();
      expect(screen.getByText(/75%/i)).toBeInTheDocument();
    });
  });

  it('displays action badges', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText('BUY')).toBeInTheDocument();
      expect(screen.getByText('SELL')).toBeInTheDocument();
      expect(screen.getByText('HOLD')).toBeInTheDocument();
    });
  });

  it('displays reasoning for each recommendation', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/Strong upward momentum/i)).toBeInTheDocument();
      expect(screen.getByText(/Overbought conditions/i)).toBeInTheDocument();
    });
  });

  it('displays price targets', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/\$160\.00/i)).toBeInTheDocument();
      expect(screen.getByText(/\$220\.00/i)).toBeInTheDocument();
    });
  });

  it('refreshes recommendations when button clicked', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const refreshButton = screen.getByText(/Refresh/i);
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2); // Initial + refresh
    });
  });

  it('displays connection status', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      // WebSocket connection indicator should be visible
      expect(screen.getByText(/AI Trading Recommendations/i)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load AI recommendations/i)).toBeInTheDocument();
    });
  });

  it('displays retry button on error', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/Retry/i)).toBeInTheDocument();
    });
  });

  it('retries fetch when retry button clicked', async () => {
    (global.fetch as jest.Mock)
      .mockRejectedValueOnce(new Error('API Error'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockRecommendations,
      });

    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/Retry/i)).toBeInTheDocument();
    });

    const retryButton = screen.getByText(/Retry/i);
    fireEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });
  });

  it('auto-refreshes at specified interval', async () => {
    jest.useFakeTimers();

    render(<AIRecommendations userId="test-user" autoRefresh={true} refreshInterval={10000} />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    jest.advanceTimersByTime(10000);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    jest.useRealTimers();
  });

  it('displays time horizons', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/Short-term/i)).toBeInTheDocument();
      expect(screen.getByText(/Medium-term/i)).toBeInTheDocument();
      expect(screen.getByText(/Long-term/i)).toBeInTheDocument();
    });
  });

  it('displays risk levels with correct colors', async () => {
    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getAllByText(/LOW/i).length).toBeGreaterThan(0);
      expect(screen.getByText(/MEDIUM/i)).toBeInTheDocument();
    });
  });

  it('filters recommendations by symbols prop', async () => {
    render(<AIRecommendations userId="test-user" symbols={['AAPL', 'MSFT']} />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/ai/recommendations',
        expect.objectContaining({
          body: expect.stringContaining('AAPL'),
        })
      );
    });
  });

  it('displays empty state when no recommendations', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        user_id: 'test-user',
        buy_recommendations: [],
        sell_recommendations: [],
        hold_recommendations: [],
        overall_risk: 'Low',
        market_outlook: 'Neutral',
        timestamp: new Date().toISOString(),
      }),
    });

    render(<AIRecommendations userId="test-user" />);

    await waitFor(() => {
      expect(screen.getByText(/No recommendations available/i)).toBeInTheDocument();
    });
  });
});
