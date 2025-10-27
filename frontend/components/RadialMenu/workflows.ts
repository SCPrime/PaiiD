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
    id: "execute",
    name: "EXECUTE\nTRADE",
    color: "#FF4444",
    icon: "⚡",
    description: "Execute trades with pre-filled orders and real-time confirmation.",
  },
];
