import { StrategyConfigResponse, StrategyPerformanceLog, StrategySavePayload, StrategyVersion } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || "https://paiid-backend.onrender.com";
const API_TOKEN = process.env.NEXT_PUBLIC_API_TOKEN || "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${API_TOKEN}`,
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export async function fetchStrategyConfig(strategyType: string): Promise<StrategyConfigResponse> {
  return request<StrategyConfigResponse>(`/api/strategies/load/${strategyType}`);
}

export async function fetchStrategyHistory(strategyType: string): Promise<StrategyVersion[]> {
  const data = await request<{ history: StrategyVersion[] }>(
    `/api/strategies/history/${strategyType}`,
  );
  return data.history;
}

export async function fetchStrategyPerformance(
  strategyType: string,
): Promise<StrategyPerformanceLog[]> {
  const data = await request<{ performance: StrategyPerformanceLog[] }>(
    `/api/strategies/performance/${strategyType}`,
  );
  return data.performance;
}

export async function saveStrategyConfig(
  payload: StrategySavePayload,
): Promise<StrategyConfigResponse> {
  const data = await request<{ strategy: StrategyConfigResponse }>(`/api/strategies/save`, {
    method: "POST",
    body: JSON.stringify(payload),
  });

  return data.strategy;
}
