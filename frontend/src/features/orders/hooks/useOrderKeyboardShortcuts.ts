import { useEffect } from "react";

interface ShortcutOptions {
  onSubmit?: () => void;
  onPreview?: () => void;
  onSaveTemplate?: () => void;
}

export function useOrderKeyboardShortcuts({
  onSubmit,
  onPreview,
  onSaveTemplate,
}: ShortcutOptions) {
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.defaultPrevented) return;

      const key = event.key.toLowerCase();
      const hasMod = event.metaKey || event.ctrlKey;

      if (hasMod && key === "enter") {
        event.preventDefault();
        if (event.shiftKey) {
          onSubmit?.();
        } else {
          onPreview?.();
        }
        return;
      }

      if (hasMod && key === "s") {
        event.preventDefault();
        onSaveTemplate?.();
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onPreview, onSaveTemplate, onSubmit]);
}
