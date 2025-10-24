import { MonitorDashboard } from "@/components/MonitorDashboard";

/**
 * Monitor Page
 *
 * Displays GitHub repository monitoring dashboard with real-time metrics
 */
export default function MonitorPage() {
  return (
    <div className="container mx-auto px-4 py-6 max-w-7xl">
      <MonitorDashboard />
    </div>
  );
}

export const metadata = {
  title: "Repository Monitor | PaiiD",
  description: "Real-time GitHub repository activity monitoring and metrics",
};
