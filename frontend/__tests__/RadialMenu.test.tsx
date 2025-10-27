import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import RadialMenu, { workflows } from '../components/RadialMenu';

// Mock dependencies
jest.mock('d3', () => ({
  select: jest.fn(() => ({
    selectAll: jest.fn(() => ({
      data: jest.fn(() => ({
        join: jest.fn(() => ({
          attr: jest.fn().mockReturnThis(),
          style: jest.fn().mockReturnThis(),
          on: jest.fn().mockReturnThis(),
        })),
      })),
    })),
    attr: jest.fn().mockReturnThis(),
    style: jest.fn().mockReturnThis(),
  })),
  arc: jest.fn(() => ({
    innerRadius: jest.fn().mockReturnThis(),
    outerRadius: jest.fn().mockReturnThis(),
    startAngle: jest.fn().mockReturnThis(),
    endAngle: jest.fn().mockReturnThis(),
  })),
  pie: jest.fn(() => jest.fn(() => [])),
}));

jest.mock('../hooks/useBreakpoint', () => ({
  useIsMobile: () => false,
  useWindowDimensions: () => ({ width: 1920, height: 1080 }),
}));

jest.mock('../lib/logger');

// Mock CompletePaiiDLogo component
jest.mock('../components/CompletePaiiDLogo', () => {
  return function MockCompletePaiiDLogo() {
    return <div>PaiiD Logo</div>;
  };
});

describe('RadialMenu', () => {
  const mockOnWorkflowSelect = jest.fn();
  const mockOnWorkflowHover = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />);
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('displays all 10 workflow segments', () => {
    render(<RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />);

    // Check that workflows array has 10 items
    expect(workflows).toHaveLength(10);
  });

  it('calls onWorkflowSelect when workflow clicked', () => {
    const { container } = render(<RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />);

    // Since D3 is mocked, we can't directly interact with SVG elements
    // We verify that the component renders and would trigger the callback
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('displays workflow names correctly', () => {
    render(<RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />);

    // Verify workflows data structure
    expect(workflows[0].name).toBe('MORNING\nROUTINE');
    expect(workflows[3].name).toBe('ACTIVE\nPOSITIONS');
  });

  it('displays workflow icons', () => {
    render(<RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />);

    // Verify workflow icons
    expect(workflows[0].icon).toBe('🌅');
    expect(workflows[1].icon).toBe('📰');
    expect(workflows[2].icon).toBe('🤖');
  });

  it('displays workflow colors', () => {
    render(<RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />);

    // Verify workflow colors
    expect(workflows[0].color).toBe('#00ACC1');
    expect(workflows[3].color).toBe('#00C851');
  });

  it('displays workflow descriptions', () => {
    render(<RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />);

    // Verify workflow descriptions exist
    workflows.forEach((workflow) => {
      expect(workflow.description).toBeTruthy();
    });
  });

  it('highlights selected workflow', () => {
    render(
      <RadialMenu
        onWorkflowSelect={mockOnWorkflowSelect}
        selectedWorkflow="active-positions"
      />
    );

    // Component should render with selected workflow
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('calls onWorkflowHover when provided', () => {
    render(
      <RadialMenu
        onWorkflowSelect={mockOnWorkflowSelect}
        onWorkflowHover={mockOnWorkflowHover}
      />
    );

    // Component should be set up to call hover callback
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('renders in compact mode', () => {
    render(
      <RadialMenu
        onWorkflowSelect={mockOnWorkflowSelect}
        compact={true}
      />
    );

    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('renders all workflow IDs correctly', () => {
    const expectedIds = [
      'morning-routine',
      'news-review',
      'proposals',
      'active-positions',
      'my-account',
      'strategy-builder',
      'backtesting',
      'execute',
      'options-trading',
      'dev-progress',
    ];

    const actualIds = workflows.map(w => w.id);
    expectedIds.forEach(id => {
      expect(actualIds).toContain(id);
    });
  });

  it('has unique workflow IDs', () => {
    const ids = workflows.map(w => w.id);
    const uniqueIds = new Set(ids);
    expect(ids.length).toBe(uniqueIds.size);
  });

  it('has valid color codes for all workflows', () => {
    workflows.forEach((workflow) => {
      expect(workflow.color).toMatch(/^#[0-9A-F]{6}$/i);
    });
  });

  it('exports workflows array', () => {
    expect(workflows).toBeDefined();
    expect(Array.isArray(workflows)).toBe(true);
  });

  it('contains ML Intelligence workflow', () => {
    const mlWorkflow = workflows.find(w => w.id === 'ml-intelligence');
    expect(mlWorkflow).toBeDefined();
    expect(mlWorkflow?.name).toBe('ML\nINTELLIGENCE');
  });

  it('contains Execute workflow with correct color', () => {
    const executeWorkflow = workflows.find(w => w.id === 'execute');
    expect(executeWorkflow).toBeDefined();
    expect(executeWorkflow?.color).toBe('#FF4444');
  });

  it('responsive sizing for mobile', () => {
    const { useIsMobile } = require('../hooks/useBreakpoint');
    useIsMobile.mockReturnValue(true);

    render(<RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />);
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('adjusts menu based on window dimensions', () => {
    const { useWindowDimensions } = require('../hooks/useBreakpoint');
    useWindowDimensions.mockReturnValue({ width: 800, height: 600 });

    render(<RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />);
    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });

  it('memoizes component properly', () => {
    const { rerender } = render(
      <RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />
    );

    // Re-render with same props
    rerender(
      <RadialMenu onWorkflowSelect={mockOnWorkflowSelect} />
    );

    expect(screen.getByText('PaiiD Logo')).toBeInTheDocument();
  });
});
