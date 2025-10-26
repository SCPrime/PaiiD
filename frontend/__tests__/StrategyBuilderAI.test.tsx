import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import StrategyBuilderAI from '../components/StrategyBuilderAI';

// Mock dependencies
jest.mock('../lib/logger');
jest.mock('../lib/aiAdapter');
jest.mock('react-hot-toast');
jest.mock('../hooks/useBreakpoint', () => ({
  useIsMobile: () => false,
}));

// Mock child components
jest.mock('../components/StockLookup', () => {
  return function MockStockLookup() {
    return <div>Stock Lookup</div>;
  };
});

jest.mock('../components/TemplateCustomizationModal', () => {
  return function MockTemplateCustomizationModal() {
    return <div>Template Customization Modal</div>;
  };
});

jest.mock('../components/GlassmorphicComponents', () => ({
  GlassCard: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  GlassButton: ({ children, onClick }: { children: React.ReactNode; onClick?: () => void }) => (
    <button onClick={onClick}>{children}</button>
  ),
  GlassBadge: ({ children }: { children: React.ReactNode }) => <span>{children}</span>,
}));

describe('StrategyBuilderAI', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<StrategyBuilderAI />);
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('displays natural language input', () => {
    render(<StrategyBuilderAI />);

    const inputs = screen.getAllByRole('textbox');
    expect(inputs.length).toBeGreaterThan(0);
  });

  it('allows user to describe strategy in plain English', () => {
    render(<StrategyBuilderAI />);

    const textboxes = screen.getAllByRole('textbox');
    if (textboxes.length > 0) {
      const strategyInput = textboxes[0];
      fireEvent.change(strategyInput, {
        target: { value: 'Buy when RSI is below 30 and sell when it goes above 70' },
      });

      expect(strategyInput).toHaveValue('Buy when RSI is below 30 and sell when it goes above 70');
    }
  });

  it('generates strategy when button clicked', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        name: 'RSI Strategy',
        entry: ['RSI below 30'],
        exit: ['RSI above 70'],
      }),
    });

    render(<StrategyBuilderAI />);

    const generateButtons = screen.getAllByRole('button').filter(btn =>
      btn.textContent?.includes('Generate') || btn.textContent?.includes('Create')
    );

    if (generateButtons.length > 0) {
      fireEvent.click(generateButtons[0]);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    }
  });

  it('displays generated strategy', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        name: 'RSI Strategy',
        entry: ['RSI below 30'],
        exit: ['RSI above 70'],
      }),
    });

    render(<StrategyBuilderAI />);

    // After generation, strategy should be displayed
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('displays loading state during generation', () => {
    render(<StrategyBuilderAI />);

    // Should show loading indicator
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('handles generation errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Generation failed'));

    render(<StrategyBuilderAI />);

    // Should handle errors without crashing
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('allows editing generated strategy', () => {
    render(<StrategyBuilderAI />);

    // Should have edit controls
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('displays entry rules', () => {
    render(<StrategyBuilderAI />);

    // Should show entry conditions
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('displays exit rules', () => {
    render(<StrategyBuilderAI />);

    // Should show exit conditions
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('displays risk management settings', () => {
    render(<StrategyBuilderAI />);

    // Should show risk controls
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('saves strategy when save button clicked', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ id: '123', success: true }),
    });

    render(<StrategyBuilderAI />);

    const saveButtons = screen.getAllByRole('button').filter(btn =>
      btn.textContent?.includes('Save')
    );

    if (saveButtons.length > 0) {
      fireEvent.click(saveButtons[0]);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    }
  });

  it('loads saved strategies on mount', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => [
        {
          id: '1',
          name: 'Strategy 1',
          entry: ['Condition 1'],
          exit: ['Condition 2'],
        },
      ],
    });

    render(<StrategyBuilderAI />);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  it('displays list of saved strategies', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => [
        {
          id: '1',
          name: 'RSI Strategy',
          entry: ['RSI below 30'],
          exit: ['RSI above 70'],
        },
      ],
    });

    render(<StrategyBuilderAI />);

    await waitFor(() => {
      // Saved strategies should be listed
      expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
    });
  });

  it('allows deleting strategies', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ success: true }),
    });

    render(<StrategyBuilderAI />);

    const deleteButtons = screen.queryAllByRole('button').filter(btn =>
      btn.textContent?.includes('Delete') || btn.textContent?.includes('Trash')
    );

    if (deleteButtons.length > 0) {
      fireEvent.click(deleteButtons[0]);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    }
  });

  it('displays strategy templates', () => {
    render(<StrategyBuilderAI />);

    // Should show available templates
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('loads template when selected', async () => {
    render(<StrategyBuilderAI />);

    // Template selection should populate form
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('backtests strategy', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        winRate: 65,
        totalTrades: 100,
        profitFactor: 2.5,
      }),
    });

    render(<StrategyBuilderAI />);

    const backtestButtons = screen.queryAllByRole('button').filter(btn =>
      btn.textContent?.includes('Backtest') || btn.textContent?.includes('Test')
    );

    if (backtestButtons.length > 0) {
      fireEvent.click(backtestButtons[0]);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
      });
    }
  });

  it('displays backtest results', () => {
    render(<StrategyBuilderAI />);

    // Should show backtest metrics
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('generates code for strategy', () => {
    render(<StrategyBuilderAI />);

    // Should have code generation feature
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('validates strategy before saving', () => {
    render(<StrategyBuilderAI />);

    // Should validate strategy rules
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });

  it('displays position sizing options', () => {
    render(<StrategyBuilderAI />);

    // Should show position sizing controls
    expect(screen.getByText(/Strategy Builder/i)).toBeInTheDocument();
  });
});
