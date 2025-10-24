export type OrderSide = "buy" | "sell";
export type OrderType = "market" | "limit" | "stop" | "stop_limit";
export type OrderClass = "simple" | "bracket" | "oco";
export type AssetClass = "stock" | "option";

export interface TakeProfitDraft {
  limitPrice: number;
}

export interface StopLossDraft {
  stopPrice: number;
  limitPrice?: number | null;
}

export interface OrderDraft {
  symbol: string;
  side: OrderSide;
  quantity: number;
  orderType: OrderType;
  limitPrice?: number;
  assetClass: AssetClass;
  optionType?: "call" | "put";
  strikePrice?: number;
  expirationDate?: string;
  orderClass: OrderClass;
  takeProfit?: TakeProfitDraft | null;
  stopLoss?: StopLossDraft | null;
  trailPrice?: number | null;
  trailPercent?: number | null;
  estimatedPrice?: number | null;
}

export interface OrderPayload {
  symbol: string;
  side: OrderSide;
  qty: number;
  type: OrderType;
  limit_price?: number;
  asset_class?: AssetClass;
  option_type?: "call" | "put";
  strike_price?: number;
  expiration_date?: string;
  order_class?: OrderClass;
  take_profit?: { limit_price: number } | null;
  stop_loss?: { stop_price: number; limit_price?: number | null } | null;
  trail_price?: number | null;
  trail_percent?: number | null;
  estimated_price?: number | null;
}

export interface OrderTemplateResponse {
  id: number;
  user_id?: number | null;
  name: string;
  description?: string | null;
  symbol: string;
  side: OrderSide;
  quantity: number;
  order_type: OrderType;
  limit_price?: number | null;
  asset_class: AssetClass;
  option_type?: "call" | "put" | null;
  strike_price?: number | null;
  expiration_date?: string | null;
  order_class: OrderClass;
  take_profit?: { limit_price: number } | null;
  stop_loss?: { stop_price: number; limit_price?: number | null } | null;
  trail_price?: number | null;
  trail_percent?: number | null;
  created_at: string;
  updated_at: string;
  last_used_at?: string | null;
}

export interface OrderTemplatePayload {
  name: string;
  description?: string | null;
  symbol: string;
  side: OrderSide;
  quantity: number;
  order_type: OrderType;
  limit_price?: number | null;
  asset_class: AssetClass;
  option_type?: "call" | "put";
  strike_price?: number | null;
  expiration_date?: string | null;
  order_class: OrderClass;
  take_profit?: { limit_price: number } | null;
  stop_loss?: { stop_price: number; limit_price?: number | null } | null;
  trail_price?: number | null;
  trail_percent?: number | null;
}

export interface OrderPreviewBreakdown {
  symbol: string;
  side: OrderSide;
  quantity: number;
  order_type: OrderType;
  order_class: OrderClass;
  entry_price: number | null;
  notional: number | null;
  take_profit_price: number | null;
  stop_loss_price: number | null;
  max_profit: number | null;
  max_loss: number | null;
  risk_reward_ratio: number | null;
}

export interface OrderPreviewResponse {
  total_notional: number;
  total_max_profit: number;
  total_max_loss: number;
  orders: OrderPreviewBreakdown[];
}
