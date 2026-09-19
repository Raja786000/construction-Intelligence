import React, { useState, useEffect } from "react";
import {
  LayoutDashboard,
  Building2,
  Users,
  ShieldCheck,
  Search,
  Activity,
  CloudRain,
  Bell,
  FileText,
  LogOut,
  HardHat,
  ChevronDown,
  UserCheck
} from "lucide-react";

// Module Components
import LoginModal from "./components/LoginModal";
import DashboardOverview from "./components/DashboardOverview";
import ProjectManagement from "./components/ProjectManagement";
import WorkerManagement from "./components/WorkerManagement";
import SafetySurveillance from "./components/SafetySurveillance";
import QualityMonitoring from "./components/QualityMonitoring";
import RiskPrediction from "./components/RiskPrediction";
import WeatherWidget from "./components/WeatherWidget";
import AlertsCenter from "./components/AlertsCenter";
import ReportConsolidator from "./components/ReportConsolidator";

export default function App() {
  // Authentication State (Note #1)
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState("dashboard"); // "dashboard", "projects", "workers", "safety", "quality", "risk", "weather", "alerts", "reports"
  
  // Shared Site & Projects State
  const [projects, setProjects] = useState([]);
  const [activeProjectId, setActiveProjectId] = useState("PROJ-METRO");
  const [alertsCount, setAlertsCount] = useState(5);
  const [siteWeather, setSiteWeather] = useState(null);

  // Initialize Session
  useEffect(() => {
    const savedUser = localStorage.getItem("ci_user");
    if (savedUser) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem("ci_user");
      }
    }
    fetchProjects();
    fetchWeather();
    fetchAlertsCount();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/projects");
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
        if (data.length > 0 && !data.find(p => (p._id || p.id) === activeProjectId)) {
          setActiveProjectId(data[0]._id || data[0].id);
        }
      }
    } catch (err) {
      console.warn("Could not load projects on mount:", err);
    }
  };

  const fetchWeather = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/weather");
      if (res.ok) {
        const data = await res.json();
        setSiteWeather(data);
      }
    } catch (err) {
      // Weather fallback
    }
  };

  const fetchAlertsCount = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/alerts?unresolved_only=true");
      if (res.ok) {
        const data = await res.json();
        setAlertsCount(data.length);
      }
    } catch (err) {
      // Use default
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("ci_user");
    localStorage.removeItem("ci_token");
    setCurrentUser(null);
  };

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "projects", label: "Project Management", icon: Building2 },
    { id: "workers", label: "Worker Management", icon: Users },
    { id: "safety", label: "Safety Detection (YOLO)", icon: HardHat },
    { id: "quality", label: "Quality Monitoring", icon: Search },
    { id: "risk", label: "Risk Prediction (ML)", icon: Activity },
    { id: "weather", label: "Weather Integration", icon: CloudRain },
    { id: "alerts", label: "Alerts & Notifications", icon: Bell, badge: alertsCount },
    { id: "reports", label: "Executive Reports (PDF)", icon: FileText }
  ];

  // If not logged in, present the Login Module (Note #1)
  if (!currentUser) {
    return <LoginModal onLoginSuccess={(user) => setCurrentUser(user)} />;
  }

  return (
    <div className="app-container">
      {/* SIDEBAR NAVIGATION (Exact Site Map from Handwritten Note #3) */}
      <aside className="app-sidebar">
        {/* Brand Header */}
        <div className="sidebar-brand">
          <div className="brand-icon">
            <HardHat size={22} />
          </div>
          <div className="brand-text">
            <div className="brand-title">Construction AI</div>
            <div className="brand-subtitle">Intelligence Hub v3.0</div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                className={`nav-item-btn ${isActive ? "active" : ""}`}
                onClick={() => setActiveTab(item.id)}
              >
                <Icon size={18} />
                <span className="nav-text">{item.label}</span>
                {item.badge > 0 && <span className="nav-badge">{item.badge}</span>}
              </button>
            );
          })}
        </nav>

        {/* Sidebar Footer User Info */}
        <div className="sidebar-footer">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                background: "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#fff",
                fontWeight: "700",
                fontSize: "0.85rem"
              }}>
                {currentUser.name ? currentUser.name[0] : "A"}
              </div>
              <div className="sidebar-footer-text">
                <div style={{ fontSize: "0.85rem", fontWeight: "600", color: "#fff" }}>
                  {currentUser.name || "Site Admin"}
                </div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                  {currentUser.role || "Administrator"}
                </div>
              </div>
            </div>

            <button
              title="Sign Out"
              style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer", padding: "6px" }}
              onClick={handleLogout}
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>

      {/* MAIN VIEWPORT */}
      <main className="app-main">
        {/* Top Header Bar */}
        <header className="app-header">
          <div className="header-title-wrap">
            <h1>
              {navItems.find((n) => n.id === activeTab)?.label}
            </h1>
            <p>Construction Intelligence Enterprise Hub</p>
          </div>

          <div className="header-actions">
            {/* Quick Weather Capsule */}
            {siteWeather && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  background: "rgba(30, 41, 59, 0.6)",
                  border: "1px solid var(--border-color)",
                  borderRadius: "9999px",
                  padding: "5px 14px",
                  cursor: "pointer",
                  fontSize: "0.82rem"
                }}
                onClick={() => setActiveTab("weather")}
              >
                <CloudRain size={16} color="#38bdf8" />
                <span style={{ color: "#fff", fontWeight: "600" }}>{siteWeather.temperature_c}°C</span>
                <span style={{ color: "var(--text-muted)" }}>•</span>
                <span style={{ color: "#38bdf8" }}>{siteWeather.condition}</span>
                {siteWeather.tomorrow_rain_alert && (
                  <span className="badge-pill badge-warning" style={{ fontSize: "0.68rem", padding: "1px 6px" }}>
                    Tmrw: Rain
                  </span>
                )}
              </div>
            )}

            {/* Active Project Selector */}
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <select
                className="form-control-ci"
                style={{ width: "auto", padding: "6px 14px", fontSize: "0.85rem", height: "36px" }}
                value={activeProjectId}
                onChange={(e) => setActiveProjectId(e.target.value)}
              >
                {projects.map((p) => (
                  <option key={p._id || p.id} value={p._id || p.id}>
                    {p.name} ({p.budget_currency || "₹"} {p.budget || 20} Cr)
                  </option>
                ))}
              </select>
            </div>

            {/* Alerts Bell Shortcut */}
            <button
              style={{
                background: "rgba(30, 41, 59, 0.6)",
                border: "1px solid var(--border-color)",
                borderRadius: "10px",
                width: "36px",
                height: "36px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: alertsCount > 0 ? "#f87171" : "#94a3b8",
                cursor: "pointer",
                position: "relative"
              }}
              onClick={() => setActiveTab("alerts")}
              title="View Alerts"
            >
              <Bell size={18} />
              {alertsCount > 0 && (
                <span style={{
                  position: "absolute",
                  top: "-4px",
                  right: "-4px",
                  width: "10px",
                  height: "10px",
                  backgroundColor: "#ef4444",
                  borderRadius: "50%",
                  border: "2px solid #0f172a"
                }} />
              )}
            </button>
          </div>
        </header>

        {/* Content Body Router */}
        <div className="content-wrapper">
          {activeTab === "dashboard" && (
            <DashboardOverview onNavigate={(tab) => setActiveTab(tab)} />
          )}

          {activeTab === "projects" && (
            <ProjectManagement
              activeProject={activeProjectId}
              setActiveProject={setActiveProjectId}
            />
          )}

          {activeTab === "workers" && (
            <WorkerManagement />
          )}

          {activeTab === "safety" && (
            <SafetySurveillance />
          )}

          {activeTab === "quality" && (
            <QualityMonitoring />
          )}

          {activeTab === "risk" && (
            <RiskPrediction />
          )}

          {activeTab === "weather" && (
            <WeatherWidget />
          )}

          {activeTab === "alerts" && (
            <AlertsCenter />
          )}

          {activeTab === "reports" && (
            <ReportConsolidator
              projects={projects}
              activeProject={activeProjectId}
            />
          )}
        </div>
      </main>
    </div>
  );
}