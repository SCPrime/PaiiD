/**
 * Pattern Recognition Component
 * 
 * Visual pattern recognition with explanations for friends and family.
 * Makes complex technical analysis accessible and understandable.
 */

import {
    Info,
    Minus,
    Target,
    TrendingDown,
    TrendingUp,
    XCircle
} from 'lucide-react';
import React, { useEffect, useState } from 'react';

interface Pattern {
  pattern_type: string;
  signal: 'bullish' | 'bearish' | 'neutral';
  confidence: number;
  description: string;
  target_price?: number;
  stop_loss?: number;
  key_levels: Record<string, number>;
  start_date: string;
  end_date: string;
}

interface PatternRecognitionProps {
  symbol?: string;
  onPatternSelect?: (pattern: Pattern) => void;
}

export const PatternRecognition: React.FC<PatternRecognitionProps> = ({ 
  symbol = 'SPY',
  onPatternSelect 
}) => {
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPattern, setSelectedPattern] = useState<Pattern | null>(null);
  const [showExplanations, setShowExplanations] = useState(true);

  useEffect(() => {
    loadPatterns();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol]);

  const loadPatterns = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL}/api/ml/detect-patterns?symbol=${symbol}&lookback_days=90&min_confidence=0.6`
      );
      const data = await response.json();
      setPatterns(data.patterns || []);
    } catch (error) {
      console.error('Failed to load patterns:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPatternIcon = (patternType: string) => {
    switch (patternType) {
      case 'double_top':
      case 'head_shoulders':
        return <TrendingDown className="w-5 h-5 text-red-500" />;
      case 'double_bottom':
      case 'inverse_head_shoulders':
        return <TrendingUp className="w-5 h-5 text-green-500" />;
      case 'ascending_triangle':
        return <TrendingUp className="w-5 h-5 text-blue-500" />;
      case 'descending_triangle':
        return <TrendingDown className="w-5 h-5 text-orange-500" />;
      case 'symmetric_triangle':
        return <Minus className="w-5 h-5 text-gray-500" />;
      default:
        return <Target className="w-5 h-5 text-purple-500" />;
    }
  };

  const getPatternExplanation = (pattern: Pattern) => {
    const explanations = {
      'double_top': {
        title: 'Double Top Pattern',
        description: 'This is a bearish reversal pattern that forms when the price reaches a similar high twice, creating a "M" shape. It suggests the uptrend may be ending.',
        what_it_means: 'The market tried to break higher twice but failed both times, indicating selling pressure is building.',
        what_to_watch: 'Watch for a break below the "neckline" (the low between the two peaks) to confirm the pattern.',
        confidence_tip: 'Higher confidence when the two peaks are similar in height and the pattern forms over several weeks.'
      },
      'double_bottom': {
        title: 'Double Bottom Pattern',
        description: 'This is a bullish reversal pattern that forms when the price reaches a similar low twice, creating a "W" shape. It suggests the downtrend may be ending.',
        what_it_means: 'The market tried to break lower twice but failed both times, indicating buying pressure is building.',
        what_to_watch: 'Watch for a break above the "neckline" (the high between the two bottoms) to confirm the pattern.',
        confidence_tip: 'Higher confidence when the two bottoms are similar in depth and the pattern forms over several weeks.'
      },
      'head_shoulders': {
        title: 'Head and Shoulders Pattern',
        description: 'This is a major bearish reversal pattern with three peaks: a higher middle peak (head) and two lower peaks (shoulders). It\'s one of the most reliable reversal patterns.',
        what_it_means: 'The market made one final push higher (head) but couldn\'t sustain it, suggesting exhaustion of the uptrend.',
        what_to_watch: 'Watch for a break below the "neckline" (the line connecting the two shoulder lows) to confirm the reversal.',
        confidence_tip: 'Most reliable when the head is significantly higher than the shoulders and volume decreases on the right shoulder.'
      },
      'ascending_triangle': {
        title: 'Ascending Triangle Pattern',
        description: 'This is a bullish continuation pattern with a flat top (resistance) and rising bottom (support). It suggests accumulation before a breakout.',
        what_it_means: 'Buyers are getting more aggressive (higher lows) while sellers are holding the same price level.',
        what_to_watch: 'Watch for a breakout above the resistance line with increased volume.',
        confidence_tip: 'More reliable when the triangle forms over several weeks and volume increases on the breakout.'
      },
      'descending_triangle': {
        title: 'Descending Triangle Pattern',
        description: 'This is a bearish continuation pattern with a flat bottom (support) and falling top (resistance). It suggests distribution before a breakdown.',
        what_it_means: 'Sellers are getting more aggressive (lower highs) while buyers are holding the same price level.',
        what_to_watch: 'Watch for a breakdown below the support line with increased volume.',
        confidence_tip: 'More reliable when the triangle forms over several weeks and volume increases on the breakdown.'
      },
      'symmetric_triangle': {
        title: 'Symmetric Triangle Pattern',
        description: 'This is a neutral pattern with both rising support and falling resistance lines converging. It suggests indecision before a directional move.',
        what_it_means: 'Neither buyers nor sellers are in control, creating a balance that will eventually break one way.',
        what_to_watch: 'Watch for a breakout in either direction with increased volume to determine the next move.',
        confidence_tip: 'The direction of the breakout often follows the previous trend before the triangle formed.'
      }
    };

    return explanations[pattern.pattern_type as keyof typeof explanations] || {
      title: 'Unknown Pattern',
      description: 'This pattern type is not yet explained.',
      what_it_means: 'Pattern analysis is still being processed.',
      what_to_watch: 'Monitor the pattern for confirmation signals.',
      confidence_tip: 'Higher confidence patterns are more reliable for trading decisions.'
    };
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'bullish': return 'text-green-600 bg-green-50 border-green-200';
      case 'bearish': return 'text-red-600 bg-red-50 border-red-200';
      case 'neutral': return 'text-gray-600 bg-gray-50 border-gray-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const handlePatternClick = (pattern: Pattern) => {
    setSelectedPattern(pattern);
    onPatternSelect?.(pattern);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Analyzing patterns...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Target className="w-6 h-6 text-purple-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Pattern Recognition</h3>
            <p className="text-sm text-gray-600">AI-detected chart patterns with explanations</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowExplanations(!showExplanations)}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              showExplanations 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Info className="w-4 h-4" />
            <span>{showExplanations ? 'Hide' : 'Show'} Explanations</span>
          </button>
        </div>
      </div>

      {/* Patterns List */}
      {patterns.length > 0 ? (
        <div className="space-y-4">
          {patterns.map((pattern, index) => (
            <div
              key={index}
              className={`border rounded-xl p-4 cursor-pointer transition-all hover:shadow-md ${getSignalColor(pattern.signal)}`}
              onClick={() => handlePatternClick(pattern)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  {getPatternIcon(pattern.pattern_type)}
                  <div>
                    <h4 className="font-semibold text-gray-900">
                      {pattern.pattern_type.replace('_', ' ').toUpperCase()}
                    </h4>
                    <p className="text-sm text-gray-600">{pattern.description}</p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className={`font-semibold ${getConfidenceColor(pattern.confidence)}`}>
                    {Math.round(pattern.confidence * 100)}%
                  </div>
                  <div className="text-xs text-gray-500">confidence</div>
                </div>
              </div>

              {/* Pattern Details */}
              <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Signal:</span>
                  <span className={`ml-2 font-medium ${
                    pattern.signal === 'bullish' ? 'text-green-600' :
                    pattern.signal === 'bearish' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {pattern.signal.toUpperCase()}
                  </span>
                </div>
                {pattern.target_price && (
                  <div>
                    <span className="text-gray-500">Target:</span>
                    <span className="ml-2 font-medium">${pattern.target_price.toFixed(2)}</span>
                  </div>
                )}
                {pattern.stop_loss && (
                  <div>
                    <span className="text-gray-500">Stop Loss:</span>
                    <span className="ml-2 font-medium">${pattern.stop_loss.toFixed(2)}</span>
                  </div>
                )}
                <div>
                  <span className="text-gray-500">Duration:</span>
                  <span className="ml-2 font-medium">
                    {Math.ceil((new Date(pattern.end_date).getTime() - new Date(pattern.start_date).getTime()) / (1000 * 60 * 60 * 24))} days
                  </span>
                </div>
              </div>

              {/* Explanations */}
              {showExplanations && (
                <div className="mt-4 p-3 bg-white bg-opacity-50 rounded-lg">
                  {(() => {
                    const explanation = getPatternExplanation(pattern);
                    return (
                      <div className="space-y-2">
                        <h5 className="font-medium text-gray-900">{explanation.title}</h5>
                        <p className="text-sm text-gray-700">{explanation.description}</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                          <div>
                            <div className="text-xs font-medium text-gray-500 mb-1">What it means:</div>
                            <div className="text-xs text-gray-700">{explanation.what_it_means}</div>
                          </div>
                          <div>
                            <div className="text-xs font-medium text-gray-500 mb-1">What to watch:</div>
                            <div className="text-xs text-gray-700">{explanation.what_to_watch}</div>
                          </div>
                        </div>
                        <div className="mt-2 p-2 bg-blue-50 rounded text-xs text-blue-800">
                          <strong>💡 Tip:</strong> {explanation.confidence_tip}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Patterns Detected</h3>
          <p className="text-gray-600 mb-4">
            No significant chart patterns found in the recent price action for {symbol}.
          </p>
          <div className="text-sm text-gray-500">
            Patterns typically form over several weeks. Try checking back later or analyze a different time period.
          </div>
        </div>
      )}

      {/* Selected Pattern Details */}
      {selectedPattern && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Pattern Details</h3>
              <button
                onClick={() => setSelectedPattern(null)}
                className="text-gray-400 hover:text-gray-600"
                aria-label="Close pattern details"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                {getPatternIcon(selectedPattern.pattern_type)}
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">
                    {selectedPattern.pattern_type.replace('_', ' ').toUpperCase()}
                  </h4>
                  <p className="text-gray-600">{selectedPattern.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Signal</div>
                  <div className={`font-semibold ${
                    selectedPattern.signal === 'bullish' ? 'text-green-600' :
                    selectedPattern.signal === 'bearish' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {selectedPattern.signal.toUpperCase()}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Confidence</div>
                  <div className={`font-semibold ${getConfidenceColor(selectedPattern.confidence)}`}>
                    {Math.round(selectedPattern.confidence * 100)}%
                  </div>
                </div>
              </div>

              {Object.keys(selectedPattern.key_levels).length > 0 && (
                <div>
                  <div className="text-sm font-medium text-gray-500 mb-2">Key Levels</div>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(selectedPattern.key_levels).map(([key, value]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-600">{key.replace('_', ' ')}:</span>
                        <span className="font-medium">${value.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-4 border-t">
                <h5 className="font-medium text-gray-900 mb-2">Trading Considerations</h5>
                <div className="space-y-2 text-sm text-gray-700">
                  {selectedPattern.target_price && (
                    <div>🎯 <strong>Target Price:</strong> ${selectedPattern.target_price.toFixed(2)}</div>
                  )}
                  {selectedPattern.stop_loss && (
                    <div>🛡️ <strong>Stop Loss:</strong> ${selectedPattern.stop_loss.toFixed(2)}</div>
                  )}
                  <div>📊 <strong>Risk/Reward:</strong> {
                    selectedPattern.target_price && selectedPattern.stop_loss 
                      ? ((selectedPattern.target_price - selectedPattern.stop_loss) / selectedPattern.stop_loss * 100).toFixed(1) + '%'
                      : 'Calculate based on your entry'
                  }</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
