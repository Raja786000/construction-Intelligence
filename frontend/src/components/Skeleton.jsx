import React from "react";

/** A single shimmering placeholder block. Sizes via props, not classes,
 * so it can stand in for text lines, avatars, or whole cards. */
export function SkeletonBlock({ width = "100%", height = "16px", radius = "6px", style }) {
  return (
    <div
      className="skeleton-ci"
      style={{ width, height, borderRadius: radius, ...style }}
    />
  );
}

/** Placeholder for the KPI card row shown at the top of most pages while
 * their first fetch is in flight. */
export function KpiSkeletonGrid({ count = 4 }) {
  return (
    <div className="kpi-grid">
      {Array.from({ length: count }).map((_, i) => (
        <div className="kpi-card" key={i}>
          <div className="kpi-header">
            <SkeletonBlock width="90px" height="12px" />
            <SkeletonBlock width="38px" height="38px" radius="10px" />
          </div>
          <SkeletonBlock width="70%" height="28px" style={{ marginBottom: "8px" }} />
          <SkeletonBlock width="50%" height="12px" />
        </div>
      ))}
    </div>
  );
}

/** Placeholder for a table's rows, matching ci-table's row height roughly. */
export function TableSkeletonRows({ rows = 4, columns = 4 }) {
  return (
    <>
      {Array.from({ length: rows }).map((_, r) => (
        <tr key={r}>
          {Array.from({ length: columns }).map((__, c) => (
            <td key={c}>
              <SkeletonBlock height="14px" width={c === 0 ? "70%" : "50%"} />
            </td>
          ))}
        </tr>
      ))}
    </>
  );
}
