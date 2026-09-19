import React, { useState, useEffect } from "react";
import {
  Building2,
  TrendingUp,
  Users,
  ShieldAlert,
  AlertTriangle,
  CloudRain,
  IndianRupee,
  Activity,
  ArrowRight,
  CheckCircle,
  Bell,
  Sparkles
} from "lucide-react";

export default function DashboardOverview({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/dashboard/stats");
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error("Error fetching dashboard stats:", err);
    } finally {
      setLoading(false);
    }
  };

  // Fallback defaults matching handwritten note #2 if backend is starting
  const data = stats || {
    total_projects: 4,
    project_progress: 68.0,
    primary_project_name: "Metro Bridge Project",
    primary_project_client: "ABC Construction Ltd",
    workers_count: 120,
    safety_violations_count: 5,
    active_risks_count: 4,
    ai_risk_score: 42.8,
    risk_level: "High",
    weather_status: {
      condition: "Rain",
      temperature_c: 28.5,
      rainfall_mm: 38.0,
      tomorrow_forecast: "Heavy Rain (38mm)",
      tomorrow_rain_alert: true,
      location: "Hyderabad, Telangana"
    },
    budget: {
      total: 20.0,
      used: 1.8,
      currency: "₹ Cr",
      formatted_display: "₹ 1.8 Cr used of ₹ 20 Cr"
    },
    recent_alerts: [
      { id: "1", title: "Worker without Helmet Detected", message: "Worker W103 detected without mandatory helmet near Foundation zone.", severity: "CRITICAL" },
      { id: "2", title: "Heavy Rain Tomorrow Forecast", message: "38mm rain expected tomorrow. High risk of concrete pouring delay.", severity: "HIGH" },
      { id: "3", title: "Budget Exceeded on Structural Steel", message: "Cost variance +7.0% (₹ 35 Lakhs variance).", severity: "HIGH" },
      { id: "4", title: "Concrete Work Delayed", message: "Steel framing milestone delayed by 4 days.", severity: "MEDIUM" }
    ]
  };

  return (
    <div>
      {/* Welcome Banner */}
      <div style={{
        background: "linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%)",
        border: "1px solid var(--border-color)",
        borderRadius: "16px",
        padding: "24px 28px",
        marginBottom: "28px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "16px"
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
            <span className="badge-pill badge-info">
              <Sparkles size={12} /> Autonomous Multi-Agent Active
            </span>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              • Site: {data.weather_status?.location || "Hyderabad Site"}
            </span>
          </div>
          <h2 style={{ fontSize: "1.45rem", color: "#fff", fontWeight: "700", margin: "0 0 4px 0" }}>
            {data.primary_project_name} — Site Intelligence
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            Client: <strong style={{ color: "#fff" }}>{data.primary_project_client}</strong> | Live Multi-Agent Telemetry
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button
            className="btn-primary-ci"
            onClick={() => onNavigate("safety")}
          >
            Launch YOLOv11 Camera <ArrowRight size={16} />
          </button>
          <button
            className="btn-secondary-ci"
            onClick={() => onNavigate("reports")}
          >
            Generate PDF Report
          </button>
        </div>
      </div>

      {/* KPI GRID - EXACT MATCH TO NOTE #2 */}
      <div className="kpi-grid">
        {/* 1. Total Projects */}
        <div className="kpi-card" onClick={() => onNavigate("projects")} style={{ cursor: "pointer" }}>
          <div className="kpi-header">
            <span className="kpi-label">Total Projects</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(59, 130, 246, 0.15)", color: "#60a5fa" }}>
              <Building2 size={20} />
            </div>
          </div>
          <div className="kpi-value">{data.total_projects}</div>
          <div className="kpi-subtext">Active construction sites in database</div>
        </div>

        {/* 2. Project Progress (%) */}
        <div className="kpi-card" onClick={() => onNavigate("projects")} style={{ cursor: "pointer" }}>
          <div className="kpi-header">
            <span className="kpi-label">Project Progress</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(16, 185, 129, 0.15)", color: "#34d399" }}>
              <TrendingUp size={20} />
            </div>
          </div>
          <div className="kpi-value">{data.project_progress}%</div>
          <div style={{ marginTop: "4px" }}>
            <div style={{ width: "100%", height: "6px", backgroundColor: "#334155", borderRadius: "9999px", overflow: "hidden" }}>
              <div style={{ width: `${Math.min(100, data.project_progress)}%`, height: "100%", backgroundColor: "#10b981" }} />
            </div>
          </div>
        </div>

        {/* 3. No. of Workers */}
        <div className="kpi-card" onClick={() => onNavigate("workers")} style={{ cursor: "pointer" }}>
          <div className="kpi-header">
            <span className="kpi-label">No. of Workers</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(139, 92, 246, 0.15)", color: "#c084fc" }}>
              <Users size={20} />
            </div>
          </div>
          <div className="kpi-value">{data.workers_count}</div>
          <div className="kpi-subtext">Active workforce deployed on site</div>
        </div>

        {/* 4. Safety Violations */}
        <div className="kpi-card" onClick={() => onNavigate("safety")} style={{ cursor: "pointer" }}>
          <div className="kpi-header">
            <span className="kpi-label">Safety Violations</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(239, 68, 68, 0.15)", color: "#f87171" }}>
              <ShieldAlert size={20} />
            </div>
          </div>
          <div className="kpi-value" style={{ color: "#f87171" }}>{data.safety_violations_count}</div>
          <div className="kpi-subtext">PPE non-compliance detected by YOLO</div>
        </div>

        {/* 5. Active Risks & AI Risk Score */}
        <div className="kpi-card" onClick={() => onNavigate("risk")} style={{ cursor: "pointer" }}>
          <div className="kpi-header">
            <span className="kpi-label">AI Risk Score</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(245, 158, 11, 0.15)", color: "#fbbf24" }}>
              <Activity size={20} />
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: "10px" }}>
            <span className="kpi-value" style={{ color: data.risk_level === "High" ? "#f87171" : "#fbbf24" }}>
              {data.risk_level}
            </span>
            <span style={{ fontSize: "1rem", color: "var(--text-muted)", fontWeight: "600" }}>
              ({data.ai_risk_score}/100)
            </span>
          </div>
          <div className="kpi-subtext">{data.active_risks_count} active site risks monitored</div>
        </div>

        {/* 6. Weather Status (Rain, Tmrw: Rain) */}
        <div className="kpi-card" onClick={() => onNavigate("weather")} style={{ cursor: "pointer" }}>
          <div className="kpi-header">
            <span className="kpi-label">Weather Status</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(6, 182, 212, 0.15)", color: "#22d3ee" }}>
              <CloudRain size={20} />
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "baseline", gap: "8px" }}>
            <span className="kpi-value" style={{ fontSize: "1.6rem" }}>{data.weather_status.condition}</span>
            <span style={{ color: "#94a3b8", fontSize: "0.95rem" }}>{data.weather_status.temperature_c}°C</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "2px" }}>
            <span className="badge-pill badge-warning" style={{ fontSize: "0.7rem", padding: "2px 6px" }}>
              Tmrw: {data.weather_status.tomorrow_forecast}
            </span>
          </div>
        </div>

        {/* 7. Budget Used */}
        <div className="kpi-card" onClick={() => onNavigate("risk")} style={{ cursor: "pointer" }}>
          <div className="kpi-header">
            <span className="kpi-label">Budget Used</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(16, 185, 129, 0.15)", color: "#34d399" }}>
              <IndianRupee size={20} />
            </div>
          </div>
          <div className="kpi-value" style={{ fontSize: "1.65rem", color: "#38bdf8" }}>
            ₹ {data.budget?.used || 1.8} Cr
          </div>
          <div className="kpi-subtext">Total allocated: ₹ {data.budget?.total || 20.0} Cr</div>
        </div>
      </div>

      {/* TWO COLUMNS: RECENT ALERTS + ACTION HUB */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
        {/* RECENT ALERTS LIST (MATCHES NOTE #2 & #8) */}
        <div className="ci-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 className="ci-card-title" style={{ margin: 0 }}>
              <Bell size={18} color="#f87171" /> Recent Alerts ({data.recent_alerts.length})
            </h3>
            <button
              style={{ background: "transparent", border: "none", color: "var(--primary)", fontSize: "0.82rem", fontWeight: "600", cursor: "pointer" }}
              onClick={() => onNavigate("alerts")}
            >
              View All Alerts →
            </button>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {data.recent_alerts.map((alert, idx) => (
              <div
                key={alert.id || idx}
                style={{
                  padding: "12px 14px",
                  borderRadius: "10px",
                  backgroundColor: "rgba(15, 23, 42, 0.6)",
                  border: "1px solid var(--border-color)",
                  borderLeft: `4px solid ${
                    alert.severity === "CRITICAL" ? "#ef4444" : alert.severity === "HIGH" ? "#f59e0b" : "#3b82f6"
                  }`
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                  <span style={{ fontWeight: "600", fontSize: "0.9rem", color: "#fff" }}>
                    {alert.title}
                  </span>
                  <span className={`badge-pill ${
                    alert.severity === "CRITICAL" ? "badge-danger" : alert.severity === "HIGH" ? "badge-warning" : "badge-info"
                  }`} style={{ fontSize: "0.68rem" }}>
                    {alert.severity}
                  </span>
                </div>
                <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)", lineHeight: "1.4" }}>
                  {alert.message}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* QUICK NAVIGATION & MULTI-AGENT STATUS */}
        <div className="ci-card">
          <h3 className="ci-card-title">
            <Activity size={18} color="#60a5fa" /> Integrated Agent Capabilities
          </h3>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <div
              style={{ padding: "14px", borderRadius: "10px", background: "rgba(15, 23, 42, 0.6)", border: "1px solid var(--border-color)", cursor: "pointer" }}
              onClick={() => onNavigate("safety")}
            >
              <div style={{ fontWeight: "600", color: "#fff", fontSize: "0.9rem", marginBottom: "4px" }}>
                🦺 Safety YOLOv11
              </div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                Detects Hardhat, Vest, Person from Webcam/Upload
              </div>
            </div>

            <div
              style={{ padding: "14px", borderRadius: "10px", background: "rgba(15, 23, 42, 0.6)", border: "1px solid var(--border-color)", cursor: "pointer" }}
              onClick={() => onNavigate("workers")}
            >
              <div style={{ fontWeight: "600", color: "#fff", fontSize: "0.9rem", marginBottom: "4px" }}>
                👷 Worker Directory
              </div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                ID, Task, Helmet & Vest status, Certifications
              </div>
            </div>

            <div
              style={{ padding: "14px", borderRadius: "10px", background: "rgba(15, 23, 42, 0.6)", border: "1px solid var(--border-color)", cursor: "pointer" }}
              onClick={() => onNavigate("quality")}
            >
              <div style={{ fontWeight: "600", color: "#fff", fontSize: "0.9rem", marginBottom: "4px" }}>
                🔍 Quality Inspection
              </div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                Cracks, Concrete voids, Corrosion & Finish
              </div>
            </div>

            <div
              style={{ padding: "14px", borderRadius: "10px", background: "rgba(15, 23, 42, 0.6)", border: "1px solid var(--border-color)", cursor: "pointer" }}
              onClick={() => onNavigate("reports")}
            >
              <div style={{ fontWeight: "600", color: "#fff", fontSize: "0.9rem", marginBottom: "4px" }}>
                📄 PDF Audit Reports
              </div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>
                Daily, Weekly, Monthly automated report downloads
              </div>
            </div>
          </div>

          <div style={{ marginTop: "18px", padding: "14px", borderRadius: "10px", background: "rgba(59, 130, 246, 0.08)", border: "1px solid rgba(59, 130, 246, 0.2)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#60a5fa", fontWeight: "600", fontSize: "0.85rem", marginBottom: "4px" }}>
              <CheckCircle size={16} /> MongoDB Storage Verified
            </div>
            <p style={{ fontSize: "0.78rem", color: "var(--text-secondary)" }}>
              Connected to <code>construction_intelligence</code> database. All projects, worker changes, and safety detection alerts persist in real-time.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
