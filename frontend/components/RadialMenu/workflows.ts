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
    id: "active-positions",
    name: "ACTIVE\nPOSITIONS",
    color: "#00C851",
    icon: "📊",
    description: "Monitor and manage your current open positions and orders.",
  },
  {
    id: "execute",
    name: "EXECUTE\nTRADE",
    color: "#FF4444",
    icon: "⚡",
    description: "Execute trades with pre-filled orders and real-time confirmation.",
  },
  {
    id: "research",
    name: "RESEARCH",
    color: "#3B82F6",
    icon: "🔍",
    description: "Market scanner for discovering trading opportunities and analyzing trends.",
  },
  {
    id: "proposals",
    name: "AI\nRECOMMENDATIONS",
    color: "#0097A7",
    icon: "🤖",
    description: "Review AI-generated trading recommendations and strategy proposals.",
  },
  {
    id: "my-account",
    name: "P&L\nDASHBOARD",
    color: "#FF8800",
    icon: "💰",
    description: "Simple view of your account value with clean line graph.",
  },
  {
    id: "news-review",
    name: "NEWS\nREVIEW",
    color: "#7E57C2",
    icon: "📰",
    description: "Real-time market news aggregation with AI-powered sentiment analysis.",
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
    name: "BACKTESTING",
    color: "#00BCD4",
    icon: "📈",
    description: "Test strategies against historical data to validate performance.",
  },
  {
    id: "settings",
    name: "SETTINGS",
    color: "#64748b",
    icon: "⚙️",
    description: "Trading journal, risk control, system configuration, ML Intelligence, Options Trading, and Repo Monitor.",
  },
];
