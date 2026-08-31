import React, { useState, useEffect } from "react";

export default function ProjectMonitoring({ projects, activeProject, setActiveProject, onPrediction }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [projectDetail, setProjectDetail] = useState(null);

  // Fetch project detail (tasks, milestones) when project changes
  useEffect(() => {
    if (activeProject) {
      fetchProjectDetail();
    }
  }, [activeProject]);

  const fetchProjectDetail = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/projects/${activeProject}`);
      if (response.ok) {
        const data = await response.json();
        setProjectDetail(data);
        // Clear previous predictions when swapping projects
        setPrediction(null);
      }
    } catch (err) {
      console.error("Error fetching project details:", err);
    }
  };

  const runPrediction = async () => {
    setLoading(true);
    setPrediction(null);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/project-monitoring/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: activeProject }),
      });
      if (response.ok) {
        const data = await response.json();
        setPrediction(data);
        if (onPrediction) {
          onPrediction(data);
        }
      } else {
        alert("Failed to run ML prediction model.");
      }
    } catch (err) {
      console.error(err);
      alert("Error calling prediction API.");
    } finally {
      setLoading(false);
    }
  };

  if (!projectDetail) {
    return (
      <div className="text-center my-5">
        <div className="spinner-border text-primary" role="status" />
        <p className="mt-2 text-muted">Loading project details...</p>
      </div>
    );
  }

  const { project, tasks, milestones } = projectDetail;

  return (
    <div className="mt-4">
      {/* Selector and Run Button */}
      <div className="card shadow mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-6 mb-3 mb-md-0">
              <label className="form-label fw-bold">Select Construction Project</label>
              <select
                className="form-select"
                value={activeProject}
                onChange={(e) => setActiveProject(e.target.value)}
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.type})
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-6 text-md-end">
              <button
                className="btn btn-primary btn-lg mt-md-4"
                onClick={runPrediction}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Running ML Models...
                  </>
                ) : (
                  "🔍 Run Project Monitoring ML Model"
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Basic Metrics Dashboard */}
      <div className="row">
        <div className="col-md-4 mb-4">
          <div className="card shadow text-center h-100">
            <div className="card-body">
              <h5 className="text-muted text-uppercase small font-monospace">Project Health Score</h5>
              <div
                style={{
                  fontSize: "48px",
                  fontWeight: "black",
                  color: project.actual_progress >= project.planned_progress ? "#2F855A" : "#C53030",
                }}
              >
                {prediction ? prediction.project_health_score : "—"} <span style={{ fontSize: "18px", color: "#A0AEC0" }}>/ 100</span>
              </div>
              <p className="text-muted small">
                {prediction
                  ? `Status: ${prediction.project_health_score >= 80 ? "Healthy" : prediction.project_health_score >= 60 ? "Attention Required" : "Critical"}`
                  : "Run prediction to assess health"}
              </p>
            </div>
          </div>
        </div>

        <div className="col-md-4 mb-4">
          <div className="card shadow h-100">
            <div className="card-body d-flex flex-column justify-content-center">
              <h5 className="text-muted text-uppercase text-center small font-monospace">Progress Comparison</h5>
              <div className="mt-2">
                <div className="d-flex justify-content-between small text-muted mb-1">
                  <span>Actual Progress</span>
                  <span className="fw-bold">{project.actual_progress.toFixed(1)}%</span>
                </div>
                <div className="progress mb-3" style={{ height: "10px" }}>
                  <div
                    className="progress-bar bg-success"
                    role="progressbar"
                    style={{ width: `${project.actual_progress}%` }}
                  />
                </div>
                
                <div className="d-flex justify-content-between small text-muted mb-1">
                  <span>Planned Target</span>
                  <span className="fw-bold">{project.planned_progress.toFixed(1)}%</span>
                </div>
                <div className="progress" style={{ height: "10px" }}>
                  <div
                    className="progress-bar bg-secondary"
                    role="progressbar"
                    style={{ width: `${project.planned_progress}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-4 mb-4">
          <div className="card shadow text-center h-100">
            <div className="card-body">
              <h5 className="text-muted text-uppercase small font-monospace">Schedule Variance</h5>
              <div
                style={{
                  fontSize: "48px",
                  fontWeight: "bold",
                  color: project.schedule_variance >= 0 ? "#2F855A" : "#C53030",
                }}
              >
                {project.schedule_variance > 0 ? "+" : ""}
                {project.schedule_variance.toFixed(1)}%
              </div>
              <span className={`badge ${project.schedule_variance >= 0 ? "bg-success" : "bg-danger"}`}>
                {project.schedule_status}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ML Prediction Outputs */}
      {prediction && (
        <div className="row">
          {/* Timeline & Delay prediction */}
          <div className="col-md-6 mb-4">
            <div className="card shadow h-100">
              <div className="card-header bg-dark text-white fw-bold">📅 AI Delay & Completion Forecasts</div>
              <div className="card-body">
                <table className="table table-borderless align-middle mb-0">
                  <tbody>
                    <tr>
                      <td className="text-muted">Delay Probability:</td>
                      <td className="text-end fw-bold">
                        <span className="text-danger" style={{ fontSize: "1.2rem" }}>
                          {(prediction.delay_probability * 100).toFixed(0)}%
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td className="text-muted">Expected Delay Days:</td>
                      <td className="text-end fw-bold text-danger">
                        {prediction.predicted_delay_days > 0
                          ? `${prediction.predicted_delay_days} Days Late`
                          : prediction.predicted_delay_days < 0
                          ? `${Math.abs(prediction.predicted_delay_days)} Days Early`
                          : "On Time"}
                      </td>
                    </tr>
                    <tr>
                      <td className="text-muted">Planned End Date:</td>
                      <td className="text-end fw-bold">{prediction.planned_completion_date}</td>
                    </tr>
                    <tr>
                      <td className="text-muted">Predicted Completion Date:</td>
                      <td className="text-end fw-bold text-primary">{prediction.predicted_completion_date}</td>
                    </tr>
                    <tr>
                      <td className="text-muted">ML Delay Severity Class:</td>
                      <td className="text-end">
                        <span
                          className={`badge ${
                            prediction.project_status.includes("Severe")
                              ? "bg-danger"
                              : prediction.project_status.includes("Moderate")
                              ? "bg-warning text-dark"
                              : "bg-success"
                          }`}
                        >
                          {prediction.project_status}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Explainable AI (SHAP) */}
          <div className="col-md-6 mb-4">
            <div className="card shadow h-100">
              <div className="card-header bg-dark text-white fw-bold">🧠 SHAP Explainable AI Report</div>
              <div className="card-body">
                <p className="text-muted small">
                  Below is the natural-language translation of the SHAP values explaining the model's predicted delay:
                </p>
                <div className="p-3 bg-light rounded border border-secondary text-dark font-monospace small">
                  " {prediction.explainable_ai_summary} "
                </div>
                <div className="mt-3 text-muted small">
                  <strong>Primary Features Contributing to Prediction:</strong>
                  <ul className="mb-0 mt-1">
                    <li>Schedule progress variance (variance: {prediction.schedule_variance.toFixed(1)}%)</li>
                    <li>Total active and delayed tasks count ({prediction.delayed_tasks} delayed tasks)</li>
                    <li>Critical path delay activities ({prediction.delayed_critical_tasks_count} items)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Critical Tasks & Milestones Lists */}
      <div className="row">
        {/* Milestone Monitoring */}
        <div className="col-md-6 mb-4">
          <div className="card shadow h-100">
            <div className="card-header bg-secondary text-white fw-bold">🚩 Milestone Tracking</div>
            <div className="card-body">
              <div className="d-flex justify-content-between mb-2">
                <span className="text-muted">Milestone Completion Rate:</span>
                <span className="fw-bold">
                  {prediction ? `${prediction.milestone_completion}%` : "—"}
                </span>
              </div>
              <ul className="list-group list-group-flush">
                {milestones.map((m) => (
                  <li className="list-group-item d-flex justify-content-between align-items-center" key={m._id}>
                    <div>
                      <span className="fw-semibold">{m.name}</span>
                      <div className="text-muted small">Due: {m.due_date}</div>
                    </div>
                    <span
                      className={`badge ${
                        m.status === "Completed"
                          ? "bg-success"
                          : m.status === "In Progress"
                          ? "bg-warning text-dark"
                          : "bg-secondary"
                      }`}
                    >
                      {m.status}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Critical Path Monitoring */}
        <div className="col-md-6 mb-4">
          <div className="card shadow h-100">
            <div className="card-header bg-secondary text-white fw-bold">🚧 Critical Path Activities</div>
            <div className="card-body">
              <p className="text-muted small">
                Critical path activities directly impact the completion date. Delayed tasks here block overall progress.
              </p>
              <ul className="list-group list-group-flush">
                {tasks
                  .filter((t) => t.is_critical)
                  .map((t) => (
                    <li className="list-group-item d-flex justify-content-between align-items-center" key={t._id}>
                      <div>
                        <span className="fw-semibold">{t.name}</span>
                        <div className="text-muted small">
                          Planned: {t.planned_start} to {t.planned_end}
                        </div>
                      </div>
                      <span
                        className={`badge ${
                          t.status === "Completed"
                            ? "bg-success"
                            : t.time_deviation > 0
                            ? "bg-danger"
                            : "bg-warning text-dark"
                        }`}
                      >
                        {t.time_deviation > 0 ? `Delayed +${t.time_deviation}d` : t.status}
                      </span>
                    </li>
                  ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
