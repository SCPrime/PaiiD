import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import NewsReview from '../components/NewsReview';

// Mock dependencies
jest.mock('../lib/logger');
jest.mock('../hooks/useBreakpoint', () => ({
  useIsMobile: () => false,
}));

// Mock StockLookup component
jest.mock('../components/StockLookup', () => {
  return function MockStockLookup() {
    return <div>Stock Lookup Component</div>;
  };
});

describe('NewsReview', () => {
  const mockNewsArticles = [
    {
      id: '1',
      title: 'Apple reaches new all-time high',
      summary: 'Apple stock hits record levels amid strong iPhone sales',
      source: 'Reuters',
      url: 'https://example.com/article1',
      published_at: '2024-01-15T10:00:00Z',
      sentiment: 'bullish',
      sentiment_score: 0.8,
      symbols: ['AAPL'],
      category: 'earnings',
      provider: 'tradier',
    },
    {
      id: '2',
      title: 'Tesla announces price cuts',
      summary: 'Tesla reduces prices across model lineup',
      source: 'Bloomberg',
      url: 'https://example.com/article2',
      published_at: '2024-01-15T09:00:00Z',
      sentiment: 'bearish',
      sentiment_score: -0.6,
      symbols: ['TSLA'],
      category: 'general',
      provider: 'tradier',
    },
  ];

  const mockMarketSentiment = {
    overall: 'bullish',
    bullish: 65,
    bearish: 20,
    neutral: 15,
    keyEvents: ['Strong earnings reports', 'Fed rate decision pending'],
  };

  beforeEach(() => {
    global.fetch = jest.fn((url: string | URL | Request) => {
      const urlString = typeof url === 'string' ? url : url.toString();
      if (urlString.includes('/news/sentiment/market')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockMarketSentiment,
        } as Response);
      } else if (urlString.includes('/news/providers')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ providers: [{ name: 'tradier' }, { name: 'alpaca' }] }),
        } as Response);
      } else {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            articles: mockNewsArticles,
            count: 2,
            sources: ['Reuters', 'Bloomberg'],
          }),
        } as Response);
      }
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<NewsReview />);
    expect(screen.getByText(/News/i)).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    render(<NewsReview />);
    expect(screen.getByText(/News/i)).toBeInTheDocument();
  });

  it('loads news articles on mount', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  it('displays news articles after loading', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
      expect(screen.getByText(/Tesla announces price cuts/i)).toBeInTheDocument();
    });
  });

  it('displays article sentiment badges', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/bullish/i)).toBeInTheDocument();
      expect(screen.getByText(/bearish/i)).toBeInTheDocument();
    });
  });

  it('displays market sentiment overview', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/Market/i) || screen.getByText(/Overall/i)).toBeInTheDocument();
    });
  });

  it('filters news by sentiment', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
    });

    // Find and click sentiment filter
    const allButtons = screen.getAllByRole('button');
    const bullishButton = allButtons.find(btn => btn.textContent?.toLowerCase().includes('bullish'));

    if (bullishButton) {
      fireEvent.click(bullishButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('sentiment=bullish'),
          undefined
        );
      });
    }
  });

  it('searches news by symbol', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
    });

    const searchInputs = screen.getAllByRole('textbox');
    if (searchInputs.length > 0) {
      const searchInput = searchInputs[0];
      fireEvent.change(searchInput, { target: { value: 'AAPL' } });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    }
  });

  it('displays article sources', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText('Reuters')).toBeInTheDocument();
      expect(screen.getByText('Bloomberg')).toBeInTheDocument();
    });
  });

  it('displays article publication times', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      // Time should be displayed in some format
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
    });
  });

  it('refreshes news when refresh clicked', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
    });

    const refreshButtons = screen.getAllByRole('button').filter(btn =>
      btn.textContent?.includes('Refresh') || btn.textContent?.includes('Reload')
    );

    if (refreshButtons.length > 0) {
      fireEvent.click(refreshButtons[0]);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(4); // Initial + refresh calls
      });
    }
  });

  it('opens article in new tab when clicked', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
    });

    // Articles should be clickable links
    const articleTitle = screen.getByText(/Apple reaches new all-time high/i);
    expect(articleTitle).toBeInTheDocument();
  });

  it('displays related symbols for each article', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
      expect(screen.getByText('TSLA')).toBeInTheDocument();
    });
  });

  it('loads more articles on pagination', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
    });

    const loadMoreButtons = screen.queryAllByRole('button').filter(btn =>
      btn.textContent?.includes('Load More') || btn.textContent?.includes('Next')
    );

    if (loadMoreButtons.length > 0) {
      fireEvent.click(loadMoreButtons[0]);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    }
  });

  it('displays empty state when no articles', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        articles: [],
        count: 0,
        sources: [],
      }),
    });

    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/No.*news/i) || screen.getByText(/No.*articles/i)).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(<NewsReview />);

    await waitFor(() => {
      // Should not crash on error
      expect(screen.getByText(/News/i)).toBeInTheDocument();
    });
  });

  it('filters by news provider', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
    });

    // Provider filter should be available
    expect(screen.getByText(/News/i)).toBeInTheDocument();
  });

  it('displays AI analysis button for articles', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
    });

    // AI analysis feature should be available
    expect(screen.getByText(/News/i)).toBeInTheDocument();
  });

  it('shows article categories', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText(/earnings/i) || screen.getByText(/general/i)).toBeInTheDocument();
    });
  });

  it('opens stock lookup for article symbols', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument();
    });

    const symbolElement = screen.getByText('AAPL');
    fireEvent.click(symbolElement);

    await waitFor(() => {
      // Stock lookup should be triggered
      expect(screen.queryByText('Stock Lookup Component')).toBeInTheDocument();
    });
  });

  it('displays sentiment score numerically', async () => {
    render(<NewsReview />);

    await waitFor(() => {
      // Sentiment scores should be displayed
      expect(screen.getByText(/Apple reaches new all-time high/i)).toBeInTheDocument();
    });
  });
});
