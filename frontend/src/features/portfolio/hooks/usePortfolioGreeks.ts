import useSWR from "swr";

import { PortfolioGreekAnalytics } from "@/src/features/portfolio/types";

const fetcher = async (url: string): Promise<PortfolioGreekAnalytics> => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load portfolio Greeks: ${response.status}`);
  }
  return response.json();
};

export function usePortfolioGreeks() {
  const swr = useSWR<PortfolioGreekAnalytics>("/api/proxy/portfolio/greeks", fetcher, {
    refreshInterval: 30000,
    revalidateOnFocus: true,
  });

  return {
    data: swr.data,
    isLoading: swr.isLoading,
    error: swr.error,
    refresh: swr.mutate,
  };
}
