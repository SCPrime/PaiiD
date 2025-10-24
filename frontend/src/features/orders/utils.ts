import {
  OrderDraft,
  OrderPayload,
  OrderTemplatePayload,
  OrderTemplateResponse,
} from "./types";

export function draftToOrderPayload(draft: OrderDraft): OrderPayload {
  return {
    symbol: draft.symbol.toUpperCase(),
    side: draft.side,
    qty: draft.quantity,
    type: draft.orderType,
    limit_price: draft.limitPrice ?? undefined,
    asset_class: draft.assetClass,
    option_type: draft.optionType ?? undefined,
    strike_price: draft.strikePrice ?? undefined,
    expiration_date: draft.expirationDate ?? undefined,
    order_class: draft.orderClass,
    take_profit: draft.takeProfit ? { limit_price: draft.takeProfit.limitPrice } : null,
    stop_loss: draft.stopLoss
      ? {
          stop_price: draft.stopLoss.stopPrice,
          limit_price: draft.stopLoss.limitPrice ?? undefined,
        }
      : null,
    trail_price: draft.trailPrice ?? null,
    trail_percent: draft.trailPercent ?? null,
    estimated_price: draft.estimatedPrice ?? null,
  };
}

export function templateToDraft(template: OrderTemplateResponse): OrderDraft {
  return {
    symbol: template.symbol,
    side: template.side,
    quantity: template.quantity,
    orderType: template.order_type,
    limitPrice: template.limit_price ?? undefined,
    assetClass: template.asset_class,
    optionType: template.option_type ?? undefined,
    strikePrice: template.strike_price ?? undefined,
    expirationDate: template.expiration_date ?? undefined,
    orderClass: template.order_class,
    takeProfit: template.take_profit
      ? { limitPrice: template.take_profit.limit_price }
      : null,
    stopLoss: template.stop_loss
      ? {
          stopPrice: template.stop_loss.stop_price,
          limitPrice: template.stop_loss.limit_price ?? null,
        }
      : null,
    trailPrice: template.trail_price ?? null,
    trailPercent: template.trail_percent ?? null,
    estimatedPrice: undefined,
  };
}

export function draftToTemplatePayload(
  draft: OrderDraft,
  name: string,
  description: string | null,
): OrderTemplatePayload {
  return {
    name,
    description,
    symbol: draft.symbol.toUpperCase(),
    side: draft.side,
    quantity: draft.quantity,
    order_type: draft.orderType,
    limit_price: draft.limitPrice ?? null,
    asset_class: draft.assetClass,
    option_type: draft.optionType ?? undefined,
    strike_price: draft.strikePrice ?? null,
    expiration_date: draft.expirationDate ?? null,
    order_class: draft.orderClass,
    take_profit: draft.takeProfit ? { limit_price: draft.takeProfit.limitPrice } : null,
    stop_loss: draft.stopLoss
      ? {
          stop_price: draft.stopLoss.stopPrice,
          limit_price: draft.stopLoss.limitPrice ?? undefined,
        }
      : null,
    trail_price: draft.trailPrice ?? null,
    trail_percent: draft.trailPercent ?? null,
  };
}
