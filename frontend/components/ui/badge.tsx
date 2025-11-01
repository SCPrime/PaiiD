import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-slate-950 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-teal-600/90 text-white shadow hover:bg-teal-700",
        secondary: "border-transparent bg-slate-700/80 text-slate-200 hover:bg-slate-600",
        destructive: "border-transparent bg-red-600/90 text-white shadow hover:bg-red-700",
        outline: "text-slate-300 border-slate-600",
        success: "border-transparent bg-green-600/90 text-white shadow",
        warning: "border-transparent bg-orange-600/90 text-white shadow",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
