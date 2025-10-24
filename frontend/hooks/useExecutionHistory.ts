import { useCallback, useEffect, useMemo, useReducer, useRef } from "react";

export interface ExecutionRecord {
  id: string;
  schedule_id: string;
  schedule_name: string;
  started_at: string;
  completed_at?: string | null;
  status: "pending" | "running" | "completed" | "failed" | "awaiting_approval";
  result?: string | null;
  error?: string | null;
}

interface ExecutionHistoryResponse {
  items: ExecutionRecord[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

type State = {
  items: ExecutionRecord[];
  loading: boolean;
  error: string | null;
  page: number;
  pageSize: number;
  total: number;
  hasMore: boolean;
};

type Action =
  | { type: "REQUEST"; page: number }
  | { type: "SUCCESS"; payload: ExecutionHistoryResponse; append: boolean }
  | { type: "FAILURE"; error: string }
  | { type: "RESET"; pageSize: number };

const initialState: State = {
  items: [],
  loading: false,
  error: null,
  page: 1,
  pageSize: 20,
  total: 0,
  hasMore: false,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "RESET":
      return {
        ...initialState,
        pageSize: action.pageSize,
      };
    case "REQUEST":
      return {
        ...state,
        loading: true,
        error: null,
        page: action.page,
      };
    case "SUCCESS":
      return {
        ...state,
        loading: false,
        error: null,
        items: action.append ? [...state.items, ...action.payload.items] : action.payload.items,
        total: action.payload.total,
        hasMore: action.payload.has_more,
        page: action.payload.page,
        pageSize: action.payload.page_size,
      };
    case "FAILURE":
      return {
        ...state,
        loading: false,
        error: action.error,
      };
    default:
      return state;
  }
}

export interface UseExecutionHistoryOptions {
  pageSize?: number;
  scheduleId?: string | null;
  autoStart?: boolean;
}

export interface UseExecutionHistoryResult {
  items: ExecutionRecord[];
  loading: boolean;
  error: string | null;
  hasMore: boolean;
  total: number;
  page: number;
  refresh: () => Promise<void>;
  loadNextPage: () => Promise<void>;
}

/**
 * Data loader for the scheduler execution history tab.
 * Handles pagination, empty datasets and network failure resiliency.
 */
export function useExecutionHistory(
  options: UseExecutionHistoryOptions = {}
): UseExecutionHistoryResult {
  const { pageSize = 20, scheduleId = null, autoStart = true } = options;
  const [state, dispatch] = useReducer(reducer, { ...initialState, pageSize });
  const activeRequest = useRef<AbortController | null>(null);
  const lastScheduleId = useRef<string | null | undefined>(scheduleId);

  const buildUrl = useCallback(
    (page: number) => {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      });
      if (scheduleId) {
        params.append("schedule_id", scheduleId);
      }
      return `/api/proxy/scheduler/executions?${params.toString()}`;
    },
    [pageSize, scheduleId]
  );

  const performFetch = useCallback(
    async (page: number, append: boolean) => {
      if (activeRequest.current) {
        activeRequest.current.abort();
      }

      const controller = new AbortController();
      activeRequest.current = controller;

      dispatch({ type: "REQUEST", page });

      try {
        const response = await fetch(buildUrl(page), {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Request failed: ${response.status}`);
        }

        const payload = (await response.json()) as ExecutionHistoryResponse;
        dispatch({ type: "SUCCESS", payload, append });
      } catch (error: unknown) {
        if ((error as DOMException)?.name === "AbortError") {
          return;
        }
        dispatch({ type: "FAILURE", error: (error as Error)?.message || "Unknown error" });
      }
    },
    [buildUrl]
  );

  const refresh = useCallback(async () => {
    dispatch({ type: "RESET", pageSize });
    await performFetch(1, false);
  }, [performFetch, pageSize]);

  const loadNextPage = useCallback(async () => {
    if (state.loading || !state.hasMore) {
      return;
    }
    const nextPage = state.page + 1;
    await performFetch(nextPage, true);
  }, [performFetch, state.hasMore, state.loading, state.page]);

  useEffect(() => {
    if (lastScheduleId.current !== scheduleId) {
      lastScheduleId.current = scheduleId;
      dispatch({ type: "RESET", pageSize });
    }
  }, [scheduleId, pageSize]);

  useEffect(() => {
    if (!autoStart) {
      return;
    }
    performFetch(1, false);

    return () => {
      activeRequest.current?.abort();
    };
  }, [performFetch, autoStart]);

  const memoizedItems = useMemo(() => state.items, [state.items]);

  return {
    items: memoizedItems,
    loading: state.loading,
    error: state.error,
    hasMore: state.hasMore,
    total: state.total,
    page: state.page,
    refresh,
    loadNextPage,
  };
}

export default useExecutionHistory;
