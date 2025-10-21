import React, { useState } from 'react';

/**
 * 🔒 LOCKED FINAL PaiiD CHAT BOX 🔒
 *
 * DO NOT MODIFY THIS FILE WITHOUT EXPLICIT APPROVAL
 *
 * This is the final approved version with complete logo integration
 * All logos are size 21 and aligned inline with text
 */

interface CompletePaiiDLogoProps {
  size?: number;
}

const CompletePaiiDLogo: React.FC<CompletePaiiDLogoProps> = ({ size = 80 }) => {
  const iPiWidth = size * 0.56;
  const leftSpacingGap = size * 0.08;
  const rightSpacingGap = size * 0.02436;
  const viewBoxWidth = size * 2 + iPiWidth + leftSpacingGap + rightSpacingGap;
  const viewBoxHeight = size * 1.5;
  const baseline = size * 1.063;

  const scaleFactor = size / 120;
  const leftDotOffsetX = -15 * scaleFactor;
  const rightDotOffsetX = 15 * scaleFactor;
  const dotOffsetY = -75 * scaleFactor;
  const dotRadius = 6 * scaleFactor;
  const piCenterX = size * 0.55 + size * 0.5 + leftSpacingGap + (iPiWidth / 2);

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <style>{`
        @keyframes ipi-glow-breathe-${size} {
          0%, 100% {
            filter: drop-shadow(0 0 15px rgba(69, 240, 192, 0.6))
                    drop-shadow(0 0 30px rgba(69, 240, 192, 0.4));
          }
          50% {
            filter: drop-shadow(0 0 25px rgba(69, 240, 192, 0.9))
                    drop-shadow(0 0 50px rgba(69, 240, 192, 0.6))
                    drop-shadow(0 0 75px rgba(69, 240, 192, 0.3));
          }
        }
        .ipi-glow-pi-${size} {
          animation: ipi-glow-breathe-${size} 3s ease-in-out infinite;
        }
      `}</style>

      <svg
        width={viewBoxWidth}
        height={viewBoxHeight}
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
        style={{ display: 'block', overflow: 'visible' }}
      >
        <defs>
          <linearGradient id={`paiid-blue-${size}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style={{ stopColor: '#1a7560', stopOpacity: 1 }} />
            <stop offset="100%" style={{ stopColor: '#0d5a4a', stopOpacity: 1 }} />
          </linearGradient>
        </defs>

        <text
          x={0}
          y={baseline}
          fontFamily="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
          fontSize={size}
          fontWeight="bold"
          fill={`url(#paiid-blue-${size})`}
        >
          P
        </text>

        <text
          x={size * 0.55}
          y={baseline}
          fontFamily="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
          fontSize={size}
          fontWeight="bold"
          fill={`url(#paiid-blue-${size})`}
        >
          a
        </text>

        <circle
          cx={piCenterX + leftDotOffsetX}
          cy={baseline + dotOffsetY}
          r={dotRadius}
          fill="#45f0c0"
        />

        <circle
          cx={piCenterX + rightDotOffsetX}
          cy={baseline + dotOffsetY}
          r={dotRadius}
          fill="#45f0c0"
        />

        <text
          x={piCenterX}
          y={baseline}
          textAnchor="middle"
          fontFamily="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
          fontSize={size}
          fontWeight="bold"
          fill="#45f0c0"
          className={`ipi-glow-pi-${size}`}
        >
          π
        </text>

        <text
          x={size * 0.55 + size * 0.5 + leftSpacingGap + iPiWidth + rightSpacingGap}
          y={baseline}
          fontFamily="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
          fontSize={size}
          fontWeight="bold"
          fill={`url(#paiid-blue-${size})`}
        >
          D
        </text>
      </svg>
    </div>
  );
};

const PaiiDChatBoxWithLogo = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [query, setQuery] = useState('');

  const capabilitiesLeft = [
    'Morning Routine',
    'Active Positions',
    'Execute Trade',
    'P&L Dashboard',
    'News Review'
  ];

  const capabilitiesRight = [
    'Recommendations',
    'Strategy Builder',
    'Backtesting',
    'Research',
    'Settings'
  ];

  const handleQuerySubmit = () => {
    if (query.trim()) {
      console.log('User query:', query);
      setQuery('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleQuerySubmit();
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#0a0e12',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative'
    }}>
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(8px)',
            zIndex: 999
          }}
        />
      )}

      {isOpen && (
        <div
          style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            maxWidth: '100%',
            maxHeight: '70vh',
            backgroundColor: '#0f172a',
            borderTopLeftRadius: '24px',
            borderTopRightRadius: '24px',
            border: '2px solid #45f0c0',
            padding: '32px',
            zIndex: 1000,
            overflowY: 'auto'
          }}
        >
          <button
            onClick={() => setIsOpen(false)}
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
            alignItems: 'center'
          }}>
            <CompletePaiiDLogo size={60} />
          </div>

          <div style={{
            color: '#cbd5e1',
            fontSize: '16px',
            lineHeight: '1.6',
            textAlign: 'center',
            marginBottom: '30px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px'
          }}>
            Your <CompletePaiiDLogo size={21} /> assistant is here to inform your financial decisions
          </div>

          <div style={{
            marginBottom: '30px',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '20px'
          }}>
            <div style={{
              padding: '20px',
              backgroundColor: 'rgba(69, 240, 192, 0.05)',
              borderRadius: '12px',
              border: '1px solid rgba(69, 240, 192, 0.2)'
            }}>
              <div style={{
                color: '#45f0c0',
                fontSize: '14px',
                fontWeight: 'bold',
                marginBottom: '16px',
                textAlign: 'center',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}>
                <span>5 Active</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0px' }}>
                  <CompletePaiiDLogo size={21} />
                  <span style={{ fontStyle: 'italic' }}>Abilities</span>
                </div>
              </div>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}>
                {capabilitiesLeft.map((capability, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: 'rgba(15, 23, 42, 0.6)',
                      borderRadius: '8px',
                      border: '1px solid rgba(69, 240, 192, 0.3)',
                      color: '#cbd5e1',
                      fontSize: '14px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}
                  >
                    <span style={{ color: '#45f0c0', fontSize: '18px' }}>•</span>
                    {capability}
                  </div>
                ))}
              </div>
            </div>

            <div style={{
              padding: '20px',
              backgroundColor: 'rgba(69, 240, 192, 0.05)',
              borderRadius: '12px',
              border: '1px solid rgba(69, 240, 192, 0.2)'
            }}>
              <div style={{
                color: '#45f0c0',
                fontSize: '14px',
                fontWeight: 'bold',
                marginBottom: '16px',
                textAlign: 'center',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}>
                <span>5 Active</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0px' }}>
                  <CompletePaiiDLogo size={21} />
                  <span style={{ fontStyle: 'italic' }}>Abilities</span>
                </div>
              </div>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}>
                {capabilitiesRight.map((capability, index) => (
                  <div
                    key={index}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: 'rgba(15, 23, 42, 0.6)',
                      borderRadius: '8px',
                      border: '1px solid rgba(69, 240, 192, 0.3)',
                      color: '#cbd5e1',
                      fontSize: '14px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}
                  >
                    <span style={{ color: '#45f0c0', fontSize: '18px' }}>•</span>
                    {index === 0 ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <CompletePaiiDLogo size={21} />
                        <span>{capability}</span>
                      </div>
                    ) : capability}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div>
            <div style={{
              marginBottom: '12px',
              textAlign: 'center',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              fontSize: '16px',
              fontWeight: 'bold'
            }}>
              <span style={{ color: '#45f0c0' }}>Ask</span>
              <CompletePaiiDLogo size={21} />
            </div>

            <div style={{ position: 'relative' }}>
              {!query && (
                <div style={{
                  position: 'absolute',
                  top: '16px',
                  left: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  pointerEvents: 'none',
                  color: '#64748b',
                  fontSize: '16px'
                }}>
                  <span>Investment questions? Ask here to get</span>
                  <CompletePaiiDLogo size={21} />
                  <span>! ...</span>
                </div>
              )}

              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
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
            </div>

            <div style={{
              marginTop: '8px',
              fontSize: '12px',
              color: '#94a3b8',
              textAlign: 'center'
            }}>
              Press Enter to submit
            </div>
          </div>
        </div>
      )}

      <div style={{
        textAlign: 'center',
        color: 'rgba(255, 255, 255, 0.8)',
        maxWidth: '600px',
        padding: '2rem'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          marginBottom: '1rem'
        }}>
          <CompletePaiiDLogo size={80} />
        </div>
        <h1 style={{ color: '#45f0c0', marginBottom: '1rem', fontSize: '2rem' }}>
          🔒 Chat Box with Full Logo - LOCKED FINAL
        </h1>
        <p style={{ marginBottom: '2rem' }}>
          Complete integration ready for implementation
        </p>
        <button
          onClick={() => setIsOpen(true)}
          style={{
            padding: '14px 28px',
            backgroundColor: '#45f0c0',
            color: '#0a0e12',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          Open Chat Box
        </button>
      </div>
    </div>
  );
};

export default PaiiDChatBoxWithLogo;
