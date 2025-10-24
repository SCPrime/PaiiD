"use client";
import { useState, useEffect, useMemo } from "react";
import { TrendingUp, Check, AlertCircle, ChevronDown } from "lucide-react";
import { Card, Button } from "./ui";
import { theme } from "../styles/theme";
import ConfirmDialog from "./ConfirmDialog";
import { addOrderToHistory } from "./OrderHistory";
import { showSuccess, showError, showWarning } from "../lib/toast";
import { useIsMobile } from "../hooks/useBreakpoint";
import { useWorkflow } from "../contexts/WorkflowContext";
import StockLookup from "./StockLookup";
import OptionsGreeksDisplay from "./OptionsGreeksDisplay";
import RiskCalculator from "./trading/RiskCalculator";

import { PreviewModal } from "@/src/features/orders/components/PreviewModal";
import { TemplateManager } from "@/src/features/orders/components/TemplateManager";
import { useOrderKeyboardShortcuts } from "@/src/features/orders/hooks/useOrderKeyboardShortcuts";
import {
  OrderDraft,
  OrderPayload,
  OrderTemplateResponse,
  OrderClass,
} from "@/src/features/orders/types";
import {
  draftToOrderPayload,
  draftToTemplatePayload,
  templateToDraft,
} from "@/src/features/orders/utils";

interface ExecuteResponse {
  accepted: boolean;
  duplicate?: boolean;
  dryRun?: boolean;
  orders?: OrderPayload[];
}

export default function ExecuteTradeForm() {
  // Mobile detection
  const isMobile = useIsMobile();

  // Workflow context
  const { pendingNavigation, clearPendingNavigation } = useWorkflow();

  // Responsive sizing
  const responsiveSizes = {
    headerLogo: isMobile ? "32px" : "42px",
    iconSize: isMobile ? 24 : 32,
    titleSize: isMobile ? "20px" : "28px",
    inputPadding: isMobile ? "14px 16px" : "12px 16px",
    inputFontSize: "16px", // Always 16px to prevent iOS zoom
  };

  const [symbol, setSymbol] = useState("SPY");
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [qty, setQty] = useState(1);
  const [orderType, setOrderType] = useState<"market" | "limit">("market");
  const [limitPrice, setLimitPrice] = useState("");
  const [orderClass, setOrderClass] = useState<OrderClass>("simple");
  const [takeProfitPrice, setTakeProfitPrice] = useState("");
  const [stopLossPrice, setStopLossPrice] = useState("");
  const [stopLossLimitPrice, setStopLossLimitPrice] = useState("");
  const [trailPrice, setTrailPrice] = useState("");
  const [trailPercent, setTrailPercent] = useState("");
  const [estimatedPrice, setEstimatedPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<ExecuteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastRequestId, setLastRequestId] = useState<string | null>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [pendingOrder, setPendingOrder] = useState<OrderPayload | null>(null);
  const [showRawJson, setShowRawJson] = useState(false);

  // Template-related state
  const [templates, setTemplates] = useState<OrderTemplateResponse[]>([]);
  const [showTemplateCreator, setShowTemplateCreator] = useState(false);

  // Stock research state
  const [showStockLookup, setShowStockLookup] = useState(false);

  // Options trading state
  const [assetClass, setAssetClass] = useState<"stock" | "option">("stock");
  const [optionType, setOptionType] = useState<"call" | "put">("call");
  const [strikePrice, setStrikePrice] = useState<string>("");
  const [expirationDate, setExpirationDate] = useState<string>("");
  const [availableExpirations, setAvailableExpirations] = useState<string[]>([]);
  const [availableStrikes, setAvailableStrikes] = useState<number[]>([]);
  const [loadingOptionsChain, setLoadingOptionsChain] = useState(false);

  const [showPreview, setShowPreview] = useState(false);
  const [previewOrders, setPreviewOrders] = useState<OrderPayload[]>([]);

  // AI Analysis state
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);

  const currentDraft = useMemo<OrderDraft>(() => {
    const toNumber = (value: string) => {
      const parsed = parseFloat(value);
      return Number.isNaN(parsed) ? undefined : parsed;
    };

    const limit = toNumber(limitPrice);
    const tp = toNumber(takeProfitPrice);
    const sl = toNumber(stopLossPrice);
    const slLimit = toNumber(stopLossLimitPrice);
    const trailingPrice = toNumber(trailPrice);
    const trailingPercent = toNumber(trailPercent);
    const estPrice = toNumber(estimatedPrice);

    const draft: OrderDraft = {
      symbol,
      side,
      quantity: qty,
      orderType,
      limitPrice: limit,
      assetClass,
      orderClass,
      takeProfit: tp ? { limitPrice: tp } : null,
      stopLoss: sl
        ? {
            stopPrice: sl,
            limitPrice: slLimit ?? null,
          }
        : null,
      trailPrice: trailingPrice ?? null,
      trailPercent: trailingPercent ?? null,
      estimatedPrice: estPrice ?? null,
    };

    if (assetClass === "option") {
      draft.optionType = optionType;
      const strike = toNumber(strikePrice);
      if (strike) draft.strikePrice = strike;
      if (expirationDate) draft.expirationDate = expirationDate;
    }

    return draft;
  }, [
    symbol,
    side,
    qty,
    orderType,
    limitPrice,
    assetClass,
    optionType,
    strikePrice,
    expirationDate,
    orderClass,
    takeProfitPrice,
    stopLossPrice,
    stopLossLimitPrice,
    trailPrice,
    trailPercent,
    estimatedPrice,
  ]);

  // Load templates on mount
  useEffect(() => {
    loadTemplates();
  }, []);

  // Consume pre-filled data from workflow navigation
  useEffect(() => {
    if (
      pendingNavigation &&
      pendingNavigation.workflow === "execute-trade" &&
      pendingNavigation.tradeData
    ) {
      const { tradeData } = pendingNavigation;

      // eslint-disable-next-line no-console
      console.info("[ExecuteTradeForm] Pre-filling form with trade data:", tradeData);

      // Pre-fill form fields
      if (tradeData.symbol) setSymbol(tradeData.symbol);
      if (tradeData.side) setSide(tradeData.side);
      if (tradeData.quantity && tradeData.quantity > 0) setQty(tradeData.quantity);

      // Set order type and price based on available data
      if (tradeData.entryPrice && tradeData.entryPrice > 0) {
        setOrderType("limit");
        setLimitPrice(tradeData.entryPrice.toString());
      } else if (
        tradeData.orderType &&
        (tradeData.orderType === "market" || tradeData.orderType === "limit")
      ) {
        // Only use orderType if it's supported (market or limit)
        setOrderType(tradeData.orderType);
        if (tradeData.orderType === "limit" && tradeData.entryPrice) {
          setLimitPrice(tradeData.entryPrice.toString());
        }
      }

      // Show success toast
      showSuccess(
        `✅ Pre-filled trade data for ${tradeData.symbol}${tradeData.entryPrice ? ` at $${tradeData.entryPrice.toFixed(2)}` : ""}`
      );

      // Clear the pending navigation
      clearPendingNavigation();
    }
  }, [pendingNavigation, clearPendingNavigation]);

  const loadTemplates = async () => {
    try {
      const res = await fetch("/api/proxy/api/order-templates");
      if (res.ok) {
        const data = await res.json();
        setTemplates(data);
      }
    } catch (err) {
      console.error("Failed to load templates:", err);
    }
  };

  // Fetch available expiration dates when symbol changes (for options mode)
  const fetchExpirations = async (sym: string) => {
    if (!sym || sym.trim() === "" || assetClass !== "option") return;

    setLoadingOptionsChain(true);
    try {
      const response = await fetch(`/api/proxy/api/options/chain?symbol=${sym.toUpperCase()}`);
      if (response.ok) {
        const data = await response.json();
        setAvailableExpirations(data.expirations || []);
        if (data.expirations && data.expirations.length > 0) {
          setExpirationDate(data.expirations[0]); // Auto-select first expiration
        }
      }
    } catch (err) {
      console.error("Failed to fetch expirations:", err);
    } finally {
      setLoadingOptionsChain(false);
    }
  };

  // Fetch available strikes when expiration changes
  const fetchStrikes = async (sym: string, expiry: string) => {
    if (!sym || !expiry || assetClass !== "option") return;

    setLoadingOptionsChain(true);
    try {
      const response = await fetch(
        `/api/proxy/api/options/chain?symbol=${sym.toUpperCase()}&expiration=${expiry}`
      );
      if (response.ok) {
        const data = await response.json();
        setAvailableStrikes(data.strikes || []);
        if (data.strikes && data.strikes.length > 0) {
          // Auto-select strike closest to ATM
          const middleIndex = Math.floor(data.strikes.length / 2);
          setStrikePrice(data.strikes[middleIndex].toString());
        }
      }
    } catch (err) {
      console.error("Failed to fetch strikes:", err);
    } finally {
      setLoadingOptionsChain(false);
    }
  };

  // Fetch expirations when symbol or asset class changes
  useEffect(() => {
    if (assetClass === "option" && symbol.trim()) {
      fetchExpirations(symbol);
    }
  }, [symbol, assetClass]);

  // Fetch strikes when expiration changes
  useEffect(() => {
    if (assetClass === "option" && symbol.trim() && expirationDate) {
      fetchStrikes(symbol, expirationDate);
    }
  }, [expirationDate]);

  // Debounced AI analysis when symbol changes
  useEffect(() => {
    // Reset AI state if symbol is empty or invalid
    if (!symbol || symbol.trim() === "" || symbol.trim().length < 1) {
      setAiAnalysis(null);
      setAiError(null);
      return;
    }

    // Debounce: Wait 800ms after user stops typing
    const timeoutId = setTimeout(async () => {
      await fetchAIAnalysis(symbol.trim().toUpperCase());
    }, 800);

    return () => clearTimeout(timeoutId);
  }, [symbol]); // Re-run when symbol changes

  const fetchAIAnalysis = async (sym: string) => {
    setAiLoading(true);
    setAiError(null);

    try {
      const apiToken = process.env.NEXT_PUBLIC_API_TOKEN;

      const response = await fetch(`/api/proxy/api/ai/analyze-symbol/${sym}`, {
        headers: {
          'Authorization': `Bearer ${apiToken}`
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Symbol ${sym} not found`);
        } else if (response.status === 400) {
          throw new Error(`Insufficient data for ${sym}`);
        } else {
          throw new Error(`${response.status} ${response.statusText}`);
        }
      }

      const data = await response.json();
      setAiAnalysis(data);
    } catch (err: any) {
      console.error("AI analysis error:", err);
      setAiError(err.message || "Failed to load AI analysis");
      setAiAnalysis(null);
    } finally {
      setAiLoading(false);
    }
  };

  const applyTemplate = (template: OrderTemplateResponse) => {
    setSymbol(template.symbol);
    setSide(template.side);
    setQty(template.quantity);
    setOrderType(template.order_type);
    setLimitPrice(template.limit_price ? template.limit_price.toString() : "");
    setOrderClass(template.order_class);
    setAssetClass(template.asset_class);
    setTakeProfitPrice(
      template.take_profit?.limit_price ? template.take_profit.limit_price.toString() : ""
    );
    setStopLossPrice(
      template.stop_loss?.stop_price ? template.stop_loss.stop_price.toString() : ""
    );
    setStopLossLimitPrice(
      template.stop_loss?.limit_price ? template.stop_loss.limit_price.toString() : ""
    );
    setTrailPrice(template.trail_price ? template.trail_price.toString() : "");
    setTrailPercent(template.trail_percent ? template.trail_percent.toString() : "");
    setEstimatedPrice("");

    if (template.asset_class === "option") {
      setOptionType(template.option_type ?? "call");
      setStrikePrice(template.strike_price ? template.strike_price.toString() : "");
      setExpirationDate(template.expiration_date ?? "");
    } else {
      setOptionType("call");
      setStrikePrice("");
      setExpirationDate("");
    }

    showSuccess(`✅ Template "${template.name}" loaded`);

    fetch(`/api/proxy/api/order-templates/${template.id}/use`, {
      method: "POST",
    }).catch((err) => console.error("Failed to mark template as used:", err));
  };

  const saveTemplateFromDraft = async (name: string, description: string | null) => {
    const validationError = validateDraft();
    if (validationError) {
      showError(`❌ Cannot save template: ${validationError}`);
      throw new Error(validationError);
    }

    const payload = draftToTemplatePayload(currentDraft, name, description);

    const res = await fetch("/api/proxy/api/order-templates", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const message = `${res.status} ${res.statusText}`;
      showError(`❌ Failed to save template: ${message}`);
      throw new Error(message);
    }

    const newTemplate: OrderTemplateResponse = await res.json();
    setTemplates((prev) => [...prev, newTemplate]);
    showSuccess(`✅ Template "${newTemplate.name}" saved`);
  };

  const deleteTemplate = async (templateId: number) => {
    if (!confirm("Are you sure you want to delete this template?")) return;

    try {
      const res = await fetch(`/api/proxy/api/order-templates/${templateId}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);

      setTemplates((prev) => prev.filter((t) => t.id !== templateId));
      showSuccess("✅ Template deleted");
    } catch (err: any) {
      showError(`❌ Failed to delete template: ${err.message}`);
    }
  };

  const generateRequestId = () =>
    `req-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;

  const validateDraft = (): string | null => {
    if (!symbol || symbol.trim() === "") {
      return "Symbol is required";
    }
    if (qty <= 0) {
      return "Quantity must be greater than 0";
    }
    if (orderType === "limit") {
      const limit = parseFloat(limitPrice);
      if (!limit || limit <= 0) {
        return "Limit price is required for limit orders";
      }
    }

    if (assetClass === "option") {
      if (!optionType) {
        return "Option type (call/put) is required";
      }
      const strike = parseFloat(strikePrice);
      if (!strike || strike <= 0) {
        return "Strike price is required for options";
      }
      if (!expirationDate) {
        return "Expiration date is required for options";
      }
    }

    const tp = takeProfitPrice ? parseFloat(takeProfitPrice) : undefined;
    const sl = stopLossPrice ? parseFloat(stopLossPrice) : undefined;
    const slLimit = stopLossLimitPrice ? parseFloat(stopLossLimitPrice) : undefined;
    const trailingP = trailPrice ? parseFloat(trailPrice) : undefined;
    const trailingPct = trailPercent ? parseFloat(trailPercent) : undefined;

    if (orderClass === "bracket" && !tp && !sl) {
      return "Bracket orders require a take-profit or stop-loss";
    }

    if (orderClass === "oco" && (!tp || !sl)) {
      return "OCO orders require both take-profit and stop-loss";
    }

    if (trailPrice && trailPercent) {
      return "Choose either trailing price or trailing percent";
    }

    if (tp !== undefined && tp <= 0) {
      return "Take-profit price must be greater than 0";
    }

    if (sl !== undefined && sl <= 0) {
      return "Stop-loss price must be greater than 0";
    }

    if (slLimit !== undefined && sl !== undefined && slLimit < sl) {
      return "Stop-loss limit must be greater than or equal to stop price";
    }

    if (trailingP !== undefined && trailingP <= 0) {
      return "Trail price must be greater than 0";
    }

    if (trailingPct !== undefined && (trailingPct <= 0 || trailingPct > 100)) {
      return "Trail percent must be between 0 and 100";
    }

    if (estimatedPrice) {
      const estimated = parseFloat(estimatedPrice);
      if (!estimated || estimated <= 0) {
        return "Estimated price must be greater than 0";
      }
    }

    return null;
  };

  const reviewOrder = () => {
    const validationError = validateDraft();
    if (validationError) {
      setError(validationError);
      showError(`❌ ${validationError}`);
      return;
    }

    const orderPayload = draftToOrderPayload(currentDraft);
    setPendingOrder(orderPayload);
    setShowConfirmDialog(true);
  };

  const openPreviewModal = () => {
    const validationError = validateDraft();
    if (validationError) {
      setError(validationError);
      showError(`❌ ${validationError}`);
      return;
    }

    const orderPayload = draftToOrderPayload(currentDraft);
    setPreviewOrders([orderPayload]);
    setShowPreview(true);
  };

  useOrderKeyboardShortcuts({
    onPreview: openPreviewModal,
    onSubmit: reviewOrder,
    onSaveTemplate: () => setShowTemplateCreator(true),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    reviewOrder();
  };

  const executeOrder = async () => {
    if (!pendingOrder) return;

    setShowConfirmDialog(false);
    setLoading(true);
    setError(null);
    setResponse(null);

    const requestId = generateRequestId();
    setLastRequestId(requestId);

    const body = {
      dryRun: false, // Paper trading via Alpaca
      requestId,
      orders: [pendingOrder],
    };

    try {
      const res = await fetch("/api/proxy/trading/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error(`${res.status} ${res.statusText}`);
      }

      const data: ExecuteResponse = await res.json();
      setResponse(data);

      // Show appropriate toast
      if (data.duplicate) {
        showWarning(`⚠️ Duplicate request detected - Order not resubmitted`);
      } else if (data.accepted) {
        showSuccess(
          `✅ ${pendingOrder.side.toUpperCase()} order accepted (Dry-Run): ${pendingOrder.qty} ${pendingOrder.asset_class === "option" ? "contracts" : "shares"} of ${pendingOrder.symbol}`
        );
      }

      // Add to order history
      addOrderToHistory({
        symbol: pendingOrder.symbol,
        side: pendingOrder.side,
        qty: pendingOrder.qty,
        type: pendingOrder.type,
        limitPrice: pendingOrder.limit_price ?? undefined,
        status: data.accepted ? "executed" : "cancelled",
        dryRun: false,
      });
    } catch (err: any) {
      setError(err.message);
      showError(`❌ Order failed: ${err.message}`);
    } finally {
      setLoading(false);
      setPendingOrder(null);
    }
  };

  const testDuplicate = async () => {
    if (!lastRequestId) {
      setError("No previous request to duplicate. Submit a new order first.");
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    const order = draftToOrderPayload(currentDraft);

    const body = {
      dryRun: false, // Paper trading via Alpaca
      requestId: lastRequestId, // Re-use same ID
      orders: [order],
    };

    try {
      const res = await fetch("/api/proxy/trading/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error(`${res.status} ${res.statusText}`);
      }

      const data: ExecuteResponse = await res.json();
      setResponse(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getConfirmMessage = () => {
    if (!pendingOrder) return "";

    const priceStr =
      pendingOrder.type === "limit" && pendingOrder.limit_price
        ? ` at $${pendingOrder.limit_price.toFixed(2)}`
        : " at market price";

    if (pendingOrder.asset_class === "option") {
      return `${pendingOrder.side.toUpperCase()} ${pendingOrder.qty} ${pendingOrder.symbol} $${pendingOrder.strike_price} ${pendingOrder.option_type?.toUpperCase()} (exp: ${pendingOrder.expiration_date})${priceStr}?`;
    }

    return `${pendingOrder.side.toUpperCase()} ${pendingOrder.qty} shares of ${pendingOrder.symbol}${priceStr}?`;
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return { bg: 'rgba(16, 185, 129, 0.2)', border: theme.colors.primary, text: theme.colors.primary };
    if (score >= 60) return { bg: 'rgba(255, 136, 0, 0.2)', border: theme.colors.warning, text: theme.colors.warning };
    return { bg: 'rgba(255, 68, 68, 0.2)', border: theme.colors.danger, text: theme.colors.danger };
  };

  const getMomentumColor = (momentum: string) => {
    if (momentum.toLowerCase().includes('bullish')) return theme.colors.primary;
    if (momentum.toLowerCase().includes('bearish')) return theme.colors.danger;
    return theme.colors.textMuted;
  };

  const getMomentumIcon = (momentum: string) => {
    if (momentum.toLowerCase().includes('strong bullish')) return '🚀';
    if (momentum.toLowerCase().includes('bullish')) return '📈';
    if (momentum.toLowerCase().includes('bearish')) return '📉';
    if (momentum.toLowerCase().includes('strong bearish')) return '⬇️';
    return '➡️';
  };

  const getTrendIcon = (trend: string) => {
    if (trend.toLowerCase().includes('uptrend')) return '📊';
    if (trend.toLowerCase().includes('downtrend')) return '📉';
    return '➖';
  };

  return (
    <>
      <style jsx>{`
        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
      <PreviewModal
        open={showPreview}
        orders={previewOrders}
        onClose={() => setShowPreview(false)}
      />
      <ConfirmDialog
        isOpen={showConfirmDialog}
        title="Confirm Order"
        message={getConfirmMessage()}
        confirmText="Execute Order"
        cancelText="Cancel"
        confirmVariant={pendingOrder?.side === "sell" ? "danger" : "primary"}
        onConfirm={executeOrder}
        onCancel={() => {
          setShowConfirmDialog(false);
          setPendingOrder(null);
        }}
      />

      <div style={{ padding: theme.spacing.lg }}>
        <Card glow="green">
          {/* Header with PaiiD Logo */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: theme.spacing.md,
              marginBottom: theme.spacing.xl,
              flexWrap: isMobile ? "wrap" : "nowrap",
            }}
          >
            {/* PaiiD Logo */}
            <div
              style={{ fontSize: responsiveSizes.headerLogo, fontWeight: "900", lineHeight: "1" }}
            >
              <span
                style={{
                  background: "linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  filter: "drop-shadow(0 3px 8px rgba(26, 117, 96, 0.4))",
                }}
              >
                P
              </span>
              <span
                style={{
                  background: "linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  textShadow: "0 0 18px rgba(69, 240, 192, 0.8), 0 0 36px rgba(69, 240, 192, 0.4)",
                  animation: "glow-ai 3s ease-in-out infinite",
                }}
              >
                aii
              </span>
              <span
                style={{
                  background: "linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  filter: "drop-shadow(0 3px 8px rgba(26, 117, 96, 0.4))",
                }}
              >
                D
              </span>
            </div>

            <div
              style={{
                padding: theme.spacing.md,
                background: "rgba(16, 185, 129, 0.1)",
                borderRadius: theme.borderRadius.lg,
                border: "1px solid rgba(16, 185, 129, 0.2)",
              }}
            >
              <TrendingUp
                style={{
                  width: responsiveSizes.iconSize,
                  height: responsiveSizes.iconSize,
                  color: theme.colors.primary,
                }}
              />
            </div>
            <div>
              <h1
                style={{
                  margin: 0,
                  fontSize: responsiveSizes.titleSize,
                  fontWeight: "700",
                  color: theme.colors.text,
                }}
              >
                Execute Trade
              </h1>
              <p
                style={{
                  margin: 0,
                  marginTop: "4px",
                  color: theme.colors.textMuted,
                  fontSize: "14px",
                }}
              >
                Place orders with dry-run mode enabled
              </p>
            </div>
          </div>

          <TemplateManager
            templates={templates}
            onApplyTemplate={applyTemplate}
            onCreateTemplate={saveTemplateFromDraft}
            onDeleteTemplate={deleteTemplate}
            onRefresh={loadTemplates}
            busy={loading}
            createOpen={showTemplateCreator}
            onCreateOpenChange={setShowTemplateCreator}
          />

          {/* Asset Class Toggle (Stock vs Options) */}
          <div
            style={{
              marginBottom: theme.spacing.xl,
              padding: theme.spacing.lg,
              background: theme.background.input,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.lg,
            }}
          >
            <label
              style={{
                display: "block",
                fontSize: "14px",
                fontWeight: "600",
                color: theme.colors.textMuted,
                marginBottom: theme.spacing.md,
              }}
            >
              Asset Type
            </label>
            <div style={{ display: "flex", gap: theme.spacing.sm }}>
              <button
                type="button"
                onClick={() => setAssetClass("stock")}
                style={{
                  flex: 1,
                  padding: "12px",
                  background: assetClass === "stock" ? theme.colors.primary : theme.background.card,
                  border: `2px solid ${assetClass === "stock" ? theme.colors.primary : theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                  color: assetClass === "stock" ? "#0f172a" : theme.colors.text,
                  fontSize: "14px",
                  fontWeight: "600",
                  cursor: "pointer",
                  transition: theme.transitions.normal,
                }}
              >
                Stock
              </button>
              <button
                type="button"
                onClick={() => setAssetClass("option")}
                style={{
                  flex: 1,
                  padding: "12px",
                  background:
                    assetClass === "option" ? theme.colors.primary : theme.background.card,
                  border: `2px solid ${assetClass === "option" ? theme.colors.primary : theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                  color: assetClass === "option" ? "#0f172a" : theme.colors.text,
                  fontSize: "14px",
                  fontWeight: "600",
                  cursor: "pointer",
                  transition: theme.transitions.normal,
                }}
              >
                Options
              </button>
            </div>
          </div>

          {/* Form */}
          <form
            onSubmit={handleSubmit}
            style={{ display: "flex", flexDirection: "column", gap: theme.spacing.xl }}
          >
            {/* Form Grid */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: isMobile ? "1fr" : "1fr 1fr",
                gap: theme.spacing.xl,
              }}
            >
              {/* Symbol */}
              <div>
                <label
                  style={{
                    display: "block",
                    fontSize: "14px",
                    fontWeight: "600",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm,
                  }}
                >
                  Symbol
                </label>
                <div style={{ display: "flex", gap: theme.spacing.sm }}>
                  <input
                    type="text"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    placeholder="SPY, AAPL, QQQ..."
                    disabled={loading}
                    required
                    style={{
                      flex: 1,
                      padding: responsiveSizes.inputPadding,
                      background: theme.background.input,
                      border: `1px solid ${theme.colors.border}`,
                      borderRadius: theme.borderRadius.md,
                      color: theme.colors.text,
                      fontSize: responsiveSizes.inputFontSize,
                      transition: theme.transitions.normal,
                      opacity: loading ? 0.5 : 1,
                    }}
                  />
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => {
                      if (symbol.trim()) {
                        setShowStockLookup(!showStockLookup);
                      } else {
                        showWarning("⚠️ Enter a symbol first");
                      }
                    }}
                    disabled={loading}
                    style={{
                      padding: isMobile ? "12px" : "12px 16px",
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                    }}
                  >
                    <Search size={18} />
                    {!isMobile && <span>Research</span>}
                  </Button>
                </div>
              </div>

              {/* AI Analysis Section */}
              {symbol.trim() && (
                <div style={{
                  marginTop: theme.spacing.md,
                  padding: theme.spacing.lg,
                  background: aiAnalysis ? theme.background.input : 'rgba(30, 41, 59, 0.3)',
                  border: `1px solid ${aiAnalysis ? theme.colors.primary : theme.colors.border}`,
                  borderRadius: theme.borderRadius.lg,
                  boxShadow: aiAnalysis ? '0 0 15px rgba(69, 240, 192, 0.2)' : 'none',
                  transition: 'all 0.3s ease',
                }}>
                  {/* Loading State */}
                  {aiLoading && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: theme.spacing.sm,
                      color: theme.colors.textMuted,
                      fontSize: '14px'
                    }}>
                      <div style={{
                        animation: 'spin 1s linear infinite',
                        display: 'inline-block'
                      }}>⏳</div>
                      <span>Analyzing {symbol.toUpperCase()} with PaπD AI...</span>
                    </div>
                  )}

                  {/* Error State */}
                  {aiError && !aiLoading && (
                    <div style={{
                      color: theme.colors.danger,
                      fontSize: '13px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: theme.spacing.sm
                    }}>
                      <span>⚠️</span>
                      <span>AI analysis unavailable: {aiError}</span>
                    </div>
                  )}

                  {/* AI Analysis Display */}
                  {aiAnalysis && !aiLoading && (
                    <div>
                      {/* Header with Risk Score Badge */}
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        marginBottom: theme.spacing.md,
                        flexWrap: isMobile ? 'wrap' : 'nowrap',
                        gap: theme.spacing.sm
                      }}>
                        <h4 style={{
                          margin: 0,
                          fontSize: '16px',
                          fontWeight: '600',
                          color: theme.colors.text,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px'
                        }}>
                          <span>🤖</span>
                          <span>PaπD AI Analysis</span>
                        </h4>

                        {/* Confidence Score Badge */}
                        <div style={{
                          padding: '6px 12px',
                          background: getRiskColor(aiAnalysis.confidence_score).bg,
                          border: `2px solid ${getRiskColor(aiAnalysis.confidence_score).border}`,
                          borderRadius: theme.borderRadius.sm,
                          fontSize: '13px',
                          fontWeight: '700',
                          color: getRiskColor(aiAnalysis.confidence_score).text,
                          whiteSpace: 'nowrap'
                        }}>
                          Confidence: {aiAnalysis.confidence_score.toFixed(1)}%
                        </div>
                      </div>

                      {/* Summary Banner */}
                      <div style={{
                        padding: theme.spacing.md,
                        background: theme.background.card,
                        borderRadius: theme.borderRadius.sm,
                        marginBottom: theme.spacing.md,
                        borderLeft: `4px solid ${theme.colors.primary}`,
                      }}>
                        <div style={{
                          fontSize: '13px',
                          color: theme.colors.text,
                          lineHeight: '1.5'
                        }}>
                          <strong style={{ color: theme.colors.primary }}>Summary:</strong> {aiAnalysis.summary}
                        </div>
                      </div>

                      {/* Key Metrics Grid */}
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
                        gap: theme.spacing.sm,
                        marginBottom: theme.spacing.md
                      }}>

                        {/* Current Price */}
                        <div style={{
                          padding: theme.spacing.sm,
                          background: theme.background.card,
                          borderRadius: theme.borderRadius.sm,
                          border: `1px solid ${theme.colors.border}`
                        }}>
                          <div style={{ fontSize: '11px', color: theme.colors.textMuted, marginBottom: '4px' }}>
                            Current Price
                          </div>
                          <div style={{ fontSize: '16px', fontWeight: '600', color: theme.colors.text }}>
                            ${aiAnalysis.current_price.toFixed(2)}
                          </div>
                        </div>

                        {/* Momentum */}
                        <div style={{
                          padding: theme.spacing.sm,
                          background: theme.background.card,
                          borderRadius: theme.borderRadius.sm,
                          border: `1px solid ${theme.colors.border}`
                        }}>
                          <div style={{ fontSize: '11px', color: theme.colors.textMuted, marginBottom: '4px' }}>
                            Momentum
                          </div>
                          <div style={{
                            fontSize: '14px',
                            fontWeight: '600',
                            color: getMomentumColor(aiAnalysis.momentum),
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px'
                          }}>
                            <span>{getMomentumIcon(aiAnalysis.momentum)}</span>
                            <span>{aiAnalysis.momentum}</span>
                          </div>
                        </div>

                        {/* Trend */}
                        <div style={{
                          padding: theme.spacing.sm,
                          background: theme.background.card,
                          borderRadius: theme.borderRadius.sm,
                          border: `1px solid ${theme.colors.border}`
                        }}>
                          <div style={{ fontSize: '11px', color: theme.colors.textMuted, marginBottom: '4px' }}>
                            Trend
                          </div>
                          <div style={{
                            fontSize: '14px',
                            fontWeight: '600',
                            color: theme.colors.text,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px'
                          }}>
                            <span>{getTrendIcon(aiAnalysis.trend)}</span>
                            <span>{aiAnalysis.trend}</span>
                          </div>
                        </div>

                        {/* Risk Assessment */}
                        <div style={{
                          padding: theme.spacing.sm,
                          background: theme.background.card,
                          borderRadius: theme.borderRadius.sm,
                          border: `1px solid ${theme.colors.border}`
                        }}>
                          <div style={{ fontSize: '11px', color: theme.colors.textMuted, marginBottom: '4px' }}>
                            Risk Level
                          </div>
                          <div style={{ fontSize: '13px', fontWeight: '600', color: theme.colors.text }}>
                            {aiAnalysis.risk_assessment.split(' - ')[0]}
                          </div>
                        </div>

                      </div>

                      {/* Support & Resistance Levels */}
                      <div style={{
                        padding: theme.spacing.md,
                        background: theme.background.card,
                        borderRadius: theme.borderRadius.sm,
                        marginBottom: theme.spacing.md,
                        border: `1px solid ${theme.colors.border}`
                      }}>
                        <div style={{ fontSize: '12px', fontWeight: '600', color: theme.colors.textMuted, marginBottom: theme.spacing.sm }}>
                          Key Levels
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', gap: theme.spacing.md }}>
                          <div>
                            <div style={{ fontSize: '11px', color: theme.colors.textMuted }}>Support</div>
                            <div style={{ fontSize: '15px', fontWeight: '600', color: theme.colors.success }}>
                              ${aiAnalysis.support_level.toFixed(2)}
                            </div>
                          </div>
                          <div>
                            <div style={{ fontSize: '11px', color: theme.colors.textMuted }}>Resistance</div>
                            <div style={{ fontSize: '15px', fontWeight: '600', color: theme.colors.danger }}>
                              ${aiAnalysis.resistance_level.toFixed(2)}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* AI Suggestions */}
                      <div style={{
                        padding: theme.spacing.md,
                        background: theme.background.card,
                        borderRadius: theme.borderRadius.sm,
                        fontSize: '12px',
                        color: theme.colors.textMuted,
                        lineHeight: '1.6',
                        borderLeft: `3px solid ${theme.colors.primary}`,
                      }}>
                        <div style={{ fontWeight: '600', color: theme.colors.text, marginBottom: '8px' }}>
                          💡 AI Entry Suggestion
                        </div>
                        <div>{aiAnalysis.entry_suggestion}</div>

                        {aiAnalysis.stop_loss_suggestion && (
                          <div style={{ marginTop: '8px', fontSize: '11px' }}>
                            <strong>Stop Loss:</strong> ${aiAnalysis.stop_loss_suggestion.toFixed(2)} |
                            <strong> Take Profit:</strong> ${aiAnalysis.take_profit_suggestion.toFixed(2)}
                          </div>
                        )}
                      </div>

                    </div>
                  )}
                </div>
              )}

              {/* Side */}
              <div>
                <label
                  style={{
                    display: "block",
                    fontSize: "14px",
                    fontWeight: "600",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm,
                  }}
                >
                  Side
                </label>
                <select
                  value={side}
                  onChange={(e) => setSide(e.target.value as "buy" | "sell")}
                  disabled={loading}
                  style={{
                    width: "100%",
                    padding: responsiveSizes.inputPadding,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: responsiveSizes.inputFontSize,
                    transition: theme.transitions.normal,
                    opacity: loading ? 0.5 : 1,
                  }}
                >
                  <option value="buy">Buy</option>
                  <option value="sell">Sell</option>
                </select>
              </div>

              {/* Quantity */}
              <div>
                <label
                  style={{
                    display: "block",
                    fontSize: "14px",
                    fontWeight: "600",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm,
                  }}
                >
                  Quantity
                </label>
                <input
                  type="number"
                  value={qty}
                  onChange={(e) => setQty(parseInt(e.target.value) || 0)}
                  min="1"
                  step="1"
                  disabled={loading}
                  required
                  style={{
                    width: "100%",
                    padding: responsiveSizes.inputPadding,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: responsiveSizes.inputFontSize,
                    transition: theme.transitions.normal,
                    opacity: loading ? 0.5 : 1,
                  }}
                />
              </div>

              {/* Order Type */}
              <div>
                <label
                  style={{
                    display: "block",
                    fontSize: "14px",
                    fontWeight: "600",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm,
                  }}
                >
                  Order Type
                </label>
                <select
                  value={orderType}
                  onChange={(e) => setOrderType(e.target.value as "market" | "limit")}
                  disabled={loading}
                  style={{
                    width: "100%",
                    padding: responsiveSizes.inputPadding,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: responsiveSizes.inputFontSize,
                    transition: theme.transitions.normal,
                    opacity: loading ? 0.5 : 1,
                  }}
                >
                  <option value="market">Market</option>
                  <option value="limit">Limit</option>
                </select>
              </div>

              {/* Options-specific fields (conditional) */}
              {assetClass === "option" && (
                <>
                  {/* Call/Put Selector */}
                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                        marginBottom: theme.spacing.sm,
                      }}
                    >
                      Option Type
                    </label>
                    <select
                      value={optionType}
                      onChange={(e) => setOptionType(e.target.value as "call" | "put")}
                      disabled={loading}
                      style={{
                        width: "100%",
                        padding: responsiveSizes.inputPadding,
                        background: theme.background.input,
                        border: `1px solid ${theme.colors.border}`,
                        borderRadius: theme.borderRadius.md,
                        color: theme.colors.text,
                        fontSize: responsiveSizes.inputFontSize,
                        transition: theme.transitions.normal,
                        opacity: loading ? 0.5 : 1,
                      }}
                    >
                      <option value="call">Call</option>
                      <option value="put">Put</option>
                    </select>
                  </div>

                  {/* Expiration Date */}
                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                        marginBottom: theme.spacing.sm,
                      }}
                    >
                      Expiration Date
                    </label>
                    <select
                      value={expirationDate}
                      onChange={(e) => setExpirationDate(e.target.value)}
                      disabled={loading || loadingOptionsChain || availableExpirations.length === 0}
                      style={{
                        width: "100%",
                        padding: responsiveSizes.inputPadding,
                        background: theme.background.input,
                        border: `1px solid ${theme.colors.border}`,
                        borderRadius: theme.borderRadius.md,
                        color: theme.colors.text,
                        fontSize: responsiveSizes.inputFontSize,
                        transition: theme.transitions.normal,
                        opacity: loading || loadingOptionsChain ? 0.5 : 1,
                      }}
                    >
                      {availableExpirations.length === 0 ? (
                        <option value="">Loading expirations...</option>
                      ) : (
                        availableExpirations.map((exp) => (
                          <option key={exp} value={exp}>
                            {exp}
                          </option>
                        ))
                      )}
                    </select>
                  </div>

                  {/* Strike Price */}
                  <div style={{ gridColumn: isMobile ? "auto" : "span 2" }}>
                    <label
                      style={{
                        display: "block",
                        fontSize: "14px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                        marginBottom: theme.spacing.sm,
                      }}
                    >
                      Strike Price
                    </label>
                    <select
                      value={strikePrice}
                      onChange={(e) => setStrikePrice(e.target.value)}
                      disabled={loading || loadingOptionsChain || availableStrikes.length === 0}
                      style={{
                        width: "100%",
                        padding: responsiveSizes.inputPadding,
                        background: theme.background.input,
                        border: `1px solid ${theme.colors.border}`,
                        borderRadius: theme.borderRadius.md,
                        color: theme.colors.text,
                        fontSize: responsiveSizes.inputFontSize,
                        transition: theme.transitions.normal,
                        opacity: loading || loadingOptionsChain ? 0.5 : 1,
                      }}
                    >
                      {availableStrikes.length === 0 ? (
                        <option value="">Select expiration first...</option>
                      ) : (
                        availableStrikes.map((strike) => (
                          <option key={strike} value={strike}>
                            ${strike.toFixed(2)}
                          </option>
                        ))
                      )}
                    </select>
                  </div>
                </>
              )}

              {/* Limit Price (conditional) */}
              {orderType === "limit" && (
                <div style={{ gridColumn: isMobile ? "auto" : "span 2" }}>
                  <label
                    style={{
                      display: "block",
                      fontSize: "14px",
                      fontWeight: "600",
                      color: theme.colors.textMuted,
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    Limit Price
                  </label>
                  <input
                    type="number"
                    value={limitPrice}
                    onChange={(e) => setLimitPrice(e.target.value)}
                    min="0.01"
                    step="0.01"
                    placeholder="0.00"
                    disabled={loading}
                    required
                    style={{
                      width: "100%",
                      padding: responsiveSizes.inputPadding,
                      background: theme.background.input,
                      border: `1px solid ${theme.colors.border}`,
                      borderRadius: theme.borderRadius.md,
                      color: theme.colors.text,
                      fontSize: responsiveSizes.inputFontSize,
                      transition: theme.transitions.normal,
                    opacity: loading ? 0.5 : 1,
                  }}
                />
              </div>
              )}

              <div style={{ gridColumn: isMobile ? "auto" : "span 2" }}>
                <label
                  style={{
                    display: "block",
                    fontSize: "14px",
                    fontWeight: "600",
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm,
                  }}
                >
                  Order Class & Advanced Legs
                </label>
                <select
                  value={orderClass}
                  onChange={(event) => setOrderClass(event.target.value as OrderClass)}
                  disabled={loading}
                  style={{
                    width: "100%",
                    padding: responsiveSizes.inputPadding,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: responsiveSizes.inputFontSize,
                    transition: theme.transitions.normal,
                    opacity: loading ? 0.5 : 1,
                    marginBottom: theme.spacing.sm,
                  }}
                >
                  <option value="simple">Simple</option>
                  <option value="bracket">Bracket</option>
                  <option value="oco">OCO Exit</option>
                </select>

                {(orderClass === "bracket" || orderClass === "oco") && (
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: isMobile ? "1fr" : "repeat(2, minmax(0, 1fr))",
                      gap: theme.spacing.sm,
                      marginTop: theme.spacing.sm,
                    }}
                  >
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "13px",
                          fontWeight: "600",
                          color: theme.colors.textMuted,
                          marginBottom: theme.spacing.xs,
                        }}
                      >
                        Take-Profit Limit
                      </label>
                      <input
                        type="number"
                        value={takeProfitPrice}
                        onChange={(event) => setTakeProfitPrice(event.target.value)}
                        min="0"
                        step="0.01"
                        placeholder="Target price"
                        disabled={loading}
                        style={{
                          width: "100%",
                          padding: responsiveSizes.inputPadding,
                          background: theme.background.input,
                          border: `1px solid ${theme.colors.border}`,
                          borderRadius: theme.borderRadius.md,
                          color: theme.colors.text,
                          fontSize: responsiveSizes.inputFontSize,
                        }}
                      />
                    </div>
                    <div>
                      <label
                        style={{
                          display: "block",
                          fontSize: "13px",
                          fontWeight: "600",
                          color: theme.colors.textMuted,
                          marginBottom: theme.spacing.xs,
                        }}
                      >
                        Stop-Loss Trigger
                      </label>
                      <input
                        type="number"
                        value={stopLossPrice}
                        onChange={(event) => setStopLossPrice(event.target.value)}
                        min="0"
                        step="0.01"
                        placeholder="Stop price"
                        disabled={loading}
                        style={{
                          width: "100%",
                          padding: responsiveSizes.inputPadding,
                          background: theme.background.input,
                          border: `1px solid ${theme.colors.border}`,
                          borderRadius: theme.borderRadius.md,
                          color: theme.colors.text,
                          fontSize: responsiveSizes.inputFontSize,
                          marginBottom: theme.spacing.xs,
                        }}
                      />
                      <input
                        type="number"
                        value={stopLossLimitPrice}
                        onChange={(event) => setStopLossLimitPrice(event.target.value)}
                        min="0"
                        step="0.01"
                        placeholder="Optional stop-limit price"
                        disabled={loading}
                        style={{
                          width: "100%",
                          padding: responsiveSizes.inputPadding,
                          background: theme.background.input,
                          border: `1px solid ${theme.colors.border}`,
                          borderRadius: theme.borderRadius.md,
                          color: theme.colors.text,
                          fontSize: responsiveSizes.inputFontSize,
                        }}
                      />
                    </div>
                  </div>
                )}

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: isMobile ? "1fr" : "repeat(2, minmax(0, 1fr))",
                    gap: theme.spacing.sm,
                    marginTop: theme.spacing.sm,
                  }}
                >
                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: "13px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                        marginBottom: theme.spacing.xs,
                      }}
                    >
                      Trailing Stop ($)
                    </label>
                    <input
                      type="number"
                      value={trailPrice}
                      onChange={(event) => setTrailPrice(event.target.value)}
                      min="0"
                      step="0.01"
                      placeholder="Dollar trail"
                      disabled={loading}
                      style={{
                        width: "100%",
                        padding: responsiveSizes.inputPadding,
                        background: theme.background.input,
                        border: `1px solid ${theme.colors.border}`,
                        borderRadius: theme.borderRadius.md,
                        color: theme.colors.text,
                        fontSize: responsiveSizes.inputFontSize,
                      }}
                    />
                  </div>
                  <div>
                    <label
                      style={{
                        display: "block",
                        fontSize: "13px",
                        fontWeight: "600",
                        color: theme.colors.textMuted,
                        marginBottom: theme.spacing.xs,
                      }}
                    >
                      Trailing Stop (%)
                    </label>
                    <input
                      type="number"
                      value={trailPercent}
                      onChange={(event) => setTrailPercent(event.target.value)}
                      min="0"
                      step="0.1"
                      placeholder="Percent trail"
                      disabled={loading}
                      style={{
                        width: "100%",
                        padding: responsiveSizes.inputPadding,
                        background: theme.background.input,
                        border: `1px solid ${theme.colors.border}`,
                        borderRadius: theme.borderRadius.md,
                        color: theme.colors.text,
                        fontSize: responsiveSizes.inputFontSize,
                      }}
                    />
                  </div>
                </div>

                <label
                  style={{
                    display: "block",
                    fontSize: "13px",
                    fontWeight: "600",
                    color: theme.colors.textMuted,
                    marginTop: theme.spacing.sm,
                    marginBottom: theme.spacing.xs,
                  }}
                >
                  Estimated Fill (for preview)
                </label>
                <input
                  type="number"
                  value={estimatedPrice}
                  onChange={(event) => setEstimatedPrice(event.target.value)}
                  min="0"
                  step="0.01"
                  placeholder="Optional estimated execution price"
                  disabled={loading}
                  style={{
                    width: "100%",
                    padding: responsiveSizes.inputPadding,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.text,
                    fontSize: responsiveSizes.inputFontSize,
                  }}
                />
              </div>
            </div>

            {/* Options Greeks Preview (conditional) */}
            {assetClass === "option" && symbol.trim() && strikePrice && expirationDate && (
              <div
                style={{
                  marginTop: theme.spacing.lg,
                  padding: theme.spacing.lg,
                  background: theme.background.input,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.lg,
                }}
              >
                <h4
                  style={{
                    margin: 0,
                    marginBottom: theme.spacing.md,
                    fontSize: "16px",
                    fontWeight: "600",
                    color: theme.colors.text,
                  }}
                >
                  Live Greeks Preview
                </h4>
                <OptionsGreeksDisplay
                  symbol={symbol.trim().toUpperCase()}
                  strike={parseFloat(strikePrice)}
                  expiry={expirationDate}
                  optionType={optionType}
                />
              </div>
            )}

            {/* Risk Analysis & Proposal System (conditional) */}
            {assetClass === "option" && symbol.trim() && (
              <div
                style={{
                  marginTop: theme.spacing.lg,
                }}
              >
                <RiskCalculator
                  onCreateProposal={(proposal) => {
                    console.log("Proposal created:", proposal);
                    showSuccess("Trade proposal created with risk analysis");
                  }}
                  onExecuteProposal={(proposal, limitPrice) => {
                    console.log("Executing proposal:", proposal, "at price:", limitPrice);
                    showSuccess(`Order submitted for ${proposal.option_symbol}`);
                  }}
                />
              </div>
            )}

            {/* Action Buttons */}
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: theme.spacing.md,
                marginTop: theme.spacing.lg,
              }}
            >
              <Button
                type="button"
                onClick={openPreviewModal}
                variant="secondary"
                style={{ flex: 1, minWidth: "180px" }}
              >
                Preview Risk (Ctrl + Enter)
              </Button>

              <Button type="submit" loading={loading} variant="primary" style={{ flex: 1, minWidth: "180px" }}>
                {loading ? "Processing..." : "Submit Order (Dry-Run)"}
              </Button>

              {lastRequestId && (
                <Button type="button" onClick={testDuplicate} loading={loading} variant="secondary">
                  Test Duplicate
                </Button>
              )}
            </div>
          </form>

          {/* Last Request ID */}
          {lastRequestId && (
            <div
              style={{
                marginTop: theme.spacing.lg,
                padding: theme.spacing.md,
                background: theme.background.input,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.sm,
                fontSize: "12px",
                color: theme.colors.textMuted,
                fontFamily: "monospace",
              }}
            >
              <strong>Last Request ID:</strong> {lastRequestId}
            </div>
          )}

          {/* Success Response */}
          {response && !error && (
            <div style={{ marginTop: theme.spacing.lg }}>
              <div
                style={{
                  padding: theme.spacing.lg,
                  background: response.duplicate
                    ? "rgba(255, 136, 0, 0.2)"
                    : "rgba(16, 185, 129, 0.2)",
                  border: `2px solid ${response.duplicate ? theme.colors.warning : theme.colors.primary}`,
                  borderRadius: theme.borderRadius.md,
                  boxShadow: response.duplicate ? theme.glow.orange : theme.glow.green,
                  marginBottom: theme.spacing.md,
                }}
              >
                <div style={{ display: "flex", alignItems: "flex-start", gap: theme.spacing.md }}>
                  <div
                    style={{
                      padding: theme.spacing.sm,
                      background: response.duplicate
                        ? "rgba(255, 136, 0, 0.2)"
                        : "rgba(16, 185, 129, 0.2)",
                      borderRadius: theme.borderRadius.sm,
                    }}
                  >
                    {response.duplicate ? (
                      <AlertCircle style={{ width: 24, height: 24, color: theme.colors.warning }} />
                    ) : (
                      <Check style={{ width: 24, height: 24, color: theme.colors.primary }} />
                    )}
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3
                      style={{
                        fontSize: "18px",
                        fontWeight: "700",
                        color: response.duplicate ? theme.colors.warning : theme.colors.primary,
                        marginBottom: theme.spacing.sm,
                      }}
                    >
                      {response.duplicate ? "⚠️ Duplicate Detected" : "✅ Order Accepted"}
                    </h3>
                    <div style={{ fontSize: "14px", color: theme.colors.textMuted }}>
                      <p style={{ marginBottom: theme.spacing.xs }}>
                        <strong>Status:</strong> {response.accepted ? "Accepted" : "Rejected"}
                      </p>
                      {response.dryRun && (
                        <p>
                          <strong>Mode:</strong>{" "}
                          <span style={{ color: theme.colors.info }}>Dry Run</span>
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setShowRawJson(!showRawJson)}
                style={{
                  width: "100%",
                  padding: `${theme.spacing.md} ${theme.spacing.lg}`,
                  background: theme.background.input,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                  color: theme.colors.textMuted,
                  fontSize: "14px",
                  fontWeight: "600",
                  cursor: "pointer",
                  transition: theme.transitions.normal,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <span>View Raw Response</span>
                <ChevronDown
                  style={{
                    width: 20,
                    height: 20,
                    transform: showRawJson ? "rotate(180deg)" : "rotate(0deg)",
                    transition: theme.transitions.normal,
                  }}
                />
              </button>

              {showRawJson && (
                <div
                  style={{
                    marginTop: theme.spacing.md,
                    padding: theme.spacing.md,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    overflowX: "auto",
                  }}
                >
                  <pre
                    style={{
                      fontSize: "12px",
                      fontFamily: "monospace",
                      margin: 0,
                      whiteSpace: "pre-wrap",
                      wordBreak: "break-word",
                      color: theme.colors.textMuted,
                    }}
                  >
                    {JSON.stringify(response, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div
              style={{
                marginTop: theme.spacing.lg,
                padding: theme.spacing.lg,
                background: "rgba(255, 68, 68, 0.2)",
                border: `2px solid ${theme.colors.danger}`,
                borderRadius: theme.borderRadius.md,
                boxShadow: theme.glow.red,
              }}
            >
              <div style={{ display: "flex", alignItems: "flex-start", gap: theme.spacing.md }}>
                <div
                  style={{
                    padding: theme.spacing.sm,
                    background: "rgba(255, 68, 68, 0.2)",
                    borderRadius: theme.borderRadius.sm,
                  }}
                >
                  <AlertCircle style={{ width: 24, height: 24, color: theme.colors.danger }} />
                </div>
                <div>
                  <h3
                    style={{
                      fontSize: "18px",
                      fontWeight: "700",
                      color: theme.colors.danger,
                      marginBottom: theme.spacing.sm,
                    }}
                  >
                    ❌ Error
                  </h3>
                  <p style={{ fontSize: "14px", color: theme.colors.text, margin: 0 }}>{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Stock Research Section */}
          {showStockLookup && symbol.trim() && (
            <div
              style={{
                marginTop: theme.spacing.xl,
                padding: theme.spacing.lg,
                background: theme.background.input,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.lg,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: theme.spacing.lg,
                  paddingBottom: theme.spacing.md,
                  borderBottom: `1px solid ${theme.colors.border}`,
                }}
              >
                <h3
                  style={{
                    margin: 0,
                    fontSize: "20px",
                    fontWeight: "700",
                    color: theme.colors.text,
                  }}
                >
                  Research: {symbol.toUpperCase()}
                </h3>
                <Button
                  variant="secondary"
                  onClick={() => setShowStockLookup(false)}
                  style={{ fontSize: "14px", padding: "8px 16px" }}
                >
                  Close
                </Button>
              </div>
              <StockLookup
                initialSymbol={symbol.trim().toUpperCase()}
                showChart={true}
                showIndicators={true}
                showCompanyInfo={true}
                showNews={false}
                enableAIAnalysis={true}
                onSymbolSelect={(sym) => setSymbol(sym)}
              />
            </div>
          )}
        </Card>
      </div>
    </>
  );
}
