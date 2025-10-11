import type { AppProps } from 'next/app';
import { useState } from 'react';
import { TelemetryProvider } from '../components/TelemetryProvider';
import { ChatProvider, useChat } from '../components/ChatContext';
import AIChatBot from '../components/AIChatBot';
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
    </TelemetryProvider>
  );
}

export default function App({ Component, pageProps }: AppProps) {
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

  // Check if telemetry is enabled from environment variable
  const telemetryEnabled = process.env.NEXT_PUBLIC_TELEMETRY_ENABLED !== 'false';

  return (
    <ChatProvider>
      <AppContent
        Component={Component}
        pageProps={pageProps}
        userId={user.id}
        userRole={user.role}
        telemetryEnabled={telemetryEnabled}
      />
    </ChatProvider>
  );
}
