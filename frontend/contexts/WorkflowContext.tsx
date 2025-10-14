import React, { createContext, useContext, useState, ReactNode } from 'react';

/**
 * WorkflowContext
 *
 * Manages workflow navigation and data passing between different workflows.
 * Enables components to navigate to other workflows with pre-filled data.
 *
 * Example: AI Analysis → Execute Trade with symbol, entry price, stop loss pre-filled
 */

export type WorkflowType =
  | 'morning-routine'
  | 'active-positions'
  | 'execute-trade'
  | 'research'
  | 'ai-recommendations'
  | 'analytics'
  | 'news-review'
  | 'strategy-builder'
  | 'backtesting'
  | 'settings';

export interface TradeData {
  symbol: string;
  side?: 'buy' | 'sell';
  quantity?: number;
  entryPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
  orderType?: 'market' | 'limit' | 'stop' | 'stop_limit';
  timeInForce?: 'day' | 'gtc' | 'ioc' | 'fok';
  notes?: string;
}

export interface WorkflowNavigationData {
  workflow: WorkflowType;
  data?: any; // Flexible data payload
  tradeData?: TradeData; // Specific for trade execution
  timestamp: string;
}

interface WorkflowContextType {
  currentWorkflow: WorkflowType | null;
  pendingNavigation: WorkflowNavigationData | null;
  setCurrentWorkflow: (workflow: WorkflowType) => void;
  navigateToWorkflow: (workflow: WorkflowType, data?: any) => void;
  navigateToTrade: (tradeData: TradeData) => void;
  clearPendingNavigation: () => void;
}

const WorkflowContext = createContext<WorkflowContextType | undefined>(undefined);

export const useWorkflow = () => {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflow must be used within a WorkflowProvider');
  }
  return context;
};

interface WorkflowProviderProps {
  children: ReactNode;
}

export const WorkflowProvider: React.FC<WorkflowProviderProps> = ({ children }) => {
  const [currentWorkflow, setCurrentWorkflow] = useState<WorkflowType | null>(null);
  const [pendingNavigation, setPendingNavigation] = useState<WorkflowNavigationData | null>(null);

  const navigateToWorkflow = (workflow: WorkflowType, data?: any) => {
    const navigationData: WorkflowNavigationData = {
      workflow,
      data,
      timestamp: new Date().toISOString()
    };

    setPendingNavigation(navigationData);
    setCurrentWorkflow(workflow);

    // Dispatch custom event for components that listen
    window.dispatchEvent(
      new CustomEvent('workflow-navigate', { detail: navigationData })
    );

    console.log('[WorkflowContext] Navigating to:', workflow, data);
  };

  const navigateToTrade = (tradeData: TradeData) => {
    const navigationData: WorkflowNavigationData = {
      workflow: 'execute-trade',
      tradeData,
      timestamp: new Date().toISOString()
    };

    setPendingNavigation(navigationData);
    setCurrentWorkflow('execute-trade');

    // Dispatch custom event
    window.dispatchEvent(
      new CustomEvent('workflow-navigate', { detail: navigationData })
    );

    console.log('[WorkflowContext] Navigating to Execute Trade:', tradeData);
  };

  const clearPendingNavigation = () => {
    setPendingNavigation(null);
  };

  const value: WorkflowContextType = {
    currentWorkflow,
    pendingNavigation,
    setCurrentWorkflow,
    navigateToWorkflow,
    navigateToTrade,
    clearPendingNavigation
  };

  return (
    <WorkflowContext.Provider value={value}>
      {children}
    </WorkflowContext.Provider>
  );
};

export default WorkflowContext;
