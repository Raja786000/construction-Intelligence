import React from "react";

/**
 * A consistent "nothing here yet" placeholder for tables/lists, instead of
 * silently rendering an empty <div> (which reads as a bug, not a state).
 *
 * <EmptyState icon={Bell} title="No alerts yet" subtitle="..." action={{label:"Add", onClick: fn}} />
 */
export default function EmptyState({ icon: Icon, title, subtitle, action }) {
  return (
    <div
      style={{
        textAlign: "center",
        padding: "56px 24px",
        border: "1px dashed var(--border-color, rgba(255,255,255,0.08))",
        borderRadius: "16px",
        color: "var(--text-secondary, #94a3b8)",
      }}
    >
      {Icon && (
        <div
          style={{
            width: "52px",
            height: "52px",
            borderRadius: "14px",
            background: "rgba(148, 163, 184, 0.1)",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: "16px",
          }}
        >
          <Icon size={24} color="var(--text-muted, #64748b)" />
        </div>
      )}
      <h4 style={{ color: "#fff", fontSize: "1.05rem", marginBottom: "6px" }}>{title}</h4>
      {subtitle && (
        <p style={{ fontSize: "0.85rem", maxWidth: "360px", margin: "0 auto 18px" }}>{subtitle}</p>
      )}
      {action && (
        <button className="btn-primary-ci" style={{ margin: "0 auto" }} onClick={action.onClick}>
          {action.label}
        </button>
      )}
    </div>
  );
}
