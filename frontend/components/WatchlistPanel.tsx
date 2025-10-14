import React, { useState, useEffect } from 'react';
import { useIsMobile } from '../hooks/useBreakpoint';
import {
  UserProfile,
  Watchlist,
  getOrCreateProfile
} from '../types/profile';
import { TrendingUp, TrendingDown, ChevronDown, ChevronUp, RefreshCw, Star } from 'lucide-react';

interface WatchlistPanelProps {
  onSymbolClick?: (symbol: string) => void;
  refreshInterval?: number; // milliseconds (default 60000 = 1 minute)
  showHeader?: boolean;
  compact?: boolean;
}

interface SymbolQuote {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume?: number;
  lastUpdate: string;
}

const WatchlistPanel: React.FC<WatchlistPanelProps> = ({
  onSymbolClick,
  refreshInterval = 60000,
  showHeader = true,
  compact = false
}) => {
  const [profile, setProfile] = useState<UserProfile>(getOrCreateProfile());
  const [selectedWatchlistId, setSelectedWatchlistId] = useState<string | null>(null);
  const [quotes, setQuotes] = useState<Record<string, SymbolQuote>>({});
  const [loading, setLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [isExpanded, setIsExpanded] = useState(true);
  const isMobile = useIsMobile();

  const theme = {
    bg: 'rgba(15, 23, 42, 0.7)',
    bgLight: 'rgba(30, 41, 59, 0.8)',
    text: '#e2e8f0',
    textMuted: '#94a3b8',
    primary: '#10b981',
    danger: '#ef4444',
    border: 'rgba(148, 163, 184, 0.2)',
    warning: '#f59e0b',
    spacing: {
      xs: '4px',
      sm: '8px',
      md: '12px',
      lg: '16px',
      xl: '24px',
    }
  };

  useEffect(() => {
    // Load profile and set first watchlist as selected
    const loadedProfile = getOrCreateProfile();
    setProfile(loadedProfile);

    if (loadedProfile.watchlists.length > 0 && !selectedWatchlistId) {
      setSelectedWatchlistId(loadedProfile.watchlists[0].id);
    }

    // Listen for profile updates
    const handleProfileUpdate = (event: CustomEvent) => {
      const updatedProfile = event.detail;
      setProfile(updatedProfile);

      // If selected watchlist was deleted, select first available
      if (selectedWatchlistId && !updatedProfile.watchlists.find((w: Watchlist) => w.id === selectedWatchlistId)) {
        setSelectedWatchlistId(
          updatedProfile.watchlists.length > 0 ? updatedProfile.watchlists[0].id : null
        );
      }
    };

    window.addEventListener('profile-updated', handleProfileUpdate as EventListener);
    return () => {
      window.removeEventListener('profile-updated', handleProfileUpdate as EventListener);
    };
  }, []);

  useEffect(() => {
    // Fetch quotes for selected watchlist
    if (selectedWatchlistId) {
      fetchQuotes();

      // Set up refresh interval
      const intervalId = setInterval(fetchQuotes, refreshInterval);
      return () => clearInterval(intervalId);
    }
  }, [selectedWatchlistId, refreshInterval]);

  const fetchQuotes = async () => {
    const watchlist = profile.watchlists.find(w => w.id === selectedWatchlistId);
    if (!watchlist || watchlist.symbols.length === 0) return;

    setLoading(true);
    try {
      const newQuotes: Record<string, SymbolQuote> = {};

      // Fetch all symbols in parallel
      await Promise.all(
        watchlist.symbols.map(async (symbol) => {
          try {
            const response = await fetch(`/api/proxy/api/stock/${symbol}/info`, {
              headers: {
                'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`
              }
            });

            if (response.ok) {
              const data = await response.json();
              newQuotes[symbol] = {
                symbol,
                price: data.current_price,
                change: data.change,
                changePercent: data.change_percent,
                volume: data.avg_volume,
                lastUpdate: new Date().toISOString()
              };
            }
          } catch (err) {
            console.error(`Failed to fetch quote for ${symbol}:`, err);
            // Keep previous quote if fetch fails
            if (quotes[symbol]) {
              newQuotes[symbol] = quotes[symbol];
            }
          }
        })
      );

      setQuotes(newQuotes);
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Failed to fetch quotes:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectedWatchlist = profile.watchlists.find(w => w.id === selectedWatchlistId);

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  if (compact && selectedWatchlist) {
    // Compact view - just list of symbols with prices
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing.sm,
        width: '100%'
      }}>
        {selectedWatchlist.symbols.map((symbol) => {
          const quote = quotes[symbol];
          return (
            <div
              key={symbol}
              onClick={() => onSymbolClick?.(symbol)}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: theme.spacing.md,
                background: theme.bgLight,
                borderRadius: '8px',
                cursor: onSymbolClick ? 'pointer' : 'default',
                transition: 'all 0.2s',
                border: `1px solid ${theme.border}`
              }}
            >
              <div style={{ fontWeight: 600, color: theme.text }}>{symbol}</div>
              {quote ? (
                <div style={{ textAlign: 'right' }}>
                  <div style={{ color: theme.text, fontSize: '16px', fontWeight: 600 }}>
                    ${quote.price.toFixed(2)}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: quote.change >= 0 ? theme.primary : theme.danger,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    justifyContent: 'flex-end'
                  }}>
                    {quote.change >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    {quote.change >= 0 ? '+' : ''}{quote.changePercent.toFixed(2)}%
                  </div>
                </div>
              ) : (
                <div style={{ fontSize: '12px', color: theme.textMuted }}>
                  {loading ? 'Loading...' : 'No data'}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div style={{
      width: '100%',
      background: theme.bg,
      borderRadius: '12px',
      border: `1px solid ${theme.border}`,
      overflow: 'hidden'
    }}>
      {/* Header */}
      {showHeader && (
        <div style={{
          padding: theme.spacing.lg,
          borderBottom: `1px solid ${theme.border}`,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: theme.bgLight
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
            <Star size={20} color={theme.primary} />
            <h3 style={{
              margin: 0,
              fontSize: isMobile ? '16px' : '18px',
              fontWeight: 700,
              color: theme.text
            }}>
              Watchlist
            </h3>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
            <button
              onClick={fetchQuotes}
              disabled={loading}
              style={{
                padding: theme.spacing.sm,
                background: 'transparent',
                border: `1px solid ${theme.border}`,
                borderRadius: '6px',
                color: theme.text,
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s'
              }}
              title="Refresh quotes"
            >
              <RefreshCw
                size={16}
                style={{
                  animation: loading ? 'spin 1s linear infinite' : 'none'
                }}
              />
            </button>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              style={{
                padding: theme.spacing.sm,
                background: 'transparent',
                border: 'none',
                color: theme.text,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center'
              }}
            >
              {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>
          </div>
        </div>
      )}

      {/* Content */}
      {isExpanded && (
        <div style={{ padding: theme.spacing.lg }}>
          {/* Watchlist Selector */}
          {profile.watchlists.length > 1 && (
            <div style={{
              display: 'flex',
              gap: theme.spacing.sm,
              marginBottom: theme.spacing.lg,
              overflowX: 'auto',
              paddingBottom: theme.spacing.xs
            }}>
              {profile.watchlists.map((watchlist) => (
                <button
                  key={watchlist.id}
                  onClick={() => setSelectedWatchlistId(watchlist.id)}
                  style={{
                    padding: `${theme.spacing.sm} ${theme.spacing.md}`,
                    background: selectedWatchlistId === watchlist.id ? theme.primary : theme.bgLight,
                    color: selectedWatchlistId === watchlist.id ? '#0f172a' : theme.text,
                    border: `1px solid ${selectedWatchlistId === watchlist.id ? theme.primary : theme.border}`,
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: theme.spacing.xs
                  }}
                >
                  {watchlist.name}
                  <span style={{
                    fontSize: '12px',
                    padding: '2px 6px',
                    background: selectedWatchlistId === watchlist.id ? 'rgba(15, 23, 42, 0.2)' : theme.bg,
                    borderRadius: '4px'
                  }}>
                    {watchlist.symbols.length}
                  </span>
                </button>
              ))}
            </div>
          )}

          {/* Last Refresh Time */}
          <div style={{
            fontSize: '12px',
            color: theme.textMuted,
            marginBottom: theme.spacing.md,
            textAlign: 'right'
          }}>
            Last updated: {formatTime(lastRefresh)}
          </div>

          {/* Symbols List */}
          {selectedWatchlist && selectedWatchlist.symbols.length > 0 ? (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: theme.spacing.sm
            }}>
              {selectedWatchlist.symbols.map((symbol) => {
                const quote = quotes[symbol];
                return (
                  <div
                    key={symbol}
                    onClick={() => onSymbolClick?.(symbol)}
                    style={{
                      padding: theme.spacing.md,
                      background: theme.bgLight,
                      borderRadius: '8px',
                      border: `1px solid ${theme.border}`,
                      cursor: onSymbolClick ? 'pointer' : 'default',
                      transition: 'all 0.2s',
                      display: 'grid',
                      gridTemplateColumns: isMobile ? '1fr 1fr' : '2fr 1fr 1fr 1fr',
                      gap: theme.spacing.md,
                      alignItems: 'center'
                    }}
                    onMouseEnter={(e) => {
                      if (onSymbolClick) {
                        e.currentTarget.style.background = 'rgba(30, 41, 59, 1)';
                        e.currentTarget.style.borderColor = theme.primary;
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = theme.bgLight;
                      e.currentTarget.style.borderColor = theme.border;
                    }}
                  >
                    {/* Symbol */}
                    <div>
                      <div style={{
                        fontSize: '16px',
                        fontWeight: 700,
                        color: theme.text
                      }}>
                        {symbol}
                      </div>
                      {quote?.volume && !isMobile && (
                        <div style={{
                          fontSize: '11px',
                          color: theme.textMuted,
                          marginTop: '2px'
                        }}>
                          Vol: {(quote.volume / 1e6).toFixed(2)}M
                        </div>
                      )}
                    </div>

                    {/* Price */}
                    {quote ? (
                      <>
                        <div style={{ textAlign: isMobile ? 'right' : 'left' }}>
                          <div style={{
                            fontSize: '18px',
                            fontWeight: 700,
                            color: theme.text
                          }}>
                            ${quote.price.toFixed(2)}
                          </div>
                        </div>

                        {/* Change ($) */}
                        {!isMobile && (
                          <div style={{ textAlign: 'left' }}>
                            <div style={{
                              fontSize: '14px',
                              fontWeight: 600,
                              color: quote.change >= 0 ? theme.primary : theme.danger
                            }}>
                              {quote.change >= 0 ? '+' : ''}${Math.abs(quote.change).toFixed(2)}
                            </div>
                          </div>
                        )}

                        {/* Change (%) */}
                        <div style={{
                          textAlign: 'right',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: isMobile ? 'flex-end' : 'flex-start',
                          gap: '6px'
                        }}>
                          {quote.change >= 0 ? (
                            <TrendingUp size={16} color={theme.primary} />
                          ) : (
                            <TrendingDown size={16} color={theme.danger} />
                          )}
                          <span style={{
                            fontSize: '16px',
                            fontWeight: 700,
                            color: quote.change >= 0 ? theme.primary : theme.danger
                          }}>
                            {quote.change >= 0 ? '+' : ''}{quote.changePercent.toFixed(2)}%
                          </span>
                        </div>
                      </>
                    ) : (
                      <div style={{
                        gridColumn: isMobile ? '2' : '2 / 5',
                        textAlign: 'right',
                        fontSize: '14px',
                        color: theme.textMuted
                      }}>
                        {loading ? 'Loading...' : 'No data'}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{
              padding: `${theme.spacing.xl} ${theme.spacing.lg}`,
              textAlign: 'center',
              color: theme.textMuted
            }}>
              {selectedWatchlist ? (
                <>
                  <Star size={48} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
                  <p style={{ margin: 0, fontSize: '16px' }}>
                    No symbols in this watchlist
                  </p>
                  <p style={{ margin: '8px 0 0 0', fontSize: '14px' }}>
                    Add symbols to track their prices
                  </p>
                </>
              ) : (
                <>
                  <Star size={48} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
                  <p style={{ margin: 0, fontSize: '16px' }}>
                    No watchlists created yet
                  </p>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* Animations */}
      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default WatchlistPanel;
