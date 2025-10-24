import { exportRecommendationsToCsv, Recommendation } from "@/src/features/recommendations";

describe("exportRecommendationsToCsv", () => {
  test("serialises recommendation data without downloading", () => {
    const sample: Recommendation[] = [
      {
        symbol: "AAPL",
        action: "BUY",
        confidence: 95,
        score: 8.8,
        reason: "Strong growth",
        targetPrice: 210,
        currentPrice: 180,
        risk: "Low",
        volatility: {
          atr: 1.2,
          atr_percent: 0.8,
          bb_width: 2.1,
          volatility_class: "Low",
          volatility_score: 2,
        },
        momentum: {
          sma_20: 178,
          sma_50: 170,
          sma_200: 160,
          price_vs_sma_20: 4,
          price_vs_sma_50: 6,
          price_vs_sma_200: 12,
          avg_volume_20d: 1500000,
          volume_strength: "High",
          volume_ratio: 1.6,
          trend_alignment: "Bullish",
        },
      },
    ];

    const csv = exportRecommendationsToCsv(sample, { download: false, fileName: "test.csv" });
    expect(csv).toContain("Symbol,Action");
    expect(csv).toContain("AAPL");
    expect(csv.split("\n")).toHaveLength(2);
  });
});
