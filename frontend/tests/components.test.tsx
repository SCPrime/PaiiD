import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { HelpTooltip } from '../components/HelpTooltip';
import { HelpPanel } from '../components/HelpPanel';
import { TradingModeIndicator } from '../components/TradingModeIndicator';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { LoadingState } from '../components/ui/LoadingState';

describe('Component Tests', () => {
  test('HelpTooltip displays content correctly', () => {
    render(
      <HelpTooltip content="This is a test tooltip" title="Test Tooltip">
        <button>Hover me</button>
      </HelpTooltip>
    );
    
    const button = screen.getByText('Hover me');
    expect(button).toBeInTheDocument();
    
    fireEvent.mouseEnter(button);
    expect(screen.getByText('This is a test tooltip')).toBeInTheDocument();
  });

  test('HelpPanel opens and closes correctly', () => {
    const mockOnClose = jest.fn();
    
    render(
      <HelpPanel isOpen={true} onClose={mockOnClose} />
    );
    
    expect(screen.getByText(/Help Center/i)).toBeInTheDocument();
    
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    expect(mockOnClose).toHaveBeenCalled();
  });

  test('TradingModeIndicator shows correct mode', () => {
    const mockOnModeChange = jest.fn();
    
    render(
      <TradingModeIndicator 
        mode="paper" 
        onModeChange={mockOnModeChange} 
      />
    );
    
    expect(screen.getByText(/PAPER TRADING/i)).toBeInTheDocument();
  });

  test('ConfirmDialog shows trade details', () => {
    const mockOnConfirm = jest.fn();
    const mockOnCancel = jest.fn();
    
    const orderDetails = {
      symbol: 'AAPL',
      side: 'buy',
      quantity: 100,
      type: 'market'
    };
    
    render(
      <ConfirmDialog
        isOpen={true}
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
        orderDetails={orderDetails}
        riskWarning={true}
      />
    );
    
    expect(screen.getByText(/Trade Preview/i)).toBeInTheDocument();
    expect(screen.getByText(/AAPL/i)).toBeInTheDocument();
    expect(screen.getByText(/Risk Warning/i)).toBeInTheDocument();
  });

  test('LoadingState components render correctly', () => {
    render(<LoadingState />);
    expect(screen.getByText(/Loading.../i)).toBeInTheDocument();
    
    render(<LoadingState type="spinner" />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('Skeleton components show loading state', () => {
    render(<LoadingState type="skeleton" />);
    expect(screen.getByTestId('skeleton')).toBeInTheDocument();
  });
});
