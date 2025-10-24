import { FC } from "react";

type FeatureDefinition = {
  key: string;
  label: string;
  description: string;
};

interface FeatureToggleListProps {
  features: FeatureDefinition[];
  values: Record<string, boolean>;
  onChange: (key: string, value: boolean) => void;
  disabled?: boolean;
}

const containerStyle: React.CSSProperties = {
  display: "grid",
  gap: "12px",
};

const rowStyle: React.CSSProperties = {
  display: "flex",
  gap: "12px",
  alignItems: "flex-start",
};

const checkboxStyle: React.CSSProperties = {
  width: "18px",
  height: "18px",
  marginTop: "2px",
};

export const FeatureToggleList: FC<FeatureToggleListProps> = ({
  features,
  values,
  onChange,
  disabled = false,
}) => {
  return (
    <div style={containerStyle}>
      {features.map((feature) => (
        <div key={feature.key} style={rowStyle}>
          <input
            type="checkbox"
            style={checkboxStyle}
            checked={Boolean(values[feature.key])}
            onChange={(event) => onChange(feature.key, event.target.checked)}
            disabled={disabled}
          />
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <span style={{ fontSize: "14px", color: "rgba(255,255,255,0.85)", fontWeight: 600 }}>
              {feature.label}
            </span>
            <span style={{ fontSize: "12px", color: "rgba(255,255,255,0.6)" }}>
              {feature.description}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

export type { FeatureToggleListProps, FeatureDefinition };
