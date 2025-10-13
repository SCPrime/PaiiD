"use client";

import { useState } from "react";
import { Card, Button } from "./ui";
import { theme } from "../styles/theme";

interface Recommendation {
  symbol: string;
  action: "BUY" | "SELL" | "HOLD";
  confidence: number;
  reason: string;
  targetPrice: number;
  currentPrice: number;
  timeframe?: string;
  risk?: string;
  entryPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
  riskRewardRatio?: number;
  indicators?: {
    rsi?: number;
    macd?: { macd: number; signal: number; histogram: number };
    bollinger_bands?: { upper: number; middle: number; lower: number };
    moving_averages?: { sma_20?: number; sma_50?: number; sma_200?: number; ema_12?: number };
    trend?: { direction: string; strength: number; support: number; resistance: number };
  };
}

export default function AIRecommendations() {
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);
  const [useTechnical, setUseTechnical] = useState(true);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      // Use new /ai/signals endpoint with technical analysis
      const endpoint = useTechnical
        ? "/api/proxy/ai/signals?use_technical=true&min_confidence=60"
        : "/api/proxy/ai/recommendations";

      const res = await fetch(endpoint);

      if (!res.ok) {
        throw new Error(`Failed to fetch recommendations: ${res.status}`);
      }

      const data = await res.json();
      setRecommendations(data.recommendations || []);
    } catch (err: any) {
      console.error('Error fetching recommendations:', err);
      setError(err.message || 'Failed to load AI recommendations. Please ensure backend is running.');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case "BUY": return theme.colors.primary;
      case "SELL": return theme.colors.danger;
      case "HOLD": return theme.colors.warning;
      default: return theme.colors.textMuted;
    }
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 80) return "High";
    if (confidence >= 60) return "Medium";
    return "Low";
  };

  const getRiskColor = (risk?: string) => {
    switch (risk) {
      case "Low": return theme.colors.primary;
      case "Medium": return theme.colors.warning;
      case "High": return theme.colors.danger;
      default: return theme.colors.textMuted;
    }
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
            AI-powered trading suggestions based on {useTechnical ? 'technical indicators' : 'market analysis'}
          </p>
        </div>

        <div style={{ display: 'flex', gap: theme.spacing.md, alignItems: 'center' }}>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.sm,
            fontSize: '14px',
            color: theme.colors.text,
            cursor: 'pointer'
          }}>
            <input
              type="checkbox"
              checked={useTechnical}
              onChange={(e) => setUseTechnical(e.target.checked)}
              style={{ cursor: 'pointer' }}
            />
            Use Technical Analysis
          </label>
          <Button onClick={fetchRecommendations} loading={loading} variant="primary">
            Generate Recommendations
          </Button>
        </div>
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
              {/* Symbol & Price */}
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
                {rec.risk && (
                  <div style={{
                    fontSize: '12px',
                    color: getRiskColor(rec.risk),
                    marginTop: theme.spacing.xs,
                    fontWeight: '600'
                  }}>
                    {rec.risk} Risk
                  </div>
                )}
              </div>

              {/* Reason */}
              <div>
                <div style={{
                  fontSize: '14px',
                  color: theme.colors.text,
                  lineHeight: '1.6'
                }}>
                  {rec.reason}
                </div>
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

              {/* Execute Button */}
              <div>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => {
                    // TODO: Navigate to Execute Trade with pre-filled data
                    alert(`Execute ${rec.action} order for ${rec.symbol}\nEntry: $${rec.entryPrice?.toFixed(2)}\nStop Loss: $${rec.stopLoss?.toFixed(2)}\nTake Profit: $${rec.takeProfit?.toFixed(2)}`);
                  }}
                >
                  Execute Signal
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setSelectedRec(selectedRec?.symbol === rec.symbol ? null : rec)}
                  style={{ marginTop: theme.spacing.sm }}
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
                    Risk/Reward
                  </div>
                  <div style={{
                    fontSize: '18px',
                    fontWeight: '600',
                    color: theme.colors.secondary
                  }}>
                    {rec.riskRewardRatio?.toFixed(2)}
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
    </div>
  );
}
