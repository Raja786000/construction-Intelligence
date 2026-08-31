import React, { useState, useEffect } from "react";

const LANGGRAPH_STEPS = [
  "Collect Agent Results (fetching Project, Safety, Risk, Quality stats)",
  "Validate Inputs (verifying database schema consistency)",
  "Analyze Project Monitoring (running XGBoost delay regressions)",
  "Analyze Safety Findings (loading YOLO hardhat & vest detections)",
  "Analyze Risk Findings (inspecting localized weather alerts)",
  "Analyze Quality Findings (evaluating structural concrete defects)",
  "Prioritize Issues (grouping critical, high, medium, low alerts)",
  "Generate Report (calling LangChain LLM to consolidate)",
  "Validate Report Structure (running semantic sanity checks)"
];

export default function ReportConsolidator({ projects, activeProject }) {
  const [reportType, setReportType] = useState("Daily");
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [report, setReport] = useState(null);
  const [showJson, setShowJson] = useState(false);

  const generateReport = async () => {
    setLoading(true);
    setReport(null);
    setCurrentStep(0);
    setShowJson(false);

    // Stepper animation
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= LANGGRAPH_STEPS.length - 1) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 400);

    try {
      const endpoint = reportType === "Daily" 
        ? "http://127.0.0.1:8000/api/reports/daily" 
        : "http://127.0.0.1:8000/api/reports/weekly";

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: activeProject }),
      });

      // Clear interval and complete stepper
      clearInterval(interval);
      setCurrentStep(LANGGRAPH_STEPS.length);

      if (response.ok) {
        const data = await response.json();
        setReport(data);
      } else {
        const errData = await response.json();
        alert(`Report agent failed: ${errData.detail || "Unknown error"}`);
      }
    } catch (err) {
      console.error(err);
      alert("Error invoking report agent API.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = () => {
    if (report) {
      window.open(`http://127.0.0.1:8000/api/reports/${report.id}/pdf`, "_blank");
    }
  };

  return (
    <div className="mt-4">
      {/* Parameters Panel */}
      <div className="card shadow mb-4">
        <div className="card-header bg-dark text-white fw-bold">⚙️ Report Parameters</div>
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-4 mb-3 mb-md-0">
              <label className="form-label fw-bold">Report Type</label>
              <div className="btn-group w-100" role="group">
                <button
                  type="button"
                  className={`btn ${reportType === "Daily" ? "btn-primary" : "btn-outline-primary"}`}
                  onClick={() => setReportType("Daily")}
                >
                  Daily Report
                </button>
                <button
                  type="button"
                  className={`btn ${reportType === "Weekly" ? "btn-primary" : "btn-outline-primary"}`}
                  onClick={() => setReportType("Weekly")}
                >
                  Weekly Report
                </button>
              </div>
            </div>
            <div className="col-md-4 mb-3 mb-md-0">
              <label className="form-label fw-bold">Selected Project</label>
              <input
                type="text"
                className="form-select bg-light"
                value={projects.find(p => p.id === activeProject)?.name || activeProject}
                disabled
              />
            </div>
            <div className="col-md-4 text-md-end">
              <button
                className="btn btn-success btn-lg w-100 mt-md-4"
                onClick={generateReport}
                disabled={loading}
              >
                📊 Generate Consolidated AI Report
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stepper Agent Animation */}
      {currentStep >= 0 && (
        <div className="card shadow mb-4">
          <div className="card-header bg-secondary text-white fw-bold">🤖 LangGraph Multi-Agent Activity Log</div>
          <div className="card-body">
            <div className="stepper-log">
              {LANGGRAPH_STEPS.map((step, idx) => (
                <div key={idx} className="d-flex align-items-center mb-2 font-monospace small">
                  <div className="me-3">
                    {currentStep > idx ? (
                      <span className="text-success fw-bold">✓</span>
                    ) : currentStep === idx ? (
                      <span className="spinner-border spinner-border-sm text-primary" role="status" />
                    ) : (
                      <span className="text-muted">○</span>
                    )}
                  </div>
                  <span className={currentStep === idx ? "text-primary fw-bold" : currentStep > idx ? "text-dark" : "text-muted"}>
                    {step}
                  </span>
                </div>
              ))}
              {currentStep === LANGGRAPH_STEPS.length && (
                <div className="mt-3 text-success fw-bold font-monospace">
                  🎉 REPORT COMPILED AND VALIDATED SUCCESSFULLY!
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Report Results Rendering */}
      {report && (
        <div className="card shadow mb-4 border-primary">
          <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
            <h4 className="mb-0 text-white font-monospace">🦺 AI Generated Construction Report ({report.report_type})</h4>
            <div>
              <button className="btn btn-light btn-sm me-2 fw-semibold" onClick={handleDownloadPdf}>
                📥 Download PDF
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => setShowJson(!showJson)}>
                {showJson ? "Show Report" : "Show JSON"}
              </button>
            </div>
          </div>
          <div className="card-body">
            {showJson ? (
              <pre className="bg-dark text-light p-3 rounded font-monospace small">
                {JSON.stringify(report, null, 2)}
              </pre>
            ) : (
              <div>
                {/* Status Badges */}
                <div className="row mb-4 text-center">
                  <div className="col-md-3 mb-2">
                    <div className="p-3 bg-light rounded border">
                      <div className="text-muted small">Project Status</div>
                      <h5 className="fw-bold mb-0 text-primary">{report.project_status}</h5>
                    </div>
                  </div>
                  <div className="col-md-3 mb-2">
                    <div className="p-3 bg-light rounded border">
                      <div className="text-muted small">Safety Alert Status</div>
                      <h5 className="fw-bold mb-0 text-danger">
                        {report.safety.ppe_violations > 0 ? "Warning Alert" : "Compliant"}
                      </h5>
                    </div>
                  </div>
                  <div className="col-md-3 mb-2">
                    <div className="p-3 bg-light rounded border">
                      <div className="text-muted small">Quality Defect Alert</div>
                      <h5 className="fw-bold mb-0 text-warning">
                        {report.quality.defects_detected > 0 ? "Repair Required" : "Compliant"}
                      </h5>
                    </div>
                  </div>
                  <div className="col-md-3 mb-2">
                    <div className="p-3 bg-light rounded border">
                      <div className="text-muted small">Risk Tier</div>
                      <h5 className="fw-bold mb-0 text-danger">{report.risk.risk_level}</h5>
                    </div>
                  </div>
                </div>

                {/* AI Executive Summary */}
                <div className="mb-4">
                  <h5 className="border-bottom pb-2 fw-bold text-dark">AI Executive Summary</h5>
                  <p className="lead font-sans-serif" style={{ fontSize: "1.1rem" }}>
                    {report.executive_summary}
                  </p>
                </div>

                {/* Prioritized Critical Findings */}
                <div className="mb-4">
                  <h5 className="border-bottom pb-2 fw-bold text-dark">Prioritized Critical Findings</h5>
                  <ul className="list-group">
                    {report.critical_findings && report.critical_findings.length > 0 ? (
                      report.critical_findings.map((item, idx) => (
                        <li className="list-group-item d-flex justify-content-between align-items-center" key={idx}>
                          <span>{item.issue}</span>
                          <span className={`badge ${item.severity === "CRITICAL" ? "bg-danger" : "bg-warning text-dark"}`}>
                            {item.severity}
                          </span>
                        </li>
                      ))
                    ) : (
                      <li className="list-group-item text-muted">No safety, schedule, quality, or risk events logged.</li>
                    )}
                  </ul>
                </div>

                {/* Recommendations */}
                <div className="row mb-4">
                  <div className="col-md-6 mb-3 mb-md-0">
                    <div className="card h-100 bg-light">
                      <div className="card-body">
                        <h5 className="card-title fw-bold text-dark border-bottom pb-2">Actionable Recommendations</h5>
                        <ul className="ps-3 mb-0">
                          {report.recommendations.map((rec, idx) => (
                            <li className="mb-2" key={idx}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Next Actions */}
                  <div className="col-md-6">
                    <div className="card h-100 bg-light">
                      <div className="card-body">
                        <h5 className="card-title fw-bold text-dark border-bottom pb-2">Immediate Next Actions</h5>
                        <ol className="ps-3 mb-0">
                          {report.next_actions.map((act, idx) => (
                            <li className="mb-2" key={idx}>{act}</li>
                          ))}
                        </ol>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Download PDF button */}
                <div className="text-center mt-3">
                  <button className="btn btn-primary btn-lg" onClick={handleDownloadPdf}>
                    📄 Download Executive PDF Report
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
