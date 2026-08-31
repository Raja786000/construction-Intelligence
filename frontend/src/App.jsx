import { useState, useEffect } from "react";

import Navbar from "./components/Navbar";
import UploadSection from "./components/UploadSection";
import ImageComparison from "./components/ImageComparison";
import SummaryCards from "./components/SummaryCards";
import LoadingSpinner from "./components/LoadingSpinner";
import RiskBadge from "./components/RiskBadge";
import Recommendation from "./components/Recommendation";
import Report from "./components/Report";
import ComplianceCard from "./components/ComplianceCard";
import LiveMonitoring from "./components/LiveMonitoring";

// Import E2E Project and Report Components
import ProjectMonitoring from "./components/ProjectMonitoring";
import ReportConsolidator from "./components/ReportConsolidator";

function App() {
  const [activeTab, setActiveTab] = useState("safety"); // "safety", "project", "report"
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState("P001");
  
  // Teammate Safety States
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch project list from backend on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/projects");
      if (response.ok) {
        const data = await response.json();
        setProjects(data);
        if (data.length > 0) {
          // Find if P001 is in the seeded list and set it as active default
          const hasP001 = data.find(p => p.id === "P001");
          setActiveProject(hasP001 ? "P001" : data[0].id);
        }
      }
    } catch (err) {
      console.error("Error fetching projects:", err);
    }
  };

  const detectSafety = async () => {
    if (!file) {
      alert("Please select an image or video");
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const isVideo = file.type.startsWith("video/");

      const endpoint = isVideo
        ? "http://127.0.0.1:8000/safety/video-detect"
        : "http://127.0.0.1:8000/safety/detect";

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Server returned an error");
      }

      const data = await response.json();

      setResult({
        ...data,
        mediaType: isVideo ? "video" : "image",
      });

    } catch (err) {
      console.error(err);
      alert("Backend Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />

      <div className="container my-4">
        {/* Navigation Tabs */}
        <div className="d-flex justify-content-center mb-4">
          <div className="btn-group bg-light p-1 rounded shadow-sm" role="group">
            <button
              className={`btn btn-lg px-4 ${activeTab === "safety" ? "btn-dark text-white" : "btn-light text-secondary"}`}
              onClick={() => setActiveTab("safety")}
            >
              🦺 Safety Surveillance (YOLO)
            </button>
            <button
              className={`btn btn-lg px-4 ${activeTab === "project" ? "btn-dark text-white" : "btn-light text-secondary"}`}
              onClick={() => setActiveTab("project")}
            >
              📅 Project Monitoring (ML)
            </button>
            <button
              className={`btn btn-lg px-4 ${activeTab === "report" ? "btn-dark text-white" : "btn-light text-secondary"}`}
              onClick={() => setActiveTab("report")}
            >
              📊 Multi-Agent AI Report (LangGraph)
            </button>
          </div>
        </div>

        {/* TAB 1: SAFETY MONITORING */}
        {activeTab === "safety" && (
          <div>
            <UploadSection
              file={file}
              setFile={setFile}
              preview={preview}
              setPreview={setPreview}
              detectSafety={detectSafety}
            />

            {loading && <LoadingSpinner />}

            {!loading && result && result.mediaType === "image" && (
              <>
                <ImageComparison preview={preview} result={result} />
                <SummaryCards detections={result.detections} />
                <ComplianceCard detections={result.detections} />
                <RiskBadge risk={result.risk_level} />
                <Recommendation recommendation={result.recommendation} />
                <Report report={result.report} />
              </>
            )}

            {!loading && result && result.mediaType === "video" && (
              <>
                <div className="card shadow mt-4">
                  <div className="card-body text-center">
                    <h3 className="mb-4">🎥 AI Video Detection</h3>
                    <p>Video processed successfully.</p>
                    <video
                      controls
                      style={{
                        width: "100%",
                        maxWidth: "800px",
                        borderRadius: "10px",
                      }}
                      src={`http://127.0.0.1:8000/results/${result.output_video.replace(
                        "runs/",
                        ""
                      )}`}
                    />
                  </div>
                </div>

                <div className="card shadow mt-4">
                  <div className="card-body">
                    <h3 className="text-center mb-4">Detection Summary</h3>
                    <div className="row">
                      {Object.entries(result.detections || {}).map(([name, count]) => (
                        <div className="col-md-3 mb-3" key={name}>
                          <div className="card text-center h-100">
                            <div className="card-body">
                              <h5>{name}</h5>
                              <h3 className="text-primary">{count}</h3>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="card shadow mt-4">
                  <div className="card-body text-center">
                    <h4>Compliance Score</h4>
                    <div
                      style={{
                        fontSize: "42px",
                        fontWeight: "bold",
                        color:
                          result.compliance_score >= 90
                            ? "green"
                            : result.compliance_score >= 70
                            ? "orange"
                            : "red",
                      }}
                    >
                      {result.compliance_score}%
                    </div>
                    <p className="text-muted">
                      Based on {result.analyzed_frames} analyzed frames with {result.violation_frames} violation frames.
                    </p>
                  </div>
                </div>

                <RiskBadge risk={result.risk_level} />
              </>
            )}

            <LiveMonitoring />
          </div>
        )}

        {/* TAB 2: PROJECT MONITORING */}
        {activeTab === "project" && projects.length > 0 && (
          <ProjectMonitoring
            projects={projects}
            activeProject={activeProject}
            setActiveProject={setActiveProject}
          />
        )}

        {/* TAB 3: REPORT CONSOLIDATOR */}
        {activeTab === "report" && projects.length > 0 && (
          <ReportConsolidator
            projects={projects}
            activeProject={activeProject}
          />
        )}
      </div>
    </>
  );
}

export default App;