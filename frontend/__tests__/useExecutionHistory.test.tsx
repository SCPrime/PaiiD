import { renderHook, act, waitFor } from "@testing-library/react";
import useExecutionHistory from "../hooks/useExecutionHistory";

describe("useExecutionHistory", () => {
  beforeEach(() => {
    global.fetch = jest.fn() as jest.Mock;
  });

  afterEach(() => {
    (global.fetch as jest.Mock).mockReset();
  });

  const mockJsonResponse = (data: unknown) =>
    Promise.resolve({
      ok: true,
      json: async () => data,
    } as unknown as Response);

  it("handles empty dataset gracefully", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce(
      mockJsonResponse({
        items: [],
        total: 0,
        page: 1,
        page_size: 10,
        has_more: false,
      })
    );

    const { result } = renderHook(() => useExecutionHistory({ pageSize: 10 }));

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.items).toEqual([]);
    expect(result.current.hasMore).toBe(false);
    expect(result.current.total).toBe(0);
  });

  it("appends new pages when pagination is requested", async () => {
    (global.fetch as jest.Mock)
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [
            {
              id: "1",
              schedule_id: "schedule-1",
              schedule_name: "Morning Routine",
              started_at: new Date().toISOString(),
              completed_at: null,
              status: "completed",
              result: "Success",
              error: null,
            },
          ],
          total: 2,
          page: 1,
          page_size: 1,
          has_more: true,
        })
      )
      .mockResolvedValueOnce(
        mockJsonResponse({
          items: [
            {
              id: "2",
              schedule_id: "schedule-2",
              schedule_name: "AI Recommendations",
              started_at: new Date().toISOString(),
              completed_at: null,
              status: "failed",
              result: null,
              error: "Network timeout",
            },
          ],
          total: 2,
          page: 2,
          page_size: 1,
          has_more: false,
        })
      );

    const { result } = renderHook(() => useExecutionHistory({ pageSize: 1 }));

    await waitFor(() => expect(result.current.items).toHaveLength(1));
    expect(result.current.hasMore).toBe(true);

    await act(async () => {
      await result.current.loadNextPage();
    });

    await waitFor(() => expect(result.current.items).toHaveLength(2));
    expect(result.current.hasMore).toBe(false);
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it("surfaces network failures", async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useExecutionHistory());

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.error).toContain("Network error");
    expect(result.current.items).toEqual([]);
  });
});
