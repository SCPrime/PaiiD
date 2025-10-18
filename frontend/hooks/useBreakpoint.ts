import { useState, useEffect } from "react";

export type Breakpoint = "mobile" | "tablet" | "desktop";

/**
 * Custom hook to detect current viewport breakpoint
 *
 * Breakpoints:
 * - mobile: 0 - 767px
 * - tablet: 768px - 1023px
 * - desktop: 1024px+
 *
 * @returns current breakpoint ('mobile' | 'tablet' | 'desktop')
 *
 * @example
 * const breakpoint = useBreakpoint();
 * if (breakpoint === 'mobile') {
 *   // Render mobile layout
 * }
 */
export const useBreakpoint = (): Breakpoint => {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>("desktop");

  useEffect(() => {
    const checkBreakpoint = () => {
      const width = window.innerWidth;

      if (width < 768) {
        setBreakpoint("mobile");
      } else if (width < 1024) {
        setBreakpoint("tablet");
      } else {
        setBreakpoint("desktop");
      }
    };

    // Check on mount
    checkBreakpoint();

    // Check on resize
    window.addEventListener("resize", checkBreakpoint);

    // Cleanup
    return () => window.removeEventListener("resize", checkBreakpoint);
  }, []);

  return breakpoint;
};

/**
 * Helper hook that returns boolean for mobile detection
 *
 * @returns true if viewport is mobile (< 768px)
 *
 * @example
 * const isMobile = useIsMobile();
 * return isMobile ? <MobileLayout /> : <DesktopLayout />;
 */
export const useIsMobile = (): boolean => {
  const breakpoint = useBreakpoint();
  return breakpoint === "mobile";
};

/**
 * Helper hook that returns boolean for tablet detection
 *
 * @returns true if viewport is tablet (768px - 1023px)
 */
export const useIsTablet = (): boolean => {
  const breakpoint = useBreakpoint();
  return breakpoint === "tablet";
};

/**
 * Helper hook that returns boolean for desktop detection
 *
 * @returns true if viewport is desktop (>= 1024px)
 */
export const useIsDesktop = (): boolean => {
  const breakpoint = useBreakpoint();
  return breakpoint === "desktop";
};

/**
 * Helper hook that returns window dimensions
 *
 * @returns { width: number, height: number }
 *
 * @example
 * const { width, height } = useWindowDimensions();
 * const menuSize = Math.min(width * 0.9, 500);
 */
export const useWindowDimensions = () => {
  const [dimensions, setDimensions] = useState({
    width: typeof window !== "undefined" ? window.innerWidth : 1024,
    height: typeof window !== "undefined" ? window.innerHeight : 768,
  });

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return dimensions;
};
