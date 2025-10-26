import React from 'react';

// Skeleton card with shimmer animation
export const SkeletonCard: React.FC<{ height?: string; width?: string }> = ({
  height = '80px',
  width = '100%'
}) => (
  <div
    className="skeleton-card"
    style={{
      background: 'linear-gradient(90deg, #1e293b 25%, #334155 50%, #1e293b 75%)',
      backgroundSize: '200% 100%',
      animation: 'shimmer 1.5s infinite',
      height,
      width,
      borderRadius: '8px',
      marginBottom: '12px'
    }}
  />
);

// Inline spinner
export const Spinner: React.FC<{ size?: 'small' | 'medium' | 'large'; color?: string }> = ({
  size = 'medium',
  color = '#3b82f6'
}) => {
  const sizes = { small: '16px', medium: '24px', large: '40px' };
  return (
    <div
      className="spinner"
      style={{
        width: sizes[size],
        height: sizes[size],
        border: `3px solid ${color}33`,
        borderTop: `3px solid ${color}`,
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        display: 'inline-block'
      }}
    />
  );
};

// Error state with retry
export const ErrorState: React.FC<{
  message: string;
  onRetry?: () => void;
  isRetrying?: boolean;
}> = ({ message, onRetry, isRetrying }) => (
  <div style={{
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.3)',
    borderRadius: '8px',
    padding: '24px',
    textAlign: 'center'
  }}>
    <div style={{
      color: '#ef4444',
      fontSize: '18px',
      marginBottom: '12px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px'
    }}>
      <span>⚠️</span>
      <span>Error</span>
    </div>
    <p style={{ color: '#cbd5e1', marginBottom: onRetry ? '16px' : 0 }}>
      {message}
    </p>
    {onRetry && (
      <button
        onClick={onRetry}
        disabled={isRetrying}
        style={{
          background: '#3b82f6',
          color: 'white',
          padding: '8px 16px',
          borderRadius: '6px',
          border: 'none',
          cursor: isRetrying ? 'not-allowed' : 'pointer',
          opacity: isRetrying ? 0.6 : 1,
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '14px',
          fontWeight: '600'
        }}
      >
        {isRetrying && <Spinner size="small" color="#fff" />}
        {isRetrying ? 'Retrying...' : 'Retry'}
      </button>
    )}
  </div>
);

// Empty state with CTA
export const EmptyState: React.FC<{
  icon: string;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}> = ({ icon, title, description, actionLabel, onAction }) => (
  <div style={{
    textAlign: 'center',
    padding: '48px 24px',
    color: '#94a3b8'
  }}>
    <div style={{ fontSize: '48px', marginBottom: '16px' }}>{icon}</div>
    <h3 style={{ color: '#cbd5e1', marginBottom: '8px', fontSize: '20px', fontWeight: '600' }}>
      {title}
    </h3>
    <p style={{ marginBottom: actionLabel ? '24px' : 0, fontSize: '14px', lineHeight: '1.6' }}>
      {description}
    </p>
    {actionLabel && onAction && (
      <button
        onClick={onAction}
        style={{
          background: '#10b981',
          color: 'white',
          padding: '12px 24px',
          borderRadius: '8px',
          border: 'none',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: '600',
          transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = '#059669';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = '#10b981';
        }}
      >
        {actionLabel}
      </button>
    )}
  </div>
);

// Loading overlay (for full-screen loading)
export const LoadingOverlay: React.FC<{ message?: string }> = ({ message = 'Loading...' }) => (
  <div style={{
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(15, 23, 42, 0.9)',
    backdropFilter: 'blur(4px)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999
  }}>
    <Spinner size="large" />
    <p style={{
      color: '#cbd5e1',
      marginTop: '16px',
      fontSize: '16px',
      fontWeight: '500'
    }}>
      {message}
    </p>
  </div>
);

// Skeleton list (multiple skeleton cards)
export const SkeletonList: React.FC<{ count?: number; height?: string }> = ({
  count = 3,
  height = '80px'
}) => (
  <>
    {[...Array(count)].map((_, i) => (
      <SkeletonCard key={i} height={height} />
    ))}
  </>
);

// Inline loading indicator for buttons
export const ButtonLoadingIndicator: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
    <Spinner size="small" color="#fff" />
    <span>{children}</span>
  </div>
);

// Progressive loading (partial content with loading indicator)
export const ProgressiveLoader: React.FC<{
  children: React.ReactNode;
  isLoadingMore: boolean;
  loadingMessage?: string;
}> = ({ children, isLoadingMore, loadingMessage = 'Loading more...' }) => (
  <>
    {children}
    {isLoadingMore && (
      <div style={{
        textAlign: 'center',
        padding: '20px',
        color: '#94a3b8'
      }}>
        <Spinner size="medium" />
        <p style={{ marginTop: '12px', fontSize: '14px' }}>{loadingMessage}</p>
      </div>
    )}
  </>
);

// Inject global CSS animations
if (typeof document !== 'undefined') {
  const styleId = 'loading-states-animations';
  if (!document.getElementById(styleId)) {
    const styleSheet = document.createElement('style');
    styleSheet.id = styleId;
    styleSheet.textContent = `
      @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
      }

      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }

      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }

      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
    `;
    document.head.appendChild(styleSheet);
  }
}
