export interface StrategyVersion {
  version_number: number;
  created_at: string;
  created_by?: string | null;
  changes_summary?: string | null;
}

export interface StrategyPerformanceLog {
  id: number;
  version_number: number;
  run_type: string;
  metrics: Record<string, unknown>;
  notes?: string | null;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
}

export interface StrategyConfigResponse {
  strategy_type: string;
  config: Record<string, unknown>;
  model_key?: string | null;
  feature_flags: Record<string, boolean>;
  version: number;
  history: StrategyVersion[];
  performance: StrategyPerformanceLog[];
  is_default: boolean;
}

export interface StrategySavePayload {
  strategy_type: string;
  config: Record<string, unknown>;
  model_key: string;
  feature_flags: Record<string, boolean>;
  changes_summary?: string;
}

export interface StrategyListEntry {
  strategy_type: string;
  has_config: boolean;
  model_key?: string | null;
  updated_at?: string | null;
}
