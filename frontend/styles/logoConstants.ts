/**
 * Shared PaiiD Logo Style Constants
 *
 * Single source of truth for logo styling across all components.
 * UPDATED: New π-based logo design with #45f0c0 cyan color scheme
 * LOGO FORMAT: "P-a-π-D" where π has two glowing dots above it
 */

export const LOGO_STYLES = {
  /**
   * Primary brand color - Cyan (#45f0c0)
   * Used for all logo text and glow effects
   */
  COLOR: {
    primary: '#45f0c0',                    // Main cyan color
    rgb: 'rgb(69, 240, 192)',              // RGB format
    rgba: (opacity: number) => `rgba(69, 240, 192, ${opacity})`, // RGBA helper
  },

  /**
   * Glow effects for the π symbol (animated breathing effect)
   * Applied via text-shadow property
   */
  GLOW: {
    // Base glow (animation start/end state)
    base: '0 0 15px rgba(69, 240, 192, 0.6), 0 0 30px rgba(69, 240, 192, 0.4)',

    // Peak glow (animation mid-point, brightest)
    peak: '0 0 25px rgba(69, 240, 192, 0.9), 0 0 50px rgba(69, 240, 192, 0.6), 0 0 75px rgba(69, 240, 192, 0.3)',

    // Initial inline style (before animation)
    initial: '0 0 20px rgba(69, 240, 192, 0.7), 0 0 40px rgba(69, 240, 192, 0.5)',

    // Hover state (enhanced glow)
    hover: '0 0 30px rgba(69, 240, 192, 1), 0 0 60px rgba(69, 240, 192, 0.7), 0 0 90px rgba(69, 240, 192, 0.4)',
  },

  /**
   * π symbol dots styling
   * Two glowing dots positioned above the π legs (like mathematical notation)
   */
  PI_DOTS: {
    background: '#45f0c0',
    boxShadow: '0 0 10px rgba(69, 240, 192, 0.8)',
    borderRadius: '50%',
    // Sizes calculated dynamically based on font size
  },

  /**
   * Animation keyframe for π breathing glow effect
   * Duration: 3s ease-in-out infinite
   */
  ANIMATION: {
    name: 'glow-ai',
    duration: '3s',
    timing: 'ease-in-out',
    iteration: 'infinite',
  },
};

/**
 * CSS keyframe animation string for use in styled-jsx
 * Animates the π symbol with breathing glow effect
 */
export const LOGO_ANIMATION_KEYFRAME = `
  @keyframes glow-ai {
    0%, 100% {
      text-shadow: ${LOGO_STYLES.GLOW.base};
    }
    50% {
      text-shadow: ${LOGO_STYLES.GLOW.peak};
    }
  }
`;

/**
 * Full animation CSS property value
 */
export const LOGO_ANIMATION_CSS = `${LOGO_STYLES.ANIMATION.name} ${LOGO_STYLES.ANIMATION.duration} ${LOGO_STYLES.ANIMATION.timing} ${LOGO_STYLES.ANIMATION.iteration}`;

/**
 * Common inline styles for π symbol (animated)
 */
export const PI_SYMBOL_STYLES = {
  color: LOGO_STYLES.COLOR.primary,
  animation: LOGO_ANIMATION_CSS,
  cursor: 'pointer',
  position: 'relative' as const,
  display: 'inline-block',
  transition: 'transform 0.2s ease',
};

/**
 * Common inline styles for P, a, D letters (static, no animation)
 */
export const STATIC_LETTER_STYLES = {
  color: LOGO_STYLES.COLOR.primary,
};

/**
 * Modal slide-up animation for AI interface
 */
export const MODAL_ANIMATIONS = {
  slideUp: `
    @keyframes slideUpFromBottom {
      from {
        transform: translateY(100%);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }
  `,
  slideDown: `
    @keyframes slideDownToBottom {
      from {
        transform: translateY(0);
        opacity: 1;
      }
      to {
        transform: translateY(100%);
        opacity: 0;
      }
    }
  `,
};

/**
 * DEPRECATED: Old constants kept for backwards compatibility during migration
 * Will be removed in future update after all components are migrated to π design
 */
export const DEPRECATED = {
  GRADIENT: {
    teal: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
  },
  DROP_SHADOW: {
    standard: 'drop-shadow(0 4px 12px rgba(26, 117, 96, 0.6))',
    subtle: 'drop-shadow(0 2px 4px rgba(26, 117, 96, 0.4))',
  },
  OLD_COLOR: '#10b981', // Old emerald green
};
