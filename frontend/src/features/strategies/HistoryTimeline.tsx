import { FC } from "react";
import { StrategyPerformanceLog, StrategyVersion } from "./types";

interface HistoryTimelineProps {
  versions: StrategyVersion[];
  performance: StrategyPerformanceLog[];
}

const containerStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: "14px",
  fontWeight: 600,
  color: "rgba(255,255,255,0.8)",
};

const timelineItemStyle: React.CSSProperties = {
  borderLeft: "2px solid rgba(100, 126, 255, 0.4)",
  paddingLeft: "12px",
  marginLeft: "4px",
};

const metaStyle: React.CSSProperties = {
  fontSize: "12px",
  color: "rgba(255,255,255,0.55)",
};

export const HistoryTimeline: FC<HistoryTimelineProps> = ({ versions, performance }) => {
  return (
    <div style={containerStyle}>
      <div>
        <div style={sectionTitleStyle}>Version History</div>
        {versions.length === 0 && (
          <div style={metaStyle}>No saved versions yet – defaults are in use.</div>
        )}
        {versions.map((version) => (
          <div key={version.version_number} style={timelineItemStyle}>
            <div style={{ fontSize: "13px", color: "rgba(255,255,255,0.85)", fontWeight: 600 }}>
              v{version.version_number}
            </div>
            <div style={metaStyle}>
              {new Date(version.created_at).toLocaleString()} · {version.changes_summary || "Initial configuration"}
            </div>
            {version.created_by && (
              <div style={metaStyle}>Updated by {version.created_by}</div>
            )}
          </div>
        ))}
      </div>

      <div>
        <div style={sectionTitleStyle}>Recent Performance Logs</div>
        {performance.length === 0 && (
          <div style={metaStyle}>No performance runs recorded yet.</div>
        )}
        {performance.map((log) => (
          <div key={log.id} style={timelineItemStyle}>
            <div style={{ fontSize: "13px", color: "rgba(255,255,255,0.85)", fontWeight: 600 }}>
              {log.run_type.toUpperCase()} · v{log.version_number}
            </div>
            <div style={metaStyle}>{new Date(log.created_at).toLocaleString()}</div>
            {log.notes && <div style={metaStyle}>{log.notes}</div>}
            {log.metrics && (
              <pre
                style={{
                  marginTop: "4px",
                  background: "rgba(15,15,32,0.6)",
                  padding: "8px",
                  borderRadius: "10px",
                  fontSize: "12px",
                  color: "rgba(255,255,255,0.7)",
                  overflowX: "auto",
                }}
              >
                {JSON.stringify(log.metrics, null, 2)}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export type { HistoryTimelineProps };
