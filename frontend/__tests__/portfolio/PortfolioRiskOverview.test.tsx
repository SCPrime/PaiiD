import React from "react";
import "@testing-library/jest-dom";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SWRConfig } from "swr";

import PortfolioRiskOverview from "@/src/features/portfolio/components/PortfolioRiskOverview";
import { PortfolioGreekAnalytics } from "@/src/features/portfolio/types";

declare global {
  // eslint-disable-next-line no-var
  var ResizeObserver: any;
}

global.ResizeObserver = class ResizeObserver {
  observe() {
    return null;
  }
  unobserve() {
    return null;
  }
  disconnect() {
    return null;
  }
};

const mockResponse = (data: PortfolioGreekAnalytics) =>
  ({
    ok: true,
    json: async () => data,
  } as unknown as Response);

describe("PortfolioRiskOverview", () => {
  afterEach(() => {
    (global.fetch as jest.Mock | undefined)?.mockReset?.();
  });

  it("renders aggregated totals", async () => {
    const sample: PortfolioGreekAnalytics = {
      totals: { delta: 125, gamma: 3.25, theta: -12.5, vega: 24.8, rho: 8.2 },
      breakdown: [],
    };

    global.fetch = jest
      .fn()
      .mockResolvedValue(mockResponse(sample)) as unknown as typeof fetch;

    render(
      <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
        <div style={{ width: 800, height: 400 }}>
          <PortfolioRiskOverview />
        </div>
      </SWRConfig>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("greek-total-delta")).toHaveTextContent("125.00"),
    );
    expect(screen.getByTestId("greek-total-theta")).toHaveTextContent("-12.50");
  });

  it("refreshes data when the user clicks refresh", async () => {
    const initial: PortfolioGreekAnalytics = {
      totals: { delta: 100, gamma: 2, theta: -10, vega: 20, rho: 5 },
      breakdown: [],
    };
    const updated: PortfolioGreekAnalytics = {
      totals: { delta: 150, gamma: 4, theta: -8, vega: 30, rho: 6 },
      breakdown: [],
    };

    const fetchMock = jest
      .fn()
      .mockResolvedValueOnce(mockResponse(initial))
      .mockResolvedValueOnce(mockResponse(updated));

    global.fetch = fetchMock as unknown as typeof fetch;

    render(
      <SWRConfig value={{ provider: () => new Map(), dedupingInterval: 0 }}>
        <div style={{ width: 800, height: 400 }}>
          <PortfolioRiskOverview />
        </div>
      </SWRConfig>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("greek-total-delta")).toHaveTextContent("100.00"),
    );

    fireEvent.click(screen.getByRole("button", { name: /refresh/i }));

    await waitFor(() =>
      expect(screen.getByTestId("greek-total-delta")).toHaveTextContent("150.00"),
    );
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
