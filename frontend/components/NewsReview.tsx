import React, { useState, useEffect } from 'react';
import StockLookup from './StockLookup';
import { useIsMobile } from '../hooks/useBreakpoint';

interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  source: string;
  url: string;
  published_at: string;
  sentiment: string;
  sentiment_score: number;
  symbols: string[];
  category: string;
  image_url?: string;
  provider: string;
}

interface NewsResponse {
  category?: string;
  articles: NewsArticle[];
  count: number;
  sources: string[];
}

const NewsReview: React.FC = () => {
  const isMobile = useIsMobile();
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'bullish' | 'bearish' | 'neutral'>('all');
  const [searchSymbol, setSearchSymbol] = useState('');
  const [providers, setProviders] = useState<string[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [selectedProvider, setSelectedProvider] = useState<string>('all');
  const [marketSentiment, setMarketSentiment] = useState<any>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  const [showStockLookup, setShowStockLookup] = useState(false);
  const ARTICLES_PER_PAGE = 20;

  const fetchProviders = async () => {
    try {
      const response = await fetch('/api/proxy/news/providers');
      if (!response.ok) throw new Error('Failed to fetch providers');
      const data = await response.json();
      setProviders(data.providers.map((p: any) => p.name));
    } catch (err) {
      console.error('[NEWS] Provider fetch error:', err);
    }
  };

  const fetchMarketSentiment = async () => {
    try {
      const response = await fetch('/api/proxy/news/sentiment/market?category=general');
      if (response.ok) {
        const data = await response.json();
        setMarketSentiment(data);
      }
    } catch (err) {
      console.error('[NEWS] Sentiment fetch error:', err);
    }
  };

  const fetchNews = async (symbol?: string, loadMore: boolean = false) => {
    if (!loadMore) {
      setLoading(true);
      setError(null);
      setPage(1);
    }

    try {
      // Build query parameters
      const params = new URLSearchParams();

      if (symbol) {
        params.append('days_back', '14');
        if (filter !== 'all') params.append('sentiment', filter);
        if (selectedProvider !== 'all') params.append('provider', selectedProvider);
      } else {
        params.append('category', 'general');
        params.append('limit', String((loadMore ? page + 1 : 1) * ARTICLES_PER_PAGE));
        if (filter !== 'all') params.append('sentiment', filter);
        if (selectedProvider !== 'all') params.append('provider', selectedProvider);
      }

      const endpoint = symbol
        ? `/api/proxy/news/company/${symbol}?${params.toString()}`
        : `/api/proxy/news/market?${params.toString()}`;

      const response = await fetch(endpoint);

      if (!response.ok) {
        throw new Error(`Failed to fetch news: ${response.status}`);
      }

      const data: NewsResponse = await response.json();

      if (loadMore) {
        setNews(prev => [...prev, ...data.articles]);
        setPage(prev => prev + 1);
      } else {
        setNews(data.articles);
      }

      setHasMore(data.articles.length === (loadMore ? page + 1 : 1) * ARTICLES_PER_PAGE);
      setLastUpdate(new Date());
    } catch (err: any) {
      setError(err.message || 'Failed to load news');
      console.error('[NEWS] Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProviders();
    fetchNews();
    fetchMarketSentiment();

    // Auto-refresh every 5 minutes
    const interval = setInterval(() => {
      fetchNews(searchSymbol || undefined);
      fetchMarketSentiment();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  // Refetch when filters change
  useEffect(() => {
    if (providers.length > 0) {  // Only fetch after providers are loaded
      fetchNews(searchSymbol || undefined);
    }
  }, [filter, selectedProvider]);

  const handleSearch = () => {
    if (searchSymbol.trim()) {
      fetchNews(searchSymbol.trim().toUpperCase());
    } else {
      fetchNews();
    }
  };

  // Filtering now happens on the backend, so we don't need client-side filtering
  const filteredNews = news;

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'bullish':
        return '#10b981'; // green
      case 'bearish':
        return '#ef4444'; // red
      case 'neutral':
        return '#6b7280'; // gray
      default:
        return '#6b7280';
    }
  };

  const getSentimentBadge = (sentiment: string, score: number) => (
    <div style={{
      display: 'inline-block',
      padding: '4px 12px',
      borderRadius: '12px',
      backgroundColor: `${getSentimentColor(sentiment)}22`,
      border: `1px solid ${getSentimentColor(sentiment)}`,
      fontSize: '12px',
      fontWeight: '600',
      color: getSentimentColor(sentiment),
    }}>
      {sentiment.toUpperCase()} ({score > 0 ? '+' : ''}{(score * 100).toFixed(0)}%)
    </div>
  );

  const formatDate = (isoString: string | null | undefined) => {
    // Defensive parsing: handle null, undefined, or malformed dates
    if (!isoString) {
      return 'Recently';
    }

    try {
      const date = new Date(isoString);

      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Recently';
      }

      const now = new Date();
      const diffMs = now.getTime() - date.getTime();

      // Handle future dates (malformed data)
      if (diffMs < 0) {
        return 'Recently';
      }

      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;
      return date.toLocaleDateString();
    } catch (error) {
      console.error('[NEWS] Date format error:', error, 'for', isoString);
      return 'Recently';
    }
  };

  return (
    <div style={{
      padding: isMobile ? '16px' : '24px',
      color: '#e2e8f0',
      height: '100%',
      overflowY: 'auto',
    }}>
      {/* Header with PaiiD Logo */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: isMobile ? '8px' : '16px', marginBottom: '8px' }}>
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

          <h2 style={{
            fontSize: isMobile ? '22px' : '28px',
            fontWeight: '700',
            margin: 0,
            background: 'linear-gradient(135deg, #3B82F6, #A855F7)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            News Review
          </h2>
        </div>
        <div style={{ fontSize: '14px', color: '#94a3b8', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <span>{filteredNews.length} articles</span>
          <span>•</span>
          <span>{providers.length} providers: {providers.join(', ')}</span>
          <span>•</span>
          <span>Updated {formatDate(lastUpdate.toISOString())}</span>
        </div>
      </div>

      {/* Market Sentiment Widget */}
      {marketSentiment && (
        <div style={{
          marginBottom: '24px',
          padding: '16px',
          borderRadius: '12px',
          background: `linear-gradient(135deg, ${getSentimentColor(marketSentiment.overall_sentiment)}15, transparent)`,
          border: `1px solid ${getSentimentColor(marketSentiment.overall_sentiment)}40`,
          display: 'flex',
          flexDirection: isMobile ? 'column' : 'row',
          justifyContent: 'space-between',
          alignItems: isMobile ? 'flex-start' : 'center',
          gap: '16px',
        }}>
          <div>
            <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '4px' }}>Market Sentiment</div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: getSentimentColor(marketSentiment.overall_sentiment) }}>
              {marketSentiment.overall_sentiment.toUpperCase()}
            </div>
            <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
              Based on {marketSentiment.total_articles} articles
            </div>
          </div>
          <div style={{ display: 'flex', gap: '24px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '20px', fontWeight: '600', color: '#10b981' }}>
                {marketSentiment.sentiment_distribution.bullish_percent}%
              </div>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Bullish</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '20px', fontWeight: '600', color: '#6b7280' }}>
                {marketSentiment.sentiment_distribution.neutral_percent}%
              </div>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Neutral</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '20px', fontWeight: '600', color: '#ef4444' }}>
                {marketSentiment.sentiment_distribution.bearish_percent}%
              </div>
              <div style={{ fontSize: '12px', color: '#94a3b8' }}>Bearish</div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div style={{
        marginBottom: '24px',
        display: 'flex',
        gap: '12px',
        flexWrap: 'wrap',
        alignItems: 'center',
      }}>
        {/* Search */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            placeholder="Search by symbol (e.g., AAPL)"
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            style={{
              padding: '10px 16px',
              borderRadius: '8px',
              border: '1px solid #334155',
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              color: '#e2e8f0',
              fontSize: '14px',
              minWidth: '220px',
            }}
          />
          <button
            onClick={handleSearch}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: '1px solid #3B82F6',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              color: '#3B82F6',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            Search
          </button>
          {searchSymbol && (
            <button
              onClick={() => {
                setSearchSymbol('');
                fetchNews();
              }}
              style={{
                padding: '10px 20px',
                borderRadius: '8px',
                border: '1px solid #6b7280',
                backgroundColor: 'rgba(107, 114, 128, 0.1)',
                color: '#6b7280',
                fontSize: '14px',
                cursor: 'pointer',
              }}
            >
              Clear
            </button>
          )}
        </div>

        {/* Sentiment Filter */}
        <div style={{ display: 'flex', gap: '8px' }}>
          {(['all', 'bullish', 'neutral', 'bearish'] as const).map((sentiment) => (
            <button
              key={sentiment}
              onClick={() => setFilter(sentiment)}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: filter === sentiment ? `1px solid ${getSentimentColor(sentiment)}` : '1px solid #334155',
                backgroundColor: filter === sentiment
                  ? `${getSentimentColor(sentiment)}22`
                  : 'rgba(15, 23, 42, 0.6)',
                color: filter === sentiment ? getSentimentColor(sentiment) : '#94a3b8',
                fontSize: '13px',
                fontWeight: filter === sentiment ? '600' : '400',
                cursor: 'pointer',
                textTransform: 'capitalize',
              }}
            >
              {sentiment}
            </button>
          ))}
        </div>

        {/* Provider Filter */}
        {providers.length > 0 && (
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{ fontSize: '13px', color: '#94a3b8' }}>Source:</span>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #334155',
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                color: '#e2e8f0',
                fontSize: '13px',
                cursor: 'pointer',
              }}
            >
              <option value="all">All Sources</option>
              {providers.map((provider) => (
                <option key={provider} value={provider}>
                  {provider.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Refresh */}
        <button
          onClick={() => fetchNews(searchSymbol || undefined)}
          disabled={loading}
          style={{
            padding: '8px 16px',
            borderRadius: '8px',
            border: '1px solid #334155',
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
            color: '#94a3b8',
            fontSize: '13px',
            cursor: loading ? 'not-allowed' : 'pointer',
            marginLeft: 'auto',
          }}
        >
          {loading ? '⟳ Loading...' : '↻ Refresh'}
        </button>
      </div>

      {/* Error State */}
      {error && (
        <div style={{
          padding: '16px',
          borderRadius: '8px',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid #ef4444',
          color: '#ef4444',
          marginBottom: '24px',
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Loading State */}
      {loading && !error && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#94a3b8' }}>
          Loading news...
        </div>
      )}

      {/* News Articles */}
      {!loading && !error && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {filteredNews.length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: '40px',
              color: '#94a3b8',
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              borderRadius: '12px',
              border: '1px solid #334155',
            }}>
              No articles found matching your criteria.
            </div>
          ) : (
            filteredNews.map((article) => (
              <div
                key={article.id}
                style={{
                  padding: '20px',
                  borderRadius: '12px',
                  backgroundColor: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid #334155',
                  backdropFilter: 'blur(10px)',
                  transition: 'all 0.2s',
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#3B82F6';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#334155';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
                onClick={() => window.open(article.url, '_blank')}
              >
                {/* Article Header */}
                <div style={{ display: 'flex', gap: '16px', marginBottom: '12px' }}>
                  {article.image_url && !isMobile && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={article.image_url}
                      alt={article.title}
                      style={{
                        width: '120px',
                        height: '80px',
                        objectFit: 'cover',
                        borderRadius: '8px',
                        flexShrink: 0,
                      }}
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  )}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3 style={{
                      fontSize: '18px',
                      fontWeight: '600',
                      margin: '0 0 8px 0',
                      color: '#e2e8f0',
                      lineHeight: '1.4',
                    }}>
                      {article.title}
                    </h3>
                    <div style={{
                      fontSize: '13px',
                      color: '#94a3b8',
                      display: 'flex',
                      gap: '12px',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                    }}>
                      <span>{article.source}</span>
                      <span>•</span>
                      <span>{formatDate(article.published_at)}</span>
                      {article.symbols.length > 0 && (
                        <>
                          <span>•</span>
                          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                            {article.symbols.map((sym, idx) => (
                              <button
                                key={idx}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedSymbol(sym);
                                  setShowStockLookup(true);
                                }}
                                style={{
                                  padding: '2px 8px',
                                  borderRadius: '4px',
                                  border: '1px solid #3B82F6',
                                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                  color: '#3B82F6',
                                  fontSize: '11px',
                                  fontWeight: '600',
                                  cursor: 'pointer',
                                  transition: 'all 0.2s',
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.2)';
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                                }}
                              >
                                ${sym}
                              </button>
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Article Summary */}
                {article.summary && (
                  <p style={{
                    fontSize: '14px',
                    color: '#cbd5e1',
                    lineHeight: '1.6',
                    margin: '0 0 12px 0',
                  }}>
                    {article.summary}
                  </p>
                )}

                {/* Article Footer */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '12px',
                }}>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    {getSentimentBadge(article.sentiment, article.sentiment_score)}
                    <span style={{ fontSize: '12px', color: '#64748b' }}>
                      via {article.provider}
                    </span>
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: '#3B82F6',
                    fontWeight: '500',
                  }}>
                    Read more →
                  </div>
                </div>
              </div>
            ))
          )}

          {/* Load More Button */}
          {!loading && !error && filteredNews.length > 0 && hasMore && (
            <div style={{ textAlign: 'center', marginTop: '24px' }}>
              <button
                onClick={() => fetchNews(searchSymbol || undefined, true)}
                style={{
                  padding: '12px 32px',
                  borderRadius: '8px',
                  border: '1px solid #3B82F6',
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  color: '#3B82F6',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.2)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                }}
              >
                Load More Articles
              </button>
            </div>
          )}
        </div>
      )}

      {/* Stock Research Section */}
      {showStockLookup && selectedSymbol && (
        <div style={{
          marginTop: '32px',
          padding: isMobile ? '16px' : '24px',
          borderRadius: '12px',
          backgroundColor: 'rgba(15, 23, 42, 0.8)',
          border: '1px solid #334155',
          backdropFilter: 'blur(10px)',
        }}>
          <div style={{
            display: 'flex',
            flexDirection: isMobile ? 'column' : 'row',
            justifyContent: 'space-between',
            alignItems: isMobile ? 'stretch' : 'center',
            gap: isMobile ? '12px' : 0,
            marginBottom: '24px',
            paddingBottom: '16px',
            borderBottom: '1px solid #334155',
          }}>
            <h2 style={{
              margin: 0,
              fontSize: isMobile ? '18px' : '24px',
              fontWeight: '700',
              color: '#e2e8f0',
              background: 'linear-gradient(135deg, #3B82F6, #A855F7)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}>
              Stock Research: {selectedSymbol}
            </h2>
            <button
              onClick={() => setShowStockLookup(false)}
              style={{
                padding: '8px 20px',
                borderRadius: '8px',
                border: '1px solid #6b7280',
                backgroundColor: 'rgba(107, 114, 128, 0.1)',
                color: '#94a3b8',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(107, 114, 128, 0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'rgba(107, 114, 128, 0.1)';
              }}
            >
              Close
            </button>
          </div>
          <StockLookup
            initialSymbol={selectedSymbol}
            showChart={true}
            showIndicators={true}
            showCompanyInfo={true}
            showNews={true}
            enableAIAnalysis={true}
            onSymbolSelect={(sym) => setSelectedSymbol(sym)}
          />
        </div>
      )}
    </div>
  );
};

export default NewsReview;
