/**
 * Options Test Fixtures
 *
 * Shared test constants and data for Playwright tests.
 * Ensures deterministic testing across different environments.
 */

// Test symbols available in backend fixtures
export const TEST_SYMBOLS = ["OPTT", "SPY"] as const;

// Test expiration dates (must match backend fixtures)
export const TEST_EXPIRATIONS = ["2025-11-15", "2025-11-22", "2025-11-29"] as const;

// Test configuration
export const TEST_CONFIG = {
  // Backend URL for testing
  BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_API_BASE_URL || "http://localhost:8001",

  // API Token for testing
  API_TOKEN: process.env.NEXT_PUBLIC_API_TOKEN || "test-token",

  // Test timeouts
  TIMEOUTS: {
    API_REQUEST: 10000, // 10 seconds
    PAGE_LOAD: 30000, // 30 seconds
    ELEMENT_WAIT: 5000, // 5 seconds
  },

  // Test retry configuration
  RETRIES: {
    MAX_ATTEMPTS: 3,
    DELAY_MS: 1000,
  },
} as const;

// Expected data shapes for validation
export const EXPECTED_OPTIONS_CHAIN_SHAPE = {
  symbol: "string",
  expiration_date: "string",
  underlying_price: "number",
  calls: "array",
  puts: "array",
  total_contracts: "number",
} as const;

export const EXPECTED_OPTION_CONTRACT_SHAPE = {
  symbol: "string",
  underlying_symbol: "string",
  option_type: "string",
  strike_price: "number",
  expiration_date: "string",
  bid: "number",
  ask: "number",
  last_price: "number",
  volume: "number",
  open_interest: "number",
  delta: "number",
  gamma: "number",
  theta: "number",
  vega: "number",
  implied_volatility: "number",
} as const;

// Test data generators
export const generateTestOptionContract = (
  overrides: Partial<typeof EXPECTED_OPTION_CONTRACT_SHAPE> = {}
) => ({
  symbol: "TEST251115C00045000",
  underlying_symbol: "SPY",
  option_type: "call",
  strike_price: 450,
  expiration_date: "2025-11-15",
  bid: 1.5,
  ask: 1.6,
  last_price: 1.55,
  volume: 100,
  open_interest: 1000,
  delta: 0.5,
  gamma: 0.01,
  theta: -0.05,
  vega: 0.1,
  implied_volatility: 0.2,
  ...overrides,
});

export const generateTestOptionsChain = (symbol: string = "SPY", overrides: any = {}) => ({
  symbol,
  expiration_date: "2025-11-15",
  underlying_price: 450.0,
  calls: [generateTestOptionContract({ underlying_symbol: symbol, option_type: "call" })],
  puts: [generateTestOptionContract({ underlying_symbol: symbol, option_type: "put" })],
  total_contracts: 2,
  ...overrides,
});

// Error scenarios for testing
export const ERROR_SCENARIOS = {
  INVALID_SYMBOL: "INVALID",
  NETWORK_ERROR: "NETWORK_ERROR",
  SERVER_ERROR: "SERVER_ERROR",
  TIMEOUT: "TIMEOUT",
} as const;

// Test selectors (centralized for maintainability)
export const SELECTORS = {
  // Options chain page
  OPTIONS_CHAIN_PAGE: '[data-testid="options-chain-page"]',
  SYMBOL_INPUT: 'input[data-testid="symbol-input"]',
  EXPIRATION_SELECT: 'select[data-testid="expiration-select"]',
  LOAD_BUTTON: 'button[data-testid="load-options"]',

  // Options table
  OPTIONS_TABLE: '[data-testid="options-table"]',
  CALLS_SECTION: '[data-testid="calls-section"]',
  PUTS_SECTION: '[data-testid="puts-section"]',
  OPTION_ROW: '[data-testid="option-row"]',

  // Greeks display
  DELTA_CELL: '[data-testid="delta"]',
  GAMMA_CELL: '[data-testid="gamma"]',
  THETA_CELL: '[data-testid="theta"]',
  VEGA_CELL: '[data-testid="vega"]',

  // Loading states
  LOADING_SPINNER: '[data-testid="loading-spinner"]',
  ERROR_MESSAGE: '[data-testid="error-message"]',

  // Navigation
  RADIAL_MENU: '[data-testid="radial-menu"]',
  OPTIONS_WEDGE: '[data-testid="options-wedge"]',
} as const;

// Test assertions helpers
export const assertValidOptionsChain = (data: any) => {
  expect(data).toHaveProperty("symbol");
  expect(data).toHaveProperty("expiration_date");
  expect(data).toHaveProperty("underlying_price");
  expect(data).toHaveProperty("calls");
  expect(data).toHaveProperty("puts");
  expect(data).toHaveProperty("total_contracts");
  expect(Array.isArray(data.calls)).toBe(true);
  expect(Array.isArray(data.puts)).toBe(true);
  expect(typeof data.total_contracts).toBe("number");
};

export const assertValidOptionContract = (contract: any) => {
  expect(contract).toHaveProperty("symbol");
  expect(contract).toHaveProperty("strike_price");
  expect(contract).toHaveProperty("option_type");
  expect(contract).toHaveProperty("delta");
  expect(contract).toHaveProperty("gamma");
  expect(contract).toHaveProperty("theta");
  expect(contract).toHaveProperty("vega");
  expect(typeof contract.strike_price).toBe("number");
  expect(typeof contract.delta).toBe("number");
};

// Test utilities
export const waitForApiResponse = async (
  page: any,
  timeout: number = TEST_CONFIG.TIMEOUTS.API_REQUEST
) => {
  return page.waitForResponse((response: any) => response.url().includes("/api/options/"), {
    timeout,
  });
};

export const fillSymbolInput = async (page: any, symbol: string) => {
  await page.fill(SELECTORS.SYMBOL_INPUT, symbol);
};

export const clickLoadButton = async (page: any) => {
  await page.click(SELECTORS.LOAD_BUTTON);
};

export const waitForOptionsTable = async (page: any) => {
  await page.waitForSelector(SELECTORS.OPTIONS_TABLE, {
    timeout: TEST_CONFIG.TIMEOUTS.ELEMENT_WAIT,
  });
};

export const waitForLoadingToComplete = async (page: any) => {
  // Wait for loading spinner to disappear
  await page.waitForSelector(SELECTORS.LOADING_SPINNER, {
    state: "hidden",
    timeout: TEST_CONFIG.TIMEOUTS.ELEMENT_WAIT,
  });
};

// Test data for specific scenarios
export const TEST_SCENARIOS = {
  BASIC_OPTIONS_CHAIN: {
    symbol: "SPY",
    expectedExpirations: 3,
    expectedContracts: 30,
  },
  SMALL_OPTIONS_CHAIN: {
    symbol: "OPTT",
    expectedExpirations: 1,
    expectedContracts: 2,
  },
  INVALID_SYMBOL: {
    symbol: "INVALID",
    expectedError: "No fixture data available",
  },
} as const;
