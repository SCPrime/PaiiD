/**
 * Protected Route Component
 *
 * HOC/wrapper to protect routes that require authentication.
 * Shows loading state while checking auth, redirects if unauthenticated.
 */

import { ReactNode, useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import AuthModal from './AuthModal';

interface ProtectedRouteProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export default function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      setShowAuthModal(true);
    }
  }, [isLoading, isAuthenticated]);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
        color: '#94a3b8',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '3px solid rgba(16, 185, 129, 0.3)',
            borderTopColor: '#10b981',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
            margin: '0 auto 16px',
          }} />
          <p style={{ margin: 0 }}>Loading...</p>
        </div>
        <style jsx>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        {fallback || (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '400px',
            color: '#cbd5e1',
            textAlign: 'center',
            padding: '40px 20px',
          }}>
            <div style={{
              fontSize: '48px',
              marginBottom: '16px',
            }}>
              🔒
            </div>
            <h2 style={{ margin: '0 0 8px', fontSize: '24px', fontWeight: 600 }}>
              Authentication Required
            </h2>
            <p style={{ margin: '0 0 24px', color: '#94a3b8', maxWidth: '400px' }}>
              Please log in to access this feature
            </p>
            <button
              onClick={() => setShowAuthModal(true)}
              style={{
                padding: '12px 32px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                border: 'none',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '16px',
                fontWeight: 600,
                cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
              }}
            >
              Login / Register
            </button>
          </div>
        )}
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />
      </>
    );
  }

  return <>{children}</>;
}
