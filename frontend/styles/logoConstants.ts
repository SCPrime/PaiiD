/**
 * Shared PaiiD Logo Style Constants
 *
 * Single source of truth for logo styling across all components.
 * Based on the STRONG glow effect from RadialMenu "open screen".
 */

export const LOGO_STYLES = {
  /**
   * Text shadow glow effects for the "aii" letters
   * Values: Increased by 75% for stronger visual impact
   * Original: 40px/80px/120px → New: 70px/140px/210px
   */
  GLOW: {
    // Base glow (animation start/end state)
    base: '0 0 52px rgba(16, 185, 129, 0.9), 0 0 105px rgba(16, 185, 129, 0.6), 0 0 158px rgba(16, 185, 129, 0.4)',

    // Peak glow (animation mid-point, brightest)
    peak: '0 0 88px rgba(16, 185, 129, 1), 0 0 175px rgba(16, 185, 129, 0.8), 0 0 263px rgba(16, 185, 129, 0.5)',

    // Initial inline style (before animation)
    initial: '0 0 70px rgba(16, 185, 129, 1), 0 0 140px rgba(16, 185, 129, 0.7), 0 0 210px rgba(16, 185, 129, 0.4)',

    // Hover state (enhanced glow)
    hover: '0 0 88px rgba(16, 185, 129, 1), 0 0 175px rgba(16, 185, 129, 0.8), 0 0 263px rgba(16, 185, 129, 0.5)',
  },

  /**
   * Gradient for P, a, D letters
   */
  GRADIENT: {
    teal: 'linear-gradient(135deg, #1a7560 0%, #0d5a4a 100%)',
  },

  /**
   * Drop shadow for non-glowing letters (P and D)
   */
  DROP_SHADOW: {
    standard: 'drop-shadow(0 4px 12px rgba(26, 117, 96, 0.6))',
    subtle: 'drop-shadow(0 2px 4px rgba(26, 117, 96, 0.4))',
  },

  /**
   * Animation keyframe for "aii" breathing glow effect
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
 * Common inline styles for "aii" span
 */
export const AII_SPAN_STYLES = {
  background: LOGO_STYLES.GRADIENT.teal,
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  textShadow: LOGO_STYLES.GLOW.initial,
  animation: LOGO_ANIMATION_CSS,
  cursor: 'pointer',
  transition: 'transform 0.2s ease',
};

/**
 * Common inline styles for P and D letters
 */
export const PD_SPAN_STYLES = {
  background: LOGO_STYLES.GRADIENT.teal,
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  filter: LOGO_STYLES.DROP_SHADOW.standard,
};
