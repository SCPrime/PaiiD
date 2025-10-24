import React from "react";
import { cn } from "../../lib/utils";

interface StatusIndicatorProps {
  status: "online" | "offline" | "warning" | "error" | "loading";
  size?: "sm" | "md" | "lg";
  label?: string;
  className?: string;
  animated?: boolean;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  size = "md",
  label,
  className,
  animated = true,
}) => {
  const sizeClasses = {
    sm: "w-2 h-2",
    md: "w-3 h-3",
    lg: "w-4 h-4",
  };

  const statusClasses = {
    online: "bg-green-500 shadow-green-500/50",
    offline: "bg-gray-500",
    warning: "bg-yellow-500 shadow-yellow-500/50",
    error: "bg-red-500 shadow-red-500/50",
    loading: "bg-blue-500 shadow-blue-500/50",
  };

  const animationClasses = animated
    ? {
        online: "animate-pulse",
        offline: "",
        warning: "animate-pulse",
        error: "animate-pulse",
        loading: "animate-spin",
      }
    : {};

  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div
        className={cn(
          "rounded-full shadow-lg",
          sizeClasses[size],
          statusClasses[status],
          animationClasses[status]
        )}
      />
      {label && <span className="text-sm font-medium text-slate-300 capitalize">{label}</span>}
    </div>
  );
};

export default StatusIndicator;
