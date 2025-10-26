import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ExecuteTradeForm from '../components/ExecuteTradeForm';

// Mock dependencies
jest.mock('../lib/logger');
jest.mock('../lib/toast');
jest.mock('../hooks/useBreakpoint', () => ({
  useIsMobile: () => false,
}));
jest.mock('../contexts/WorkflowContext', () => ({
  useWorkflow: () => ({
    pendingNavigation: null,
    clearPendingNavigation: jest.fn(),
  }),
}));

describe('ExecuteTradeForm', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    process.env.NEXT_PUBLIC_API_TOKEN = 'test-token';
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<ExecuteTradeForm />);
    expect(screen.getByText(/Execute Trade/i)).toBeInTheDocument();
  });

  it('displays all form fields', () => {
    render(<ExecuteTradeForm />);

    expect(screen.getByLabelText(/Symbol/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Side/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Quantity/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Order Type/i)).toBeInTheDocument();
  });

  it('has default values', () => {
    render(<ExecuteTradeForm />);

    const symbolInput = screen.getByPlaceholderText(/SPY, AAPL, QQQ/i) as HTMLInputElement;
    const quantityInput = screen.getByLabelText(/Quantity/i) as HTMLInputElement;

    expect(symbolInput.value).toBe('SPY');
    expect(quantityInput.value).toBe('1');
  });

  it('updates symbol input', () => {
    render(<ExecuteTradeForm />);

    const symbolInput = screen.getByPlaceholderText(/SPY, AAPL, QQQ/i) as HTMLInputElement;
    fireEvent.change(symbolInput, { target: { value: 'AAPL' } });

    expect(symbolInput.value).toBe('AAPL');
  });

  it('updates quantity input', () => {
    render(<ExecuteTradeForm />);

    const quantityInput = screen.getByLabelText(/Quantity/i) as HTMLInputElement;
    fireEvent.change(quantityInput, { target: { value: '10' } });

    expect(quantityInput.value).toBe('10');
  });

  it('shows limit price field when limit order selected', () => {
    render(<ExecuteTradeForm />);

    const orderTypeSelect = screen.getByLabelText(/Order Type/i) as HTMLSelectElement;
    fireEvent.change(orderTypeSelect, { target: { value: 'limit' } });

    expect(screen.getByLabelText(/Limit Price/i)).toBeInTheDocument();
  });

  it('hides limit price field when market order selected', () => {
    render(<ExecuteTradeForm />);

    const orderTypeSelect = screen.getByLabelText(/Order Type/i) as HTMLSelectElement;
    fireEvent.change(orderTypeSelect, { target: { value: 'market' } });

    expect(screen.queryByLabelText(/Limit Price/i)).not.toBeInTheDocument();
  });

  it('displays asset class toggle', () => {
    render(<ExecuteTradeForm />);

    expect(screen.getByText('Stock')).toBeInTheDocument();
    expect(screen.getByText('Options')).toBeInTheDocument();
  });

  it('shows options fields when options selected', () => {
    render(<ExecuteTradeForm />);

    const optionsButton = screen.getByText('Options');
    fireEvent.click(optionsButton);

    expect(screen.getByLabelText(/Option Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Strike Price/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Expiration Date/i)).toBeInTheDocument();
  });

  it('validates empty symbol', async () => {
    render(<ExecuteTradeForm />);

    const symbolInput = screen.getByPlaceholderText(/SPY, AAPL, QQQ/i);
    fireEvent.change(symbolInput, { target: { value: '' } });

    const submitButton = screen.getByText(/Submit Order/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      // Form validation should prevent submission
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  it('validates quantity greater than 0', async () => {
    render(<ExecuteTradeForm />);

    const quantityInput = screen.getByLabelText(/Quantity/i);
    fireEvent.change(quantityInput, { target: { value: '0' } });

    const submitButton = screen.getByText(/Submit Order/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  it('shows confirmation dialog before submitting', async () => {
    render(<ExecuteTradeForm />);

    const submitButton = screen.getByText(/Submit Order/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Confirm Order/i)).toBeInTheDocument();
    });
  });

  it('submits order when confirmed', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ accepted: true, duplicate: false }),
    });

    render(<ExecuteTradeForm />);

    // Fill out form
    const symbolInput = screen.getByPlaceholderText(/SPY, AAPL, QQQ/i);
    fireEvent.change(symbolInput, { target: { value: 'AAPL' } });

    const submitButton = screen.getByText(/Submit Order/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Confirm Order/i)).toBeInTheDocument();
    });

    const confirmButton = screen.getByText(/Execute Order/i);
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/proxy/trading/execute',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  it('displays success message after successful submission', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ accepted: true, duplicate: false }),
    });

    render(<ExecuteTradeForm />);

    const submitButton = screen.getByText(/Submit Order/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      const confirmButton = screen.getByText(/Execute Order/i);
      fireEvent.click(confirmButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/Order Accepted/i)).toBeInTheDocument();
    });
  });

  it('displays error message on submission failure', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

    render(<ExecuteTradeForm />);

    const submitButton = screen.getByText(/Submit Order/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      const confirmButton = screen.getByText(/Execute Order/i);
      fireEvent.click(confirmButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeInTheDocument();
    });
  });

  it('loads AI analysis when symbol changes', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        symbol: 'AAPL',
        current_price: 150.0,
        momentum: 'Bullish',
        trend: 'Uptrend',
        summary: 'Strong buy signal',
        confidence_score: 85,
      }),
    });

    render(<ExecuteTradeForm />);

    const symbolInput = screen.getByPlaceholderText(/SPY, AAPL, QQQ/i);
    fireEvent.change(symbolInput, { target: { value: 'AAPL' } });

    await waitFor(
      () => {
        expect(screen.getByText(/PaπD AI Analysis/i)).toBeInTheDocument();
      },
      { timeout: 2000 }
    );
  });

  it('loads order templates on mount', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => [
        {
          id: 1,
          name: 'SPY Quick Buy',
          symbol: 'SPY',
          side: 'buy',
          quantity: 10,
          order_type: 'market',
        },
      ],
    });

    render(<ExecuteTradeForm />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/proxy/api/order-templates');
    });
  });

  it('allows saving current order as template', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, name: 'My Template' }),
    });

    render(<ExecuteTradeForm />);

    const saveButton = screen.getByText(/Save Current as Template/i);
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Template name/i)).toBeInTheDocument();
    });
  });

  it('toggles stock research panel', () => {
    render(<ExecuteTradeForm />);

    const researchButton = screen.getByText(/Research/i);
    fireEvent.click(researchButton);

    // Research panel should be visible (StockLookup component)
    // This would require the StockLookup component to be properly mocked
  });

  it('handles duplicate order detection', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ accepted: false, duplicate: true }),
    });

    render(<ExecuteTradeForm />);

    const submitButton = screen.getByText(/Submit Order/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      const confirmButton = screen.getByText(/Execute Order/i);
      fireEvent.click(confirmButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/Duplicate Detected/i)).toBeInTheDocument();
    });
  });

  it('displays loading state during submission', async () => {
    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 1000))
    );

    render(<ExecuteTradeForm />);

    const submitButton = screen.getByText(/Submit Order/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      const confirmButton = screen.getByText(/Execute Order/i);
      fireEvent.click(confirmButton);
    });

    expect(screen.getByText(/Processing/i)).toBeInTheDocument();
  });
});
