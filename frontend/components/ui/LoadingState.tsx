/**
 * Loading State Components
 * Enterprise-grade loading states with skeleton screens
 */

import { Loader2 } from "lucide-react";
import { theme as _theme } from "../../styles/theme";

interface LoadingStateProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  className?: string;
}

export function LoadingSpinner({ size = "md", text, className = "" }: LoadingStateProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6", 
    lg: "w-8 h-8",
  };

  return (
    <div className={`flex items-center justify-center gap-2 ${className}`}>
      <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-500`} />
      {text && (
        <span className="text-gray-600 text-sm">{text}</span>
      )}
    </div>
  );
}

interface SkeletonProps {
  width?: string;
  height?: string;
  className?: string;
  lines?: number;
}

export function Skeleton({ width = "100%", height = "20px", className = "", lines = 1 }: SkeletonProps) {
  if (lines > 1) {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className="animate-pulse bg-gray-200 rounded"
            style={{ width, height: i === lines - 1 ? "60%" : height }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={`animate-pulse bg-gray-200 rounded ${className}`}
      style={{ width, height }}
    />
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex gap-4">
        <Skeleton width="20%" height="16px" />
        <Skeleton width="15%" height="16px" />
        <Skeleton width="15%" height="16px" />
        <Skeleton width="15%" height="16px" />
        <Skeleton width="15%" height="16px" />
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <Skeleton width="20%" height="20px" />
          <Skeleton width="15%" height="20px" />
          <Skeleton width="15%" height="20px" />
          <Skeleton width="15%" height="20px" />
          <Skeleton width="15%" height="20px" />
        </div>
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="space-y-4">
      {/* Chart header */}
      <div className="flex justify-between items-center">
        <Skeleton width="200px" height="24px" />
        <div className="flex gap-2">
          <Skeleton width="60px" height="32px" />
          <Skeleton width="60px" height="32px" />
        </div>
      </div>
      
      {/* Chart area */}
      <div className="relative h-64 bg-gray-50 rounded-lg overflow-hidden">
        {/* Simulate chart lines */}
        <svg className="absolute inset-0 w-full h-full">
          <defs>
            <linearGradient id="chartGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#e5e7eb" stopOpacity="0.3" />
              <stop offset="50%" stopColor="#e5e7eb" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#e5e7eb" stopOpacity="0.3" />
            </linearGradient>
          </defs>
          <path
            d="M 0,200 Q 50,150 100,120 T 200,80 T 300,100 T 400,60 T 500,40 T 600,20"
            stroke="url(#chartGradient)"
            strokeWidth="2"
            fill="none"
            className="animate-pulse"
          />
        </svg>
        
        {/* Loading overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-50">
          <LoadingSpinner text="Loading chart data..." />
        </div>
      </div>
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton width="120px" height="20px" />
        <Skeleton width="60px" height="16px" />
      </div>
      <Skeleton width="80%" height="24px" />
      <Skeleton lines={3} />
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <Skeleton width="200px" height="32px" />
        <div className="flex gap-2">
          <Skeleton width="100px" height="40px" />
          <Skeleton width="100px" height="40px" />
        </div>
      </div>
      
      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
      
      {/* Chart and table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartSkeleton />
        <div className="space-y-4">
          <Skeleton width="150px" height="20px" />
          <TableSkeleton rows={4} />
        </div>
      </div>
    </div>
  );
}
