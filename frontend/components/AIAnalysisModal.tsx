import React, { useState, useEffect, useRef } from 'react';
import { X, TrendingUp, TrendingDown, AlertTriangle, Target, Shield, Brain, Loader2, Plus, Star } from 'lucide-react';
import { useIsMobile } from '../hooks/useBreakpoint';
import { useWorkflow } from '../contexts/WorkflowContext';
import {
  UserProfile,
  Watchlist,
  getOrCreateProfile,
  saveProfile
} from '../types/profile';

interface AIAnalysisData {
  symbol: string;
  current_price: number;
  analysis: string;
  momentum: string;
  trend: string;
  support_level: number;
  resistance_level: number;
  risk_assessment: string;
  entry_suggestion: string;
  exit_suggestion: string;
  stop_loss_suggestion: number;
  take_profit_suggestion: number;
  confidence_score: number;
  key_indicators: {
    rsi: number;
    macd_histogram: number;
    sma_20?: number;
    sma_50?: number;
    sma_200?: number;
    current_vs_sma20?: number;
    current_vs_sma50?: number;
  };
  summary: string;
}

interface AIAnalysisModalProps {
  symbol: string;
  isOpen: boolean;
  onClose: () => void;
  onExecuteTrade?: (symbol: string) => void;
  onAddToWatchlist?: (symbol: string) => void;
}

interface ThemeColors {
  bg: string;
  bgLight: string;
  text: string;
  textMuted: string;
  primary: string;
  danger: string;
  warning: string;
  info: string;
  border: string;
}

const AIAnalysisModal: React.FC<AIAnalysisModalProps> = ({
  symbol,
  isOpen,
  onClose,
  onExecuteTrade,
  onAddToWatchlist
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AIAnalysisData | null>(null);
  const [showWatchlistDropdown, setShowWatchlistDropdown] = useState(false);
  const [profile, setProfile] = useState<UserProfile>(getOrCreateProfile());
  const [newWatchlistName, setNewWatchlistName] = useState('');
  const [showCreateWatchlist, setShowCreateWatchlist] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const isMobile = useIsMobile();
  const { navigateToTrade } = useWorkflow();

  const theme = {
    bg: 'rgba(15, 23, 42, 0.95)',
    bgLight: 'rgba(30, 41, 59, 0.9)',
    text: '#e2e8f0',
    textMuted: '#94a3b8',
    primary: '#10b981',
    danger: '#ef4444',
    warning: '#eab308',
    info: '#3b82f6',
    border: 'rgba(148, 163, 184, 0.2)',
  };

  useEffect(() => {
    if (isOpen && symbol) {
      fetchAnalysis();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, symbol]);

  useEffect(() => {
    // Load profile on mount
    const loadedProfile = getOrCreateProfile();
    setProfile(loadedProfile);

    // Listen for profile updates
    const handleProfileUpdate = (event: CustomEvent) => {
      setProfile(event.detail);
    };

    window.addEventListener('profile-updated', handleProfileUpdate as EventListener);
    return () => {
      window.removeEventListener('profile-updated', handleProfileUpdate as EventListener);
    };
  }, []);

  useEffect(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowWatchlistDropdown(false);
      }
    };

    if (showWatchlistDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showWatchlistDropdown]);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/proxy/api/ai/analyze-symbol/${symbol}`, {
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch analysis: ${response.status}`);
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch AI analysis');
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message: string) => {
    // Dispatch custom event for toast notifications
    window.dispatchEvent(
      new CustomEvent('show-toast', { detail: { message } })
    );
  };

  const handleAddToWatchlist = (watchlistId: string) => {
    const watchlistIndex = profile.watchlists.findIndex(w => w.id === watchlistId);
    if (watchlistIndex === -1) {
      showToast('⚠️ Watchlist not found');
      return;
    }

    // Check if symbol already exists
    if (profile.watchlists[watchlistIndex].symbols.includes(symbol)) {
      showToast(`ℹ️ ${symbol} is already in "${profile.watchlists[watchlistIndex].name}"`);
      setShowWatchlistDropdown(false);
      return;
    }

    const updatedProfile = { ...profile };
    updatedProfile.watchlists[watchlistIndex].symbols.push(symbol);
    updatedProfile.watchlists[watchlistIndex].updatedAt = new Date().toISOString();

    setProfile(updatedProfile);
    saveProfile(updatedProfile);
    setShowWatchlistDropdown(false);
    showToast(`✅ Added ${symbol} to "${profile.watchlists[watchlistIndex].name}"`);

    // Call legacy callback if provided
    if (onAddToWatchlist) {
      onAddToWatchlist(symbol);
    }
  };

  const handleCreateWatchlist = () => {
    if (!newWatchlistName.trim()) {
      showToast('⚠️ Please enter a watchlist name');
      return;
    }

    const newWatchlist: Watchlist = {
      id: `watchlist-${Date.now()}`,
      name: newWatchlistName.trim(),
      symbols: [symbol],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    const updatedProfile = { ...profile };
    updatedProfile.watchlists.push(newWatchlist);
    updatedProfile.updatedAt = new Date().toISOString();

    setProfile(updatedProfile);
    saveProfile(updatedProfile);
    setNewWatchlistName('');
    setShowCreateWatchlist(false);
    setShowWatchlistDropdown(false);
    showToast(`✅ Created "${newWatchlist.name}" with ${symbol}`);
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(4px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: isMobile ? '16px' : '40px',
        overflowY: 'auto',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '900px',
          background: theme.bg,
          border: `1px solid ${theme.border}`,
          borderRadius: '16px',
          backdropFilter: 'blur(20px)',
          maxHeight: '90vh',
          overflowY: 'auto',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{
          padding: isMobile ? '20px' : '24px',
          borderBottom: `1px solid ${theme.border}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          background: theme.bg,
          zIndex: 10,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Brain size={28} color={theme.info} />
            <div>
              <h2 style={{
                margin: 0,
                fontSize: isMobile ? '20px' : '24px',
                fontWeight: '700',
                color: theme.text,
              }}>
                AI Analysis: {symbol}
              </h2>
              {analysis && (
                <p style={{
                  margin: '4px 0 0 0',
                  fontSize: '14px',
                  color: theme.textMuted,
                }}>
                  Confidence: {analysis.confidence_score.toFixed(1)}%
                </p>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: theme.textMuted,
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '8px',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = theme.bgLight;
              e.currentTarget.style.color = theme.text;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.color = theme.textMuted;
            }}
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: isMobile ? '20px' : '24px' }}>
          {loading && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '60px 20px',
              color: theme.textMuted,
            }}>
              <Loader2 size={48} style={{ animation: 'spin 1s linear infinite' }} />
              <p style={{ marginTop: '16px', fontSize: '16px' }}>
                Analyzing {symbol}...
              </p>
            </div>
          )}

          {error && (
            <div style={{
              padding: '20px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: `1px solid ${theme.danger}`,
              borderRadius: '12px',
              color: theme.danger,
              fontSize: '14px',
            }}>
              <AlertTriangle size={20} style={{ display: 'inline', marginRight: '8px' }} />
              {error}
            </div>
          )}

          {!loading && !error && analysis && (
            <>
              {/* Summary Card */}
              <div style={{
                padding: '20px',
                background: theme.bgLight,
                border: `1px solid ${theme.border}`,
                borderRadius: '12px',
                marginBottom: '24px',
              }}>
                <h3 style={{
                  margin: '0 0 12px 0',
                  fontSize: '16px',
                  fontWeight: '600',
                  color: theme.text,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}>
                  Summary
                </h3>
                <p style={{
                  margin: 0,
                  fontSize: '15px',
                  lineHeight: '1.6',
                  color: theme.text,
                }}>
                  {analysis.summary}
                </p>
              </div>

              {/* Key Metrics Grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: isMobile ? '1fr 1fr' : 'repeat(4, 1fr)',
                gap: '16px',
                marginBottom: '24px',
              }}>
                <MetricCard
                  label="Current Price"
                  value={`$${analysis.current_price.toFixed(2)}`}
                  color={theme.info}
                  icon={<TrendingUp size={20} />}
                />
                <MetricCard
                  label="Support"
                  value={`$${analysis.support_level.toFixed(2)}`}
                  color={theme.primary}
                  icon={<Shield size={20} />}
                />
                <MetricCard
                  label="Resistance"
                  value={`$${analysis.resistance_level.toFixed(2)}`}
                  color={theme.danger}
                  icon={<Target size={20} />}
                />
                <MetricCard
                  label="Take Profit"
                  value={`$${analysis.take_profit_suggestion.toFixed(2)}`}
                  color={theme.primary}
                  icon={<TrendingUp size={20} />}
                />
              </div>

              {/* Trend & Momentum */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
                gap: '16px',
                marginBottom: '24px',
              }}>
                <InfoCard
                  title="Trend"
                  content={analysis.trend}
                  icon={<TrendingUp size={20} color={theme.info} />}
                  theme={theme}
                />
                <InfoCard
                  title="Momentum"
                  content={analysis.momentum}
                  icon={<TrendingDown size={20} color={theme.warning} />}
                  theme={theme}
                />
              </div>

              {/* Risk Assessment */}
              <div style={{
                padding: '20px',
                background: 'rgba(234, 179, 8, 0.1)',
                border: `1px solid ${theme.warning}`,
                borderRadius: '12px',
                marginBottom: '24px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <AlertTriangle size={20} color={theme.warning} />
                  <h3 style={{
                    margin: 0,
                    fontSize: '14px',
                    fontWeight: '600',
                    color: theme.text,
                    textTransform: 'uppercase',
                  }}>
                    Risk Assessment
                  </h3>
                </div>
                <p style={{ margin: 0, fontSize: '14px', color: theme.text }}>
                  {analysis.risk_assessment}
                </p>
              </div>

              {/* Entry & Exit Suggestions */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
                gap: '16px',
                marginBottom: '24px',
              }}>
                <SuggestionCard
                  title="Entry Suggestion"
                  content={analysis.entry_suggestion}
                  color={theme.primary}
                  theme={theme}
                />
                <SuggestionCard
                  title="Exit Suggestion"
                  content={analysis.exit_suggestion}
                  color={theme.danger}
                  theme={theme}
                />
              </div>

              {/* Full Analysis */}
              <div style={{
                padding: '20px',
                background: theme.bgLight,
                border: `1px solid ${theme.border}`,
                borderRadius: '12px',
                marginBottom: '24px',
              }}>
                <h3 style={{
                  margin: '0 0 16px 0',
                  fontSize: '16px',
                  fontWeight: '600',
                  color: theme.text,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}>
                  Detailed Analysis
                </h3>
                <div style={{
                  fontSize: '14px',
                  lineHeight: '1.8',
                  color: theme.text,
                  whiteSpace: 'pre-line',
                }}>
                  {analysis.analysis}
                </div>
              </div>

              {/* Technical Indicators */}
              <div style={{
                padding: '20px',
                background: theme.bgLight,
                border: `1px solid ${theme.border}`,
                borderRadius: '12px',
              }}>
                <h3 style={{
                  margin: '0 0 16px 0',
                  fontSize: '16px',
                  fontWeight: '600',
                  color: theme.text,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}>
                  Key Indicators
                </h3>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: isMobile ? '1fr 1fr' : 'repeat(3, 1fr)',
                  gap: '12px',
                }}>
                  <IndicatorItem label="RSI" value={analysis.key_indicators.rsi.toFixed(1)} theme={theme} />
                  <IndicatorItem label="MACD Histogram" value={analysis.key_indicators.macd_histogram.toFixed(4)} theme={theme} />
                  {analysis.key_indicators.sma_20 && (
                    <IndicatorItem label="SMA 20" value={`$${analysis.key_indicators.sma_20.toFixed(2)}`} theme={theme} />
                  )}
                  {analysis.key_indicators.sma_50 && (
                    <IndicatorItem label="SMA 50" value={`$${analysis.key_indicators.sma_50.toFixed(2)}`} theme={theme} />
                  )}
                  {analysis.key_indicators.sma_200 && (
                    <IndicatorItem label="SMA 200" value={`$${analysis.key_indicators.sma_200.toFixed(2)}`} theme={theme} />
                  )}
                  {analysis.key_indicators.current_vs_sma20 !== null && analysis.key_indicators.current_vs_sma20 !== undefined && (
                    <IndicatorItem
                      label="vs SMA20"
                      value={`${analysis.key_indicators.current_vs_sma20 > 0 ? '+' : ''}${analysis.key_indicators.current_vs_sma20.toFixed(2)}%`}
                      theme={theme}
                    />
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer Actions */}
        {!loading && !error && analysis && (
          <div style={{
            padding: isMobile ? '20px' : '24px',
            borderTop: `1px solid ${theme.border}`,
            display: 'flex',
            gap: '12px',
            flexWrap: 'wrap',
            position: 'sticky',
            bottom: 0,
            background: theme.bg,
            zIndex: 10,
          }}>
            <button
              onClick={() => {
                // Navigate to Execute Trade workflow with pre-filled data
                navigateToTrade({
                  symbol,
                  side: 'buy',
                  entryPrice: analysis.current_price,
                  stopLoss: analysis.stop_loss_suggestion,
                  takeProfit: analysis.take_profit_suggestion,
                  notes: `AI Analysis (${new Date().toLocaleDateString()}): ${analysis.summary.substring(0, 100)}...`
                });

                // Call legacy callback if provided
                if (onExecuteTrade) {
                  onExecuteTrade(symbol);
                }

                onClose();
                showToast(`✅ Navigating to Execute Trade with pre-filled data for ${symbol}`);
              }}
              style={{
                flex: 1,
                minWidth: isMobile ? '100%' : '120px',
                padding: '12px 24px',
                background: theme.primary,
                color: '#0f172a',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              Execute Trade
            </button>
            <div style={{
              flex: 1,
              minWidth: isMobile ? '100%' : '120px',
              position: 'relative'
            }} ref={dropdownRef}>
              <button
                onClick={() => setShowWatchlistDropdown(!showWatchlistDropdown)}
                style={{
                  width: '100%',
                  padding: '12px 24px',
                  background: theme.bgLight,
                  color: theme.text,
                  border: `1px solid ${theme.border}`,
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(30, 41, 59, 1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = theme.bgLight;
                }}
              >
                <Star size={18} />
                Add to Watchlist
              </button>

              {/* Watchlist Dropdown */}
              {showWatchlistDropdown && (
                <div style={{
                  position: 'absolute',
                  bottom: '100%',
                  left: 0,
                  right: 0,
                  marginBottom: '8px',
                  background: theme.bg,
                  border: `1px solid ${theme.border}`,
                  borderRadius: '12px',
                  padding: '12px',
                  boxShadow: '0 -4px 24px rgba(0, 0, 0, 0.3)',
                  zIndex: 1000,
                  maxHeight: '300px',
                  overflowY: 'auto'
                }}>
                  <div style={{
                    fontSize: '12px',
                    fontWeight: 600,
                    color: theme.textMuted,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    marginBottom: '12px'
                  }}>
                    Select Watchlist
                  </div>

                  {/* Existing Watchlists */}
                  {profile.watchlists.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '12px' }}>
                      {profile.watchlists.map((watchlist) => (
                        <button
                          key={watchlist.id}
                          onClick={() => handleAddToWatchlist(watchlist.id)}
                          style={{
                            padding: '10px 12px',
                            background: theme.bgLight,
                            border: `1px solid ${theme.border}`,
                            borderRadius: '8px',
                            color: theme.text,
                            fontSize: '14px',
                            fontWeight: 500,
                            cursor: 'pointer',
                            textAlign: 'left',
                            transition: 'all 0.2s',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(30, 41, 59, 1)';
                            e.currentTarget.style.borderColor = theme.primary;
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = theme.bgLight;
                            e.currentTarget.style.borderColor = theme.border;
                          }}
                        >
                          <span>{watchlist.name}</span>
                          <span style={{
                            fontSize: '12px',
                            color: theme.textMuted,
                            padding: '2px 8px',
                            background: theme.bg,
                            borderRadius: '4px'
                          }}>
                            {watchlist.symbols.length}
                          </span>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div style={{
                      padding: '16px',
                      textAlign: 'center',
                      color: theme.textMuted,
                      fontSize: '14px',
                      marginBottom: '12px'
                    }}>
                      No watchlists yet
                    </div>
                  )}

                  {/* Create New Watchlist */}
                  {!showCreateWatchlist ? (
                    <button
                      onClick={() => setShowCreateWatchlist(true)}
                      style={{
                        width: '100%',
                        padding: '10px 12px',
                        background: `${theme.primary}20`,
                        border: `1px solid ${theme.primary}`,
                        borderRadius: '8px',
                        color: theme.primary,
                        fontSize: '14px',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '6px',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = `${theme.primary}30`;
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = `${theme.primary}20`;
                      }}
                    >
                      <Plus size={16} />
                      Create New Watchlist
                    </button>
                  ) : (
                    <div style={{
                      padding: '12px',
                      background: theme.bgLight,
                      borderRadius: '8px',
                      border: `1px solid ${theme.border}`
                    }}>
                      <input
                        type="text"
                        value={newWatchlistName}
                        onChange={(e) => setNewWatchlistName(e.target.value)}
                        placeholder="Watchlist name"
                        autoFocus
                        style={{
                          width: '100%',
                          padding: '8px 12px',
                          background: theme.bg,
                          border: `1px solid ${theme.border}`,
                          borderRadius: '6px',
                          color: theme.text,
                          fontSize: '14px',
                          marginBottom: '8px',
                          outline: 'none'
                        }}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleCreateWatchlist();
                          if (e.key === 'Escape') setShowCreateWatchlist(false);
                        }}
                      />
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          onClick={handleCreateWatchlist}
                          style={{
                            flex: 1,
                            padding: '8px 12px',
                            background: theme.primary,
                            color: '#0f172a',
                            border: 'none',
                            borderRadius: '6px',
                            fontSize: '13px',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          Create
                        </button>
                        <button
                          onClick={() => {
                            setShowCreateWatchlist(false);
                            setNewWatchlistName('');
                          }}
                          style={{
                            flex: 1,
                            padding: '8px 12px',
                            background: theme.bgLight,
                            color: theme.text,
                            border: `1px solid ${theme.border}`,
                            borderRadius: '6px',
                            fontSize: '13px',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Animations */}
        <style>{`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
};

// Helper Components
const MetricCard = ({ label, value, color, icon }: { label: string; value: string; color: string; icon: React.ReactNode }) => (
  <div style={{
    padding: '16px',
    background: `${color}15`,
    border: `1px solid ${color}40`,
    borderRadius: '8px',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color }}>
      {icon}
      <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: '600' }}>
        {label}
      </div>
    </div>
    <div style={{ fontSize: '20px', fontWeight: '700', color }}>
      {value}
    </div>
  </div>
);

const InfoCard = ({ title, content, icon, theme }: { title: string; content: string; icon: React.ReactNode; theme: ThemeColors }) => (
  <div style={{
    padding: '16px',
    background: theme.bgLight,
    border: `1px solid ${theme.border}`,
    borderRadius: '8px',
  }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
      {icon}
      <div style={{ fontSize: '12px', color: theme.textMuted, textTransform: 'uppercase', fontWeight: '600' }}>
        {title}
      </div>
    </div>
    <div style={{ fontSize: '16px', fontWeight: '600', color: theme.text }}>
      {content}
    </div>
  </div>
);

const SuggestionCard = ({ title, content, color, theme }: { title: string; content: string; color: string; theme: ThemeColors }) => (
  <div style={{
    padding: '16px',
    background: `${color}10`,
    border: `1px solid ${color}40`,
    borderRadius: '8px',
  }}>
    <h4 style={{
      margin: '0 0 8px 0',
      fontSize: '12px',
      color,
      textTransform: 'uppercase',
      fontWeight: '600',
      letterSpacing: '0.5px',
    }}>
      {title}
    </h4>
    <p style={{
      margin: 0,
      fontSize: '14px',
      lineHeight: '1.6',
      color: theme.text,
    }}>
      {content}
    </p>
  </div>
);

const IndicatorItem = ({ label, value, theme }: { label: string; value: string; theme: ThemeColors }) => (
  <div>
    <div style={{ fontSize: '11px', color: theme.textMuted, marginBottom: '4px', textTransform: 'uppercase' }}>
      {label}
    </div>
    <div style={{ fontSize: '15px', fontWeight: '600', color: theme.text }}>
      {value}
    </div>
  </div>
);

export default AIAnalysisModal;
