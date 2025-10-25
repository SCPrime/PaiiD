/**
 * Help Panel Component
 * Slide-out help drawer with searchable guides
 */

import { AlertCircle, BookOpen, Lightbulb, Search, TrendingUp, X } from "lucide-react";
import { useEffect, useState } from "react";

interface HelpItem {
  id: string;
  title: string;
  content: string;
  category: "getting-started" | "trading" | "ml-signals" | "troubleshooting";
  icon: React.ReactNode;
}

const helpItems: HelpItem[] = [
  {
    id: "what-is-paiid",
    title: "What is PaiiD?",
    content:
      "PaiiD is an AI-powered trading platform that provides real-time market analysis, sentiment tracking, options trading with Greeks, and risk management tools. It's designed for both beginners and experienced traders.",
    category: "getting-started",
    icon: <BookOpen size={16} />,
  },
  {
    id: "paper-trading",
    title: "Paper Trading Mode",
    content:
      "Paper trading lets you practice with virtual money. Your trades won't affect real money, but you'll see real market data and learn how the platform works. Perfect for beginners!",
    category: "getting-started",
    icon: <Lightbulb size={16} />,
  },
  {
    id: "ml-signals",
    title: "Understanding ML Signals",
    content:
      "Our AI analyzes market sentiment, news, and technical patterns to provide trading signals. Green signals suggest bullish sentiment, red suggests bearish. Always do your own research too!",
    category: "ml-signals",
    icon: <TrendingUp size={16} />,
  },
  {
    id: "risk-management",
    title: "Risk Management",
    content:
      "Never risk more than you can afford to lose. Start with paper trading, use stop-losses, and never invest more than 5% of your portfolio in a single trade. The platform shows risk metrics for each trade.",
    category: "trading",
    icon: <AlertCircle size={16} />,
  },
  {
    id: "options-greeks",
    title: "Options Greeks",
    content:
      "Greeks show how option prices change with market conditions. Delta = price sensitivity, Gamma = delta changes, Theta = time decay, Vega = volatility sensitivity. Higher numbers = more risk.",
    category: "trading",
    icon: <TrendingUp size={16} />,
  },
  {
    id: "troubleshooting",
    title: "Common Issues",
    content:
      "If the platform seems slow, try refreshing. If data isn't loading, check your internet connection. If you see errors, the backend might be updating - try again in a few minutes.",
    category: "troubleshooting",
    icon: <AlertCircle size={16} />,
  },
];

interface HelpPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function HelpPanel({ isOpen, onClose }: HelpPanelProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [filteredItems, setFilteredItems] = useState<HelpItem[]>(helpItems);

  // Filter items based on search and category
  useEffect(() => {
    let filtered = helpItems;

    // Filter by category
    if (selectedCategory !== "all") {
      filtered = filtered.filter((item) => item.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (item) =>
          item.title.toLowerCase().includes(query) || item.content.toLowerCase().includes(query)
      );
    }

    setFilteredItems(filtered);
  }, [searchQuery, selectedCategory]);

  const categories = [
    { id: "all", label: "All Topics", count: helpItems.length },
    {
      id: "getting-started",
      label: "Getting Started",
      count: helpItems.filter((i) => i.category === "getting-started").length,
    },
    {
      id: "trading",
      label: "Trading",
      count: helpItems.filter((i) => i.category === "trading").length,
    },
    {
      id: "ml-signals",
      label: "ML Signals",
      count: helpItems.filter((i) => i.category === "ml-signals").length,
    },
    {
      id: "troubleshooting",
      label: "Troubleshooting",
      count: helpItems.filter((i) => i.category === "troubleshooting").length,
    },
  ];

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity duration-300"
          onClick={onClose}
        />
      )}

      {/* Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-96 bg-gray-900 border-l border-gray-700 z-50 transform transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
        style={{
          backdropFilter: "blur(10px)",
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">Help Center</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Search */}
        <div className="p-4 border-b border-gray-700">
          <div className="relative">
            <Search
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              size={16}
            />
            <input
              type="text"
              placeholder="Search help topics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Categories */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  selectedCategory === category.id
                    ? "bg-blue-600 text-white"
                    : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                }`}
              >
                {category.label} ({category.count})
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {filteredItems.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              <Search size={32} className="mx-auto mb-2 opacity-50" />
              <p>No help topics found</p>
              <p className="text-sm">Try a different search term</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredItems.map((item) => (
                <div
                  key={item.id}
                  className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="text-blue-400 mt-0.5">{item.icon}</div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-white mb-2">{item.title}</h3>
                      <p className="text-gray-300 text-sm leading-relaxed">{item.content}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700 bg-gray-800">
          <p className="text-xs text-gray-400 text-center">
            Need more help? The platform includes contextual tooltips throughout the interface.
          </p>
        </div>
      </div>
    </>
  );
}
