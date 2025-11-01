import { Power } from "lucide-react";
import { useState } from "react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "./ui/alert-dialog";

export function KillSwitch() {
  const [isActivating, setIsActivating] = useState(false);

  const handleKillSwitch = async () => {
    setIsActivating(true);
    try {
      const response = await fetch("/api/proxy/api/kill-switch/activate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        alert("🛑 Kill switch activated! All trading operations paused.");
      } else {
        alert("❌ Failed to activate kill switch. Check connection.");
      }
    } catch (error) {
      console.error("Kill switch error:", error);
      alert("❌ Kill switch request failed. Check backend connection.");
    } finally {
      setIsActivating(false);
    }
  };

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <button
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-lg
                     bg-red-600/90 backdrop-blur-md border border-red-500/50
                     text-white font-semibold text-sm
                     hover:bg-red-700 hover:scale-105
                     focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2
                     transition-all duration-200
                     shadow-lg shadow-red-500/30"
          aria-label="Emergency kill switch - pause all trading"
        >
          <Power className="w-4 h-4" />
          <span>KILL SWITCH</span>
        </button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className="text-red-400 flex items-center gap-2">
            <Power className="w-5 h-5" />
            Emergency Kill Switch
          </AlertDialogTitle>
          <AlertDialogDescription className="text-slate-300">
            This will immediately pause all automated trading operations, cancel pending orders, and
            halt the scheduler. Manual intervention will be required to resume trading.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div className="my-4 p-4 bg-red-950/50 border border-red-500/30 rounded-md">
          <p className="text-sm text-red-200 font-semibold">⚠️ Critical Action</p>
          <p className="text-xs text-slate-400 mt-1">
            This action cannot be undone automatically. You will need to manually resume operations
            from the Settings panel.
          </p>
        </div>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleKillSwitch}
            disabled={isActivating}
            className="bg-red-600 hover:bg-red-700"
          >
            {isActivating ? "Activating..." : "Activate Kill Switch"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
