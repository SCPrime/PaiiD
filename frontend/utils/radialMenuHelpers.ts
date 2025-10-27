/**
 * Helper utilities for RadialMenu component
 */

export interface ResponsiveFontSizes {
  headerLogo: string;
  headerSubtitle1: string;
  headerSubtitle2: string;
  segmentText: string;
  centerLogo: string;
  marketLabel: string;
  marketValue: string;
  marketChange: string;
}

export interface CenterContentSpacing {
  logoOffset: number;
  dowOffset: number;
  nasdaqOffset: number;
  statusBadgeOffset: number;
}

/**
 * Calculate responsive menu size based on viewport and device type
 */
export function calculateMenuSize(isMobile: boolean, viewportWidth: number): number {
  if (isMobile) {
    // Mobile: 90% of viewport width, max 675px (35% increase from 500)
    return Math.min(viewportWidth * 0.9, 675);
  }

  // Desktop: Responsive to viewport width for split-screen mode
  // When viewport < 1900px (typical split screen), scale down proportionally
  if (viewportWidth < 1900) {
    return Math.min(viewportWidth * 0.85, 945);
  }

  // Desktop full screen: Standard 945px (35% increase from 700)
  return 945;
}

/**
 * Calculate responsive font sizes based on device type
 */
export function calculateFontSizes(isMobile: boolean): ResponsiveFontSizes {
  if (isMobile) {
    return {
      headerLogo: "65px", // 48 × 1.35
      headerSubtitle1: "22px", // 16 × 1.35
      headerSubtitle2: "19px", // 14 × 1.35
      segmentText: "22px", // 16 × 1.35
      centerLogo: "27px", // 20 × 1.35
      marketLabel: "9px", // 7 × 1.35 ≈ 9
      marketValue: "16px", // 12 × 1.35 ≈ 16
      marketChange: "11px", // 8 × 1.35 ≈ 11
    };
  }
  // Desktop sizes - scaled up 35% for better readability
  return {
    headerLogo: "130px", // 96 × 1.35
    headerSubtitle1: "30px", // 22 × 1.35
    headerSubtitle2: "24px", // 18 × 1.35
    segmentText: "30px", // 22 × 1.35
    centerLogo: "43px", // 32 × 1.35
    marketLabel: "12px", // 9 × 1.35
    marketValue: "22px", // 16 × 1.35
    marketChange: "14px", // 10 × 1.35
  };
}

/**
 * Calculate responsive center content positions based on innerRadius
 * Ensures proper spacing regardless of menu size (500px mobile → 700px desktop)
 *
 * Layout structure (Y-axis, positive = DOWN):
 * 1. FORCE FIELD (top) - calculated from DOW position
 * 2. PaiiD Logo (center at Y=0) - React overlay, ~87px tall on desktop
 * 3. DOW JONES (below logo)
 * 4. NASDAQ (below DOW)
 * 5. Status Badge (bottom)
 */
export function calculateCenterContentSpacing(innerRadius: number): CenterContentSpacing {
  return {
    logoOffset: -(innerRadius * 0.45), // Not used - logo is CSS positioned at Y=0
    dowOffset: innerRadius * 0.50, // DOW well below logo (INCREASED from 0.38 to avoid logo overlap with ~58px tall logo)
    nasdaqOffset: innerRadius * 0.82, // NASDAQ below DOW (INCREASED from 0.68 for proper spacing)
    statusBadgeOffset: innerRadius * 0.75, // Status badge at bottom (CHANGED from 0.85 to match MarketStatusBadge.tsx)
  };
}

/**
 * Get confidence color based on percentage
 */
export function getConfidenceColor(confidence: number): string {
  if (confidence >= 80) return "#45f0c0";
  if (confidence >= 60) return "#fbbf24";
  if (confidence >= 40) return "#fb923c";
  return "#ef4444";
}
