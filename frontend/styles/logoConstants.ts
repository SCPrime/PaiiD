/**
 * Shared PaiiD Logo Style Constants
 *
 * Single source of truth for logo styling across all components.
 * FIXED: Using filter:drop-shadow() instead of textShadow for gradient text compatibility
 */

export const LOGO_STYLES = {
  /**
   * Box-shadow glow effects for the "aii" letters (works with gradient text!)
   * Applied to wrapper div, not the text itself (text is transparent via background-clip)
   */
  GLOW: {
    // Base glow (animation start/end state)
    base: '0 0 30px rgba(16, 185, 129, 0.9), 0 0 60px rgba(16, 185, 129, 0.6), 0 0 90px rgba(16, 185, 129, 0.4)',

    // Peak glow (animation mid-point, brightest)
    peak: '0 0 50px rgba(16, 185, 129, 1), 0 0 100px rgba(16, 185, 129, 0.8), 0 0 150px rgba(16, 185, 129, 0.6)',

    // Initial inline style (before animation)
    initial: '0 0 40px rgba(16, 185, 129, 1), 0 0 80px rgba(16, 185, 129, 0.7), 0 0 120px rgba(16, 185, 129, 0.5)',

    // Hover state (enhanced glow)
    hover: '0 0 50px rgba(16, 185, 129, 1), 0 0 100px rgba(16, 185, 129, 0.8), 0 0 150px rgba(16, 185, 129, 0.6)',
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

  /**
   * Full PaiiD Logo Wrapper Styles (toggled via URL parameter)
   */
  RADIAL_GLOW: {
    background: 'radial-gradient(ellipse, rgba(16, 185, 129, 0.35) 0%, rgba(16, 185, 129, 0.25) 40%, rgba(16, 185, 129, 0.10) 70%, rgba(16, 185, 129, 0.02) 90%, transparent 100%)',
    borderRadius: '50px',
    padding: '8px 16px',
    backdropFilter: 'none',
  },
  HALO_GLOW: {
    background: 'rgba(16, 185, 129, 0.4)',
    borderRadius: '12px',
    padding: '6px 14px',
    backdropFilter: 'blur(8px)',
  },
};

/**
 * CSS keyframe animation string for use in styled-jsx
 * FIXED: Animates box-shadow property (applied to wrapper div, not text)
 */
export const LOGO_ANIMATION_KEYFRAME = `
  @keyframes glow-ai {
    0%, 100% {
      box-shadow: ${LOGO_STYLES.GLOW.base};
      transform: scale(1);
    }
    50% {
      box-shadow: ${LOGO_STYLES.GLOW.peak};
      transform: scale(1.02);
    }
  }
`;

/**
 * Full animation CSS property value
 */
export const LOGO_ANIMATION_CSS = `${LOGO_STYLES.ANIMATION.name} ${LOGO_STYLES.ANIMATION.duration} ${LOGO_STYLES.ANIMATION.timing} ${LOGO_STYLES.ANIMATION.iteration}`;

/**
 * Common inline styles for "aii" wrapper div (contains the glow)
 * The glow is applied to the wrapper, not the text itself
 */
export const AII_WRAPPER_STYLES = {
  display: 'inline-block',
  borderRadius: '8px',
  boxShadow: LOGO_STYLES.GLOW.initial,
  animation: LOGO_ANIMATION_CSS,
  cursor: 'pointer',
  transition: 'all 0.3s ease',
};

/**
 * Common inline styles for "aii" span (the gradient text inside the wrapper)
 */
export const AII_SPAN_STYLES = {
  background: LOGO_STYLES.GRADIENT.teal,
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  fontStyle: 'italic',
  display: 'inline-block',
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
