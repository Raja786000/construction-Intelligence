import React, { useState, useEffect } from "react";
import {
  CloudRain,
  Thermometer,
  Wind,
  Droplets,
  AlertTriangle,
  MapPin,
  RefreshCw,
  Sun,
  ShieldCheck,
  Calendar
} from "lucide-react";

export default function WeatherWidget() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWeather();
  }, []);

  const fetchWeather = async () => {
    try {
      setLoading(true);
      const res = await fetch("http://127.0.0.1:8000/api/weather");
      if (res.ok) {
        const data = await res.json();
        setWeather(data);
      }
    } catch (err) {
      console.error("Failed to load weather:", err);
    } finally {
      setLoading(false);
    }
  };

  const w = weather || {
    location: "Hyderabad, Telangana (Site #1)",
    temperature_c: 28.5,
    rainfall_mm: 38.0,
    wind_speed_kmh: 18.5,
    humidity_pct: 78,
    condition: "Rain / Thunderstorm",
    tomorrow_forecast: "Heavy Rain (45mm)",
    tomorrow_rain_alert: true,
    alert_level: "ORANGE_ALERT",
    source: "Site Station Telemetry"
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: "700", color: "#fff", margin: "0 0 4px 0" }}>
            Live Weather Intelligence & Site Environmental Telemetry
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Real-time meteorological monitoring to safeguard concrete curing, crane lifts, and earthwork
          </p>
        </div>

        <button className="btn-secondary-ci" onClick={fetchWeather} disabled={loading}>
          <RefreshCw size={16} className={loading ? "spin" : ""} /> Refresh Weather Feed
        </button>
      </div>

      {/* TOMORROW'S RAIN ALERT (NOTE #7 & #8) */}
      {w.tomorrow_rain_alert && (
        <div style={{
          backgroundColor: "rgba(245, 158, 11, 0.15)",
          border: "1px solid rgba(245, 158, 11, 0.4)",
          borderRadius: "14px",
          padding: "18px 22px",
          marginBottom: "24px",
          display: "flex",
          alignItems: "center",
          gap: "16px"
        }}>
          <div style={{
            width: "44px",
            height: "44px",
            borderRadius: "10px",
            background: "#f59e0b",
            color: "#000",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0
          }}>
            <CloudRain size={26} />
          </div>
          <div>
            <strong style={{ color: "#fff", fontSize: "1.05rem", display: "block" }}>
              ⚠️ SEVERE WEATHER WARNING: Heavy Rain Tomorrow ({w.tomorrow_forecast})
            </strong>
            <p style={{ color: "#fef3c7", fontSize: "0.85rem", marginTop: "2px" }}>
              Elevated precipitation risk for Hyderabad site. High probability of site inundation. Delay scheduled concrete slab pouring and secure external tower crane loads.
            </p>
          </div>
        </div>
      )}

      {/* 4 CORE METEOROLOGICAL TILES (NOTE #7) */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "20px", marginBottom: "28px" }}>
        {/* Temperature */}
        <div className="ci-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <span className="kpi-label">TEMPERATURE</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(245, 158, 11, 0.15)", color: "#fbbf24" }}>
              <Thermometer size={20} />
            </div>
          </div>
          <div className="kpi-value">{w.temperature_c}°C</div>
          <div className="kpi-subtext">Ambient Site Temperature</div>
        </div>

        {/* Rain (Precipitation) */}
        <div className="ci-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <span className="kpi-label">RAINFALL</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(59, 130, 246, 0.15)", color: "#60a5fa" }}>
              <CloudRain size={20} />
            </div>
          </div>
          <div className="kpi-value">{w.rainfall_mm} mm</div>
          <div className="kpi-subtext">Current Precipitation Rate</div>
        </div>

        {/* Wind Speed */}
        <div className="ci-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <span className="kpi-label">WIND SPEED</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(6, 182, 212, 0.15)", color: "#22d3ee" }}>
              <Wind size={20} />
            </div>
          </div>
          <div className="kpi-value">{w.wind_speed_kmh} km/h</div>
          <div className="kpi-subtext">Safe crane limit: &lt; 45 km/h</div>
        </div>

        {/* Humidity */}
        <div className="ci-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
            <span className="kpi-label">HUMIDITY</span>
            <div className="kpi-icon-wrap" style={{ background: "rgba(139, 92, 246, 0.15)", color: "#c084fc" }}>
              <Droplets size={20} />
            </div>
          </div>
          <div className="kpi-value">{w.humidity_pct}%</div>
          <div className="kpi-subtext">Atmospheric Moisture Level</div>
        </div>
      </div>

      {/* SITE CONDITIONS IMPACT TABLE */}
      <div className="ci-card">
        <h3 className="ci-card-title">
          <Calendar size={18} color="#60a5fa" /> Impact on Construction Activities
        </h3>

        <div className="ci-table-wrap">
          <table className="ci-table">
            <thead>
              <tr>
                <th>Site Activity</th>
                <th>Weather Threshold</th>
                <th>Current Status</th>
                <th>Impact & Mitigation Protocol</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Concrete Slab Pouring</strong></td>
                <td>Precipitation &lt; 2.0 mm</td>
                <td>
                  <span className="badge-pill badge-danger">HIGH RISK</span>
                </td>
                <td>Rain dilutes cement-water ratio. Postpone pouring or deploy waterproofing tarpaulins.</td>
              </tr>
              <tr>
                <td><strong>Tower Crane Heavy Lifts</strong></td>
                <td>Wind Speed &lt; 45 km/h</td>
                <td>
                  <span className="badge-pill badge-success">PERMITTED</span>
                </td>
                <td>Wind velocity (18.5 km/h) safely below maximum operational ceiling.</td>
              </tr>
              <tr>
                <td><strong>Scaffolding & Painting</strong></td>
                <td>Humidity &lt; 85%</td>
                <td>
                  <span className="badge-pill badge-warning">MONITORING</span>
                </td>
                <td>High ambient humidity (78%) will increase paint/primer drying time by 4 hours.</td>
              </tr>
              <tr>
                <td><strong>Excavation & Trenching</strong></td>
                <td>Rainfall &lt; 15 mm</td>
                <td>
                  <span className="badge-pill badge-danger">STANDBY</span>
                </td>
                <td>High soil saturation. Activate pit B dewatering sump pumps immediately.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
