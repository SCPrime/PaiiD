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
export const withPerformanceOptimization = <P extends object>(
  Component: React.ComponentType<P>,
  options: {
    memo?: boolean;
    lazy?: boolean;
    debounce?: number;
    throttle?: number;
  } = {}
) => {
  const { memo = true, lazy = false, debounce: debounceMs, throttle: throttleMs } = options;

  let WrappedComponent = Component;

  // Apply memoization
  if (memo) {
    WrappedComponent = React.memo(Component) as React.ComponentType<P>;
  }

  // Apply lazy loading
  if (lazy) {
    WrappedComponent = React.lazy(() => Promise.resolve({ default: WrappedComponent }));
  }

  // Apply performance optimizations
  if (debounceMs || throttleMs) {
    const OriginalComponent = WrappedComponent;
    WrappedComponent = React.forwardRef<any, P>((props, ref) => {
      const [optimizedProps, setOptimizedProps] = useState(props);

      const updateProps = useCallback(
        debounceMs
          ? debounce((newProps: P) => setOptimizedProps(newProps), debounceMs)
          : throttle((newProps: P) => setOptimizedProps(newProps), throttleMs || 16),
        [debounceMs, throttleMs]
      );

      useEffect(() => {
        updateProps(props);
      }, [props, updateProps]);

      return <OriginalComponent {...optimizedProps} ref={ref} />;
    }) as React.ComponentType<P>;
  }

  return WrappedComponent;
};

// Virtual scrolling hook
export const useVirtualScrolling = (
  items: any[],
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

  const handleScroll = useCallback(
    throttle((event: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(event.currentTarget.scrollTop);
    }, 16),
    []
  );

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
