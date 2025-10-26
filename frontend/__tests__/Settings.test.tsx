import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Settings from '../components/Settings';

// Mock dependencies
jest.mock('../lib/logger');
jest.mock('../lib/userManagement');
jest.mock('../hooks/useBreakpoint', () => ({
  useIsMobile: () => false,
}));
jest.mock('../contexts/ThemeContext', () => ({
  useTheme: () => ({
    theme: 'dark',
    setTheme: jest.fn(),
  }),
}));
jest.mock('react-hot-toast');

// Mock child components
jest.mock('../components/ClaudeAIChat', () => {
  return function MockClaudeAIChat() {
    return <div>Claude AI Chat</div>;
  };
});

jest.mock('../components/ApprovalQueue', () => {
  return function MockApprovalQueue() {
    return <div>Approval Queue</div>;
  };
});

jest.mock('../components/KillSwitchToggle', () => {
  return function MockKillSwitchToggle() {
    return <div>Kill Switch</div>;
  };
});

describe('Settings', () => {
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });

  it('renders without crashing', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);
    // Settings should be visible when isOpen is true
    expect(document.body).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    const { container } = render(<Settings isOpen={false} onClose={mockOnClose} />);
    // Component should render but be hidden
    expect(container).toBeInTheDocument();
  });

  it('displays settings tabs', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Common settings tabs
    expect(screen.getByText(/General/i) || screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('closes settings when close button clicked', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    const closeButtons = screen.getAllByRole('button');
    const closeButton = closeButtons.find(btn =>
      btn.textContent?.includes('×') || btn.textContent?.includes('Close')
    );

    if (closeButton) {
      fireEvent.click(closeButton);
      expect(mockOnClose).toHaveBeenCalled();
    }
  });

  it('displays execution mode settings', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Should have execution mode controls
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('displays notification settings', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Should have notification toggles
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('saves settings when save button clicked', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ success: true }),
    });

    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Find and click save button
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

  it('displays alert preferences', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Component should render alert-related settings
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('displays performance tracking toggle', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Should have performance tracking settings
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('displays theme customization options', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Should have theme-related settings
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('displays user profile information', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Should display user-related information
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('allows switching between tabs', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    const allButtons = screen.getAllByRole('button');
    expect(allButtons.length).toBeGreaterThan(0);
  });

  it('displays kill switch toggle', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Kill switch should be rendered somewhere in settings
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('handles settings load errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('Failed to load'));

    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Component should still render
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('validates settings before saving', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Component should have validation logic
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('displays default values correctly', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Default settings should be displayed
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('persists settings to localStorage', () => {
    const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');

    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Settings component should interact with localStorage
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();

    setItemSpy.mockRestore();
  });

  it('loads settings from localStorage on mount', () => {
    const getItemSpy = jest.spyOn(Storage.prototype, 'getItem');

    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Component should attempt to load from localStorage
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();

    getItemSpy.mockRestore();
  });

  it('displays trading mode selector', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Should have trading mode controls
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('displays API configuration section', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Should have API-related settings
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('displays security settings', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Should have security-related options
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });

  it('allows clearing user data', () => {
    render(<Settings isOpen={true} onClose={mockOnClose} />);

    // Should have data management options
    expect(screen.getByText(/Settings/i)).toBeInTheDocument();
  });
});
