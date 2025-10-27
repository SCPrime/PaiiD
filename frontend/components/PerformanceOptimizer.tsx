import { debounce, throttle } from "lodash";
import React, { useCallback, useEffect, useMemo, useState } from "react";

interface PerformanceOptimizerProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  threshold?: number;
  rootMargin?: string;
}

// Intersection Observer for lazy loading
const PerformanceOptimizer: React.FC<PerformanceOptimizerProps> = ({
  children,
  fallback = <div className="animate-pulse bg-slate-700 rounded-lg h-32" />,
  threshold = 0.1,
  rootMargin = "50px",
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const elementRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isLoaded) {
          setIsVisible(true);
          setIsLoaded(true);
        }
      },
      { threshold, rootMargin }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => observer.disconnect();
  }, [threshold, rootMargin, isLoaded]);

  return (
    <div ref={elementRef} className="w-full h-full">
      {isVisible ? children : fallback}
    </div>
  );
};

// Memoized component wrapper
export const withPerformanceOptimization = <P extends Record<string, unknown>>(
  Component: React.ComponentType<P>,
  options: {
    memo?: boolean;
    lazy?: boolean;
    debounce?: number;
    throttle?: number;
  } = {}
): React.ComponentType<P> => {
  const { memo = true, lazy = false, debounce: debounceMs, throttle: throttleMs } = options;

  // Apply memoization
  let WrappedComponent: React.ComponentType<P> = memo
    ? (React.memo(Component) as unknown as React.ComponentType<P>)
    : Component;

  // Apply lazy loading
  if (lazy) {
    const LazyComponent = React.lazy(() =>
      Promise.resolve({ default: WrappedComponent })
    );
    WrappedComponent = LazyComponent as unknown as React.ComponentType<P>;
  }

  // Apply performance optimizations
  if (debounceMs || throttleMs) {
    const OriginalComponent = WrappedComponent;
    const OptimizedComponent: React.FC<P> = (props) => {
      const [optimizedProps, setOptimizedProps] = useState<P>(props);

      const updateProps = useCallback(
        (newProps: P) => {
          if (debounceMs) {
            debounce(() => setOptimizedProps(newProps), debounceMs)();
          } else {
            throttle(() => setOptimizedProps(newProps), throttleMs || 16)();
          }
        },
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [debounceMs, throttleMs]
      );

      useEffect(() => {
        updateProps(props);
      }, [props, updateProps]);

      return <OriginalComponent {...optimizedProps} />;
    };

    WrappedComponent = OptimizedComponent as React.ComponentType<P>;
  }

  return WrappedComponent;
};

// Virtual scrolling hook
export const useVirtualScrolling = <T extends Record<string, unknown>>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan: number = 5
) => {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleItems = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );

    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      ...item,
      index: startIndex + index,
      top: (startIndex + index) * itemHeight,
    }));
  }, [items, itemHeight, containerHeight, scrollTop, overscan]);

  const totalHeight = items.length * itemHeight;

  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    throttle(() => {
      setScrollTop(event.currentTarget.scrollTop);
    }, 16)();
  }, []);

  return {
    visibleItems,
    totalHeight,
    handleScroll,
  };
};

// Image lazy loading component
export const LazyImage: React.FC<{
  src: string;
  alt: string;
  className?: string;
  placeholder?: string;
  onLoad?: () => void;
  onError?: () => void;
}> = ({ src, alt, className, placeholder, onLoad, onError }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isError, setIsError] = useState(false);

  const handleLoad = useCallback(() => {
    setIsLoaded(true);
    onLoad?.();
  }, [onLoad]);

  const handleError = useCallback(() => {
    setIsError(true);
    onError?.();
  }, [onError]);

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {!isLoaded && !isError && (
        <div className="absolute inset-0 bg-slate-700 animate-pulse flex items-center justify-center">
          {placeholder || "Loading..."}
        </div>
      )}
      {isError ? (
        <div className="absolute inset-0 bg-slate-600 flex items-center justify-center text-slate-400">
          Failed to load
        </div>
      ) : (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={src}
          alt={alt}
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            isLoaded ? "opacity-100" : "opacity-0"
          }`}
          onLoad={handleLoad}
          onError={handleError}
        />
      )}
    </div>
  );
};

export default PerformanceOptimizer;
