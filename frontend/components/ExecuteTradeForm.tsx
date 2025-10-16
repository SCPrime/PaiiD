"use client";
import { useState, useEffect } from "react";
import { TrendingUp, Check, AlertCircle, ChevronDown, Save, BookmarkPlus, Trash2, Search } from "lucide-react";
import { Card, Button } from "./ui";
import { theme } from "../styles/theme";
import ConfirmDialog from "./ConfirmDialog";
import { addOrderToHistory } from "./OrderHistory";
import { showSuccess, showError, showWarning } from "../lib/toast";
import { useIsMobile } from "../hooks/useBreakpoint";
import { useWorkflow } from "../contexts/WorkflowContext";
import StockLookup from "./StockLookup";

interface Order {
  symbol: string;
  side: "buy" | "sell";
  qty: number;
  type: "market" | "limit";
  limitPrice?: number;
}

interface ExecuteResponse {
  accepted: boolean;
  duplicate?: boolean;
  dryRun?: boolean;
  orders?: Order[];
}

interface OrderTemplate {
  id: number;
  name: string;
  description?: string;
  symbol: string;
  side: "buy" | "sell";
  quantity: number;
  order_type: "market" | "limit";
  limit_price?: number;
  created_at: string;
  updated_at: string;
  last_used_at?: string;
}

export default function ExecuteTradeForm() {
  // Mobile detection
  const isMobile = useIsMobile();

  // Workflow context
  const { pendingNavigation, clearPendingNavigation } = useWorkflow();

  // Responsive sizing
  const responsiveSizes = {
    headerLogo: isMobile ? '32px' : '42px',
    iconSize: isMobile ? 24 : 32,
    titleSize: isMobile ? '20px' : '28px',
    inputPadding: isMobile ? '14px 16px' : '12px 16px',
    inputFontSize: '16px' // Always 16px to prevent iOS zoom
  };

  const [symbol, setSymbol] = useState("SPY");
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [qty, setQty] = useState(1);
  const [orderType, setOrderType] = useState<"market" | "limit">("market");
  const [limitPrice, setLimitPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<ExecuteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastRequestId, setLastRequestId] = useState<string | null>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [pendingOrder, setPendingOrder] = useState<Order | null>(null);
  const [showRawJson, setShowRawJson] = useState(false);

  // Template-related state
  const [templates, setTemplates] = useState<OrderTemplate[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string>("");
  const [showSaveTemplate, setShowSaveTemplate] = useState(false);
  const [templateName, setTemplateName] = useState("");
  const [templateDescription, setTemplateDescription] = useState("");

  // Stock research state
  const [showStockLookup, setShowStockLookup] = useState(false);

  // Load templates on mount
  useEffect(() => {
    loadTemplates();
  }, []);

  // Consume pre-filled data from workflow navigation
  useEffect(() => {
    if (pendingNavigation && pendingNavigation.workflow === 'execute-trade' && pendingNavigation.tradeData) {
      const { tradeData } = pendingNavigation;

      // eslint-disable-next-line no-console
      console.info('[ExecuteTradeForm] Pre-filling form with trade data:', tradeData);

      // Pre-fill form fields
      if (tradeData.symbol) setSymbol(tradeData.symbol);
      if (tradeData.side) setSide(tradeData.side);
      if (tradeData.quantity && tradeData.quantity > 0) setQty(tradeData.quantity);

      // Set order type and price based on available data
      if (tradeData.entryPrice && tradeData.entryPrice > 0) {
        setOrderType('limit');
        setLimitPrice(tradeData.entryPrice.toString());
      } else if (tradeData.orderType && (tradeData.orderType === 'market' || tradeData.orderType === 'limit')) {
        // Only use orderType if it's supported (market or limit)
        setOrderType(tradeData.orderType);
        if (tradeData.orderType === 'limit' && tradeData.entryPrice) {
          setLimitPrice(tradeData.entryPrice.toString());
        }
      }

      // Show success toast
      showSuccess(`✅ Pre-filled trade data for ${tradeData.symbol}${tradeData.entryPrice ? ` at $${tradeData.entryPrice.toFixed(2)}` : ''}`);

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

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplateId(templateId);
    if (templateId === "") return;

    const template = templates.find(t => t.id === parseInt(templateId));
    if (template) {
      setSymbol(template.symbol);
      setSide(template.side);
      setQty(template.quantity);
      setOrderType(template.order_type);
      setLimitPrice(template.limit_price ? template.limit_price.toString() : "");
      showSuccess(`✅ Template "${template.name}" loaded`);

      // Mark template as used
      fetch(`/api/proxy/api/order-templates/${template.id}/use`, {
        method: "POST",
      }).catch(err => console.error("Failed to mark template as used:", err));
    }
  };

  const handleSaveTemplate = async () => {
    if (!templateName.trim()) {
      showError("❌ Template name is required");
      return;
    }

    try {
      const res = await fetch("/api/proxy/api/order-templates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: templateName,
          description: templateDescription || null,
          symbol: symbol.trim().toUpperCase(),
          side,
          quantity: qty,
          order_type: orderType,
          limit_price: orderType === "limit" ? parseFloat(limitPrice) : null,
        }),
      });

      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);

      const newTemplate = await res.json();
      setTemplates([...templates, newTemplate]);
      setShowSaveTemplate(false);
      setTemplateName("");
      setTemplateDescription("");
      showSuccess(`✅ Template "${newTemplate.name}" saved`);
    } catch (err: any) {
      showError(`❌ Failed to save template: ${err.message}`);
    }
  };

  const handleDeleteTemplate = async (templateId: number) => {
    if (!confirm("Are you sure you want to delete this template?")) return;

    try {
      const res = await fetch(`/api/proxy/api/order-templates/${templateId}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);

      setTemplates(templates.filter(t => t.id !== templateId));
      if (selectedTemplateId === templateId.toString()) {
        setSelectedTemplateId("");
      }
      showSuccess("✅ Template deleted");
    } catch (err: any) {
      showError(`❌ Failed to delete template: ${err.message}`);
    }
  };

  const generateRequestId = () =>
    `req-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    if (!symbol || symbol.trim() === "") {
      setError("Symbol is required");
      return;
    }
    if (qty <= 0) {
      setError("Quantity must be greater than 0");
      return;
    }
    if (orderType === "limit" && (!limitPrice || parseFloat(limitPrice) <= 0)) {
      setError("Limit price is required for limit orders");
      return;
    }

    const order: Order = {
      symbol: symbol.trim().toUpperCase(),
      side,
      qty,
      type: orderType,
    };

    if (orderType === "limit") {
      order.limitPrice = parseFloat(limitPrice);
    }

    // Show confirmation dialog
    setPendingOrder(order);
    setShowConfirmDialog(true);
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
      dryRun: true, // Always dry-run for now
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
        showSuccess(`✅ ${pendingOrder.side.toUpperCase()} order accepted (Dry-Run): ${pendingOrder.qty} shares of ${pendingOrder.symbol}`);
      }

      // Add to order history
      addOrderToHistory({
        symbol: pendingOrder.symbol,
        side: pendingOrder.side,
        qty: pendingOrder.qty,
        type: pendingOrder.type,
        limitPrice: pendingOrder.limitPrice,
        status: data.accepted ? "dry-run" : "cancelled",
        dryRun: true,
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

    const order: Order = {
      symbol: symbol.trim().toUpperCase(),
      side,
      qty,
      type: orderType,
    };

    if (orderType === "limit") {
      order.limitPrice = parseFloat(limitPrice);
    }

    const body = {
      dryRun: true,
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
      pendingOrder.type === "limit" && pendingOrder.limitPrice
        ? ` at $${pendingOrder.limitPrice.toFixed(2)}`
        : " at market price";
    return `${pendingOrder.side.toUpperCase()} ${pendingOrder.qty} shares of ${pendingOrder.symbol}${priceStr}?`;
  };

  return (
    <>
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
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.md,
            marginBottom: theme.spacing.xl,
            flexWrap: isMobile ? 'wrap' : 'nowrap'
          }}>
            {/* PaiiD Logo */}
            <div style={{ fontSize: responsiveSizes.headerLogo, fontWeight: '900', lineHeight: '1' }}>
              <span style={{
                background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                filter: 'drop-shadow(0 3px 8px rgba(26, 117, 96, 0.4))'
              }}>P</span>
              <span style={{
                background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textShadow: '0 0 18px rgba(69, 240, 192, 0.8), 0 0 36px rgba(69, 240, 192, 0.4)',
                animation: 'glow-ai 3s ease-in-out infinite'
              }}>aii</span>
              <span style={{
                background: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                filter: 'drop-shadow(0 3px 8px rgba(26, 117, 96, 0.4))'
              }}>D</span>
            </div>

            <div style={{
              padding: theme.spacing.md,
              background: 'rgba(16, 185, 129, 0.1)',
              borderRadius: theme.borderRadius.lg,
              border: '1px solid rgba(16, 185, 129, 0.2)'
            }}>
              <TrendingUp style={{ width: responsiveSizes.iconSize, height: responsiveSizes.iconSize, color: theme.colors.primary }} />
            </div>
            <div>
              <h1 style={{
                margin: 0,
                fontSize: responsiveSizes.titleSize,
                fontWeight: '700',
                color: theme.colors.text
              }}>
                Execute Trade
              </h1>
              <p style={{
                margin: 0,
                marginTop: '4px',
                color: theme.colors.textMuted,
                fontSize: '14px'
              }}>
                Place orders with dry-run mode enabled
              </p>
            </div>
          </div>

          {/* Template Selection and Management */}
          <div style={{
            marginBottom: theme.spacing.xl,
            padding: theme.spacing.lg,
            background: theme.background.input,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.lg
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: theme.spacing.md
            }}>
              <label style={{
                fontSize: '14px',
                fontWeight: '600',
                color: theme.colors.textMuted
              }}>
                <BookmarkPlus size={16} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
                Order Templates
              </label>
              <Button
                variant="secondary"
                onClick={() => setShowSaveTemplate(!showSaveTemplate)}
                style={{ fontSize: '12px', padding: '6px 12px' }}
              >
                <Save size={14} style={{ marginRight: '4px' }} />
                Save Current as Template
              </Button>
            </div>

            {/* Template Selector */}
            <div style={{ display: 'flex', gap: theme.spacing.sm }}>
              <select
                value={selectedTemplateId}
                onChange={(e) => handleTemplateSelect(e.target.value)}
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  background: theme.background.card,
                  border: `1px solid ${theme.colors.border}`,
                  borderRadius: theme.borderRadius.md,
                  color: theme.colors.text,
                  fontSize: '14px'
                }}
              >
                <option value="">-- Select a template --</option>
                {templates.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.symbol} - {t.side.toUpperCase()})
                  </option>
                ))}
              </select>
              {selectedTemplateId && (
                <Button
                  variant="danger"
                  onClick={() => handleDeleteTemplate(parseInt(selectedTemplateId))}
                  style={{ padding: '10px' }}
                >
                  <Trash2 size={16} />
                </Button>
              )}
            </div>

            {/* Save Template Modal */}
            {showSaveTemplate && (
              <div style={{
                marginTop: theme.spacing.md,
                padding: theme.spacing.md,
                background: theme.background.card,
                border: `1px solid ${theme.colors.primary}`,
                borderRadius: theme.borderRadius.md
              }}>
                <h4 style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: theme.colors.text,
                  marginBottom: theme.spacing.sm
                }}>
                  Save as Template
                </h4>
                <input
                  type="text"
                  placeholder="Template name (e.g., SPY Quick Buy)"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    marginBottom: theme.spacing.sm,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.sm,
                    color: theme.colors.text,
                    fontSize: '13px'
                  }}
                />
                <input
                  type="text"
                  placeholder="Description (optional)"
                  value={templateDescription}
                  onChange={(e) => setTemplateDescription(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    marginBottom: theme.spacing.sm,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.sm,
                    color: theme.colors.text,
                    fontSize: '13px'
                  }}
                />
                <div style={{ display: 'flex', gap: theme.spacing.sm }}>
                  <Button variant="primary" onClick={handleSaveTemplate} style={{ flex: 1 }}>
                    Save
                  </Button>
                  <Button variant="secondary" onClick={() => setShowSaveTemplate(false)} style={{ flex: 1 }}>
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Form */}
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.xl }}>
              {/* Form Grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
                gap: theme.spacing.xl
              }}>
                {/* Symbol */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm
                  }}>
                    Symbol
                  </label>
                  <div style={{ display: 'flex', gap: theme.spacing.sm }}>
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
                        opacity: loading ? 0.5 : 1
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
                        padding: isMobile ? '12px' : '12px 16px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                      }}
                    >
                      <Search size={18} />
                      {!isMobile && <span>Research</span>}
                    </Button>
                  </div>
                </div>

                {/* Side */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm
                  }}>
                    Side
                  </label>
                  <select
                    value={side}
                    onChange={(e) => setSide(e.target.value as "buy" | "sell")}
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: responsiveSizes.inputPadding,
                      background: theme.background.input,
                      border: `1px solid ${theme.colors.border}`,
                      borderRadius: theme.borderRadius.md,
                      color: theme.colors.text,
                      fontSize: responsiveSizes.inputFontSize,
                      transition: theme.transitions.normal,
                      opacity: loading ? 0.5 : 1
                    }}
                  >
                    <option value="buy">Buy</option>
                    <option value="sell">Sell</option>
                  </select>
                </div>

                {/* Quantity */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm
                  }}>
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
                      width: '100%',
                      padding: responsiveSizes.inputPadding,
                      background: theme.background.input,
                      border: `1px solid ${theme.colors.border}`,
                      borderRadius: theme.borderRadius.md,
                      color: theme.colors.text,
                      fontSize: responsiveSizes.inputFontSize,
                      transition: theme.transitions.normal,
                      opacity: loading ? 0.5 : 1
                    }}
                  />
                </div>

                {/* Order Type */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: theme.colors.textMuted,
                    marginBottom: theme.spacing.sm
                  }}>
                    Order Type
                  </label>
                  <select
                    value={orderType}
                    onChange={(e) => setOrderType(e.target.value as "market" | "limit")}
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: responsiveSizes.inputPadding,
                      background: theme.background.input,
                      border: `1px solid ${theme.colors.border}`,
                      borderRadius: theme.borderRadius.md,
                      color: theme.colors.text,
                      fontSize: responsiveSizes.inputFontSize,
                      transition: theme.transitions.normal,
                      opacity: loading ? 0.5 : 1
                    }}
                  >
                    <option value="market">Market</option>
                    <option value="limit">Limit</option>
                  </select>
                </div>

                {/* Limit Price (conditional) */}
                {orderType === "limit" && (
                  <div style={{ gridColumn: isMobile ? 'auto' : 'span 2' }}>
                    <label style={{
                      display: 'block',
                      fontSize: '14px',
                      fontWeight: '600',
                      color: theme.colors.textMuted,
                      marginBottom: theme.spacing.sm
                    }}>
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
                        width: '100%',
                        padding: responsiveSizes.inputPadding,
                        background: theme.background.input,
                        border: `1px solid ${theme.colors.border}`,
                        borderRadius: theme.borderRadius.md,
                        color: theme.colors.text,
                        fontSize: responsiveSizes.inputFontSize,
                        transition: theme.transitions.normal,
                        opacity: loading ? 0.5 : 1
                      }}
                    />
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: theme.spacing.md, marginTop: theme.spacing.lg }}>
                <Button type="submit" loading={loading} variant="primary" style={{ flex: 1 }}>
                  {loading ? 'Processing...' : 'Submit Order (Dry-Run)'}
                </Button>

                {lastRequestId && (
                  <Button
                    type="button"
                    onClick={testDuplicate}
                    loading={loading}
                    variant="secondary"
                  >
                    Test Duplicate
                  </Button>
                )}
              </div>
            </form>

            {/* Last Request ID */}
            {lastRequestId && (
              <div style={{
                marginTop: theme.spacing.lg,
                padding: theme.spacing.md,
                background: theme.background.input,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.sm,
                fontSize: '12px',
                color: theme.colors.textMuted,
                fontFamily: 'monospace'
              }}>
                <strong>Last Request ID:</strong> {lastRequestId}
              </div>
            )}

            {/* Success Response */}
            {response && !error && (
              <div style={{ marginTop: theme.spacing.lg }}>
                <div style={{
                  padding: theme.spacing.lg,
                  background: response.duplicate ? 'rgba(255, 136, 0, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                  border: `2px solid ${response.duplicate ? theme.colors.warning : theme.colors.primary}`,
                  borderRadius: theme.borderRadius.md,
                  boxShadow: response.duplicate ? theme.glow.orange : theme.glow.green,
                  marginBottom: theme.spacing.md
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: theme.spacing.md }}>
                    <div style={{
                      padding: theme.spacing.sm,
                      background: response.duplicate ? 'rgba(255, 136, 0, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                      borderRadius: theme.borderRadius.sm
                    }}>
                      {response.duplicate ? (
                        <AlertCircle style={{ width: 24, height: 24, color: theme.colors.warning }} />
                      ) : (
                        <Check style={{ width: 24, height: 24, color: theme.colors.primary }} />
                      )}
                    </div>
                    <div style={{ flex: 1 }}>
                      <h3 style={{
                        fontSize: '18px',
                        fontWeight: '700',
                        color: response.duplicate ? theme.colors.warning : theme.colors.primary,
                        marginBottom: theme.spacing.sm
                      }}>
                        {response.duplicate ? "⚠️ Duplicate Detected" : "✅ Order Accepted"}
                      </h3>
                      <div style={{ fontSize: '14px', color: theme.colors.textMuted }}>
                        <p style={{ marginBottom: theme.spacing.xs }}>
                          <strong>Status:</strong> {response.accepted ? "Accepted" : "Rejected"}
                        </p>
                        {response.dryRun && (
                          <p><strong>Mode:</strong> <span style={{ color: theme.colors.info }}>Dry Run</span>
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => setShowRawJson(!showRawJson)}
                  style={{
                    width: '100%',
                    padding: `${theme.spacing.md} ${theme.spacing.lg}`,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    color: theme.colors.textMuted,
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: theme.transitions.normal,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <span>View Raw Response</span>
                  <ChevronDown style={{
                    width: 20,
                    height: 20,
                    transform: showRawJson ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: theme.transitions.normal
                  }} />
                </button>

                {showRawJson && (
                  <div style={{
                    marginTop: theme.spacing.md,
                    padding: theme.spacing.md,
                    background: theme.background.input,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.md,
                    overflowX: 'auto'
                  }}>
                    <pre style={{
                      fontSize: '12px',
                      fontFamily: 'monospace',
                      margin: 0,
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      color: theme.colors.textMuted
                    }}>
                      {JSON.stringify(response, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div style={{
                marginTop: theme.spacing.lg,
                padding: theme.spacing.lg,
                background: 'rgba(255, 68, 68, 0.2)',
                border: `2px solid ${theme.colors.danger}`,
                borderRadius: theme.borderRadius.md,
                boxShadow: theme.glow.red
              }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: theme.spacing.md }}>
                  <div style={{
                    padding: theme.spacing.sm,
                    background: 'rgba(255, 68, 68, 0.2)',
                    borderRadius: theme.borderRadius.sm
                  }}>
                    <AlertCircle style={{ width: 24, height: 24, color: theme.colors.danger }} />
                  </div>
                  <div>
                    <h3 style={{
                      fontSize: '18px',
                      fontWeight: '700',
                      color: theme.colors.danger,
                      marginBottom: theme.spacing.sm
                    }}>
                      ❌ Error
                    </h3>
                    <p style={{ fontSize: '14px', color: theme.colors.text, margin: 0 }}>
                      {error}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Stock Research Section */}
            {showStockLookup && symbol.trim() && (
              <div style={{
                marginTop: theme.spacing.xl,
                padding: theme.spacing.lg,
                background: theme.background.input,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.lg
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: theme.spacing.lg,
                  paddingBottom: theme.spacing.md,
                  borderBottom: `1px solid ${theme.colors.border}`
                }}>
                  <h3 style={{
                    margin: 0,
                    fontSize: '20px',
                    fontWeight: '700',
                    color: theme.colors.text
                  }}>
                    Research: {symbol.toUpperCase()}
                  </h3>
                  <Button
                    variant="secondary"
                    onClick={() => setShowStockLookup(false)}
                    style={{ fontSize: '14px', padding: '8px 16px' }}
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
