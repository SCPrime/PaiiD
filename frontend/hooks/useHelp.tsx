/**
 * Help Context Hook
 * Provides help system state and actions throughout the app
 */

import { createContext, useContext, useState, ReactNode } from "react";

interface HelpContextType {
  isHelpPanelOpen: boolean;
  openHelpPanel: () => void;
  closeHelpPanel: () => void;
  toggleHelpPanel: () => void;
  showTooltip: (content: string, title?: string) => void;
  hideTooltip: () => void;
  tooltipContent: string;
  tooltipTitle: string;
  isTooltipVisible: boolean;
}

const HelpContext = createContext<HelpContextType | undefined>(undefined);

interface HelpProviderProps {
  children: ReactNode;
}

export function HelpProvider({ children }: HelpProviderProps) {
  const [isHelpPanelOpen, setIsHelpPanelOpen] = useState(false);
  const [tooltipContent, setTooltipContent] = useState("");
  const [tooltipTitle, setTooltipTitle] = useState("");
  const [isTooltipVisible, setIsTooltipVisible] = useState(false);

  const openHelpPanel = () => setIsHelpPanelOpen(true);
  const closeHelpPanel = () => setIsHelpPanelOpen(false);
  const toggleHelpPanel = () => setIsHelpPanelOpen(!isHelpPanelOpen);

  const showTooltip = (content: string, title?: string) => {
    setTooltipContent(content);
    setTooltipTitle(title || "");
    setIsTooltipVisible(true);
  };

  const hideTooltip = () => {
    setIsTooltipVisible(false);
    setTooltipContent("");
    setTooltipTitle("");
  };

  return (
    <HelpContext.Provider
      value={{
        isHelpPanelOpen,
        openHelpPanel,
        closeHelpPanel,
        toggleHelpPanel,
        showTooltip,
        hideTooltip,
        tooltipContent,
        tooltipTitle,
        isTooltipVisible,
      }}
    >
      {children}
    </HelpContext.Provider>
  );
}

export function useHelp() {
  const context = useContext(HelpContext);
  if (context === undefined) {
    throw new Error("useHelp must be used within a HelpProvider");
  }
  return context;
}
