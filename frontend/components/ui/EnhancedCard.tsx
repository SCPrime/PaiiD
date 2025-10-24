import React from "react";
import { cn } from "../../lib/utils";

interface EnhancedCardProps {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "glass" | "gradient" | "elevated";
  size?: "sm" | "md" | "lg" | "xl";
  hover?: boolean;
  glow?: boolean;
  border?: boolean;
}

const EnhancedCard: React.FC<EnhancedCardProps> = ({
  children,
  className,
  variant = "default",
  size = "md",
  hover = false,
  glow = false,
  border = true,
}) => {
  const baseClasses = "rounded-xl transition-all duration-300 ease-in-out";

  const variantClasses = {
    default: "bg-slate-800/90 backdrop-blur-sm",
    glass: "bg-white/5 backdrop-blur-md border border-white/10",
    gradient: "bg-gradient-to-br from-slate-800/90 to-slate-900/90 backdrop-blur-sm",
    elevated: "bg-slate-800/95 backdrop-blur-sm shadow-2xl",
  };

  const sizeClasses = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
    xl: "p-10",
  };

  const hoverClasses = hover ? "hover:scale-[1.02] hover:shadow-xl" : "";
  const glowClasses = glow ? "shadow-lg shadow-blue-500/20" : "";
  const borderClasses = border ? "border border-slate-700/50" : "";

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        hoverClasses,
        glowClasses,
        borderClasses,
        className
      )}
    >
      {children}
    </div>
  );
};

export default EnhancedCard;
