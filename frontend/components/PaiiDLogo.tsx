import { claudeAI } from '../lib/aiAdapter';
import React, { useState } from 'react';

interface PaiiDLogoProps {
  size?: 'xs' | 'small' | 'medium' | 'large' | 'xlarge';
  showSubtitle?: boolean;
  onClick?: () => void;
  className?: string;
}

const PaiiDLogo: React.FC<PaiiDLogoProps> = ({
  size = 'xlarge',
  showSubtitle = true,
  onClick,
  className = ''
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [query, setQuery] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState('');
  const [error, setError] = useState('');
  // Size mappings (from v46 artifact)
  const sizeMap = {
    xs: 18,
    small: 36,
    medium: 64,
    large: 96,
    xlarge: 120
  };

  const fontSize = sizeMap[size];

  // Dot positioning based on v46 artifact values (48.3% formula derived from 120px = 58px)
  const dotPositions = {
    xs: { top: 9, size: 2 },      // 18px logo
    small: { top: 17, size: 4 },   // 36px logo
    medium: { top: 31, size: 6 },  // 64px logo
    large: { top: 46, size: 10 },  // 96px logo
    xlarge: { top: 58, size: 12 }  // 120px logo (v46 artifact original)
  };

  const dotConfig = dotPositions[size];

  const handlePiClick = () => {
    if (onClick) {
      onClick();
    } else {
      setShowAIModal(true);
      setIsClosing(false);
    }
    console.log('AI Launch triggered!');
  };

  const handleCloseModal = () => {
    setIsClosing(true);
    setTimeout(() => {
      setShowAIModal(false);
      setIsClosing(false);
    }, 300);
  };
  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setIsLoading(true);
      setError('');
      setAiResponse('');

      // Call Claude AI with investment context
      const response = await claudeAI.chat([
        { role: 'user', content: `As a financial advisor for PaiiD (Personal AI Investment Dashboard), please help with this investment question: ${query}` }
      ]);

      setAiResponse(response);
      setQuery(''); // Clear input after successful response
    } catch (err) {
      console.error('AI Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to get AI response. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={className}>
      <style>
        {`
          @keyframes glow-ai {
            0%, 100% {
              text-shadow:
                0 0 15px rgba(69, 240, 192, 0.6),
                0 0 30px rgba(69, 240, 192, 0.4);
            }
            50% {
              text-shadow:
                0 0 25px rgba(69, 240, 192, 0.9),
                0 0 50px rgba(69, 240, 192, 0.6),
                0 0 75px rgba(69, 240, 192, 0.3);
            }
          }

          @keyframes slideUpFromBottom {
            from {
              transform: translateY(100%);
              opacity: 0;
            }
            to {
              transform: translateY(0);
              opacity: 1;
            }
          }

          @keyframes slideDownToBottom {
            from {
              transform: translateY(0);
              opacity: 1;
            }
            to {
              transform: translateY(100%);
              opacity: 0;
            }
          }

          .pi-symbol-${size} {
            position: relative;
            display: inline-block;
          }

          .pi-dot-${size} {
            position: absolute;
            background: #45f0c0;
            border-radius: 50%;
            box-shadow: 0 0 ${dotConfig.size * 0.8}px rgba(69, 240, 192, 0.8);
            cursor: pointer;
            transition: transform 0.2s ease;
          }

          .pi-dot-${size}:hover {
            transform: scale(1.2);
          }

          .pi-dot-left-${size} {
            top: ${dotConfig.top}px;
            left: 22%;
            width: ${dotConfig.size}px;
            height: ${dotConfig.size}px;
          }

          .pi-dot-right-${size} {
            top: ${dotConfig.top}px;
            right: 22%;
            width: ${dotConfig.size}px;
            height: ${dotConfig.size}px;
          }

          /* Static CSS classes for modal logos (independent of component size prop) */
          .pi-symbol-small {
            position: relative;
            display: inline-block;
          }

          .pi-symbol-medium {
            position: relative;
            display: inline-block;
          }

          .pi-dot-small {
            position: absolute;
            background: #45f0c0;
            border-radius: 50%;
            box-shadow: 0 0 2px rgba(69, 240, 192, 0.8);
            cursor: pointer;
            transition: transform 0.2s ease;
          }

          .pi-dot-small:hover {
            transform: scale(1.2);
          }

          .pi-dot-left-small {
            top: 10px;
            left: 22%;
            width: 2px;
            height: 2px;
          }

          .pi-dot-right-small {
            top: 10px;
            right: 22%;
            width: 2px;
            height: 2px;
          }

          .pi-dot-medium {
            position: absolute;
            background: #45f0c0;
            border-radius: 50%;
            box-shadow: 0 0 4px rgba(69, 240, 192, 0.8);
            cursor: pointer;
            transition: transform 0.2s ease;
          }

          .pi-dot-medium:hover {
            transform: scale(1.2);
          }

          .pi-dot-left-medium {
            top: 23px;
            left: 22%;
            width: 5px;
            height: 5px;
          }

          .pi-dot-right-medium {
            top: 23px;
            right: 22%;
            width: 5px;
            height: 5px;
          }
        `}
      </style>

      {/* Logo */}
      <div style={{
        fontSize: `${fontSize}px`,
        fontWeight: 'bold',
        fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        display: 'flex',
        alignItems: 'center',
        userSelect: 'none',
        justifyContent: 'center'
      }}>
        <span style={{ color: '#45f0c0' }}>P</span>
        <span style={{ color: '#45f0c0' }}>a</span>
        <span
          onClick={handlePiClick}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
          style={{
            color: '#45f0c0',
            animation: 'glow-ai 3s ease-in-out infinite',
            cursor: 'pointer',
            transition: 'transform 0.2s ease',
            transform: isHovered ? 'scale(1.1)' : 'scale(1)'
          }}
        >
          <span className={`pi-symbol-${size}`}>
            <span className={`pi-dot-${size} pi-dot-left-${size}`} onClick={handlePiClick}></span>
            <span className={`pi-dot-${size} pi-dot-right-${size}`} onClick={handlePiClick}></span>
            π
          </span>
        </span>
        <span style={{ color: '#45f0c0' }}>D</span>
      </div>

      {/* Subtitle */}
      {showSubtitle && (
        <div style={{ textAlign: 'center', marginTop: `${fontSize * 0.15}px` }}>
          <div style={{
            fontSize: `${fontSize * 0.18}px`,
            color: '#cbd5e1',
            marginBottom: '4px',
            fontFamily: '"Inter", sans-serif',
            letterSpacing: '0.5px'
          }}>
            Personal <span style={{ fontStyle: 'italic' }}>artificial intelligence</span>/<span style={{ fontStyle: 'italic' }}>investment</span> Dashboard
          </div>
          <div style={{
            fontSize: `${fontSize * 0.15}px`,
            color: '#94a3b8',
            fontFamily: '"Inter", sans-serif'
          }}>
            10 Stage Workflow
          </div>
        </div>
      )}

      {/* AI Modal (only if no custom onClick provided) */}
      {showAIModal && !onClick && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.6)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'flex-end'
        }}>
          <div style={{
            width: '100%',
            background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
            border: '2px solid #45f0c0',
            borderBottom: 'none',
            borderTopLeftRadius: '24px',
            borderTopRightRadius: '24px',
            padding: '40px',
            boxShadow: '0 -10px 50px rgba(69, 240, 192, 0.3)',
            animation: isClosing ? 'slideDownToBottom 0.3s ease-out forwards' : 'slideUpFromBottom 0.3s ease-out forwards'
          }}>
            <button
              onClick={handleCloseModal}
              style={{
                position: 'absolute',
                top: '16px',
                right: '16px',
                background: 'transparent',
                border: 'none',
                color: '#45f0c0',
                fontSize: '32px',
                cursor: 'pointer',
                padding: '8px',
                lineHeight: 1,
                fontWeight: 'bold'
              }}
            >
              ×
            </button>

            <div style={{
              marginBottom: '20px',
              textAlign: 'center',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '12px'
            }}>
              <div style={{
                fontSize: '48px',
                fontWeight: 'bold',
                fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                display: 'flex',
                alignItems: 'center'
              }}>
                <span style={{ color: '#45f0c0' }}>P</span>
                <span style={{ color: '#45f0c0' }}>a</span>
                <span style={{
                  color: '#45f0c0',
                  animation: 'glow-ai 3s ease-in-out infinite',
                  position: 'relative'
                }}>
                  <span className="pi-symbol-medium">
                    <span className="pi-dot-medium pi-dot-left-medium"></span>
                    <span className="pi-dot-medium pi-dot-right-medium"></span>
                    π
                  </span>
                </span>
                <span style={{ color: '#45f0c0' }}>D</span>
              </div>
              <span style={{
                color: '#cbd5e1',
                fontSize: '24px',
                fontFamily: '"Inter", sans-serif'
              }}>Interface</span>
            </div>

            <div style={{
              color: '#cbd5e1',
              fontSize: '16px',
              lineHeight: '1.6',
              textAlign: 'center',
              marginBottom: '30px'
            }}>
              This is your <span style={{ display: 'inline-flex', alignItems: 'center', fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }}>
                <span style={{ color: '#45f0c0' }}>P</span>
                <span style={{ color: '#45f0c0' }}>a</span>
                <span style={{ color: '#45f0c0', animation: 'glow-ai 3s ease-in-out infinite', position: 'relative' }}>
                  <span className="pi-symbol-small">
                    <span className="pi-dot-small pi-dot-left-small"></span>
                    <span className="pi-dot-small pi-dot-right-small"></span>
                    π
                  </span>
                </span>
                <span style={{ color: '#45f0c0' }}>D</span>
              </span> investment assistance to inform your financial decisions
            </div>

            <div style={{
              background: 'rgba(69, 240, 192, 0.1)',
              border: '1px solid rgba(69, 240, 192, 0.3)',
              borderRadius: '12px',
              padding: '24px',
              color: '#94a3b8',
              fontSize: '14px',
              marginBottom: '20px'
            }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '20px',
                  fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
                }}>
                  <span style={{ color: '#45f0c0' }}>P</span>
                  <span style={{ color: '#45f0c0' }}>a</span>
                  <span style={{
                    color: '#45f0c0',
                    animation: 'glow-ai 3s ease-in-out infinite',
                    position: 'relative'
                  }}>
                    <span className="pi-symbol-small">
                      <span className="pi-dot-small pi-dot-left-small"></span>
                      <span className="pi-dot-small pi-dot-right-small"></span>
                      π
                    </span>
                  </span>
                  <span style={{ color: '#45f0c0' }}>D</span>
                  <span style={{ color: '#45f0c0', marginLeft: '6px' }}>Capabilities Active:</span>
                </div>
              <ul style={{
                margin: '15px 0',
                paddingLeft: '20px',
                lineHeight: '1.8'
              }}>
                <li>Portfolio Analysis & Optimization</li>
                <li>Market Sentiment Analysis</li>
                <li>Risk Assessment & Management</li>
                <li>Investment Strategy Recommendations</li>
                <li>Real-time Market Insights</li>
              </ul>
            </div>

            <form onSubmit={handleQuerySubmit} style={{ marginTop: '20px' }}>
              <div style={{
                marginBottom: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                color: '#45f0c0',
                fontSize: '16px',
                fontWeight: 'bold'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  fontSize: '20px',
                  fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
                }}>
                  <span style={{ color: '#45f0c0' }}>Ask</span>
                  <span style={{ color: '#45f0c0' }}>P</span>
                  <span style={{ color: '#45f0c0' }}>a</span>
                  <span style={{
                    color: '#45f0c0',
                    animation: 'glow-ai 3s ease-in-out infinite',
                    position: 'relative'
                  }}>
                    <span className="pi-symbol-small">
                      <span className="pi-dot-small pi-dot-left-small"></span>
                      <span className="pi-dot-small pi-dot-right-small"></span>
                      π
                    </span>
                  </span>
                  <span style={{ color: '#45f0c0' }}>D</span>
                </div>
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type your investment question here..."
                disabled={isLoading}
                style={{
                  width: '100%',
                  padding: '16px',
                  background: '#0f172a',
                  border: '2px solid #45f0c0',
                  borderRadius: '8px',
                  color: '#45f0c0',
                  fontSize: '16px',
                  fontFamily: '"Inter", sans-serif',
                  outline: 'none',
                  boxSizing: 'border-box'
                }}
              />
              <div style={{
                marginTop: '8px',
                fontSize: '12px',
                color: '#94a3b8',
                textAlign: 'center'
              }}>
                Press Enter to submit
              </div>

              {/* Loading State */}
              {isLoading && (
                <div style={{
                  marginTop: '20px',
                  padding: '20px',
                  background: 'rgba(69, 240, 192, 0.05)',
                  border: '1px solid rgba(69, 240, 192, 0.2)',
                  borderRadius: '8px',
                  color: '#45f0c0',
                  textAlign: 'center',
                  fontSize: '14px'
                }}>
                  <div style={{ marginBottom: '10px' }}>⏳ Analyzing your question...</div>
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>PaπD AI is thinking</div>
                </div>
              )}

              {/* Error State */}
              {error && (
                <div style={{
                  marginTop: '20px',
                  padding: '20px',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '8px',
                  color: '#ef4444',
                  fontSize: '14px'
                }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>❌ Error</div>
                  <div>{error}</div>
                </div>
              )}

              {/* AI Response */}
              {aiResponse && !isLoading && (
                <div style={{
                  marginTop: '20px',
                  padding: '24px',
                  background: 'rgba(69, 240, 192, 0.05)',
                  border: '2px solid rgba(69, 240, 192, 0.3)',
                  borderRadius: '12px',
                  maxHeight: '400px',
                  overflowY: 'auto',
                }}>
                  <div style={{
                    color: '#45f0c0',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    marginBottom: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <span>🤖</span>
                    <span>PaπD AI Response</span>
                  </div>
                  <div style={{
                    color: '#cbd5e1',
                    fontSize: '14px',
                    lineHeight: '1.6',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {aiResponse}
                  </div>
                </div>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PaiiDLogo;
