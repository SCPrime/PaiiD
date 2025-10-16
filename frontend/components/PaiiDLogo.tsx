'use client';

import { useChat } from './ChatContext';
import { LOGO_STYLES, LOGO_ANIMATION_KEYFRAME } from '../styles/logoConstants';

interface PaiiDLogoProps {
  size?: 'small' | 'medium' | 'large' | 'xlarge' | 'custom';
  customFontSize?: number;
  showSubtitle?: boolean;
  style?: React.CSSProperties;
  onClick?: () => void;
}

const sizeMap = {
  small: 24,
  medium: 42,
  large: 64,
  xlarge: 96,
  custom: 32, // fallback if customFontSize not provided
};

export default function PaiiDLogo({
  size = 'medium',
  customFontSize,
  showSubtitle = false,
  style = {},
  onClick
}: PaiiDLogoProps) {
  const { openChat } = useChat();
  const fontSize = size === 'custom' && customFontSize ? customFontSize : sizeMap[size];

  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'center', ...style }}>
      <div
        style={{
          fontSize: `${fontSize}px`,
          fontWeight: 'bold',
          letterSpacing: size === 'xlarge' ? '4px' : size === 'large' ? '2px' : '1px',
          lineHeight: '1',
        }}
      >
        <span
          style={{
            background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            filter: 'drop-shadow(0 2px 4px rgba(26, 117, 96, 0.4))',
          }}
        >
          P
        </span>
        <span
          style={{
            background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          a
        </span>
        <span
          onClick={onClick || openChat}
          style={{
            background: LOGO_STYLES.GRADIENT.teal,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            textShadow: LOGO_STYLES.GLOW.initial,
            animation: `${LOGO_STYLES.ANIMATION.name} ${LOGO_STYLES.ANIMATION.duration} ${LOGO_STYLES.ANIMATION.timing} ${LOGO_STYLES.ANIMATION.iteration}`,
            fontStyle: 'italic',
            cursor: 'pointer',
            display: 'inline-block',
            position: 'relative',
            transition: 'all 0.3s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'scale(1.15) translateY(-2px)';
            e.currentTarget.style.textShadow = LOGO_STYLES.GLOW.hover;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1) translateY(0)';
            e.currentTarget.style.textShadow = LOGO_STYLES.GLOW.initial;
          }}
          title="Click to open AI assistant"
        >
          aii
        </span>
        <span
          style={{
            background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            filter: 'drop-shadow(0 2px 4px rgba(26, 117, 96, 0.4))',
          }}
        >
          D
        </span>
      </div>

      {showSubtitle && size === 'xlarge' && (
        <>
          <p
            style={{
              fontSize: '22px',
              color: '#cbd5e1',
              margin: '12px 0 0 0',
              letterSpacing: '1px',
              fontWeight: '500',
              textAlign: 'center',
            }}
          >
            Personal{' '}
            <span
              style={{
                color: '#45f0c0',
                fontStyle: 'italic',
                textShadow: '0 0 8px rgba(69, 240, 192, 0.5)',
              }}
            >
              artificial intelligence
            </span>
            /investment Dashboard
          </p>
          <p
            style={{
              fontSize: '16px',
              color: '#94a3b8',
              margin: '8px 0 0 0',
              letterSpacing: '0.5px',
              textAlign: 'center',
            }}
          >
            10 Stage Workflow
          </p>
        </>
      )}

      {showSubtitle && size === 'large' && (
        <p
          style={{
            fontSize: '14px',
            color: '#94a3b8',
            margin: '8px 0 0 0',
            letterSpacing: '0.5px',
            textAlign: 'center',
          }}
        >
          10 Stage Workflow
        </p>
      )}

      <style jsx>{`
        ${LOGO_ANIMATION_KEYFRAME}
      `}</style>
    </div>
  );
}
