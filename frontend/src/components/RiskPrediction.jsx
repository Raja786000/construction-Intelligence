import React, { useState, useEffect } from "react";
import {
  TrendingDown,
  Clock,
  IndianRupee,
  Cpu,
  AlertTriangle,
  ShieldCheck,
  Zap,
  Sliders,
  Sparkles
} from "lucide-react";

export default function RiskPrediction() {
  const [activeTab, setActiveTab] = useState("schedule"); // "schedule", "cost", "equipment"
  
  // Schedule Predictor States
  const [plannedDays, setPlannedDays] = useState(30);
  const [completedMilestones, setCompletedMilestones] = useState(7);
  const [totalMilestones, setTotalMilestones] = useState(12);
  const [rainfallMm, setRainfallMm] = useState(38.0);
  const [activeWorkers, setActiveWorkers] = useState(64);
  const [schedulePred, setSchedulePred] = useState(null);

  // Cost Predictor States
  const [budgetCr, setBudgetCr] = useState(20.0);
  const [spentCr, setSpentCr] = useState(1.8);
  const [delayDays, setDelayDays] = useState(3.5);
  const [materialRisk, setMaterialRisk] = useState("HIGH");
  const [costPred, setCostPred] = useState(null);

  // Equipment Predictor States
  const [operatingHours, setOperatingHours] = useState(1420.5);
  const [vibrationMmS, setVibrationMmS] = useState(8.4);
  const [daysSinceMaint, setDaysSinceMaint] = useState(24);
  const [equipPred, setEquipPred] = useState(null);

  useEffect(() => {
    runSchedulePredict();
    runCostPredict();
    runEquipPredict();
  }, []);

  const runSchedulePredict = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/risk/predict-delay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          planned_days: plannedDays,
          completed_milestones: completedMilestones,
          total_milestones: totalMilestones,
          weather_rainfall_mm: rainfallMm,
          active_workers: activeWorkers
        })
      });
      if (res.ok) {
        const data = await res.json();
        setSchedulePred(data);
      }
    } catch (err) {
      console.error("Schedule predict error:", err);
    }
  };

  const runCostPredict = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/risk/predict-cost", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          budget: budgetCr,
          spent: spentCr,
          schedule_delay_days: delayDays,
          material_shortage_risk: materialRisk
        })
      });
      if (res.ok) {
        const data = await res.json();
        setCostPred(data);
      }
    } catch (err) {
      console.error("Cost predict error:", err);
    }
  };

  const runEquipPredict = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/risk/predict-equipment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          operating_hours: operatingHours,
          vibration_mm_s: vibrationMmS,
          days_since_maintenance: daysSinceMaint
        })
      });
      if (res.ok) {
        const data = await res.json();
        setEquipPred(data);
      }
    } catch (err) {
      console.error("Equipment predict error:", err);
    }
  };

  return (
    <div>
      {/* Title */}
      <div style={{ marginBottom: "24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
          <span className="badge-pill badge-warning">
            <Sparkles size={12} /> Predictive Machine Learning Engine
          </span>
        </div>
        <h2 style={{ fontSize: "1.4rem", fontWeight: "700", color: "#fff", margin: "0 0 4px 0" }}>
          AI Risk Prediction & Future Hazard Forecasting
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
          Predict potential construction delays, budget overruns, and mechanical failures before they happen
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "24px" }}>
        <button
          className={`btn-secondary-ci ${activeTab === "schedule" ? "active" : ""}`}
          style={{ background: activeTab === "schedule" ? "var(--primary)" : "#1e293b", color: "#fff", border: "none" }}
          onClick={() => setActiveTab("schedule")}
        >
          <Clock size={16} /> Schedule Delay Forecaster
        </button>
        <button
          className={`btn-secondary-ci ${activeTab === "cost" ? "active" : ""}`}
          style={{ background: activeTab === "cost" ? "var(--primary)" : "#1e293b", color: "#fff", border: "none" }}
          onClick={() => setActiveTab("cost")}
        >
          <IndianRupee size={16} /> Budget & Cost Overrun
        </button>
        <button
          className={`btn-secondary-ci ${activeTab === "equipment" ? "active" : ""}`}
          style={{ background: activeTab === "equipment" ? "var(--primary)" : "#1e293b", color: "#fff", border: "none" }}
          onClick={() => setActiveTab("equipment")}
        >
          <Cpu size={16} /> Machinery Health Telemetry
        </button>
      </div>

      {/* TAB 1: SCHEDULE PREDICTOR */}
      {activeTab === "schedule" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
          <div className="ci-card">
            <h3 className="ci-card-title">
              <Sliders size={18} color="#60a5fa" /> Simulation Parameters
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <label className="form-label-ci">Completed Milestones</label>
                  <span style={{ color: "#38bdf8", fontWeight: "600" }}>{completedMilestones} / {totalMilestones}</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max={totalMilestones}
                  value={completedMilestones}
                  onChange={(e) => setCompletedMilestones(parseInt(e.target.value))}
                  style={{ width: "100%" }}
                />
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <label className="form-label-ci">Weather Rainfall Forecast (mm)</label>
                  <span style={{ color: "#f87171", fontWeight: "600" }}>{rainfallMm} mm</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={rainfallMm}
                  onChange={(e) => setRainfallMm(parseFloat(e.target.value))}
                  style={{ width: "100%" }}
                />
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <label className="form-label-ci">Active Labor Workforce</label>
                  <span style={{ color: "#34d399", fontWeight: "600" }}>{activeWorkers} Workers</span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="150"
                  value={activeWorkers}
                  onChange={(e) => setActiveWorkers(parseInt(e.target.value))}
                  style={{ width: "100%" }}
                />
              </div>

              <button
                className="btn-primary-ci"
                style={{ marginTop: "10px" }}
                onClick={runSchedulePredict}
              >
                Recalculate Delay Prediction
              </button>
            </div>
          </div>

          <div className="ci-card">
            <h3 className="ci-card-title">
              <TrendingDown size={18} color="#f59e0b" /> ML Delay Forecast Output
            </h3>

            {schedulePred ? (
              <div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
                  <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "16px", borderRadius: "10px" }}>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>PROJECTED DELAY</span>
                    <div style={{ fontSize: "2rem", fontWeight: "800", color: schedulePred.predicted_delay_days > 3 ? "#f87171" : "#fbbf24" }}>
                      +{schedulePred.predicted_delay_days} Days
                    </div>
                  </div>

                  <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "16px", borderRadius: "10px" }}>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>DELAY PROBABILITY</span>
                    <div style={{ fontSize: "2rem", fontWeight: "800", color: "#38bdf8" }}>
                      {Math.round(schedulePred.delay_probability * 100)}%
                    </div>
                  </div>
                </div>

                <div style={{ padding: "14px", borderRadius: "10px", background: "rgba(245, 158, 11, 0.1)", border: "1px solid rgba(245, 158, 11, 0.3)", marginBottom: "16px" }}>
                  <strong style={{ color: "#fbbf24", display: "block", fontSize: "0.85rem", marginBottom: "4px" }}>
                    Key Delay Driver: {schedulePred.key_risk_driver}
                  </strong>
                  <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem" }}>
                    {schedulePred.suggested_mitigation}
                  </p>
                </div>
              </div>
            ) : (
              <p style={{ color: "var(--text-muted)" }}>Calculating predictions...</p>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: COST OVERRUN PREDICTOR */}
      {activeTab === "cost" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
          <div className="ci-card">
            <h3 className="ci-card-title">
              <IndianRupee size={18} color="#34d399" /> Budget & Expense Gate
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div>
                <label className="form-label-ci">Total Project Budget (₹ in Crores)</label>
                <input
                  type="number"
                  step="0.5"
                  className="form-control-ci"
                  value={budgetCr}
                  onChange={(e) => setBudgetCr(parseFloat(e.target.value))}
                />
              </div>

              <div>
                <label className="form-label-ci">Current Expenditure to Date (₹ Cr)</label>
                <input
                  type="number"
                  step="0.1"
                  className="form-control-ci"
                  value={spentCr}
                  onChange={(e) => setSpentCr(parseFloat(e.target.value))}
                />
              </div>

              <div>
                <label className="form-label-ci">Critical Path Delay (Days)</label>
                <input
                  type="number"
                  step="0.5"
                  className="form-control-ci"
                  value={delayDays}
                  onChange={(e) => setDelayDays(parseFloat(e.target.value))}
                />
              </div>

              <div>
                <label className="form-label-ci">Material Shortage Risk</label>
                <select
                  className="form-control-ci"
                  value={materialRisk}
                  onChange={(e) => setMaterialRisk(e.target.value)}
                >
                  <option value="LOW">Low Risk</option>
                  <option value="MEDIUM">Medium Variance</option>
                  <option value="HIGH">High Escalation Risk</option>
                </select>
              </div>

              <button className="btn-primary-ci" onClick={runCostPredict}>
                Run Cost Risk Analysis
              </button>
            </div>
          </div>

          <div className="ci-card">
            <h3 className="ci-card-title">
              <Zap size={18} color="#fbbf24" /> Predictive Variance Output
            </h3>

            {costPred ? (
              <div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "20px" }}>
                  <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "16px", borderRadius: "10px" }}>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>OVERRUN RISK</span>
                    <div style={{ fontSize: "2rem", fontWeight: "800", color: "#f87171" }}>
                      {Math.round(costPred.overrun_probability * 100)}%
                    </div>
                  </div>

                  <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "16px", borderRadius: "10px" }}>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>PROJECTED OVERRUN</span>
                    <div style={{ fontSize: "2rem", fontWeight: "800", color: "#38bdf8" }}>
                      ₹ {costPred.projected_cost_overrun_cr} Cr
                    </div>
                  </div>
                </div>

                <div style={{ padding: "14px", borderRadius: "10px", background: "rgba(59, 130, 246, 0.1)", border: "1px solid rgba(59, 130, 246, 0.2)" }}>
                  <strong style={{ color: "#60a5fa", display: "block", fontSize: "0.85rem", marginBottom: "4px" }}>
                    Cost Recommendation:
                  </strong>
                  <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem" }}>
                    {costPred.recommendation}
                  </p>
                </div>
              </div>
            ) : (
              <p style={{ color: "var(--text-muted)" }}>Analyzing costs...</p>
            )}
          </div>
        </div>
      )}

      {/* TAB 3: EQUIPMENT PREDICTOR */}
      {activeTab === "equipment" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
          <div className="ci-card">
            <h3 className="ci-card-title">
              <Cpu size={18} color="#c084fc" /> Tower Crane IoT Sensor Telemetry
            </h3>

            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <div>
                <label className="form-label-ci">Operating Hours</label>
                <input
                  type="number"
                  className="form-control-ci"
                  value={operatingHours}
                  onChange={(e) => setOperatingHours(parseFloat(e.target.value))}
                />
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <label className="form-label-ci">Bearing Vibration (mm/s)</label>
                  <span style={{ color: vibrationMmS > 7.0 ? "#f87171" : "#34d399", fontWeight: "600" }}>
                    {vibrationMmS} mm/s (Limit: 7.0)
                  </span>
                </div>
                <input
                  type="range"
                  min="2"
                  max="15"
                  step="0.2"
                  value={vibrationMmS}
                  onChange={(e) => setVibrationMmS(parseFloat(e.target.value))}
                  style={{ width: "100%" }}
                />
              </div>

              <div>
                <label className="form-label-ci">Days Since Last Overhaul</label>
                <input
                  type="number"
                  className="form-control-ci"
                  value={daysSinceMaint}
                  onChange={(e) => setDaysSinceMaint(parseInt(e.target.value))}
                />
              </div>

              <button className="btn-primary-ci" onClick={runEquipPredict}>
                Run Mechanical Failure Screen
              </button>
            </div>
          </div>

          <div className="ci-card">
            <h3 className="ci-card-title">
              <AlertTriangle size={18} color="#f87171" /> Breakdown Probability Score
            </h3>

            {equipPred ? (
              <div>
                <div style={{ background: "rgba(15, 23, 42, 0.6)", padding: "18px", borderRadius: "10px", marginBottom: "18px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>FAILURE RISK RATING</span>
                      <div style={{ fontSize: "2rem", fontWeight: "800", color: equipPred.failure_probability > 0.4 ? "#f87171" : "#34d399" }}>
                        {Math.round(equipPred.failure_probability * 100)}%
                      </div>
                    </div>
                    <span className={`badge-pill ${equipPred.status === "DANGER" ? "badge-danger" : "badge-warning"}`} style={{ fontSize: "0.85rem", padding: "6px 12px" }}>
                      STATUS: {equipPred.status}
                    </span>
                  </div>
                </div>

                <div style={{ padding: "14px", borderRadius: "10px", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.3)" }}>
                  <strong style={{ color: "#f87171", display: "block", fontSize: "0.85rem", marginBottom: "4px" }}>
                    Action Protocol:
                  </strong>
                  <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem" }}>
                    {equipPred.recommended_action}
                  </p>
                </div>
              </div>
            ) : (
              <p style={{ color: "var(--text-muted)" }}>Evaluating equipment telemetry...</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
