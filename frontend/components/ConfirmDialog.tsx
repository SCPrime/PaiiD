"use client";

import { cn, glassVariants } from "../lib/utils";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  confirmVariant?: "primary" | "danger" | "warning";
  onConfirm: () => void;
  onCancel: () => void;
  // Enhanced props for trade preview
  orderDetails?: {
    symbol: string;
    side: "buy" | "sell";
    qty: number;
    type: "market" | "limit";
    limitPrice?: number;
    asset_class?: "stock" | "option";
    option_type?: "call" | "put";
    strike_price?: number;
    expiration_date?: string;
  } | null;
  riskWarning?: boolean;
}

export default function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  confirmVariant = "primary",
  onConfirm,
  onCancel,
  orderDetails,
  riskWarning = false,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const variantClasses: Record<NonNullable<typeof confirmVariant>, string> = {
    primary:
      "bg-[#16a394] text-[#0f172a] shadow-[0_15px_35px_rgba(22,163,148,0.45)] hover:shadow-[0_18px_40px_rgba(22,163,148,0.55)]",
    danger:
      "bg-[#FF4444] text-[#f1f5f9] shadow-[0_15px_35px_rgba(255,68,68,0.45)] hover:shadow-[0_18px_40px_rgba(255,68,68,0.55)]",
    warning:
      "bg-[#F97316] text-[#0f172a] shadow-[0_15px_35px_rgba(249,115,22,0.45)] hover:shadow-[0_18px_40px_rgba(249,115,22,0.55)]",
  };

  return (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-[#0f172a]/80 px-4 py-8 backdrop-blur-xl"
      onClick={onCancel}
    >
      <div
        className={cn(
          glassVariants.dialog,
          "w-full max-w-xl overflow-hidden border border-teal-500/20 px-6 py-8 text-slate-100 shadow-[0_25px_65px_rgba(15,24,40,0.65)]"
        )}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="mb-4 text-center text-2xl font-semibold text-slate-100">{title}</h2>

        <p className="mb-8 text-center text-base leading-relaxed text-[#cbd5e1]">{message}</p>

        {/* Trade Preview */}
        {orderDetails && (
          <div
            className={cn(
              glassVariants.card,
              "mb-6 border border-teal-500/20 bg-[#1a2a3f]/80 p-6 text-slate-100"
            )}
          >
            <h3 className="mb-4 text-center text-lg font-semibold uppercase tracking-wide text-slate-100">
              📊 Trade Preview
            </h3>

            <div className="grid grid-cols-2 gap-4 text-sm text-slate-300">
              <div>
                <span className="text-xs font-medium uppercase tracking-wide text-[#94a3b8]">
                  Symbol
                </span>
                <div className="text-base font-semibold text-slate-100">{orderDetails.symbol}</div>
              </div>
              <div>
                <span className="text-xs font-medium uppercase tracking-wide text-[#94a3b8]">
                  Side
                </span>
                <div
                  className={cn(
                    "text-base font-semibold",
                    orderDetails.side === "buy" ? "text-[#16a394]" : "text-[#FF4444]"
                  )}
                >
                  {orderDetails.side.toUpperCase()}
                </div>
              </div>
              <div>
                <span className="text-xs font-medium uppercase tracking-wide text-[#94a3b8]">
                  Quantity
                </span>
                <div className="text-base font-semibold text-slate-100">{orderDetails.qty}</div>
              </div>
              <div>
                <span className="text-xs font-medium uppercase tracking-wide text-[#94a3b8]">
                  Type
                </span>
                <div className="text-base font-semibold text-slate-100">
                  {orderDetails.type.toUpperCase()}
                </div>
              </div>
              {orderDetails.limitPrice && (
                <div className="col-span-2">
                  <span className="text-xs font-medium uppercase tracking-wide text-[#94a3b8]">
                    Limit Price
                  </span>
                  <div className="text-base font-semibold text-slate-100">
                    ${orderDetails.limitPrice}
                  </div>
                </div>
              )}
              {orderDetails.asset_class === "option" && (
                <>
                  <div>
                    <span className="text-xs font-medium uppercase tracking-wide text-[#94a3b8]">
                      Option Type
                    </span>
                    <div className="text-base font-semibold text-slate-100">
                      {orderDetails.option_type?.toUpperCase()}
                    </div>
                  </div>
                  <div>
                    <span className="text-xs font-medium uppercase tracking-wide text-[#94a3b8]">
                      Strike
                    </span>
                    <div className="text-base font-semibold text-slate-100">
                      ${orderDetails.strike_price}
                    </div>
                  </div>
                </>
              )}
            </div>

            {riskWarning && (
              <div className="mt-4 rounded-lg border border-[#FF4444]/40 bg-[#FF4444]/10 p-4 text-sm">
                <div className="mb-2 flex items-center gap-2 font-semibold text-[#FF4444]">
                  ⚠️ Risk Warning
                </div>
                <div className="leading-relaxed text-[#cbd5e1]">
                  This trade involves real money. Make sure you understand the risks and have done
                  your research.
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex flex-wrap items-center justify-center gap-4">
          <button
            type="button"
            onClick={onCancel}
            className={cn(
              glassVariants.card,
              "min-w-[120px] border border-teal-500/20 px-6 py-3 text-base font-semibold text-[#cbd5e1] transition hover:border-[#16a394]/40 hover:text-slate-100"
            )}
          >
            {cancelText}
          </button>

          <button
            type="button"
            onClick={onConfirm}
            className={cn(
              "min-w-[120px] rounded-md px-6 py-3 text-base font-bold transition-transform duration-150",
              variantClasses[confirmVariant],
              "hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-[#45f0c0]/60"
            )}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
