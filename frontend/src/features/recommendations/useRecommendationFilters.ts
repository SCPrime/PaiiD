import { useCallback, useMemo, useState } from "react";

import {
  Recommendation,
  RecommendationAction,
  RecommendationFilterState,
  RecommendationRiskLevel,
  RecommendationVolatilityClass,
  RecommendationSortKey,
  SortDirection,
} from "./types";

const DEFAULT_FILTER_STATE: RecommendationFilterState = {
  search: "",
  minConfidence: 0,
  actions: ["BUY", "SELL", "HOLD"],
  riskLevels: [],
  volatilityClass: "All",
  momentumTrend: "All",
  sortBy: "confidence",
  sortDirection: "desc",
};

const RISK_RANK: Record<RecommendationRiskLevel, number> = {
  Low: 1,
  Medium: 2,
  High: 3,
};

const normalizeRisk = (risk?: string): RecommendationRiskLevel | undefined => {
  if (!risk) return undefined;
  const value = risk.toLowerCase();
  if (value === "low") return "Low";
  if (value === "high") return "High";
  return "Medium";
};

const normalizeTrend = (trend?: string) => trend?.toLowerCase();

const sorters: Record<RecommendationSortKey, (rec: Recommendation) => number | string> = {
  confidence: (rec) => rec.confidence ?? 0,
  score: (rec) => rec.score ?? 0,
  volatility: (rec) => rec.volatility?.volatility_score ?? rec.volatility?.atr_percent ?? 0,
  momentum: (rec) => rec.momentum?.price_vs_sma_50 ?? 0,
  risk: (rec) => RISK_RANK[normalizeRisk(rec.risk) ?? "Medium"],
  symbol: (rec) => rec.symbol,
};

export const useRecommendationFilters = () => {
  const [filters, setFilters] = useState<RecommendationFilterState>(DEFAULT_FILTER_STATE);

  const setSearch = useCallback((value: string) => {
    setFilters((prev) => ({ ...prev, search: value }));
  }, []);

  const setMinConfidence = useCallback((value: number) => {
    setFilters((prev) => ({ ...prev, minConfidence: value }));
  }, []);

  const toggleAction = useCallback((action: RecommendationAction) => {
    setFilters((prev) => {
      const exists = prev.actions.includes(action);
      const actions = exists
        ? prev.actions.filter((item) => item !== action)
        : [...prev.actions, action];
      return { ...prev, actions: actions.length ? actions : [action] };
    });
  }, []);

  const toggleRiskLevel = useCallback((risk: RecommendationRiskLevel) => {
    setFilters((prev) => {
      const exists = prev.riskLevels.includes(risk);
      const riskLevels = exists
        ? prev.riskLevels.filter((item) => item !== risk)
        : [...prev.riskLevels, risk];
      return { ...prev, riskLevels };
    });
  }, []);

  const setVolatilityClass = useCallback((value: RecommendationVolatilityClass | "All") => {
    setFilters((prev) => ({ ...prev, volatilityClass: value }));
  }, []);

  const setMomentumTrend = useCallback((value: string | "All") => {
    setFilters((prev) => ({ ...prev, momentumTrend: value }));
  }, []);

  const setSort = useCallback((sortBy: RecommendationSortKey, direction: SortDirection) => {
    setFilters((prev) => ({ ...prev, sortBy, sortDirection: direction }));
  }, []);

  const resetFilters = useCallback(() => setFilters(DEFAULT_FILTER_STATE), []);

  const applyFiltersAndSort = useCallback(
    (items: Recommendation[]): Recommendation[] => {
      const filtered = items.filter((rec) => {
        const risk = normalizeRisk(rec.risk);
        const matchesAction = filters.actions.includes(rec.action);
        const matchesConfidence = rec.confidence >= filters.minConfidence;
        const matchesSearch = filters.search
          ? [
              rec.symbol,
              rec.reason,
              rec.portfolioFit,
              rec.sector,
              rec.explanation,
              rec.tags?.join(" "),
            ]
              .filter(Boolean)
              .some((value) => value!.toLowerCase().includes(filters.search.toLowerCase()))
          : true;

        const matchesRisk =
          !filters.riskLevels.length || (risk && filters.riskLevels.includes(risk));

        const volatilityClass = rec.volatility?.volatility_class;
        const matchesVolatility =
          filters.volatilityClass === "All" ||
          (volatilityClass &&
            volatilityClass.toLowerCase() === filters.volatilityClass.toLowerCase());

        const trend = normalizeTrend(rec.momentum?.trend_alignment);
        const matchesMomentum =
          filters.momentumTrend === "All" || trend === filters.momentumTrend.toLowerCase();

        return (
          matchesAction &&
          matchesConfidence &&
          matchesSearch &&
          matchesRisk &&
          matchesVolatility &&
          matchesMomentum
        );
      });

      const sorter = sorters[filters.sortBy];
      const directionFactor = filters.sortDirection === "asc" ? 1 : -1;

      return [...filtered].sort((a, b) => {
        const left = sorter(a);
        const right = sorter(b);

        if (typeof left === "string" && typeof right === "string") {
          return left.localeCompare(right) * directionFactor;
        }

        return ((left as number) - (right as number)) * directionFactor;
      });
    },
    [filters]
  );

  const filterSummary = useMemo(
    () => ({
      selectedActions: filters.actions.length,
      selectedRiskLevels: filters.riskLevels.length,
      minConfidence: filters.minConfidence,
    }),
    [filters]
  );

  return {
    filters,
    filterSummary,
    setSearch,
    setMinConfidence,
    toggleAction,
    toggleRiskLevel,
    setVolatilityClass,
    setMomentumTrend,
    setSort,
    resetFilters,
    applyFiltersAndSort,
  };
};

export type RecommendationFiltersHook = ReturnType<typeof useRecommendationFilters>;
