export interface Workflow {
  id: string;
  name: string;
  color: string;
  icon: string;
  description: string;
}

export const workflows: Workflow[] = [
  {
    id: "morning-routine",
    name: "MORNING\nROUTINE",
    color: "#00ACC1",
    icon: "🌅",
    description: "Start your day with market analysis, portfolio review, and trading alerts.",
  },
  {
    id: "news-review",
    name: "NEWS\nREVIEW",
    color: "#7E57C2",
    icon: "📰",
    description: "Real-time market news aggregation with AI-powered sentiment analysis.",
  },
  {
    id: "proposals",
    name: "AI\nRECS",
    color: "#0097A7",
    icon: "🤖",
    description: "Review AI-generated trading recommendations and strategy proposals.",
  },
  {
    id: "active-positions",
    name: "ACTIVE\nPOSITIONS",
    color: "#00C851",
    icon: "📊",
    description: "Monitor and manage your current open positions and orders.",
  },
  {
    id: "my-account",
    name: "P&L\nDASHBOARD",
    color: "#FF8800",
    icon: "💰",
    description: "Simple view of your account value with clean line graph.",
  },
  {
    id: "strategy-builder",
    name: "STRATEGY\nBUILDER",
    color: "#5E35B1",
    icon: "🎯",
    description: "Design and test custom trading strategies with drag-and-drop rules.",
  },
  {
    id: "backtesting",
    name: "BACK\nTESTING",
    color: "#00BCD4",
    icon: "📈",
    description: "Test strategies against historical data to validate performance.",
  },
  {
    id: "execute",
    name: "EXECUTE",
    color: "#FF4444",
    icon: "⚡",
    description: "Execute trades with pre-filled orders and real-time confirmation.",
  },
  {
    id: "options-trading",
    name: "OPTIONS\nTRADING",
    color: "#8B5CF6",
    icon: "📈",
    description: "Options chain viewer with Greeks, multi-leg strategies, and execution.",
  },
  {
    id: "dev-progress",
    name: "REPO\nMONITOR",
    color: "#10B981",
    icon: "🔍",
    description: "See how the PaiiD app construction is progressing with simple visuals.",
  },
  {
    id: "ml-intelligence",
    name: "ML\nINTELLIGENCE",
    color: "#8B5CF6",
    icon: "🧠",
    description: "AI-powered market analysis, pattern recognition, and personal trading insights.",
  },
  {
    id: "settings",
    name: "SETTINGS",
    color: "#64748b",
    icon: "⚙️",
    description: "Trading journal, risk control, system configuration, and GitHub monitoring.",
  },
];
