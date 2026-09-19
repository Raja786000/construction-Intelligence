import React, { useState, useEffect } from "react";
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Upload,
  Camera,
  Layers,
  Sparkles,
  FileCheck
} from "lucide-react";

export default function QualityMonitoring() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("crack");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/quality/categories");
      if (res.ok) {
        const data = await res.json();
        setCategories(data);
      }
    } catch (err) {
      console.error("Error loading categories:", err);
    }
  };

  const handleFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
  };

  const runInspection = async () => {
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("category", selectedCategory);
    formData.append("project_id", "PROJ-METRO");
    formData.append("location", "Metro Bridge Sector 4");
    if (file) {
      formData.append("file", file);
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/api/quality/inspect", {
        method: "POST",
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error("Quality inspection failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: "24px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
          <span className="badge-pill badge-info">
            <Sparkles size={12} /> Quality Inspection Agent v3.1
          </span>
        </div>
        <h2 style={{ fontSize: "1.4rem", fontWeight: "700", color: "#fff", margin: "0 0 4px 0" }}>
          Quality & Structural Defect Inspection Studio
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
          AI-driven visual screening for concrete cracks, voids, honeycombing, corrosion, and installation tolerances
        </p>
      </div>

      {/* Category Selector Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px", marginBottom: "24px" }}>
        {[
          { id: "crack", name: "Cracks & Fissures", icon: "⚡" },
          { id: "concrete", name: "Concrete Defects", icon: "🧱" },
          { id: "surface", name: "Surface & Finish", icon: "🎨" },
          { id: "component", name: "Components", icon: "📐" },
          { id: "corrosion", name: "Rust & Corrosion", icon: "🔩" }
        ].map((cat) => (
          <div
            key={cat.id}
            style={{
              background: selectedCategory === cat.id ? "linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(30, 41, 59, 0.8) 100%)" : "var(--bg-card)",
              border: `1px solid ${selectedCategory === cat.id ? "var(--primary)" : "var(--border-color)"}`,
              borderRadius: "12px",
              padding: "16px",
              cursor: "pointer",
              textAlign: "center",
              transition: "all 0.2s"
            }}
            onClick={() => setSelectedCategory(cat.id)}
          >
            <div style={{ fontSize: "1.8rem", marginBottom: "6px" }}>{cat.icon}</div>
            <strong style={{ color: "#fff", fontSize: "0.9rem", display: "block" }}>{cat.name}</strong>
          </div>
        ))}
      </div>

      {/* Upload and Run Panel */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "24px" }}>
        <div className="ci-card">
          <h3 className="ci-card-title">
            <Upload size={18} color="#60a5fa" /> Upload Inspection Photo
          </h3>

          <div style={{
            border: "2px dashed #334155",
            borderRadius: "12px",
            padding: "30px 20px",
            textAlign: "center",
            backgroundColor: "rgba(15, 23, 42, 0.4)",
            cursor: "pointer"
          }}>
            <input
              type="file"
              id="quality-file"
              accept="image/*"
              style={{ display: "none" }}
              onChange={handleFile}
            />
            <label htmlFor="quality-file" style={{ cursor: "pointer" }}>
              <Camera size={32} color="#60a5fa" style={{ marginBottom: "10px" }} />
              <h5 style={{ color: "#fff", marginBottom: "4px" }}>
                {file ? file.name : "Select Image of Wall, Concrete, or Component"}
              </h5>
              <p style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>
                High-resolution JPEG, PNG, or WEBP photos
              </p>
            </label>
          </div>

          <button
            className="btn-primary-ci"
            style={{ width: "100%", marginTop: "18px", justifyContent: "center" }}
            onClick={runInspection}
            disabled={loading}
          >
            {loading ? "Analyzing Defects..." : `Analyze for ${selectedCategory.toUpperCase()} Defects`}
          </button>
        </div>

        {/* Results Panel */}
        <div className="ci-card">
          <h3 className="ci-card-title">
            <FileCheck size={18} color="#34d399" /> Quality Analysis Report
          </h3>

          {result ? (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "18px", background: "rgba(15, 23, 42, 0.6)", padding: "16px", borderRadius: "10px" }}>
                <div>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>AI QUALITY SCORE</span>
                  <div style={{ fontSize: "2.2rem", fontWeight: "800", color: result.quality_score >= 80 ? "#34d399" : result.quality_score >= 60 ? "#fbbf24" : "#f87171" }}>
                    {result.quality_score} / 100
                  </div>
                </div>

                <div>
                  <span className={`badge-pill ${
                    result.status === "PASS" ? "badge-success" : result.status === "FAIL" ? "badge-danger" : "badge-warning"
                  }`} style={{ fontSize: "0.95rem", padding: "6px 14px" }}>
                    {result.status === "PASS" ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                    {result.status}
                  </span>
                </div>
              </div>

              {result.findings && result.findings.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                  {result.findings.map((f, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: "12px 14px",
                        borderRadius: "8px",
                        background: "rgba(15, 23, 42, 0.4)",
                        borderLeft: `4px solid ${f.severity === "HIGH" ? "#ef4444" : f.severity === "MEDIUM" ? "#f59e0b" : "#10b981"}`
                      }}
                    >
                      <strong style={{ color: "#fff", display: "block", fontSize: "0.9rem" }}>{f.title}</strong>
                      <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem", margin: "4px 0" }}>{f.description}</p>
                      <p style={{ color: "#60a5fa", fontSize: "0.78rem", margin: 0 }}><strong>Action:</strong> {f.recommendation}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: "#34d399", fontSize: "0.9rem" }}>✓ No nonconformance findings detected. Element meets QA standard.</p>
              )}
            </div>
          ) : (
            <div style={{ textAlign: "center", color: "var(--text-muted)", padding: "40px 20px" }}>
              <Layers size={40} style={{ opacity: 0.3, marginBottom: "12px" }} />
              <p>Select a defect category and click "Analyze" to execute the quality inspection model.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
