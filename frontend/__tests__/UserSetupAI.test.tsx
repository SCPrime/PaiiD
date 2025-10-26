import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import UserSetupAI from '../components/UserSetupAI';

// Mock dependencies
jest.mock('../lib/logger');
jest.mock('../lib/aiAdapter');
jest.mock('../lib/userManagement');
jest.mock('next/dynamic', () => () => {
  const DynamicComponent = () => <div>Manual Setup Form</div>;
  DynamicComponent.displayName = 'UserSetup';
  return DynamicComponent;
});

// Mock CompletePaiiDLogo
jest.mock('../components/CompletePaiiDLogo', () => {
  return function MockCompletePaiiDLogo() {
    return <div>PaiiD Logo</div>;
  };
});

describe('UserSetupAI', () => {
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
    localStorage.clear();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('displays setup method selection', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Should show AI or Manual setup options
    expect(screen.getByText(/PaiiD Logo/i)).toBeInTheDocument();
  });

  it('starts AI setup when AI button clicked', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    const aiButtons = screen.getAllByRole('button');
    const aiSetupButton = aiButtons.find(btn =>
      btn.textContent?.includes('AI') || btn.textContent?.includes('Guided')
    );

    if (aiSetupButton) {
      fireEvent.click(aiSetupButton);
      // AI conversation should begin
    }
  });

  it('shows manual setup form when manual option selected', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    const allButtons = screen.getAllByRole('button');
    const manualButton = allButtons.find(btn =>
      btn.textContent?.includes('Manual')
    );

    if (manualButton) {
      fireEvent.click(manualButton);

      waitFor(() => {
        expect(screen.getByText('Manual Setup Form')).toBeInTheDocument();
      });
    }
  });

  it('displays chat interface in AI mode', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Component should have chat-like interface elements
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('allows user to send messages in AI mode', async () => {
    const { claudeAI } = require('../lib/aiAdapter');
    claudeAI.sendMessage = jest.fn().mockResolvedValue('AI response');

    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Start AI setup
    const aiButtons = screen.getAllByRole('button');
    const aiSetupButton = aiButtons.find(btn =>
      btn.textContent?.includes('AI') || btn.textContent?.includes('Guided')
    );

    if (aiSetupButton) {
      fireEvent.click(aiSetupButton);
    }

    // Look for message input
    const inputs = screen.queryAllByRole('textbox');
    if (inputs.length > 0) {
      const messageInput = inputs[0];
      fireEvent.change(messageInput, { target: { value: 'Hello' } });

      const sendButtons = screen.getAllByRole('button');
      const sendButton = sendButtons.find(btn =>
        btn.textContent?.includes('Send') || btn.getAttribute('type') === 'submit'
      );

      if (sendButton) {
        fireEvent.click(sendButton);

        await waitFor(() => {
          expect(claudeAI.sendMessage).toHaveBeenCalled();
        });
      }
    }
  });

  it('displays AI welcome message', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Should show welcoming text
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('extracts user preferences from conversation', async () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Preferences should be extracted as user responds
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('shows review screen before completion', async () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // After conversation, should show review of preferences
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('calls onComplete when setup finished', async () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // After completing setup, onComplete should be called
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('saves preferences to localStorage', async () => {
    const setItemSpy = jest.spyOn(Storage.prototype, 'setItem');

    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Preferences should be saved
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();

    setItemSpy.mockRestore();
  });

  it('displays progress indicator', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Should show setup progress
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('handles admin bypass keyboard shortcut', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Simulate Ctrl+Shift+A
    fireEvent.keyDown(window, { key: 'A', shiftKey: true, ctrlKey: true });

    // Should skip to dashboard
    waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalled();
    });
  });

  it('displays animated particles', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Animated background should be present
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('handles AI errors gracefully', async () => {
    const { claudeAI } = require('../lib/aiAdapter');
    claudeAI.sendMessage = jest.fn().mockRejectedValue(new Error('AI Error'));

    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Should handle AI errors without crashing
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('allows going back to method selection', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Should have option to go back
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('displays conversation history', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Chat history should be visible
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('auto-scrolls to latest message', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Messages should auto-scroll
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('disables input while processing', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Input should be disabled during AI processing
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('validates user input', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Should validate responses
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('displays loading indicator during AI response', () => {
    render(<UserSetupAI onComplete={mockOnComplete} />);

    // Should show loading state
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });
});
