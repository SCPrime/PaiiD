/**
 * Type Guards and Runtime Validation Utilities
 *
 * Provides runtime type checking to complement TypeScript's compile-time type safety.
 * Use these guards when validating data from external sources (API responses, localStorage, etc.)
 */

import type {
  AlpacaAccount,
  AlpacaPosition,
  AlpacaOrder,
  AlpacaAsset,
  AlpacaBar,
  AlpacaClock,
  AlpacaCalendar,
  AlpacaWatchlist
} from './alpaca';

import type {
  WebSocketMessage,
  MarketData,
  PortfolioUpdate,
  PositionUpdate,
  TradingAlert
} from '../hooks/useWebSocket';

import type { User, Session } from './userManagement';
import type { TradeRecord, StrategyPerformance } from './tradeHistory';

/**
 * Generic type guard helper for objects
 */
function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Generic type guard helper for arrays
 */
function isArray(value: unknown): value is unknown[] {
  return Array.isArray(value);
}

/**
 * Type guard for AlpacaAccount
 */
export function isAlpacaAccount(obj: unknown): obj is AlpacaAccount {
  if (!isObject(obj)) return false;

  return (
    typeof obj.id === 'string' &&
    typeof obj.account_number === 'string' &&
    typeof obj.status === 'string' &&
    typeof obj.currency === 'string' &&
    typeof obj.buying_power === 'string' &&
    typeof obj.cash === 'string' &&
    typeof obj.portfolio_value === 'string' &&
    typeof obj.pattern_day_trader === 'boolean'
  );
}

/**
 * Type guard for AlpacaPosition
 */
export function isAlpacaPosition(obj: unknown): obj is AlpacaPosition {
  if (!isObject(obj)) return false;

  return (
    typeof obj.asset_id === 'string' &&
    typeof obj.symbol === 'string' &&
    typeof obj.qty === 'string' &&
    (obj.side === 'long' || obj.side === 'short') &&
    typeof obj.market_value === 'string' &&
    typeof obj.unrealized_pl === 'string'
  );
}

/**
 * Type guard for AlpacaOrder
 */
export function isAlpacaOrder(obj: unknown): obj is AlpacaOrder {
  if (!isObject(obj)) return false;

  return (
    typeof obj.id === 'string' &&
    typeof obj.symbol === 'string' &&
    (obj.side === 'buy' || obj.side === 'sell') &&
    typeof obj.status === 'string' &&
    typeof obj.filled_qty === 'string'
  );
}

/**
 * Type guard for AlpacaAsset
 */
export function isAlpacaAsset(obj: unknown): obj is AlpacaAsset {
  if (!isObject(obj)) return false;

  return (
    typeof obj.id === 'string' &&
    typeof obj.symbol === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.tradable === 'boolean'
  );
}

/**
 * Type guard for AlpacaBar
 */
export function isAlpacaBar(obj: unknown): obj is AlpacaBar {
  if (!isObject(obj)) return false;

  return (
    typeof obj.t === 'string' &&
    typeof obj.o === 'number' &&
    typeof obj.h === 'number' &&
    typeof obj.l === 'number' &&
    typeof obj.c === 'number' &&
    typeof obj.v === 'number'
  );
}

/**
 * Type guard for AlpacaClock
 */
export function isAlpacaClock(obj: unknown): obj is AlpacaClock {
  if (!isObject(obj)) return false;

  return (
    typeof obj.timestamp === 'string' &&
    typeof obj.is_open === 'boolean' &&
    typeof obj.next_open === 'string' &&
    typeof obj.next_close === 'string'
  );
}

/**
 * Type guard for AlpacaCalendar
 */
export function isAlpacaCalendar(obj: unknown): obj is AlpacaCalendar {
  if (!isObject(obj)) return false;

  return (
    typeof obj.date === 'string' &&
    typeof obj.open === 'string' &&
    typeof obj.close === 'string'
  );
}

/**
 * Type guard for AlpacaWatchlist
 */
export function isAlpacaWatchlist(obj: unknown): obj is AlpacaWatchlist {
  if (!isObject(obj)) return false;

  return (
    typeof obj.id === 'string' &&
    typeof obj.account_id === 'string' &&
    typeof obj.name === 'string' &&
    typeof obj.created_at === 'string'
  );
}

/**
 * Type guard for WebSocketMessage
 */
export function isWebSocketMessage(obj: unknown): obj is WebSocketMessage {
  if (!isObject(obj)) return false;

  return (
    typeof obj.type === 'string' &&
    typeof obj.timestamp === 'string'
  );
}

/**
 * Type guard for MarketData
 */
export function isMarketData(obj: unknown): obj is MarketData {
  if (!isObject(obj)) return false;

  return (
    typeof obj.symbol === 'string' &&
    typeof obj.price === 'number' &&
    typeof obj.change === 'number' &&
    typeof obj.volume === 'number' &&
    typeof obj.timestamp === 'string'
  );
}

/**
 * Type guard for PortfolioUpdate
 */
export function isPortfolioUpdate(obj: unknown): obj is PortfolioUpdate {
  if (!isObject(obj)) return false;

  return (
    typeof obj.total_value === 'number' &&
    typeof obj.total_change === 'number' &&
    isArray(obj.positions)
  );
}

/**
 * Type guard for PositionUpdate
 */
export function isPositionUpdate(obj: unknown): obj is PositionUpdate {
  if (!isObject(obj)) return false;

  return (
    typeof obj.symbol === 'string' &&
    typeof obj.quantity === 'number' &&
    typeof obj.current_price === 'number' &&
    typeof obj.market_value === 'number' &&
    typeof obj.timestamp === 'string'
  );
}

/**
 * Type guard for TradingAlert
 */
export function isTradingAlert(obj: unknown): obj is TradingAlert {
  if (!isObject(obj)) return false;

  const validTypes = ['price_alert', 'volume_alert', 'news_alert', 'system_alert'];
  const validSeverities = ['info', 'warning', 'error', 'success'];

  return (
    validTypes.includes(obj.type as string) &&
    typeof obj.message === 'string' &&
    validSeverities.includes(obj.severity as string) &&
    typeof obj.timestamp === 'string'
  );
}

/**
 * Type guard for User
 */
export function isUser(obj: unknown): obj is User {
  if (!isObject(obj)) return false;

  return (
    typeof obj.userId === 'string' &&
    typeof obj.displayName === 'string' &&
    typeof obj.createdAt === 'string' &&
    typeof obj.lastActive === 'string' &&
    typeof obj.sessionCount === 'number' &&
    isObject(obj.preferences)
  );
}

/**
 * Type guard for Session
 */
export function isSession(obj: unknown): obj is Session {
  if (!isObject(obj)) return false;

  return (
    typeof obj.sessionId === 'string' &&
    typeof obj.userId === 'string' &&
    typeof obj.startedAt === 'string' &&
    typeof obj.lastActivity === 'string' &&
    typeof obj.pageViews === 'number' &&
    typeof obj.actionsCount === 'number'
  );
}

/**
 * Type guard for TradeRecord
 */
export function isTradeRecord(obj: unknown): obj is TradeRecord {
  if (!isObject(obj)) return false;

  return (
    typeof obj.id === 'string' &&
    typeof obj.userId === 'string' &&
    typeof obj.strategy_id === 'string' &&
    typeof obj.ticker === 'string' &&
    typeof obj.entered_at === 'string' &&
    typeof obj.entry_price === 'number' &&
    typeof obj.quantity === 'number' &&
    typeof obj.was_winner === 'boolean'
  );
}

/**
 * Type guard for StrategyPerformance
 */
export function isStrategyPerformance(obj: unknown): obj is StrategyPerformance {
  if (!isObject(obj)) return false;

  return (
    typeof obj.strategy_id === 'string' &&
    typeof obj.total_trades === 'number' &&
    typeof obj.winning_trades === 'number' &&
    typeof obj.losing_trades === 'number' &&
    typeof obj.win_rate === 'number' &&
    typeof obj.sharpe_ratio === 'number'
  );
}

/**
 * Safe JSON parser with type guard validation
 * @param json - JSON string to parse
 * @param validator - Type guard function to validate the parsed result
 * @returns Typed result if validation passes, null otherwise
 */
export function safeJsonParse<T>(
  json: string,
  validator: (obj: unknown) => obj is T
): T | null {
  try {
    const parsed: unknown = JSON.parse(json);
    return validator(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

/**
 * Safe localStorage getter with type validation
 * @param key - Storage key
 * @param validator - Type guard function to validate the stored value
 * @returns Typed result if validation passes, null otherwise
 */
export function safeLocalStorageGet<T>(
  key: string,
  validator: (obj: unknown) => obj is T
): T | null {
  try {
    const item = localStorage.getItem(key);
    if (!item) return null;
    return safeJsonParse(item, validator);
  } catch {
    return null;
  }
}

/**
 * Safe sessionStorage getter with type validation
 * @param key - Storage key
 * @param validator - Type guard function to validate the stored value
 * @returns Typed result if validation passes, null otherwise
 */
export function safeSessionStorageGet<T>(
  key: string,
  validator: (obj: unknown) => obj is T
): T | null {
  try {
    const item = sessionStorage.getItem(key);
    if (!item) return null;
    return safeJsonParse(item, validator);
  } catch {
    return null;
  }
}

/**
 * Array type guard helper
 * Validates that an array contains only items of a specific type
 */
export function isArrayOf<T>(
  arr: unknown,
  itemValidator: (item: unknown) => item is T
): arr is T[] {
  return isArray(arr) && arr.every(itemValidator);
}

/**
 * Validate API response structure
 */
export function isApiResponse<T>(
  obj: unknown,
  dataValidator: (data: unknown) => data is T
): obj is { data: T; timestamp: string; status: 'success' | 'error' } {
  if (!isObject(obj)) return false;

  return (
    'data' in obj &&
    dataValidator(obj.data) &&
    typeof obj.timestamp === 'string' &&
    (obj.status === 'success' || obj.status === 'error')
  );
}
