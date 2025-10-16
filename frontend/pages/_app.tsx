import type { AppProps } from 'next/app';
import { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { TelemetryProvider } from '../components/TelemetryProvider';
import { ChatProvider, useChat } from '../components/ChatContext';
import { WorkflowProvider } from '../contexts/WorkflowContext';
import { AuthProvider } from '../contexts/AuthContext';
import AIChatBot from '../components/AIChatBot';
import { ErrorBoundary } from '../components/ErrorBoundary';
import { initSentry, setUser } from '../lib/sentry';
import '../styles/globals.css';

interface AppPropsExtended {
  Component: AppProps['Component'];
  pageProps: AppProps['pageProps'];
  userId: string;
  userRole: 'owner' | 'beta' | 'alpha' | 'user';
  telemetryEnabled: boolean;
}

function AppContent({ Component, pageProps, userId, userRole, telemetryEnabled }: AppPropsExtended) {
  const { isChatOpen, closeChat } = useChat();

  return (
    <TelemetryProvider
      userId={userId}
      userRole={userRole}
      enabled={telemetryEnabled}
    >
      <Component {...pageProps} />
      <AIChatBot isOpen={isChatOpen} onClose={closeChat} />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'rgba(30, 41, 59, 0.95)',
            color: '#fff',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '12px',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
            style: {
              border: '1px solid rgba(16, 185, 129, 0.5)',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
            style: {
              border: '1px solid rgba(239, 68, 68, 0.5)',
            },
          },
          loading: {
            iconTheme: {
              primary: '#7E57C2',
              secondary: '#fff',
            },
          },
        }}
      />
    </TelemetryProvider>
  );
}

export default function App({ Component, pageProps }: AppProps) {
  // Initialize Sentry on app startup (client-side only)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      initSentry();
    }
  }, []);

  // Get user info from localStorage (or generate unique ID)
  const [user] = useState(() => {
    if (typeof window === 'undefined') {
      return { id: 'anonymous', role: 'user' as const };
    }

    const storedUserId = localStorage.getItem('user-id');
    const userId = storedUserId || `user-${Date.now()}`;

    if (!storedUserId) {
      localStorage.setItem('user-id', userId);
    }

    const storedRole = localStorage.getItem('user-role') as 'owner' | 'beta' | 'alpha' | 'user' | null;
    const userRole = storedRole || 'user';

    return { id: userId, role: userRole };
  });

  // Set Sentry user context when user changes
  useEffect(() => {
    if (typeof window !== 'undefined' && user) {
      setUser(user.id, user.role);
    }
  }, [user]);

  // Check if telemetry is enabled from environment variable
  const telemetryEnabled = process.env.NEXT_PUBLIC_TELEMETRY_ENABLED !== 'false';

  return (
    <ErrorBoundary>
      <AuthProvider>
        <ChatProvider>
          <WorkflowProvider>
            <AppContent
              Component={Component}
              pageProps={pageProps}
              userId={user.id}
              userRole={user.role}
              telemetryEnabled={telemetryEnabled}
            />
          </WorkflowProvider>
        </ChatProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
