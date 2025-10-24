import type { Event } from "@sentry/types";

jest.mock("@sentry/nextjs", () => {
  const init = jest.fn();
  const addGlobalEventProcessor = jest.fn();
  const BrowserTracing = jest.fn().mockImplementation(() => ({ name: "BrowserTracing" }));
  const Replay = jest.fn().mockImplementation((options) => ({ name: "Replay", options }));

  return {
    init,
    addGlobalEventProcessor,
    BrowserTracing,
    Replay,
    captureException: jest.fn(),
    captureMessage: jest.fn(),
    setUser: jest.fn(),
    addBreadcrumb: jest.fn(),
  };
});

const sentryModulePath = "../lib/sentry";
const originalEnv = { ...process.env };

function resetModules() {
  jest.resetModules();
  process.env = { ...originalEnv };
}

describe("initSentry", () => {
  beforeEach(() => {
    resetModules();
    jest.clearAllMocks();
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  it("skips initialization when DSN missing", async () => {
    delete process.env.NEXT_PUBLIC_SENTRY_DSN;
    const { initSentry } = await import(sentryModulePath);
    initSentry();

    const sentry = await import("@sentry/nextjs");
    expect(sentry.init).not.toHaveBeenCalled();
  });

  it("initializes with production overrides", async () => {
    process.env.NEXT_PUBLIC_SENTRY_DSN = "https://public@sentry.io/1";
    process.env.NODE_ENV = "production";
    process.env.NEXT_PUBLIC_VERCEL_GIT_COMMIT_SHA = "abcd1234";
    process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE = "0.45";
    process.env.NEXT_PUBLIC_SENTRY_REPLAYS_SESSION_SAMPLE_RATE = "0.2";
    process.env.NEXT_PUBLIC_SENTRY_REPLAYS_ERROR_SAMPLE_RATE = "0.9";

    const { initSentry } = await import(sentryModulePath);
    initSentry();

    const sentry = await import("@sentry/nextjs");
    expect(sentry.init).toHaveBeenCalledTimes(1);

    const config = (sentry.init as jest.Mock).mock.calls[0][0];
    expect(config.environment).toBe("production");
    expect(config.release).toBe("paiid-frontend@abcd1234");
    expect(config.tracesSampleRate).toBe(0.45);
    expect(config.replaysSessionSampleRate).toBe(0.2);
    expect(config.replaysOnErrorSampleRate).toBe(0.9);

    const replayOptions = (sentry.Replay as jest.Mock).mock.calls[0][0];
    expect(replayOptions.maskAllInputs).toBe(true);
    expect(replayOptions.networkRequestHeaders).toBe(false);

    const sanitized = config.beforeSend(
      {
        request: {
          headers: {
            Authorization: "Bearer secret",
            authorization: "Bearer secondary",
          },
        },
        breadcrumbs: [
          {
            data: {
              url: "https://example.com/api?token=abc123",
              request: { headers: { Authorization: "Bearer 1" } },
            },
          },
        ],
      } as Event,
      {},
    );

    expect(sanitized?.request?.headers?.Authorization).toBe("[REDACTED]");
    expect(sanitized?.breadcrumbs?.[0]?.data?.url).toBe("https://example.com/api?token=REDACTED");
    expect(sanitized?.breadcrumbs?.[0]?.data?.request?.headers?.Authorization).toBe("[REDACTED]");

    const processor = (sentry.addGlobalEventProcessor as jest.Mock).mock.calls[0][0];
    const replayEvent = processor({
      type: "replay_event",
      contexts: {
        replay: {
          request: {
            headers: { Authorization: "Bearer 2" },
          },
        },
      },
    });
    expect(replayEvent.contexts?.replay?.request?.headers?.Authorization).toBe("[REDACTED]");
  });

  it("defaults to development-safe sampling when local", async () => {
    process.env.NEXT_PUBLIC_SENTRY_DSN = "https://public@sentry.io/1";
    process.env.NODE_ENV = "development";
    delete process.env.NEXT_PUBLIC_SENTRY_REPLAYS_SESSION_SAMPLE_RATE;

    const { initSentry } = await import(sentryModulePath);
    initSentry();

    const sentry = await import("@sentry/nextjs");
    const config = (sentry.init as jest.Mock).mock.calls[0][0];
    expect(config.environment).toBe("development");
    expect(config.replaysSessionSampleRate).toBe(0);
    expect(config.replaysOnErrorSampleRate).toBe(1);
  });
});
