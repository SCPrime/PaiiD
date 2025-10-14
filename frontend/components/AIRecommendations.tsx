"use client";

import { useState } from "react";
import { Card, Button } from "./ui";
import { theme } from "../styles/theme";
import StockLookup from "./StockLookup";
import { useWorkflow } from "../contexts/WorkflowContext";
import { showSuccess } from "../lib/toast";
import { TrendingUp, Shield, Target, AlertTriangle } from "lucide-react";

interface TradeData {
  symbol: string;
  side: "buy" | "sell";
  quantity: number;
  orderType: "market" | "limit";
  entryPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
}

interface Recommendation {
  symbol: string;
  action: "BUY" | "SELL" | "HOLD";
  confidence: number;
  score: number;  // 1-10 AI score
  reason: string;
  targetPrice: number;
  currentPrice: number;
  timeframe?: string;
  risk?: string;
  entryPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
  riskRewardRatio?: number;
  tradeData?: TradeData;
  portfolioFit?: string;
  indicators?: {
    rsi?: number;
    macd?: { macd: number; signal: number; histogram: number };
    bollinger_bands?: { upper: number; middle: number; lower: number };
    moving_averages?: { sma_20?: number; sma_50?: number; sma_200?: number; ema_12?: number };
    trend?: { direction: string; strength: number; support: number; resistance: number };
  };
}

interface PortfolioAnalysis {
  totalPositions: number;
  totalValue: number;
  topSectors: Array<{ name: string; percentage: number }>;
  riskScore: number;  // 1-10
  diversificationScore: number;  // 1-10
  recommendations: string[];
}

export default function AIRecommendations() {
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [portfolioAnalysis, setPortfolioAnalysis] = useState<PortfolioAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);

  // Stock research state
  const [researchSymbol, setResearchSymbol] = useState<string>('');
  const [showStockLookup, setShowStockLookup] = useState(false);

  // Workflow context for 1-click execution
  const { navigateToWorkflow } = useWorkflow();

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      // Use enhanced portfolio-aware recommendations endpoint
      const res = await fetch("/api/proxy/api/ai/recommendations");

      if (!res.ok) {
        throw new Error(`Failed to fetch recommendations: ${res.status}`);
      }

      const data = await res.json();
      setRecommendations(data.recommendations || []);
      setPortfolioAnalysis(data.portfolioAnalysis || null);
    } catch (err: any) {
      console.error('Error fetching recommendations:', err);
      setError(err.message || 'Failed to load AI recommendations. Please ensure backend is running.');
      setRecommendations([]);
      setPortfolioAnalysis(null);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteTrade = (rec: Recommendation) => {
    if (!rec.tradeData) {
      alert('No trade data available for this recommendation');
      return;
    }

    // Navigate to Execute Trade workflow with pre-filled data
    navigateToWorkflow('execute', rec.tradeData);
    showSuccess(`✅ Pre-filled trade for ${rec.symbol}`);
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case "BUY": return theme.colors.primary;
      case "SELL": return theme.colors.danger;
      case "HOLD": return theme.colors.warning;
      default: return theme.colors.textMuted;
    }
  };

  const getRiskColor = (risk?: string) => {
    switch (risk) {
      case "Low": return theme.colors.primary;
      case "Medium": return theme.colors.warning;
      case "High": return theme.colors.danger;
      default: return theme.colors.textMuted;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 8) return theme.colors.primary;
    if (score >= 6) return theme.colors.warning;
    return theme.colors.danger;
  };

  const getScoreLabel = (score: number) => {
    if (score >= 9) return "Excellent";
    if (score >= 8) return "Very Good";
    if (score >= 7) return "Good";
    if (score >= 6) return "Fair";
    if (score >= 5) return "Moderate";
    return "Weak";
  };

  return (
    <div style={{ padding: theme.spacing.lg }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: theme.spacing.lg
      }}>
        <div>
          <h2 style={{
            margin: 0,
            fontSize: '28px',
            fontWeight: '700',
            color: theme.colors.text,
            textShadow: theme.glow.purple,
            marginBottom: theme.spacing.xs
          }}>
            🤖 AI Recommendations
          </h2>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: theme.colors.textMuted
          }}>
            Portfolio-aware trading suggestions with 1-click execution
          </p>
        </div>

        <Button onClick={fetchRecommendations} loading={loading} variant="primary">
          Generate Recommendations
        </Button>
      </div>

      {error && (
        <div style={{
          padding: theme.spacing.md,
          background: 'rgba(255, 68, 68, 0.2)',
          border: `1px solid ${theme.colors.danger}`,
          borderRadius: theme.borderRadius.md,
          color: theme.colors.text,
          marginBottom: theme.spacing.lg,
          boxShadow: theme.glow.red
        }}>
          ❌ {error}
        </div>
      )}

      {/* Portfolio Analysis Panel */}
      {portfolioAnalysis && (
        <Card glow="green" style={{ marginBottom: theme.spacing.xl }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.md,
            marginBottom: theme.spacing.lg
          }}>
            <Shield size={32} color={theme.colors.primary} />
            <div>
              <h3 style={{
                margin: 0,
                fontSize: '20px',
                fontWeight: '700',
                color: theme.colors.text
              }}>
                Portfolio Analysis
              </h3>
              <p style={{
                margin: 0,
                marginTop: '4px',
                fontSize: '13px',
                color: theme.colors.textMuted
              }}>
                ${portfolioAnalysis.totalValue.toLocaleString()} • {portfolioAnalysis.totalPositions} positions
              </p>
            </div>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: theme.spacing.xl,
            marginBottom: theme.spacing.lg
          }}>
            {/* Risk Score */}
            <div>
              <div style={{
                fontSize: '11px',
                color: theme.colors.textMuted,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: theme.spacing.xs
              }}>
                Risk Score
              </div>
              <div style={{
                fontSize: '32px',
                fontWeight: '700',
                color: portfolioAnalysis.riskScore > 7 ? theme.colors.danger : portfolioAnalysis.riskScore > 5 ? theme.colors.warning : theme.colors.primary
              }}>
                {portfolioAnalysis.riskScore.toFixed(1)}/10
              </div>
              <div style={{
                fontSize: '11px',
                color: theme.colors.textMuted
              }}>
                {portfolioAnalysis.riskScore > 7 ? 'High Risk' : portfolioAnalysis.riskScore > 5 ? 'Moderate Risk' : 'Low Risk'}
              </div>
            </div>

            {/* Diversification Score */}
            <div>
              <div style={{
                fontSize: '11px',
                color: theme.colors.textMuted,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: theme.spacing.xs
              }}>
                Diversification
              </div>
              <div style={{
                fontSize: '32px',
                fontWeight: '700',
                color: portfolioAnalysis.diversificationScore >= 7 ? theme.colors.primary : portfolioAnalysis.diversificationScore >= 5 ? theme.colors.warning : theme.colors.danger
              }}>
                {portfolioAnalysis.diversificationScore.toFixed(1)}/10
              </div>
              <div style={{
                fontSize: '11px',
                color: theme.colors.textMuted
              }}>
                {portfolioAnalysis.diversificationScore >= 7 ? 'Well Diversified' : portfolioAnalysis.diversificationScore >= 5 ? 'Moderate' : 'Under-diversified'}
              </div>
            </div>

            {/* Top Sector */}
            <div>
              <div style={{
                fontSize: '11px',
                color: theme.colors.textMuted,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: theme.spacing.xs
              }}>
                Top Sector
              </div>
              <div style={{
                fontSize: '18px',
                fontWeight: '600',
                color: theme.colors.text
              }}>
                {portfolioAnalysis.topSectors[0]?.name || 'N/A'}
              </div>
              <div style={{
                fontSize: '11px',
                color: theme.colors.textMuted
              }}>
                {portfolioAnalysis.topSectors[0]?.percentage.toFixed(1)}% exposure
              </div>
            </div>
          </div>

          {/* Portfolio Recommendations */}
          {portfolioAnalysis.recommendations.length > 0 && (
            <div style={{
              padding: theme.spacing.md,
              background: 'rgba(16, 185, 129, 0.1)',
              border: `1px solid ${theme.colors.primary}`,
              borderRadius: theme.borderRadius.md
            }}>
              <div style={{
                fontSize: '12px',
                fontWeight: '600',
                color: theme.colors.primary,
                marginBottom: theme.spacing.sm,
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                💡 Portfolio Insights
              </div>
              {portfolioAnalysis.recommendations.map((rec, idx) => (
                <div key={idx} style={{
                  fontSize: '13px',
                  color: theme.colors.text,
                  marginBottom: theme.spacing.xs,
                  paddingLeft: theme.spacing.sm
                }}>
                  {rec}
                </div>
              ))}
            </div>
          )}
        </Card>
      )}

      {recommendations.length === 0 && !loading && !error && (
        <Card>
          <div style={{
            textAlign: 'center',
            padding: theme.spacing.xl,
            color: theme.colors.textMuted
          }}>
            <div style={{ fontSize: '48px', marginBottom: theme.spacing.md }}>🎯</div>
            <div style={{ fontSize: '16px' }}>
              Click "Generate Recommendations" to get AI-powered trading suggestions
            </div>
          </div>
        </Card>
      )}

      <div style={{ display: 'grid', gap: theme.spacing.md }}>
        {recommendations.map((rec, idx) => (
          <Card key={idx} glow="purple">
            {/* Main Recommendation Header */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'auto 1fr auto auto',
              gap: theme.spacing.lg,
              alignItems: 'center',
              marginBottom: theme.spacing.lg,
              paddingBottom: theme.spacing.lg,
              borderBottom: `1px solid ${theme.colors.border}`
            }}>
              {/* Symbol & Score */}
              <div>
                <div style={{
                  fontSize: '28px',
                  fontWeight: '700',
                  color: theme.colors.secondary,
                  textShadow: theme.glow.cyan
                }}>
                  {rec.symbol}
                </div>
                <div style={{
                  fontSize: '16px',
                  color: theme.colors.text,
                  marginTop: theme.spacing.xs
                }}>
                  ${rec.currentPrice.toFixed(2)}
                </div>

                {/* AI Score Badge */}
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '4px 12px',
                  background: `${getScoreColor(rec.score)}15`,
                  border: `2px solid ${getScoreColor(rec.score)}`,
                  borderRadius: theme.borderRadius.full,
                  marginTop: theme.spacing.sm
                }}>
                  <Target size={14} color={getScoreColor(rec.score)} />
                  <span style={{
                    fontSize: '14px',
                    fontWeight: '700',
                    color: getScoreColor(rec.score)
                  }}>
                    {rec.score.toFixed(1)} • {getScoreLabel(rec.score)}
                  </span>
                </div>

                {rec.risk && (
                  <div style={{
                    fontSize: '12px',
                    color: getRiskColor(rec.risk),
                    marginTop: theme.spacing.xs,
                    fontWeight: '600',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <AlertTriangle size={12} />
                    {rec.risk} Risk
                  </div>
                )}
              </div>

              {/* Reason & Portfolio Fit */}
              <div>
                <div style={{
                  fontSize: '14px',
                  color: theme.colors.text,
                  lineHeight: '1.6',
                  marginBottom: theme.spacing.sm
                }}>
                  {rec.reason}
                </div>

                {/* Portfolio Fit Indicator */}
                {rec.portfolioFit && (
                  <div style={{
                    display: 'inline-block',
                    padding: '6px 12px',
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: `1px solid ${theme.colors.primary}`,
                    borderRadius: theme.borderRadius.md,
                    fontSize: '12px',
                    color: theme.colors.text,
                    marginTop: theme.spacing.xs
                  }}>
                    {rec.portfolioFit}
                  </div>
                )}

                {rec.timeframe && (
                  <div style={{
                    fontSize: '12px',
                    color: theme.colors.textMuted,
                    marginTop: theme.spacing.sm
                  }}>
                    ⏱ Timeframe: {rec.timeframe}
                  </div>
                )}
              </div>

              {/* Action Badge */}
              <div style={{
                padding: `${theme.spacing.md} ${theme.spacing.lg}`,
                background: `${getActionColor(rec.action)}15`,
                border: `2px solid ${getActionColor(rec.action)}`,
                borderRadius: theme.borderRadius.md,
                textAlign: 'center'
              }}>
                <div style={{
                  color: getActionColor(rec.action),
                  fontWeight: '700',
                  fontSize: '20px',
                  marginBottom: theme.spacing.xs
                }}>
                  {rec.action}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: theme.colors.textMuted
                }}>
                  {rec.confidence.toFixed(1)}% confidence
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.sm }}>
                {rec.tradeData && rec.action !== "HOLD" && (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleExecuteTrade(rec)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <TrendingUp size={16} />
                    Execute Trade
                  </Button>
                )}
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    setResearchSymbol(rec.symbol);
                    setShowStockLookup(true);
                  }}
                >
                  Research Symbol
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setSelectedRec(selectedRec?.symbol === rec.symbol ? null : rec)}
                >
                  {selectedRec?.symbol === rec.symbol ? 'Hide Details' : 'View Details'}
                </Button>
              </div>
            </div>

            {/* Entry/Exit Details */}
            {rec.entryPrice && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: theme.spacing.md,
                marginBottom: theme.spacing.lg
              }}>
                <div>
                  <div style={{
                    fontSize: '11px',
                    color: theme.colors.textMuted,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    marginBottom: theme.spacing.xs
                  }}>
                    Entry Price
                  </div>
                  <div style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: theme.colors.primary
                  }}>
                    ${rec.entryPrice.toFixed(2)}
                  </div>
                </div>
                <div>
                  <div style={{
                    fontSize: '11px',
                    color: theme.colors.textMuted,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    marginBottom: theme.spacing.xs
                  }}>
                    Stop Loss
                  </div>
                  <div style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: theme.colors.danger
                  }}>
                    ${rec.stopLoss?.toFixed(2)}
                  </div>
                </div>
                <div>
                  <div style={{
                    fontSize: '11px',
                    color: theme.colors.textMuted,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    marginBottom: theme.spacing.xs
                  }}>
                    Take Profit
                  </div>
                  <div style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: theme.colors.primary
                  }}>
                    ${rec.takeProfit?.toFixed(2)}
                  </div>
                </div>
                <div>
                  <div style={{
                    fontSize: '11px',
                    color: theme.colors.textMuted,
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    marginBottom: theme.spacing.xs
                  }}>
                    Position Size
                  </div>
                  <div style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: theme.colors.secondary
                  }}>
                    {rec.tradeData?.quantity || 'N/A'} shares
                  </div>
                </div>
              </div>
            )}

            {/* Technical Indicators (Expandable) */}
            {selectedRec?.symbol === rec.symbol && rec.indicators && (
              <div style={{
                marginTop: theme.spacing.lg,
                paddingTop: theme.spacing.lg,
                borderTop: `1px solid ${theme.colors.border}`
              }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: theme.colors.text,
                  marginBottom: theme.spacing.md,
                  textTransform: 'uppercase',
                  letterSpacing: '1px'
                }}>
                  📊 Technical Indicators
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(2, 1fr)',
                  gap: theme.spacing.lg
                }}>
                  {/* RSI */}
                  {rec.indicators.rsi !== undefined && (
                    <div>
                      <div style={{
                        fontSize: '12px',
                        color: theme.colors.textMuted,
                        marginBottom: theme.spacing.xs
                      }}>
                        RSI (14)
                      </div>
                      <div style={{
                        fontSize: '20px',
                        fontWeight: '600',
                        color: rec.indicators.rsi < 30 ? theme.colors.primary : rec.indicators.rsi > 70 ? theme.colors.danger : theme.colors.text
                      }}>
                        {rec.indicators.rsi.toFixed(1)}
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: theme.colors.textMuted
                      }}>
                        {rec.indicators.rsi < 30 ? 'Oversold' : rec.indicators.rsi > 70 ? 'Overbought' : 'Neutral'}
                      </div>
                    </div>
                  )}

                  {/* MACD */}
                  {rec.indicators.macd && (
                    <div>
                      <div style={{
                        fontSize: '12px',
                        color: theme.colors.textMuted,
                        marginBottom: theme.spacing.xs
                      }}>
                        MACD Histogram
                      </div>
                      <div style={{
                        fontSize: '20px',
                        fontWeight: '600',
                        color: rec.indicators.macd.histogram > 0 ? theme.colors.primary : theme.colors.danger
                      }}>
                        {rec.indicators.macd.histogram.toFixed(4)}
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: theme.colors.textMuted
                      }}>
                        {rec.indicators.macd.histogram > 0 ? 'Bullish' : 'Bearish'} Crossover
                      </div>
                    </div>
                  )}

                  {/* Bollinger Bands */}
                  {rec.indicators.bollinger_bands && (
                    <div>
                      <div style={{
                        fontSize: '12px',
                        color: theme.colors.textMuted,
                        marginBottom: theme.spacing.xs
                      }}>
                        Bollinger Bands
                      </div>
                      <div style={{
                        fontSize: '14px',
                        color: theme.colors.text
                      }}>
                        <div>Upper: ${rec.indicators.bollinger_bands.upper.toFixed(2)}</div>
                        <div>Middle: ${rec.indicators.bollinger_bands.middle.toFixed(2)}</div>
                        <div>Lower: ${rec.indicators.bollinger_bands.lower.toFixed(2)}</div>
                      </div>
                    </div>
                  )}

                  {/* Trend */}
                  {rec.indicators.trend && (
                    <div>
                      <div style={{
                        fontSize: '12px',
                        color: theme.colors.textMuted,
                        marginBottom: theme.spacing.xs
                      }}>
                        Trend Analysis
                      </div>
                      <div style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: rec.indicators.trend.direction === 'bullish' ? theme.colors.primary : rec.indicators.trend.direction === 'bearish' ? theme.colors.danger : theme.colors.text,
                        textTransform: 'capitalize'
                      }}>
                        {rec.indicators.trend.direction}
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: theme.colors.textMuted
                      }}>
                        Strength: {(rec.indicators.trend.strength * 100).toFixed(0)}%
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: theme.colors.textMuted
                      }}>
                        Support: ${rec.indicators.trend.support.toFixed(2)} | Resistance: ${rec.indicators.trend.resistance.toFixed(2)}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Stock Research Section */}
      {showStockLookup && researchSymbol && (
        <div style={{
          marginTop: theme.spacing.xl,
          padding: theme.spacing.lg,
          background: 'rgba(15, 23, 42, 0.8)',
          border: `1px solid ${theme.colors.border}`,
          borderRadius: theme.borderRadius.lg,
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: theme.spacing.lg,
            paddingBottom: theme.spacing.md,
            borderBottom: `1px solid ${theme.colors.border}`
          }}>
            <h3 style={{
              margin: 0,
              fontSize: '22px',
              fontWeight: '700',
              color: theme.colors.text
            }}>
              Stock Research: {researchSymbol}
            </h3>
            <Button
              variant="secondary"
              onClick={() => {
                setShowStockLookup(false);
                setResearchSymbol('');
              }}
              style={{ fontSize: '14px', padding: '8px 20px' }}
            >
              Close
            </Button>
          </div>
          <StockLookup
            initialSymbol={researchSymbol}
            showChart={true}
            showIndicators={true}
            showCompanyInfo={true}
            showNews={false}
            enableAIAnalysis={true}
            onSymbolSelect={(sym) => setResearchSymbol(sym)}
          />
        </div>
      )}
    </div>
  );
}
