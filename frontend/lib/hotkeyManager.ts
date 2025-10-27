/**
 * Global Hotkey Manager
 * Handles keyboard shortcuts across the application
 */

export interface HotkeyConfig {
  key: string;
  ctrl?: boolean;
  shift?: boolean;
  alt?: boolean;
  description: string;
  action: () => void;
}

export interface HotkeyBinding {
  id: string;
  config: HotkeyConfig;
}

class HotkeyManager {
  private bindings: Map<string, HotkeyBinding> = new Map();
  private enabled: boolean = true;
  private debugMode: boolean = false;

  constructor() {
    if (typeof window !== 'undefined') {
      this.initialize();
    }
  }

  private initialize() {
    document.addEventListener('keydown', this.handleKeyDown.bind(this));

    if (this.debugMode) {
      console.log('[HotkeyManager] Initialized');
    }
  }

  private handleKeyDown(event: KeyboardEvent) {
    if (!this.enabled) return;

    // Don't trigger hotkeys when typing in input fields
    const target = event.target as HTMLElement;
    if (
      target.tagName === 'INPUT' ||
      target.tagName === 'TEXTAREA' ||
      target.isContentEditable
    ) {
      return;
    }

    // Build the hotkey signature
    const signature = this.buildSignature(
      event.key.toLowerCase(),
      event.ctrlKey,
      event.shiftKey,
      event.altKey
    );

    const binding = this.bindings.get(signature);
    if (binding) {
      event.preventDefault();
      event.stopPropagation();

      if (this.debugMode) {
        console.log(`[HotkeyManager] Triggered: ${binding.id} (${signature})`);
      }

      binding.config.action();
    }
  }

  private buildSignature(
    key: string,
    ctrl: boolean = false,
    shift: boolean = false,
    alt: boolean = false
  ): string {
    const parts: string[] = [];
    if (ctrl) parts.push('ctrl');
    if (shift) parts.push('shift');
    if (alt) parts.push('alt');
    parts.push(key.toLowerCase());
    return parts.join('+');
  }

  /**
   * Register a new hotkey binding
   */
  register(id: string, config: HotkeyConfig): void {
    const signature = this.buildSignature(
      config.key,
      config.ctrl,
      config.shift,
      config.alt
    );

    if (this.bindings.has(signature)) {
      console.warn(`[HotkeyManager] Overwriting existing binding: ${signature}`);
    }

    this.bindings.set(signature, { id, config });

    if (this.debugMode) {
      console.log(`[HotkeyManager] Registered: ${id} -> ${signature}`);
    }
  }

  /**
   * Unregister a hotkey binding by ID
   */
  unregister(id: string): void {
    for (const [signature, binding] of this.bindings.entries()) {
      if (binding.id === id) {
        this.bindings.delete(signature);

        if (this.debugMode) {
          console.log(`[HotkeyManager] Unregistered: ${id}`);
        }
        return;
      }
    }
  }

  /**
   * Get all registered hotkeys
   */
  getAllBindings(): HotkeyBinding[] {
    return Array.from(this.bindings.values());
  }

  /**
   * Enable or disable all hotkeys
   */
  setEnabled(enabled: boolean): void {
    this.enabled = enabled;

    if (this.debugMode) {
      console.log(`[HotkeyManager] ${enabled ? 'Enabled' : 'Disabled'}`);
    }
  }

  /**
   * Check if hotkeys are enabled
   */
  isEnabled(): boolean {
    return this.enabled;
  }

  /**
   * Enable debug mode
   */
  setDebugMode(debug: boolean): void {
    this.debugMode = debug;
  }

  /**
   * Get human-readable hotkey display string
   */
  getDisplayString(config: HotkeyConfig): string {
    const parts: string[] = [];
    if (config.ctrl) parts.push('Ctrl');
    if (config.shift) parts.push('Shift');
    if (config.alt) parts.push('Alt');
    parts.push(config.key.toUpperCase());
    return parts.join(' + ');
  }

  /**
   * Cleanup - remove event listeners
   */
  destroy(): void {
    if (typeof window !== 'undefined') {
      document.removeEventListener('keydown', this.handleKeyDown.bind(this));
    }
    this.bindings.clear();

    if (this.debugMode) {
      console.log('[HotkeyManager] Destroyed');
    }
  }
}

// Singleton instance
let hotkeyManagerInstance: HotkeyManager | null = null;

export function getHotkeyManager(): HotkeyManager {
  if (!hotkeyManagerInstance) {
    hotkeyManagerInstance = new HotkeyManager();
  }
  return hotkeyManagerInstance;
}

// Default hotkey configurations
export const DEFAULT_HOTKEYS = {
  QUICK_TRADE: {
    key: 't',
    ctrl: true,
    description: 'Quick Trade',
  },
  POSITIONS: {
    key: 'p',
    ctrl: true,
    description: 'View Positions',
  },
  RESEARCH: {
    key: 'r',
    ctrl: true,
    description: 'Research',
  },
  STORYBOARD: {
    key: 's',
    ctrl: true,
    shift: true,
    description: 'Storyboard Mode',
  },
  CLOSE_MODAL: {
    key: 'escape',
    description: 'Close Modal',
  },
  AI_CHAT: {
    key: 'k',
    ctrl: true,
    description: 'AI Chat',
  },
  SETTINGS: {
    key: ',',
    ctrl: true,
    description: 'Settings',
  },
  HELP: {
    key: '/',
    ctrl: true,
    description: 'Help',
  },
} as const;

// Helper to format hotkey for display
export function formatHotkey(
  key: string,
  modifiers: { ctrl?: boolean; shift?: boolean; alt?: boolean }
): string {
  const parts: string[] = [];
  if (modifiers.ctrl) parts.push('Ctrl');
  if (modifiers.shift) parts.push('Shift');
  if (modifiers.alt) parts.push('Alt');
  parts.push(key.toUpperCase());
  return parts.join(' + ');
}

// Helper to get OS-specific modifier key name
export function getModifierKeyName(): string {
  if (typeof window === 'undefined') return 'Ctrl';

  const isMac = /Mac|iPod|iPhone|iPad/.test(navigator.platform);
  return isMac ? '⌘' : 'Ctrl';
}

export default getHotkeyManager;
