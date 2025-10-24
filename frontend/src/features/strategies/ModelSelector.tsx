import { FC } from "react";

interface ModelOption {
  value: string;
  label: string;
  description: string;
  latency: string;
}

interface ModelSelectorProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  options: ModelOption[];
  disabled?: boolean;
}

const selectStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: "12px",
  border: "1px solid rgba(255,255,255,0.15)",
  background: "rgba(9, 9, 21, 0.6)",
  color: "#f8f9ff",
  fontSize: "14px",
  fontFamily: "inherit",
};

export const ModelSelector: FC<ModelSelectorProps> = ({
  label = "Inference model",
  value,
  onChange,
  options,
  disabled = false,
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      <label style={{ fontSize: "14px", color: "rgba(255,255,255,0.8)" }}>{label}</label>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={disabled}
        style={selectStyle}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label} · {option.latency}
          </option>
        ))}
      </select>
      <div style={{ fontSize: "12px", color: "rgba(255,255,255,0.6)" }}>
        {options.find((option) => option.value === value)?.description || ""}
      </div>
    </div>
  );
};

export type { ModelOption, ModelSelectorProps };
