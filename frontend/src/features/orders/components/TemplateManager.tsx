"use client";
import { useMemo, useState } from "react";

import { theme } from "../../../styles/theme";
import { OrderTemplateResponse } from "../types";

interface TemplateManagerProps {
  templates: OrderTemplateResponse[];
  onApplyTemplate: (template: OrderTemplateResponse) => void;
  onCreateTemplate: (name: string, description: string | null) => Promise<void> | void;
  onDeleteTemplate: (templateId: number) => Promise<void> | void;
  onRefresh?: () => void;
  busy?: boolean;
  createOpen?: boolean;
  onCreateOpenChange?: (open: boolean) => void;
}

export function TemplateManager({
  templates,
  onApplyTemplate,
  onCreateTemplate,
  onDeleteTemplate,
  onRefresh,
  busy = false,
  createOpen,
  onCreateOpenChange,
}: TemplateManagerProps) {
  const [search, setSearch] = useState("");
  const [internalShowCreate, setInternalShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);

  const isControlled = typeof createOpen === "boolean";
  const showCreate = isControlled ? !!createOpen : internalShowCreate;

  const setShowCreate = (open: boolean) => {
    if (isControlled) {
      onCreateOpenChange?.(open);
    } else {
      setInternalShowCreate(open);
    }
  };

  const filtered = useMemo(() => {
    if (!search.trim()) return templates;
    const query = search.trim().toLowerCase();
    return templates.filter((template) =>
      [template.name, template.symbol, template.description]
        .filter(Boolean)
        .some((value) => value!.toLowerCase().includes(query)),
    );
  }, [templates, search]);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim()) {
      setFeedback("Template name is required");
      return;
    }

    try {
      await onCreateTemplate(name.trim(), description.trim() ? description.trim() : null);
      setFeedback("Template saved successfully");
      setName("");
      setDescription("");
      setShowCreate(false);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to save template";
      setFeedback(message);
    }
  }

  return (
    <section
      style={{
        padding: theme.spacing.lg,
        background: theme.background.input,
        border: `1px solid ${theme.colors.border}`,
        borderRadius: theme.borderRadius.lg,
        marginBottom: theme.spacing.xl,
        display: "flex",
        flexDirection: "column",
        gap: theme.spacing.md,
      }}
    >
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: theme.spacing.md,
          flexWrap: "wrap",
        }}
      >
        <div>
          <h3 style={{ margin: 0, fontSize: "18px", fontWeight: 600 }}>Order Templates</h3>
          <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "13px" }}>
            Save frequently used order setups and re-apply them instantly (Ctrl + S to save current draft).
          </p>
        </div>
        <div style={{ display: "flex", gap: theme.spacing.sm }}>
          {onRefresh && (
            <button
              onClick={onRefresh}
              style={{
                padding: "8px 14px",
                borderRadius: theme.borderRadius.sm,
                border: `1px solid ${theme.colors.border}`,
                background: theme.background.card,
                color: theme.colors.text,
                cursor: "pointer",
              }}
            >
              Refresh
            </button>
          )}
          <button
            onClick={() => {
              setShowCreate(!showCreate);
              setFeedback(null);
            }}
            style={{
              padding: "8px 14px",
              borderRadius: theme.borderRadius.sm,
              border: "none",
              background: theme.colors.primary,
              color: "white",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {showCreate ? "Close" : "Save Current"}
          </button>
        </div>
      </header>

      {showCreate && (
        <form
          onSubmit={handleCreate}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: theme.spacing.sm,
            padding: theme.spacing.md,
            background: theme.background.card,
            borderRadius: theme.borderRadius.md,
            border: `1px solid ${theme.colors.border}`,
          }}
        >
          <label style={{ display: "flex", flexDirection: "column", gap: theme.spacing.xs }}>
            <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>Template name</span>
            <input
              type="text"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="e.g. SPY Bracket Entry"
              style={{
                padding: "10px 12px",
                borderRadius: theme.borderRadius.sm,
                border: `1px solid ${theme.colors.border}`,
                background: theme.background.input,
                color: theme.colors.text,
              }}
            />
          </label>
          <label style={{ display: "flex", flexDirection: "column", gap: theme.spacing.xs }}>
            <span style={{ fontSize: "13px", color: theme.colors.textMuted }}>Description (optional)</span>
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Stops, targets, or context for future reference"
              rows={3}
              style={{
                padding: "10px 12px",
                borderRadius: theme.borderRadius.sm,
                border: `1px solid ${theme.colors.border}`,
                background: theme.background.input,
                color: theme.colors.text,
                resize: "vertical",
              }}
            />
          </label>
          <div style={{ display: "flex", gap: theme.spacing.sm }}>
            <button
              type="submit"
              disabled={busy}
              style={{
                padding: "10px 18px",
                borderRadius: theme.borderRadius.sm,
                border: "none",
                background: theme.colors.primary,
                color: "white",
                fontWeight: 600,
                cursor: busy ? "wait" : "pointer",
              }}
            >
              Save Template
            </button>
            <button
              type="button"
              onClick={() => {
                setShowCreate(false);
                setFeedback(null);
              }}
              style={{
                padding: "10px 18px",
                borderRadius: theme.borderRadius.sm,
                border: `1px solid ${theme.colors.border}`,
                background: theme.background.card,
                color: theme.colors.text,
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
          </div>
          {feedback && (
            <p style={{ margin: 0, color: feedback.includes("successfully") ? theme.colors.success : theme.colors.danger }}>
              {feedback}
            </p>
          )}
        </form>
      )}

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: theme.spacing.md,
        }}
      >
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search templates by name, symbol, or description"
          style={{
            padding: "10px 12px",
            borderRadius: theme.borderRadius.sm,
            border: `1px solid ${theme.colors.border}`,
            background: theme.background.card,
            color: theme.colors.text,
          }}
        />

        <div style={{ display: "flex", flexDirection: "column", gap: theme.spacing.sm, maxHeight: "260px", overflowY: "auto" }}>
          {filtered.length === 0 ? (
            <div style={{ color: theme.colors.textMuted, textAlign: "center", padding: theme.spacing.lg }}>
              No templates found. Create one to speed up complex order entry.
            </div>
          ) : (
            filtered.map((template) => (
              <article
                key={template.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: theme.spacing.md,
                  padding: theme.spacing.md,
                  borderRadius: theme.borderRadius.md,
                  border: `1px solid ${theme.colors.border}`,
                  background: theme.background.card,
                }}
              >
                <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: theme.spacing.xs }}>
                  <div style={{ display: "flex", gap: theme.spacing.xs, alignItems: "center", flexWrap: "wrap" }}>
                    <strong>{template.name}</strong>
                    <span style={{ color: theme.colors.textMuted, fontSize: "12px" }}>
                      {template.symbol} · {template.side.toUpperCase()} · {template.order_type.toUpperCase()} · {template.order_class.toUpperCase()}
                    </span>
                  </div>
                  {template.description && (
                    <p style={{ margin: 0, color: theme.colors.textMuted, fontSize: "13px" }}>{template.description}</p>
                  )}
                </div>
                <div style={{ display: "flex", gap: theme.spacing.sm }}>
                  <button
                    onClick={() => onApplyTemplate(template)}
                    style={{
                      padding: "8px 14px",
                      borderRadius: theme.borderRadius.sm,
                      border: "none",
                      background: theme.colors.secondary,
                      color: "white",
                      fontWeight: 600,
                      cursor: "pointer",
                    }}
                  >
                    Apply
                  </button>
                  <button
                    onClick={() => onDeleteTemplate(template.id)}
                    style={{
                      padding: "8px 14px",
                      borderRadius: theme.borderRadius.sm,
                      border: `1px solid ${theme.colors.danger}`,
                      background: "transparent",
                      color: theme.colors.danger,
                      cursor: "pointer",
                    }}
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))
          )}
        </div>
      </div>
    </section>
  );
}
