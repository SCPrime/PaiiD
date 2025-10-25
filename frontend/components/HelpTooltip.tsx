/**
 * Help Tooltip Component
 * Enterprise-grade contextual help with smooth animations
 */

import { HelpCircle, X } from "lucide-react";
import { useState } from "react";
import { theme } from "../styles/theme";

interface HelpTooltipProps {
  content: string;
  title?: string;
  position?: "top" | "bottom" | "left" | "right";
  size?: "sm" | "md" | "lg";
  children?: React.ReactNode;
  className?: string;
}

export default function HelpTooltip({
  content,
  title,
  position = "top",
  size = "md",
  children,
  className = "",
}: HelpTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isPinned, setIsPinned] = useState(false);

  const sizeClasses = {
    sm: "text-xs",
    md: "text-sm",
    lg: "text-base",
  };

  const positionClasses = {
    top: "bottom-full left-1/2 transform -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 transform -translate-x-1/2 mt-2",
    left: "right-full top-1/2 transform -translate-y-1/2 mr-2",
    right: "left-full top-1/2 transform -translate-y-1/2 ml-2",
  };

  const arrowClasses = {
    top: "top-full left-1/2 transform -translate-x-1/2 border-t-4 border-t-gray-800",
    bottom: "bottom-full left-1/2 transform -translate-x-1/2 border-b-4 border-b-gray-800",
    left: "left-full top-1/2 transform -translate-y-1/2 border-l-4 border-l-gray-800",
    right: "right-full top-1/2 transform -translate-y-1/2 border-r-4 border-r-gray-800",
  };

  return (
    <div className={`relative inline-block ${className}`}>
      {/* Trigger */}
      <div
        className="inline-flex items-center cursor-help"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => !isPinned && setIsVisible(false)}
        onClick={() => setIsPinned(!isPinned)}
      >
        {children}
        <HelpCircle
          className="ml-1 text-gray-400 hover:text-gray-300 transition-colors"
          size={16}
        />
      </div>

      {/* Tooltip */}
      {(isVisible || isPinned) && (
        <div
          className={`absolute z-50 bg-gray-800 text-white rounded-lg shadow-xl max-w-xs p-3 ${positionClasses[position]} ${sizeClasses[size]} transition-all duration-200 ${
            isVisible || isPinned ? "opacity-100 scale-100" : "opacity-0 scale-95"
          }`}
          style={{
            backdropFilter: "blur(10px)",
            border: `1px solid ${theme.colors.border}`,
          }}
        >
          {/* Close button for pinned tooltips */}
          {isPinned && (
            <button
              onClick={() => setIsPinned(false)}
              className="absolute top-1 right-1 text-gray-400 hover:text-white transition-colors"
            >
              <X size={12} />
            </button>
          )}

          {/* Content */}
          {title && (
            <div className="font-semibold mb-1 text-white">{title}</div>
          )}
          <div className="text-gray-200 leading-relaxed">{content}</div>

          {/* Arrow */}
          <div
            className={`absolute w-0 h-0 ${arrowClasses[position]}`}
            style={{
              borderColor: "transparent",
            }}
          />
        </div>
      )}
    </div>
  );
}
