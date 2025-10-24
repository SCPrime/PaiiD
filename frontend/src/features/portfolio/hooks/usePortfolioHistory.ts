import useSWR from "swr";

import { PortfolioHistoryResponse } from "@/src/features/portfolio/types";

const fetcher = async (url: string): Promise<PortfolioHistoryResponse> => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load portfolio history: ${response.status}`);
  }
  return response.json();
};

export function usePortfolioHistory(period: string = "1M") {
  const swr = useSWR<PortfolioHistoryResponse>(
    `/api/proxy/portfolio/history?period=${encodeURIComponent(period)}`,
    fetcher,
    {
      refreshInterval: 60000,
      revalidateOnFocus: true,
    },
  );

  return {
    data: swr.data,
    isLoading: swr.isLoading,
    error: swr.error,
    refresh: swr.mutate,
  };
}
