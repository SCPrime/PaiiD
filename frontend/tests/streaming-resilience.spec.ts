import { expect, test } from "@playwright/test";
import { hasChromiumBrowser } from "./utils/chromiumAvailability";

type StreamEventCapture = {
  stream?: string;
  event?: string;
  [key: string]: unknown;
};

type MockSSEController = {
  url: string;
  emit: (type: string, payload?: unknown) => void;
  fail: (payload?: unknown) => void;
};

test.skip(
  !hasChromiumBrowser(),
  "Chromium browser binaries are not available. Run `npx playwright install` to enable streaming resilience tests."
);

test.describe("Streaming resilience instrumentation", () => {
  test("tracks SSE lifecycle events and reconnect flows", async ({ page }) => {
    const capturedEvents: StreamEventCapture[] = [];

    await page.exposeFunction("__recordStreamEvent", (detail: StreamEventCapture) => {
      capturedEvents.push(detail);
    });

    await page.addInitScript(() => {
      type RecorderWindow = Window &
        typeof globalThis & {
          __recordStreamEvent?: (detail: StreamEventCapture) => void;
        };

      window.addEventListener("paiid:stream-event", (event) => {
        const customEvent = event as CustomEvent<StreamEventCapture>;
        (window as RecorderWindow).__recordStreamEvent?.(customEvent.detail);
      });
    });

    await page.addInitScript(() => {
      class MockEventSource extends EventTarget {
        public static instances: MockEventSource[] = [];
        public url: string;
        public readyState = 0;
        public withCredentials = false;
        public onopen: ((this: EventSource, ev: Event) => void) | null = null;
        public onerror: ((this: EventSource, ev: Event) => void) | null = null;

        constructor(url: string) {
          super();
          this.url = url;
          MockEventSource.instances.push(this);

          setTimeout(() => {
            this.readyState = 1;
            const openEvent = new Event("open");
            this.dispatchEvent(openEvent);
            this.onopen?.call(this as unknown as EventSource, openEvent);
          }, 0);
        }

        emit(type: string, payload?: unknown) {
          const data =
            payload === undefined
              ? undefined
              : typeof payload === "string"
                ? payload
                : JSON.stringify(payload);
          const event = new MessageEvent(type, { data });
          this.dispatchEvent(event);
          const handler = (this as Record<string, unknown>)[`on${type}`];
          if (typeof handler === "function") {
            (handler as (event: MessageEvent) => void).call(this, event);
          }
        }

        fail(payload?: unknown) {
          const data = payload === undefined ? undefined : JSON.stringify(payload);
          const event = new MessageEvent("error", { data });
          this.readyState = 2;
          this.dispatchEvent(event);
          this.onerror?.call(this as unknown as EventSource, event);
        }

        close() {
          this.readyState = 2;
        }
      }

      type RecorderWindow = Window &
        typeof globalThis & {
          __mockSSEInstances?: MockEventSource[];
        };

      Object.defineProperty(window, "EventSource", {
        configurable: true,
        writable: true,
        value: MockEventSource,
      });

      (window as RecorderWindow).__mockSSEInstances = MockEventSource.instances;
    });

    await page.goto("/__qa__/streaming-harness");
    await expect(page.getByTestId("qa-harness-ready")).toBeVisible();

    await expect
      .poll(
        async () => {
          const text = await page.getByTestId("positions-connection").innerText();
          return text;
        },
        { timeout: 5000 }
      )
      .toContain("CONNECTED");

    await expect
      .poll(
        async () => {
          const text = await page.getByTestId("market-connection").innerText();
          return text;
        },
        { timeout: 5000 }
      )
      .toContain("CONNECTED");

    await page.evaluate(() => {
      type RecorderWindow = Window &
        typeof globalThis & {
          __mockSSEInstances: MockSSEController[];
        };

      const instances = (window as RecorderWindow).__mockSSEInstances;
      const positionsSource = instances.find((instance) =>
        instance.url.includes("/stream/positions")
      );
      positionsSource?.emit("heartbeat", { timestamp: new Date().toISOString() });
      positionsSource?.emit("position_update", [
        {
          symbol: "AAPL",
          qty: 5,
          avgEntryPrice: 150,
          currentPrice: 152,
          marketValue: 760,
          unrealizedPL: 10,
          unrealizedPLPercent: 1.2,
          side: "long",
          dayChange: 3,
          dayChangePercent: 0.5,
        },
      ]);
    });

    await expect(page.getByTestId("positions-count")).toHaveText(/1/);
    await expect(page.getByTestId("positions-summary")).toContainText("AAPL");

    await page.evaluate(() => {
      type RecorderWindow = Window &
        typeof globalThis & {
          __mockSSEInstances: MockSSEController[];
        };

      const instances = (window as RecorderWindow).__mockSSEInstances;
      const marketSource = instances.find((instance) => instance.url.includes("/stream/prices"));
      marketSource?.emit("heartbeat", { timestamp: new Date().toISOString() });
      marketSource?.emit("price_update", {
        AAPL: {
          price: 152.12,
          timestamp: new Date().toISOString(),
          type: "trade",
        },
      });
    });

    await expect(page.getByTestId("market-symbols")).toContainText("AAPL");

    const initialInstances = await page.evaluate(() => {
      type RecorderWindow = Window &
        typeof globalThis & {
          __mockSSEInstances: MockSSEController[];
        };

      const instances = (window as RecorderWindow).__mockSSEInstances;
      return instances.length;
    });

    await page.evaluate(() => {
      type RecorderWindow = Window &
        typeof globalThis & {
          __mockSSEInstances: MockSSEController[];
        };

      const instances = (window as RecorderWindow).__mockSSEInstances;
      const positionsSource = instances.find((instance) =>
        instance.url.includes("/stream/positions")
      );
      positionsSource?.fail({ error: "server-down" });
    });

    await expect
      .poll(
        async () => {
          return await page.evaluate(() => {
            type RecorderWindow = Window &
              typeof globalThis & {
                __mockSSEInstances: MockSSEController[];
              };

            const instances = (window as RecorderWindow).__mockSSEInstances;
            return instances.length;
          });
        },
        { timeout: 10000 }
      )
      .toBeGreaterThan(initialInstances);

    await expect.poll(() => capturedEvents.length, { timeout: 3000 }).toBeGreaterThan(0);

    const positionEvents = capturedEvents.filter((event) => event.stream === "positions");
    const marketEvents = capturedEvents.filter((event) => event.stream === "market-prices");

    expect(positionEvents.length).toBeGreaterThan(0);
    expect(marketEvents.length).toBeGreaterThan(0);

    const reconnectEvents = positionEvents.filter((event) => event.event === "reconnect_scheduled");
    expect(reconnectEvents.length).toBeGreaterThan(0);
  });
});
