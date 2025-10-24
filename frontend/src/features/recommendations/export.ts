import { Recommendation } from "./types";

interface ExportOptions {
  fileName?: string;
  download?: boolean;
}

const escapeCsv = (value: unknown): string => {
  if (value === null || value === undefined) return "";
  const stringValue = String(value);
  if (/[",\n]/.test(stringValue)) {
    return `"${stringValue.replace(/"/g, '""')}"`;
  }
  return stringValue;
};

export const exportRecommendationsToCsv = (
  recommendations: Recommendation[],
  options: ExportOptions = {}
): string => {
  const headers = [
    "Symbol",
    "Action",
    "Confidence",
    "Risk",
    "Volatility",
    "Momentum",
    "Score",
    "Reason",
  ];

  const rows = recommendations.map((rec) => [
    rec.symbol,
    rec.action,
    rec.confidence.toFixed(2),
    rec.risk ?? "",
    rec.volatility?.volatility_class ?? "",
    rec.momentum?.trend_alignment ?? "",
    rec.score.toFixed(2),
    rec.reason ?? "",
  ]);

  const csv = [headers, ...rows].map((row) => row.map(escapeCsv).join(",")).join("\n");

  if (
    options.download !== false &&
    typeof window !== "undefined" &&
    typeof document !== "undefined"
  ) {
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", options.fileName ?? "recommendations.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  return csv;
};
