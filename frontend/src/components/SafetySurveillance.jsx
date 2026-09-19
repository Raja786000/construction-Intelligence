import React, { useState, useRef, useEffect } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  Camera,
  Upload,
  Video,
  AlertTriangle,
  Play,
  Square,
  CheckCircle,
  FileText,
  UserCheck,
  Sparkles
} from "lucide-react";

export default function SafetySurveillance() {
  const [mode, setMode] = useState("upload"); // "upload" or "camera"
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [alertBanner, setAlertBanner] = useState(null);

  // Live Camera states
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [liveDetections, setLiveDetections] = useState(null);
  const [cameraError, setCameraError] = useState("");

  const handleFileSelect = (e) => {
    const selected = e.target.files[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setResult(null);
    setAlertBanner(null);
  };

  const runDetection = async () => {
    if (!file) {
      alert("Please select an image or video first.");
      return;
    }

    setLoading(true);
    setResult(null);
    setAlertBanner(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const isVideo = file.type.startsWith("video/");
      const endpoint = isVideo
        ? "http://127.0.0.1:8000/safety/video-detect"
        : "http://127.0.0.1:8000/safety/detect";

      const res = await fetch(endpoint, {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        throw new Error("Detection request failed.");
      }

      const data = await res.json();
      setResult({
        ...data,
        mediaType: isVideo ? "video" : "image"
      });

      if (data.alert_generated) {
        setAlertBanner(data.alert_generated);
      }
    } catch (err) {
      console.error(err);
      alert("Error communicating with YOLOv11 backend.");
    } finally {
      setLoading(false);
    }
  };

  // Camera Handlers
  const startCamera = async () => {
    try {
      setCameraError("");
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraActive(true);
      startLiveInterval();
    } catch (err) {
      console.error("Camera access error:", err);
      setCameraError("Camera permission denied or device not found. Please allow camera access in your browser.");
    }
  };

  const stopCamera = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
    setLiveDetections(null);
  };

  const startLiveInterval = () => {
    intervalRef.current = setInterval(() => {
      captureAndDetect();
    }, 1500); // Analyze frame every 1.5s
  };

  const captureAndDetect = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (video.videoWidth === 0 || video.videoHeight === 0) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const base64Data = canvas.toDataURL("image/jpeg", 0.7);

    try {
      const res = await fetch("http://127.0.0.1:8000/safety/detect-live", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: base64Data })
      });

      if (res.ok) {
        const data = await res.json();
        setLiveDetections(data);
        if (data.alert_generated) {
          setAlertBanner(data.alert_generated);
        }
      }
    } catch (err) {
      // Background frame processing failure
    }
  };

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const dets = result?.detections || liveDetections?.detections || {};
  const persons = dets["Person"] || dets["person"] || 0;
  const hardhats = dets["Hardhat"] || dets["helmet"] || 0;
  const vests = dets["Safety Vest"] || dets["vest"] || 0;
  const noHardhats = dets["NO-Hardhat"] || 0;
  const noVests = dets["NO-Safety Vest"] || 0;
  const totalViolations = noHardhats + noVests;

  return (
    <div>
      {/* Module Title */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "22px", flexWrap: "wrap", gap: "16px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span className="badge-pill badge-info">
              <Sparkles size={12} /> YOLOv11 Deep Learning (best.pt)
            </span>
          </div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: "700", color: "#fff", margin: "0 0 4px 0" }}>
            AI Safety Surveillance & PPE Violation Detector
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
            Detects Hardhats, Safety Vests, Persons, and hazards. Instantly triggers alert when PPE is missing.
          </p>
        </div>

        {/* Mode Switcher */}
        <div style={{ background: "#1e293b", padding: "4px", borderRadius: "10px", border: "1px solid var(--border-color)", display: "flex", gap: "4px" }}>
          <button
            className={`btn-secondary-ci ${mode === "upload" ? "active" : ""}`}
            style={{
              padding: "8px 16px",
              background: mode === "upload" ? "var(--primary)" : "transparent",
              color: "#fff",
              border: "none"
            }}
            onClick={() => {
              stopCamera();
              setMode("upload");
            }}
          >
            <Upload size={16} /> File Upload
          </button>
          <button
            className={`btn-secondary-ci ${mode === "camera" ? "active" : ""}`}
            style={{
              padding: "8px 16px",
              background: mode === "camera" ? "var(--primary)" : "transparent",
              color: "#fff",
              border: "none"
            }}
            onClick={() => {
              setMode("camera");
            }}
          >
            <Camera size={16} /> Live Camera Feed
          </button>
        </div>
      </div>

      {/* INSTANT VIOLATION ALERT BANNER (MATCHES NOTE #5) */}
      {(alertBanner || totalViolations > 0) && (
        <div style={{
          backgroundColor: "rgba(239, 68, 68, 0.18)",
          border: "1px solid rgba(239, 68, 68, 0.4)",
          borderRadius: "12px",
          padding: "16px 20px",
          marginBottom: "24px",
          display: "flex",
          alignItems: "center",
          gap: "14px"
        }}>
          <div style={{
            width: "42px",
            height: "42px",
            borderRadius: "10px",
            background: "#ef4444",
            color: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0
          }}>
            <ShieldAlert size={24} />
          </div>
          <div>
            <strong style={{ color: "#fff", fontSize: "1rem", display: "block" }}>
              🚨 AI SAFETY ALERT TRIGGERED: Worker PPE Non-Compliance Detected!
            </strong>
            <p style={{ color: "#fca5a5", fontSize: "0.85rem", marginTop: "2px" }}>
              {alertBanner?.message || `Worker detected without mandatory protective gear (${noHardhats} Missing Hardhat, ${noVests} Missing Vest). Automatically saved to MongoDB Alerts.`}
            </p>
          </div>
        </div>
      )}

      {/* MODE 1: FILE UPLOAD */}
      {mode === "upload" && (
        <div className="ci-card" style={{ marginBottom: "24px" }}>
          <div style={{
            border: "2px dashed #334155",
            borderRadius: "14px",
            padding: "36px 20px",
            textAlign: "center",
            backgroundColor: "rgba(15, 23, 42, 0.4)",
            cursor: "pointer"
          }}>
            <input
              type="file"
              id="safety-file-input"
              accept="image/*,video/*"
              style={{ display: "none" }}
              onChange={handleFileSelect}
            />
            <label htmlFor="safety-file-input" style={{ cursor: "pointer" }}>
              <div style={{
                width: "52px",
                height: "52px",
                borderRadius: "12px",
                background: "rgba(59, 130, 246, 0.15)",
                color: "#60a5fa",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: "14px"
              }}>
                <Upload size={24} />
              </div>
              <h4 style={{ color: "#fff", fontSize: "1.1rem", marginBottom: "6px" }}>
                {file ? file.name : "Select Construction Site Image or Video"}
              </h4>
              <p style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>
                Supports JPG, PNG, WEBP, MP4, AVI, MOV
              </p>
            </label>
          </div>

          {preview && (
            <div style={{ marginTop: "20px", textAlign: "center" }}>
              <button
                className="btn-primary-ci"
                style={{ padding: "12px 28px", fontSize: "1rem" }}
                onClick={runDetection}
                disabled={loading}
              >
                {loading ? "Running YOLOv11 Model..." : "Run AI Safety Detection"}
              </button>
            </div>
          )}
        </div>
      )}

      {/* MODE 2: LIVE WEBCAM CAMERA FEED */}
      {mode === "camera" && (
        <div className="ci-card" style={{ marginBottom: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ margin: 0, color: "#fff", fontSize: "1.1rem", display: "flex", alignItems: "center", gap: "8px" }}>
              <Camera size={18} color="#60a5fa" /> Live On-Site Camera Feed
            </h3>
            <div>
              {!cameraActive ? (
                <button className="btn-primary-ci" onClick={startCamera}>
                  <Play size={16} /> Start Camera Feed
                </button>
              ) : (
                <button className="btn-secondary-ci" onClick={stopCamera} style={{ color: "#f87171" }}>
                  <Square size={16} /> Stop Camera Feed
                </button>
              )}
            </div>
          </div>

          {cameraError && (
            <div style={{ padding: "12px", borderRadius: "8px", background: "rgba(239, 68, 68, 0.15)", color: "#f87171", fontSize: "0.85rem", marginBottom: "14px" }}>
              {cameraError}
            </div>
          )}

          <div style={{
            position: "relative",
            width: "100%",
            maxWidth: "680px",
            margin: "0 auto",
            backgroundColor: "#000",
            borderRadius: "14px",
            overflow: "hidden",
            minHeight: "380px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
          }}>
            {!cameraActive && (
              <div style={{ textAlign: "center", color: "var(--text-muted)" }}>
                <Camera size={48} style={{ opacity: 0.3, marginBottom: "10px" }} />
                <p>Camera is currently idle. Click "Start Camera Feed" to begin real-time surveillance.</p>
              </div>
            )}
            <video
              ref={videoRef}
              playsInline
              muted
              style={{ width: "100%", height: "auto", display: cameraActive ? "block" : "none" }}
            />
            <canvas ref={canvasRef} style={{ display: "none" }} />
          </div>
        </div>
      )}

      {/* RESULTS DISPLAY */}
      {(result || liveDetections) && (
        <div>
          {/* Quick Metrics Bar matching note #5 (e.g. workers, Helmet X, Vest V, Risk) */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginBottom: "24px" }}>
            <div className="ci-card" style={{ padding: "18px" }}>
              <span style={{ fontSize: "0.78rem", color: "var(--text-muted)", textTransform: "uppercase" }}>PERSONS DETECTED</span>
              <div style={{ fontSize: "1.8rem", fontWeight: "700", color: "#fff" }}>{persons}</div>
            </div>
            <div className="ci-card" style={{ padding: "18px" }}>
              <span style={{ fontSize: "0.78rem", color: "var(--text-muted)", textTransform: "uppercase" }}>HARDHATS (HELMETS)</span>
              <div style={{ fontSize: "1.8rem", fontWeight: "700", color: "#34d399" }}>
                {hardhats} <span style={{ fontSize: "0.9rem", color: noHardhats > 0 ? "#f87171" : "#34d399" }}>({noHardhats} Missing)</span>
              </div>
            </div>
            <div className="ci-card" style={{ padding: "18px" }}>
              <span style={{ fontSize: "0.78rem", color: "var(--text-muted)", textTransform: "uppercase" }}>SAFETY VESTS</span>
              <div style={{ fontSize: "1.8rem", fontWeight: "700", color: "#38bdf8" }}>
                {vests} <span style={{ fontSize: "0.9rem", color: noVests > 0 ? "#f87171" : "#34d399" }}>({noVests} Missing)</span>
              </div>
            </div>
            <div className="ci-card" style={{ padding: "18px" }}>
              <span style={{ fontSize: "0.78rem", color: "var(--text-muted)", textTransform: "uppercase" }}>RISK LEVEL</span>
              <div style={{ fontSize: "1.8rem", fontWeight: "700", color: totalViolations > 0 ? "#f87171" : "#34d399" }}>
                {totalViolations > 0 ? "HIGH RISK" : "COMPLIANT"}
              </div>
            </div>
          </div>

          {/* Comparison / Output Preview */}
          {result && result.output_image && (
            <div className="ci-card" style={{ marginBottom: "24px" }}>
              <h3 className="ci-card-title">
                <CheckCircle size={18} color="#34d399" /> YOLOv11 Detection Bounding Boxes
              </h3>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                <div>
                  <h5 style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "8px" }}>ORIGINAL UPLOAD</h5>
                  <img
                    src={preview}
                    alt="Original"
                    style={{ width: "100%", maxHeight: "380px", objectFit: "contain", borderRadius: "10px", border: "1px solid var(--border-color)" }}
                  />
                </div>
                <div>
                  <h5 style={{ color: "#60a5fa", fontSize: "0.85rem", marginBottom: "8px" }}>AI ANNOTATED OUTPUT (BOXES & CLASSES)</h5>
                  <img
                    src={result.output_image}
                    alt="Detected"
                    style={{ width: "100%", maxHeight: "380px", objectFit: "contain", borderRadius: "10px", border: "1px solid #3b82f6" }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Video Result */}
          {result && result.mediaType === "video" && result.output_video && (
            <div className="ci-card" style={{ marginBottom: "24px", textAlign: "center" }}>
              <h3 className="ci-card-title">Processed AI Video</h3>
              <video
                controls
                src={`http://127.0.0.1:8000/results/${result.output_video.replace("runs/", "")}`}
                style={{ width: "100%", maxWidth: "700px", borderRadius: "12px" }}
              />
            </div>
          )}

          {/* Recommendations & Report */}
          {result?.report && (
            <div className="ci-card">
              <h3 className="ci-card-title">
                <FileText size={18} color="#c084fc" /> AI Safety Inspector Audit
              </h3>
              <div style={{
                background: "rgba(15, 23, 42, 0.6)",
                borderRadius: "10px",
                padding: "16px 20px",
                color: "#e2e8f0",
                fontSize: "0.9rem",
                lineHeight: "1.6"
              }}>
                <p><strong>Recommendation:</strong> {result.recommendation || "All personnel adhering to safety requirements."}</p>
                <p style={{ marginTop: "8px", color: "var(--text-muted)", fontSize: "0.82rem" }}>{result.report}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
