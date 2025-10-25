/**
 * Toast Notification System
 * Enterprise-grade toast notifications with animations
 */

import { CheckCircle, XCircle, AlertTriangle, Info, X } from "lucide-react";
import { useEffect, useState } from "react";

export type ToastType = "success" | "error" | "warning" | "info";

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface ToastProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

const toastIcons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

const toastColors = {
  success: {
    bg: "bg-green-50",
    border: "border-green-200",
    icon: "text-green-500",
    title: "text-green-800",
    message: "text-green-700",
  },
  error: {
    bg: "bg-red-50",
    border: "border-red-200",
    icon: "text-red-500",
    title: "text-red-800",
    message: "text-red-700",
  },
  warning: {
    bg: "bg-yellow-50",
    border: "border-yellow-200",
    icon: "text-yellow-500",
    title: "text-yellow-800",
    message: "text-yellow-700",
  },
  info: {
    bg: "bg-blue-50",
    border: "border-blue-200",
    icon: "text-blue-500",
    title: "text-blue-800",
    message: "text-blue-700",
  },
};

function ToastComponent({ toast, onRemove }: ToastProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    // Trigger entrance animation
    const timer = setTimeout(() => setIsVisible(true), 10);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (toast.duration) {
      const timer = setTimeout(() => {
        handleRemove();
      }, toast.duration);
      return () => clearTimeout(timer);
    }
  }, [toast.duration]);

  const handleRemove = () => {
    setIsLeaving(true);
    setTimeout(() => {
      onRemove(toast.id);
    }, 300);
  };

  const Icon = toastIcons[toast.type];
  const colors = toastColors[toast.type];

  return (
    <div
      className={`
        ${colors.bg} ${colors.border} border rounded-lg p-4 shadow-lg
        transition-all duration-300 ease-in-out
        ${isVisible && !isLeaving ? "translate-x-0 opacity-100" : "translate-x-full opacity-0"}
        ${isLeaving ? "translate-x-full opacity-0" : ""}
      `}
      style={{
        backdropFilter: "blur(10px)",
        minWidth: "320px",
        maxWidth: "400px",
      }}
    >
      <div className="flex items-start gap-3">
        <Icon className={`w-5 h-5 mt-0.5 ${colors.icon} flex-shrink-0`} />
        
        <div className="flex-1 min-w-0">
          <div className={`font-semibold text-sm ${colors.title}`}>
            {toast.title}
          </div>
          {toast.message && (
            <div className={`text-sm mt-1 ${colors.message}`}>
              {toast.message}
            </div>
          )}
          {toast.action && (
            <button
              onClick={toast.action.onClick}
              className={`
                mt-2 text-sm font-medium underline hover:no-underline
                ${colors.title}
              `}
            >
              {toast.action.label}
            </button>
          )}
        </div>

        <button
          onClick={handleRemove}
          className={`
            flex-shrink-0 p-1 rounded-full hover:bg-black hover:bg-opacity-10
            transition-colors ${colors.title}
          `}
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// Toast Container
interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <ToastComponent
          key={toast.id}
          toast={toast}
          onRemove={onRemove}
        />
      ))}
    </div>
  );
}

// Toast Hook
let toastId = 0;

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (toast: Omit<Toast, "id">) => {
    const id = `toast-${++toastId}`;
    const newToast = { ...toast, id };
    
    setToasts(prev => [...prev, newToast]);
    
    return id;
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const clearAll = () => {
    setToasts([]);
  };

  // Convenience methods
  const success = (title: string, message?: string, options?: Partial<Toast>) => {
    return addToast({
      type: "success",
      title,
      message,
      duration: 5000,
      ...options,
    });
  };

  const error = (title: string, message?: string, options?: Partial<Toast>) => {
    return addToast({
      type: "error",
      title,
      message,
      duration: 7000,
      ...options,
    });
  };

  const warning = (title: string, message?: string, options?: Partial<Toast>) => {
    return addToast({
      type: "warning",
      title,
      message,
      duration: 6000,
      ...options,
    });
  };

  const info = (title: string, message?: string, options?: Partial<Toast>) => {
    return addToast({
      type: "info",
      title,
      message,
      duration: 4000,
      ...options,
    });
  };

  return {
    toasts,
    addToast,
    removeToast,
    clearAll,
    success,
    error,
    warning,
    info,
  };
}
