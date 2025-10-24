import "lightweight-charts";

declare module "lightweight-charts" {
  interface IChartApi {
    addCandlestickSeries(options?: Record<string, unknown>): unknown;
    addLineSeries(options?: Record<string, unknown>): unknown;
    addAreaSeries(options?: Record<string, unknown>): unknown;
    addHistogramSeries(options?: Record<string, unknown>): unknown;
  }
}
