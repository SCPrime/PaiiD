/**
 * Toast Notification Utilities
 *
 * Wrapper around react-hot-toast with consistent styling and messaging
 */

import toast from 'react-hot-toast';

/**
 * Show a success toast notification
 */
export const showSuccess = (message: string, duration?: number) => {
  return toast.success(message, { duration });
};

/**
 * Show an error toast notification
 */
export const showError = (message: string, duration?: number) => {
  return toast.error(message, { duration });
};

/**
 * Show an info toast notification
 */
export const showInfo = (message: string, duration?: number) => {
  return toast(message, {
    duration,
    icon: 'ℹ️',
    style: {
      border: '1px solid rgba(59, 130, 246, 0.5)',
    },
  });
};

/**
 * Show a warning toast notification
 */
export const showWarning = (message: string, duration?: number) => {
  return toast(message, {
    duration,
    icon: '⚠️',
    style: {
      border: '1px solid rgba(245, 158, 11, 0.5)',
    },
  });
};

/**
 * Show a loading toast notification
 * Returns a toast ID that can be used to dismiss/update the toast
 */
export const showLoading = (message: string) => {
  return toast.loading(message);
};

/**
 * Dismiss a specific toast by ID
 */
export const dismissToast = (toastId: string) => {
  toast.dismiss(toastId);
};

/**
 * Dismiss all active toasts
 */
export const dismissAllToasts = () => {
  toast.dismiss();
};

/**
 * Show a promise-based toast
 * Automatically shows loading, success, and error states
 */
export const showPromise = <T,>(
  promise: Promise<T>,
  messages: {
    loading: string;
    success: string | ((data: T) => string);
    error: string | ((err: any) => string);
  }
) => {
  return toast.promise(promise, messages);
};

// Export individual toast types for specific use cases
export { toast };
