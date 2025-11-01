import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// PaiiD glassmorphic variants for shadcn components
export const glassVariants = {
  card: "bg-slate-800/80 backdrop-blur-md border border-white/10 rounded-xl",
  dialog: "bg-slate-900/90 backdrop-blur-lg border border-teal-500/30 rounded-2xl",
  popover: "bg-slate-800/90 backdrop-blur-sm border border-white/20 rounded-xl",
  input: "bg-slate-900/90 backdrop-blur-sm border border-teal-500/30 rounded-md",
};
