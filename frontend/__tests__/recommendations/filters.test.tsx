import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import {
  RecommendationFilters,
  Recommendation,
  useRecommendationFilters,
} from "@/src/features/recommendations";

const SAMPLE_RECOMMENDATIONS: Recommendation[] = [
  {
    symbol: "AAPL",
    action: "BUY",
    confidence: 92,
    score: 8.5,
    reason: "Strong earnings momentum",
    targetPrice: 210,
    currentPrice: 180,
    risk: "Low",
    tradeData: {
      symbol: "AAPL",
      side: "buy",
      quantity: 10,
      orderType: "limit",
    },
    momentum: {
      sma_20: 185,
      sma_50: 178,
      sma_200: 165,
      price_vs_sma_20: 5,
      price_vs_sma_50: 2,
      price_vs_sma_200: 9,
      avg_volume_20d: 1200000,
      volume_strength: "High",
      volume_ratio: 1.4,
      trend_alignment: "Bullish",
    },
    volatility: {
      atr: 2.1,
      atr_percent: 1.2,
      bb_width: 3.2,
      volatility_class: "Low",
      volatility_score: 2,
    },
    sector: "Technology",
    sectorPerformance: {
      name: "Technology",
      changePercent: 1.2,
      rank: 1,
      isLeader: true,
      isLaggard: false,
    },
    explanation: "Breakout from consolidation",
  },
  {
    symbol: "TSLA",
    action: "SELL",
    confidence: 68,
    score: 6.1,
    reason: "Weak delivery outlook",
    targetPrice: 180,
    currentPrice: 200,
    risk: "High",
    tradeData: {
      symbol: "TSLA",
      side: "sell",
      quantity: 5,
      orderType: "market",
    },
    momentum: {
      sma_20: 205,
      sma_50: 210,
      sma_200: 220,
      price_vs_sma_20: -2,
      price_vs_sma_50: -5,
      price_vs_sma_200: -9,
      avg_volume_20d: 900000,
      volume_strength: "Normal",
      volume_ratio: 0.9,
      trend_alignment: "Bearish",
    },
    volatility: {
      atr: 5.5,
      atr_percent: 2.7,
      bb_width: 6.1,
      volatility_class: "High",
      volatility_score: 8,
    },
    sector: "Consumer Discretionary",
    sectorPerformance: {
      name: "Consumer Discretionary",
      changePercent: -0.8,
      rank: 9,
      isLeader: false,
      isLaggard: true,
    },
    explanation: "Trend reversal signal",
  },
  {
    symbol: "MSFT",
    action: "HOLD",
    confidence: 74,
    score: 7.3,
    reason: "Neutral trend",
    targetPrice: 350,
    currentPrice: 340,
    risk: "Medium",
    tradeData: {
      symbol: "MSFT",
      side: "buy",
      quantity: 8,
      orderType: "limit",
    },
    momentum: {
      sma_20: 338,
      sma_50: 330,
      sma_200: 310,
      price_vs_sma_20: 0.5,
      price_vs_sma_50: 3,
      price_vs_sma_200: 9,
      avg_volume_20d: 1000000,
      volume_strength: "Normal",
      volume_ratio: 1.0,
      trend_alignment: "Mixed",
    },
    volatility: {
      atr: 1.8,
      atr_percent: 0.6,
      bb_width: 2.3,
      volatility_class: "Medium",
      volatility_score: 4,
    },
    sector: "Technology",
    sectorPerformance: {
      name: "Technology",
      changePercent: 0.4,
      rank: 3,
      isLeader: true,
      isLaggard: false,
    },
    explanation: "Sideways consolidation",
  },
];

const FiltersHarness = () => {
  const hook = useRecommendationFilters();
  const filtered = hook.applyFiltersAndSort(SAMPLE_RECOMMENDATIONS);

  return (
    <div>
      <RecommendationFilters
        filters={hook.filters}
        onSearchChange={hook.setSearch}
        onConfidenceChange={hook.setMinConfidence}
        onToggleAction={hook.toggleAction}
        onToggleRisk={hook.toggleRiskLevel}
        onVolatilityChange={hook.setVolatilityClass}
        onMomentumChange={hook.setMomentumTrend}
        onSortChange={hook.setSort}
        onReset={hook.resetFilters}
        onExport={() => undefined}
      />
      <div data-testid="count">{filtered.length}</div>
    </div>
  );
};

describe("RecommendationFilters", () => {
  test("filters by search, confidence, and risk", async () => {
    render(<FiltersHarness />);
    const user = userEvent.setup();

    expect(screen.getByTestId("count").textContent).toBe("3");

    const searchInput = screen.getByPlaceholderText("Search symbol, sector, or reason");
    await user.type(searchInput, "TSLA");
    expect(screen.getByTestId("count").textContent).toBe("1");

    const resetButton = screen.getByRole("button", { name: /reset filters/i });
    await user.click(resetButton);
    expect(screen.getByTestId("count").textContent).toBe("3");

    const highRiskButton = screen.getByRole("button", { name: /high/i });
    await user.click(highRiskButton);
    expect(screen.getByTestId("count").textContent).toBe("1");

    const slider = screen.getByLabelText(/minimum confidence/i) as HTMLInputElement;
    fireEvent.change(slider, { target: { value: "90" } });
    expect(screen.getByTestId("count").textContent).toBe("0");

    await user.click(highRiskButton);
    expect(screen.getByTestId("count").textContent).toBe("1");
  });
});
