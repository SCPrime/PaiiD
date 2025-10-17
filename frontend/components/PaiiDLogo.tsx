'use client';

import { useChat } from './ChatContext';
import { useGlowStyle } from '../contexts/GlowStyleContext';
import styles from '../styles/logo.module.css';

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
  custom: 32,
};

export default function PaiiDLogo({
  size = 'medium',
  customFontSize,
  showSubtitle = false,
  style = {},
  onClick,
}: PaiiDLogoProps) {
  const { openChat } = useChat();
  const { glowStyle } = useGlowStyle();
  const fontSize = size === 'custom' && customFontSize ? customFontSize : sizeMap[size];

  // Determine wrapper class based on glow style
  const wrapperClass = glowStyle === 'halo' ? styles.haloGlowWrapper : styles.radialGlowWrapper;

  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', alignItems: 'center', ...style }}>
      {/* GPU-accelerated logo with CSS Modules */}
      <div
        className={wrapperClass}
        onClick={onClick || openChat}
        style={{
          fontSize: `${fontSize}px`,
          fontWeight: 'bold',
          letterSpacing: size === 'xlarge' ? '4px' : size === 'large' ? '2px' : '1px',
          lineHeight: '1',
        }}
        title="Click to open AI assistant"
      >
        <div className={styles.logoBase}>
          <span className={styles.logoText}>P</span>
          <span className={styles.logoText}>a</span>
          <span className={`${styles.logoText} ${styles.logoItalic}`}>aii</span>
          <span className={styles.logoText}>D</span>
        </div>
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
    </div>
  );
}
