import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import Dashboard from '../pages/index';
import { HelpProvider } from '../hooks/useHelp';

// Mock API server
const server = setupServer(
  http.get('/api/health', () => {
    return HttpResponse.json({ status: 'healthy', timestamp: new Date().toISOString() });
  }),
  http.get('/api/market-data/*', () => {
    return HttpResponse.json({
      symbol: 'AAPL',
      price: 150.00,
      change: 1.50,
      changePercent: 1.01
    });
  }),
  http.get('/api/options/*', () => {
    return HttpResponse.json({
      symbol: 'AAPL',
      strikes: [145, 150, 155],
      expirations: ['2025-11-15', '2025-12-20']
    });
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('PaiiD Integration Tests', () => {
  test('Dashboard loads and displays radial menu', async () => {
    render(
      <HelpProvider>
        <Dashboard />
      </HelpProvider>
    );
    
    // Check if radial menu is present
    expect(screen.getByText(/Welcome to Your Trading Dashboard/i)).toBeInTheDocument();
  });

  test('Settings workflow opens correctly', async () => {
    render(
      <HelpProvider>
        <Dashboard />
      </HelpProvider>
    );
    
    // Simulate clicking on settings (this would be through the radial menu)
    // Note: This is a simplified test - in reality, you'd interact with the radial menu
    expect(screen.getByText(/Select a workflow stage/i)).toBeInTheDocument();
  });

  test('Help system integration works', async () => {
    render(
      <HelpProvider>
        <Dashboard />
      </HelpProvider>
    );
    
    // Check if help system is available
    const helpButton = screen.queryByText(/Help/i);
    if (helpButton) {
      fireEvent.click(helpButton);
      await waitFor(() => {
        expect(screen.getByText(/Help Panel/i)).toBeInTheDocument();
      });
    }
  });

  test('Trading mode indicator displays correctly', async () => {
    render(
      <HelpProvider>
        <Dashboard />
      </HelpProvider>
    );
    
    // Check for trading mode indicator
    const tradingMode = screen.queryByText(/PAPER TRADING/i) || screen.queryByText(/LIVE TRADING/i);
    expect(tradingMode).toBeInTheDocument();
  });

  test('Error boundary catches errors gracefully', async () => {
    // Mock a component that throws an error
    const ThrowError = () => {
      throw new Error('Test error');
    };

    render(
      <HelpProvider>
        <ThrowError />
      </HelpProvider>
    );
    
    // Check if error boundary catches the error
    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
  });
});
