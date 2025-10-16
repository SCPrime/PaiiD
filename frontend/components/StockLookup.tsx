import React, { useState, useEffect } from 'react';
import { useIsMobile } from '../hooks/useBreakpoint';
import AIAnalysisModal from './AIAnalysisModal';

interface StockLookupProps {
  showChart?: boolean;
  showIndicators?: boolean;
  showCompanyInfo?: boolean;
  showNews?: boolean;
  enableAIAnalysis?: boolean;
  onSymbolSelect?: (symbol: string) => void;
  onAIAnalysisClick?: (symbol: string) => void;
  initialSymbol?: string;
}

interface CompanyInfo {
  symbol: string;
  name: string;
  description?: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  pe_ratio?: number;
  dividend_yield?: number;
  week_52_high?: number;
  week_52_low?: number;
  avg_volume?: number;
  current_price: number;
  change: number;
  change_percent: number;
}

interface NewsArticle {
  title: string;
  summary?: string;
  url: string;
  source: string;
  published_at: string;
  sentiment?: string;
}

const StockLookup: React.FC<StockLookupProps> = ({
  showChart = true,
  showIndicators = true,
  showCompanyInfo = true,
  showNews = false,
  enableAIAnalysis = true,
  onSymbolSelect,
  onAIAnalysisClick: _onAIAnalysisClick,
  initialSymbol = ''
}) => {
  const [symbol, setSymbol] = useState(initialSymbol);
  const [searchInput, setSearchInput] = useState(initialSymbol);
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAIAnalysisModal, setShowAIAnalysisModal] = useState(false);
  const isMobile = useIsMobile();

  const theme = {
    bg: 'rgba(15, 23, 42, 0.7)',
    bgLight: 'rgba(30, 41, 59, 0.8)',
    text: '#e2e8f0',
    textMuted: '#94a3b8',
    primary: '#10b981',
    danger: '#ef4444',
    border: 'rgba(148, 163, 184, 0.2)',
  };

  useEffect(() => {
    if (initialSymbol) {
      handleSearch(initialSymbol);
    }
  }, [initialSymbol]);

  const handleSearch = async (searchSymbol: string) => {
    if (!searchSymbol.trim()) {
      setError('Please enter a stock symbol');
      return;
    }

    const sym = searchSymbol.trim().toUpperCase();
    setSymbol(sym);
    setLoading(true);
    setError(null);

    try {
      // Fetch company info
      const infoResponse = await fetch(`/api/proxy/api/stock/${sym}/info`, {
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`
        }
      });

      if (!infoResponse.ok) {
        throw new Error(`Stock ${sym} not found or API error`);
      }

      const info = await infoResponse.json();
      setCompanyInfo(info);

      // Fetch news if enabled
      if (showNews) {
        const newsResponse = await fetch(`/api/proxy/api/stock/${sym}/news?limit=5`, {
          headers: {
            'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`
          }
        });

        if (newsResponse.ok) {
          const newsData = await newsResponse.json();
          setNews(newsData);
        }
      }

      // Notify parent component
      if (onSymbolSelect) {
        onSymbolSelect(sym);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stock data');
      setCompanyInfo(null);
      setNews([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(searchInput);
  };

  const formatMarketCap = (value: number | undefined): string => {
    if (!value) return 'N/A';
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  const formatVolume = (value: number | undefined): string => {
    if (!value) return 'N/A';
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value.toString();
  };

  return (
    <div style={{
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      gap: isMobile ? '16px' : '24px'
    }}>
      {/* Search Bar */}
      <form onSubmit={handleSubmit} style={{
        display: 'flex',
        gap: '12px',
        flexDirection: isMobile ? 'column' : 'row'
      }}>
        <input
          type="text"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
          placeholder="Enter stock symbol (e.g., AAPL)"
          style={{
            flex: 1,
            padding: isMobile ? '14px 16px' : '12px 16px',
            fontSize: '16px',
            background: theme.bg,
            border: `1px solid ${theme.border}`,
            borderRadius: '8px',
            color: theme.text,
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: isMobile ? '14px 24px' : '12px 24px',
            background: loading ? theme.textMuted : theme.primary,
            color: '#0f172a',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            minWidth: isMobile ? '100%' : '120px'
          }}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div style={{
          padding: '12px 16px',
          background: 'rgba(239, 68, 68, 0.1)',
          border: `1px solid ${theme.danger}`,
          borderRadius: '8px',
          color: theme.danger,
          fontSize: '14px'
        }}>
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div style={{
          padding: '40px',
          textAlign: 'center',
          color: theme.textMuted,
          fontSize: '16px'
        }}>
          Loading stock data...
        </div>
      )}

      {/* Company Info */}
      {!loading && companyInfo && showCompanyInfo && (
        <div style={{
          padding: isMobile ? '16px' : '24px',
          background: theme.bg,
          borderRadius: '12px',
          border: `1px solid ${theme.border}`
        }}>
          <div style={{
            display: 'flex',
            flexDirection: isMobile ? 'column' : 'row',
            justifyContent: 'space-between',
            alignItems: isMobile ? 'flex-start' : 'center',
            gap: '12px',
            marginBottom: '16px'
          }}>
            <div>
              <h2 style={{
                fontSize: isMobile ? '24px' : '28px',
                fontWeight: 700,
                color: theme.text,
                margin: 0
              }}>
                {companyInfo.symbol}
              </h2>
              <p style={{
                fontSize: '14px',
                color: theme.textMuted,
                margin: '4px 0 0 0'
              }}>
                {companyInfo.name}
              </p>
            </div>
            <div style={{ textAlign: isMobile ? 'left' : 'right' }}>
              <div style={{
                fontSize: isMobile ? '28px' : '32px',
                fontWeight: 700,
                color: theme.text
              }}>
                ${companyInfo.current_price.toFixed(2)}
              </div>
              <div style={{
                fontSize: '16px',
                color: companyInfo.change >= 0 ? theme.primary : theme.danger,
                fontWeight: 600
              }}>
                {companyInfo.change >= 0 ? '+' : ''}{companyInfo.change.toFixed(2)}
                ({companyInfo.change_percent >= 0 ? '+' : ''}{companyInfo.change_percent.toFixed(2)}%)
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: isMobile ? '1fr 1fr' : 'repeat(4, 1fr)',
            gap: '16px',
            paddingTop: '16px',
            borderTop: `1px solid ${theme.border}`
          }}>
            {companyInfo.market_cap && (
              <div>
                <div style={{ fontSize: '12px', color: theme.textMuted }}>Market Cap</div>
                <div style={{ fontSize: '16px', color: theme.text, fontWeight: 600 }}>
                  {formatMarketCap(companyInfo.market_cap)}
                </div>
              </div>
            )}
            {companyInfo.pe_ratio && (
              <div>
                <div style={{ fontSize: '12px', color: theme.textMuted }}>P/E Ratio</div>
                <div style={{ fontSize: '16px', color: theme.text, fontWeight: 600 }}>
                  {companyInfo.pe_ratio.toFixed(2)}
                </div>
              </div>
            )}
            <div>
              <div style={{ fontSize: '12px', color: theme.textMuted }}>52W High</div>
              <div style={{ fontSize: '16px', color: theme.text, fontWeight: 600 }}>
                ${companyInfo.week_52_high ? companyInfo.week_52_high.toFixed(2) : 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: theme.textMuted }}>52W Low</div>
              <div style={{ fontSize: '16px', color: theme.text, fontWeight: 600 }}>
                ${companyInfo.week_52_low ? companyInfo.week_52_low.toFixed(2) : 'N/A'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: theme.textMuted }}>Avg Volume</div>
              <div style={{ fontSize: '16px', color: theme.text, fontWeight: 600 }}>
                {formatVolume(companyInfo.avg_volume)}
              </div>
            </div>
            {companyInfo.dividend_yield && (
              <div>
                <div style={{ fontSize: '12px', color: theme.textMuted }}>Dividend Yield</div>
                <div style={{ fontSize: '16px', color: theme.text, fontWeight: 600 }}>
                  {(companyInfo.dividend_yield * 100).toFixed(2)}%
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TradingView Chart */}
      {!loading && symbol && showChart && (
        <div style={{
          padding: isMobile ? '16px' : '24px',
          background: theme.bg,
          borderRadius: '12px',
          border: `1px solid ${theme.border}`
        }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: 600,
            color: theme.text,
            margin: '0 0 16px 0'
          }}>
            Chart
          </h3>
          <div style={{
            width: '100%',
            height: isMobile ? '400px' : '500px',
            background: '#131722',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: theme.textMuted
          }}>
            <p>TradingView Chart Widget: {symbol}</p>
            <p style={{ fontSize: '12px', marginTop: '8px' }}>
              (To be integrated with TradingView widget)
            </p>
          </div>
        </div>
      )}

      {/* Technical Indicators */}
      {!loading && symbol && showIndicators && (
        <div style={{
          padding: isMobile ? '16px' : '24px',
          background: theme.bg,
          borderRadius: '12px',
          border: `1px solid ${theme.border}`
        }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: 600,
            color: theme.text,
            margin: '0 0 16px 0'
          }}>
            Technical Indicators
          </h3>
          <div style={{
            display: 'grid',
            gridTemplateColumns: isMobile ? '1fr' : 'repeat(2, 1fr)',
            gap: '12px'
          }}>
            <div style={{ padding: '12px', background: theme.bgLight, borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: theme.textMuted }}>RSI (14)</div>
              <div style={{ fontSize: '20px', color: theme.text, fontWeight: 600 }}>
                Calculating...
              </div>
            </div>
            <div style={{ padding: '12px', background: theme.bgLight, borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: theme.textMuted }}>MACD</div>
              <div style={{ fontSize: '20px', color: theme.text, fontWeight: 600 }}>
                Calculating...
              </div>
            </div>
            <div style={{ padding: '12px', background: theme.bgLight, borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: theme.textMuted }}>Bollinger Bands</div>
              <div style={{ fontSize: '20px', color: theme.text, fontWeight: 600 }}>
                Calculating...
              </div>
            </div>
            <div style={{ padding: '12px', background: theme.bgLight, borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: theme.textMuted }}>SMA (20/50/200)</div>
              <div style={{ fontSize: '20px', color: theme.text, fontWeight: 600 }}>
                Calculating...
              </div>
            </div>
          </div>
          <p style={{
            fontSize: '12px',
            color: theme.textMuted,
            marginTop: '12px',
            textAlign: 'center'
          }}>
            Technical indicators will be calculated using Tradier historical data
          </p>
        </div>
      )}

      {/* News */}
      {!loading && symbol && showNews && (
        <div style={{
          padding: isMobile ? '16px' : '24px',
          background: theme.bg,
          borderRadius: '12px',
          border: `1px solid ${theme.border}`
        }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: 600,
            color: theme.text,
            margin: '0 0 16px 0'
          }}>
            News
          </h3>
          {news.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {news.map((article, idx) => (
                <div key={idx} style={{
                  padding: '12px',
                  background: theme.bgLight,
                  borderRadius: '8px',
                  cursor: 'pointer'
                }} onClick={() => window.open(article.url, '_blank')}>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: theme.text }}>
                    {article.title}
                  </div>
                  <div style={{ fontSize: '12px', color: theme.textMuted, marginTop: '4px' }}>
                    {article.source} • {new Date(article.published_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: theme.textMuted, textAlign: 'center' }}>
              News integration coming soon
            </p>
          )}
        </div>
      )}

      {/* AI Analysis Button */}
      {!loading && symbol && enableAIAnalysis && (
        <button
          onClick={() => setShowAIAnalysisModal(true)}
          style={{
            padding: isMobile ? '14px 24px' : '12px 24px',
            background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 600,
            cursor: 'pointer',
            width: '100%'
          }}
        >
          🤖 Analyze {symbol} with AI
        </button>
      )}

      {/* AI Analysis Modal */}
      <AIAnalysisModal
        symbol={symbol}
        isOpen={showAIAnalysisModal}
        onClose={() => setShowAIAnalysisModal(false)}
        onExecuteTrade={(sym) => {
          // TODO: Navigate to Execute Trade workflow
          alert(`Navigate to Execute Trade for ${sym}`);
        }}
        onAddToWatchlist={(sym) => {
          // TODO: Add to watchlist
          alert(`Added ${sym} to watchlist`);
        }}
      />
    </div>
  );
};

export default StockLookup;
