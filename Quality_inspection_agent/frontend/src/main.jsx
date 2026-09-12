import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const CATS = [
  { k: "crack", n: "Cracks", icon: "⌁", desc: "Walls, slabs & linear cracking" },
  { k: "concrete", n: "Concrete defects", icon: "▦", desc: "Honeycombing, voids & anomalies" },
  { k: "surface", n: "Surface / finish", icon: "◈", desc: "Finish and texture irregularities" },
  { k: "component", n: "Components / installation", icon: "□", desc: "Installation & alignment review" },
  { k: "corrosion", n: "Corrosion", icon: "◉", desc: "Rust and corrosion indicators" },
];

const MEAS = [
  ["crack_width_mm", "Crack width", "mm"],
  ["crack_width_max_mm", "Maximum crack width", "mm"],
  ["concrete_cover_mm", "Concrete cover", "mm"],
  ["concrete_cover_min_mm", "Minimum cover", "mm"],
  ["surface_finish_score", "Finish score", ""],
  ["surface_finish_min_score", "Minimum finish score", ""],
  ["component_alignment_mm", "Alignment error", "mm"],
  ["component_alignment_max_mm", "Maximum alignment", "mm"],
  ["corrosion_depth_mm", "Corrosion depth", "mm"],
  ["corrosion_depth_max_mm", "Maximum depth", "mm"],
];

const MODES = [
  ["comprehensive", "Comprehensive", "All selected checks"],
  ["targeted", "Targeted", "Only selected checks"],
  ["quick", "Quick scan", "Fast crack screening"],
  ["checklist", "Checklist", "Measurements only"],
];

const initialMeasurements = Object.fromEntries(MEAS.map(([k]) => [k, ""]));

function App() {
  const [tab, setTab] = useState("inspect");
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [live, setLive] = useState(false);
  const [liveInfo, setLiveInfo] = useState(null);
  const [err, setErr] = useState("");
  const [caps, setCaps] = useState({});
  const video = useRef(null);
  const stream = useRef(null);

  const emptyForm = () => ({
    project_id: "",
    site_id: "",
    zone: "",
    area: "",
    mode: "comprehensive",
    categories: [],
    notes: "",
    measurements: Object.fromEntries(MEAS.map(([k]) => [k, ""])),
  });

  const [form, setForm] = useState(emptyForm);
  const [liveStats, setLiveStats] = useState({ frames: 0, detections: [] });
  const liveRequestInFlight = useRef(false);
  const liveDetectionHistory = useRef([]);

  useEffect(() => {
    fetch("/api/v1/quality/capabilities")
      .then((r) => r.json())
      .then(setCaps)
      .catch(() => {});
  }, []);

  const setField = (key, value) => setForm((p) => ({ ...p, [key]: value }));
  const setMeasurement = (key, value) =>
    setForm((p) => ({ ...p, measurements: { ...p.measurements, [key]: value } }));
  const toggleCategory = (key) =>
    setForm((p) => ({
      ...p,
      categories: p.categories.includes(key)
        ? p.categories.filter((x) => x !== key)
        : [...p.categories, key],
    }));

  const handleFiles = (incoming) => {
    const selected = Array.from(incoming || []);
    setFiles((prev) => [...prev, ...selected].filter((f, i, arr) => arr.findIndex((x) => x.name === f.name && x.size === f.size) === i));
  };

  const removeFile = (index) => setFiles((prev) => prev.filter((_, i) => i !== index));

  async function run(e) {
    e.preventDefault();
    setBusy(true);
    setErr("");

    if (form.mode !== "checklist" && !files.length) {
      setErr("Add at least one site image for visual inspection.");
      setBusy(false);
      return;
    }
    if (form.mode !== "checklist" && !form.categories.length) {
      setErr("Select at least one quality check.");
      setBusy(false);
      return;
    }

    const fd = new FormData();
    fd.append("project_id", form.project_id);
    fd.append("site_id", form.site_id);
    fd.append("zone", form.zone);
    fd.append("area", form.area);
    fd.append("inspection_mode", form.mode);
    fd.append("inspection_categories", form.categories.join(","));
    fd.append("description", form.notes);

    const measurements = {};
    Object.entries(form.measurements).forEach(([k, v]) => {
      if (v !== "") measurements[k] = Number(v);
    });
    fd.append("measurements", JSON.stringify(measurements));
    files.forEach((file) => fd.append("images", file));

    try {
      const response = await fetch("/api/v1/quality/inspect", { method: "POST", body: fd });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Inspection failed");
      setResult(data);
      setTab("results");
    } catch (error) {
      setErr(error.message || "Inspection failed.");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    let interval;
    let cancelled = false;

    const stopTracks = () => {
      if (stream.current) {
        stream.current.getTracks().forEach((track) => track.stop());
        stream.current = null;
      }
    };

    if (!live) {
      stopTracks();
      if (video.current) video.current.srcObject = null;
      return undefined;
    }

    async function startCamera() {
      try {
        if (!window.isSecureContext && !["localhost", "127.0.0.1"].includes(window.location.hostname)) {
          throw new Error("Camera access requires HTTPS or localhost. Open the app through http://localhost:5173.");
        }
        if (!navigator.mediaDevices?.getUserMedia) {
          throw new Error("Camera access is not supported by this browser.");
        }

        stopTracks();

        const constraints = [
          { video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false },
          { video: { width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false },
          { video: true, audio: false },
        ];

        let cameraStream = null;
        let lastError = null;
        for (const request of constraints) {
          try {
            cameraStream = await navigator.mediaDevices.getUserMedia(request);
            break;
          } catch (error) {
            lastError = error;
          }
        }

        if (!cameraStream) {
          const reason = lastError?.name === "NotAllowedError"
            ? "Camera permission was denied. Allow camera access for this site and try again."
            : lastError?.name === "NotReadableError"
              ? "The camera is busy or unavailable. Close other apps using the camera and try again."
              : lastError?.name === "NotFoundError"
                ? "No camera was found on this device."
                : "Could not start the camera. Check browser permissions and try again.";
          throw new Error(reason);
        }

        if (cancelled) {
          cameraStream.getTracks().forEach((track) => track.stop());
          return;
        }

        stream.current = cameraStream;
        const activeVideo = video.current;
        if (!activeVideo) {
          cameraStream.getTracks().forEach((track) => track.stop());
          return;
        }

        activeVideo.srcObject = cameraStream;
        activeVideo.muted = true;
        activeVideo.setAttribute("playsinline", "true");

        await new Promise((resolve) => {
          if (activeVideo.readyState >= 1) return resolve();
          activeVideo.onloadedmetadata = () => resolve();
        });

        try {
          await activeVideo.play();
        } catch (_) {
          setTimeout(() => activeVideo.play().catch(() => {}), 100);
        }

        setErr("");
        setLiveInfo(null);
        setLiveStats({ frames: 0, detections: [] });
        liveDetectionHistory.current = [];

        interval = setInterval(() => {
          if (cancelled || liveRequestInFlight.current || !video.current?.videoWidth) return;

          const canvas = document.createElement("canvas");
          canvas.width = video.current.videoWidth;
          canvas.height = video.current.videoHeight;
          const context = canvas.getContext("2d");
          context.drawImage(video.current, 0, 0, canvas.width, canvas.height);

          canvas.toBlob(async (blob) => {
            if (!blob || cancelled || liveRequestInFlight.current) return;
            liveRequestInFlight.current = true;
            const fd = new FormData();
            fd.append("frame", blob, "frame.jpg");

            try {
              const response = await fetch("/api/v1/quality/live/frame", { method: "POST", body: fd });
              if (!response.ok) return;
              const data = await response.json();
              if (cancelled) return;

              setLiveInfo(data);

              // A live finding must persist across multiple frames before it is
              // promoted into the session report. This removes one-frame noise
              // from faces, clothing, lighting changes and camera compression.
              const current = (data.detections || []).map((detection) => ({
                ...detection,
                key: `${detection.category || "unknown"}:${detection.label || "finding"}`,
              }));
              liveDetectionHistory.current = [
                ...liveDetectionHistory.current.slice(-2),
                current,
              ];
              const confirmed = [];
              const keys = [...new Set(liveDetectionHistory.current.flat().map((d) => d.key))];
              for (const key of keys) {
                const appearances = liveDetectionHistory.current.reduce((n, frame) => n + (frame.some((d) => d.key === key) ? 1 : 0), 0);
                if (appearances >= 2) {
                  const matches = liveDetectionHistory.current.flat().filter((d) => d.key === key);
                  confirmed.push(matches.sort((a,b) => Number(b.confidence || 0) - Number(a.confidence || 0))[0]);
                }
              }

              setLiveStats((previous) => {
                const merged = [...previous.detections];
                for (const detection of confirmed) {
                  const index = merged.findIndex((item) => item.key === detection.key);
                  if (index === -1) {
                    merged.push({
                      key: detection.key,
                      label: detection.label || "finding",
                      category: detection.category || "quality",
                      confidence: Number(detection.confidence || 0),
                      count: 1,
                      severity: detection.severity || "medium",
                    });
                  } else {
                    const rank = { low: 1, medium: 2, high: 3, critical: 4 };
                    const incomingSeverity = detection.severity || "medium";
                    merged[index] = {
                      ...merged[index],
                      confidence: Math.max(merged[index].confidence, Number(detection.confidence || 0)),
                      count: merged[index].count + 1,
                      severity: (rank[incomingSeverity] || 0) > (rank[merged[index].severity] || 0)
                        ? incomingSeverity
                        : merged[index].severity,
                    };
                  }
                }
                return { frames: previous.frames + 1, detections: merged };
              });
            } catch (_) {
              // Keep the camera running when an individual frame request fails.
            } finally {
              liveRequestInFlight.current = false;
            }
          }, "image/jpeg", 0.86);
        }, 800);
      } catch (error) {
        if (!cancelled) {
          setErr(error.message || "Could not start the camera.");
          setLive(false);
        }
      }
    }

    startCamera();

    return () => {
      cancelled = true;
      clearInterval(interval);
      liveRequestInFlight.current = false;
      stopTracks();
      if (video.current) video.current.srcObject = null;
    };
  }, [live]);
  const boxStyle = (box, width = 1280, height = 720) => ({
    left: `${(box.x1 / Math.max(width, 1)) * 100}%`,
    top: `${(box.y1 / Math.max(height, 1)) * 100}%`,
    width: `${((box.x2 - box.x1) / Math.max(width, 1)) * 100}%`,
    height: `${((box.y2 - box.y1) / Math.max(height, 1)) * 100}%`,
  });

  const selectedCount = form.categories.length;
  const statusClass = result?.status === "PASS" ? "good" : result?.status === "FAIL" ? "bad" : "warn";
  const severity = result?.severity || "none";
  const capabilityCount = useMemo(() => Object.keys(caps || {}).length, [caps]);

  const resetInspection = () => {
    setResult(null);
    setFiles([]);
    setErr("");
    setForm(emptyForm());
    setLiveInfo(null);
    setLiveStats({ frames: 0, detections: [] });
    setTab("inspect");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const startOrStopLive = () => {
    setErr("");
    if (live) {
      setLive(false);
    } else {
      setLiveInfo(null);
      setLiveStats({ frames: 0, detections: [] });
      liveDetectionHistory.current = [];
      setLive(true);
    }
  };

  const liveHighestSeverity = liveStats.detections.reduce((highest, item) => {
    const rank = { none: 0, low: 1, medium: 2, high: 3, critical: 4 };
    return (rank[item.severity] || 0) > (rank[highest] || 0) ? item.severity : highest;
  }, "none");

  const liveScore = liveStats.detections.length
    ? Math.max(0, 100 - liveStats.detections.reduce((sum, item) => {
        const penalty = { low: 5, medium: 15, high: 30, critical: 50 }[item.severity] || 0;
        return sum + penalty * Math.min(1, item.confidence);
      }, 0))
    : 100;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <button className="brand" onClick={() => setTab("inspect")} aria-label="Construction Intelligence Hub home">
            <span className="brand-mark">CI</span>
            <span className="brand-copy">
              <strong>Construction Intelligence Hub</strong>
              <small>Quality Inspection Agent</small>
            </span>
          </button>

          <nav className="main-nav" aria-label="Primary navigation">
            <button className={tab === "inspect" ? "active" : ""} onClick={() => setTab("inspect")}>
              Inspection
            </button>
            <button className={tab === "live" ? "active" : ""} onClick={() => setTab("live")}>
              Live Monitor
            </button>
            <button className={tab === "results" ? "active" : ""} disabled={!result} onClick={() => setTab("results")}>
              Results
            </button>
          </nav>

          <div className="agent-status"><span className="status-dot" /> Agent online</div>
        </div>
      </header>

      <main className="main-content">
        {tab === "inspect" && (
          <form onSubmit={run}>
            <div className="hero">
              <div>
                <div className="eyebrow">AI QUALITY CONTROL</div>
                <h1>Quality Inspection</h1>
                <p>Combine site evidence, inspection context and measured tolerances to identify visible quality risks.</p>
              </div>
              <button type="button" className="secondary-button" onClick={() => setTab("live")}>Open live monitor <span>→</span></button>
            </div>

            <button type="button" className="live-banner" onClick={() => setTab("live")}>
              <span className="live-icon">●</span>
              <span className="live-copy"><strong>Live camera detection</strong><small>Frame-by-frame visual screening with bounding boxes</small></span>
              <span className="banner-arrow">Open <b>→</b></span>
            </button>

            <section className="panel">
              <SectionHeader number="01" title="Inspection context" subtitle="Where was the evidence captured?" />
              <div className="field-grid four">
                {[["project_id", "Project ID"], ["site_id", "Site ID"], ["zone", "Zone"], ["area", "Area"]].map(([key, label]) => (
                  <label className="field" key={key}>
                    <span>{label}</span>
                    <input value={form[key]} onChange={(e) => setField(key, e.target.value)} />
                  </label>
                ))}
              </div>
              <div className="sub-label">Inspection mode</div>
              <div className="mode-grid">
                {MODES.map(([key, name, desc]) => (
                  <button type="button" key={key} className={`mode-card ${form.mode === key ? "selected" : ""}`} onClick={() => setField("mode", key)}>
                    <span className="mode-radio" />
                    <span><strong>{name}</strong><small>{desc}</small></span>
                  </button>
                ))}
              </div>
            </section>

            <section className="panel">
              <SectionHeader number="02" title="Quality checks" subtitle="Select the visual conditions you want the agent to inspect." />
              <div className="category-grid">
                {CATS.map((category) => {
                  const selected = form.categories.includes(category.k);
                  const engine = caps?.[category.k]?.engine || "Built-in CV baseline";
                  return (
                    <button type="button" key={category.k} className={`category-card ${selected ? "selected" : ""}`} onClick={() => toggleCategory(category.k)}>
                      <span className="category-icon">{category.icon}</span>
                      <span className="category-copy"><strong>{category.n}</strong><small>{category.desc}</small><em>{engine === "External YOLO" ? "AI model" : "Baseline screen"}</em></span>
                      <span className={`check ${selected ? "on" : ""}`}>{selected ? "✓" : ""}</span>
                    </button>
                  );
                })}
              </div>
              <div className="selection-summary"><span>{selectedCount} of 5 checks selected</span><span>{capabilityCount || 5} inspection engines available</span></div>
            </section>

            <section className="panel">
              <SectionHeader number="03" title="Site evidence" subtitle="Upload clear photos. Multiple images are supported." />
              <label className="dropzone" onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}>
                <input type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={(e) => handleFiles(e.target.files)} />
                <span className="upload-icon">↑</span>
                <strong>{files.length ? `${files.length} image${files.length > 1 ? "s" : ""} ready` : "Drop site images here"}</strong>
                <small>or browse files · JPG, PNG, WEBP</small>
              </label>
              {files.length > 0 && (
                <div className="file-list">
                  {files.map((file, index) => (
                    <div className="file-chip" key={`${file.name}-${file.size}`}>
                      <img src={URL.createObjectURL(file)} alt="" />
                      <span title={file.name}>{file.name}</span>
                      <button type="button" onClick={() => removeFile(index)} aria-label={`Remove ${file.name}`}>×</button>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <div className="two-column">
              <section className="panel">
                <SectionHeader number="04" title="Inspection notes" subtitle="Optional site context." />
                <textarea value={form.notes} onChange={(e) => setField("notes", e.target.value)} placeholder="Describe location, work stage, recent conditions or anything the inspector should consider." />
              </section>

              <section className="panel">
                <SectionHeader number="05" title="Measurements & tolerances" subtitle="Optional measured values. Leave blank when not applicable." />
                <div className="measurement-grid">
                  {MEAS.map(([key, label, unit]) => (
                    <label className="measurement" key={key}>
                      <span>{label}</span>
                      {unit && <small>{unit}</small>}
                      <input type="number" step=".01" value={form.measurements[key]} onChange={(e) => setMeasurement(key, e.target.value)} />
                    </label>
                  ))}
                </div>
              </section>
            </div>

            {err && <div className="error-box"><strong>Inspection not submitted</strong><span>{err}</span></div>}

            <div className="action-bar">
              <div className="ready-copy"><span className="ready-check">✓</span><span><strong>Ready for inspection</strong><small>The agent combines visual screening and deterministic tolerance checks.</small></span></div>
              <button className="primary-button" disabled={busy}>{busy ? "Analyzing evidence…" : "Run Quality Inspection →"}</button>
            </div>
          </form>
        )}

        {tab === "live" && (
          <div>
            <div className="hero">
              <div>
                <div className="eyebrow">REAL-TIME COMPUTER VISION</div>
                <h1>Live Quality Monitor</h1>
                <p>Show the construction area to the camera. Detected regions are highlighted directly on the video.</p>
              </div>
              <button className={live ? "danger-button" : "primary-button"} onClick={startOrStopLive}>
                {live ? "Stop live detection" : "Start live detection"}
              </button>
            </div>

            {err && <div className="error-box"><strong>Camera error</strong><span>{err}</span></div>}

            <section className="panel camera-panel">
              <div className="camera-head">
                <div><span className="panel-kicker">SITE CAMERA</span><strong>Live inspection view</strong><small>{live ? liveInfo?.mode || "Analyzing frames" : "Camera is stopped"}</small></div>
                <span className={`camera-state ${live ? "recording" : ""}`}><i />{live ? "LIVE" : "READY"}</span>
              </div>
              <div className="video-frame">
                <video ref={video} muted playsInline />
                {liveInfo?.detections?.map((d, i) => (
                  <div className="bbox" style={boxStyle(d.bbox, liveInfo.width, liveInfo.height)} key={`${d.label}-${i}`}>
                    <span>{d.label.replaceAll("_", " ")} · {(d.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
                {!live && <div className="video-empty"><div className="camera-glyph">◉</div><strong>Start live detection</strong><span>Your browser camera will be analyzed frame by frame.</span></div>}
              </div>
              <div className="detection-row">
                <strong>Current frame</strong>
                {liveInfo?.detections?.length ? liveInfo.detections.map((d, i) => <span className="detection-pill" key={i}>{d.label.replaceAll("_", " ")} <b>{(d.confidence * 100).toFixed(0)}%</b></span>) : <span className="muted">No validated detections in the current frame.</span>}
              </div>
            </section>

            <section className="live-report">
              <div className="live-report-head">
                <div>
                  <div className="eyebrow">SESSION REPORT</div>
                  <h2>Live Inspection Report</h2>
                  <p>Summary of validated detections collected during the current live session.</p>
                </div>
                <div className={`live-report-status ${liveStats.frames === 0 ? "ready" : liveStats.detections.length ? "review" : "pass"}`}>
                  <strong>{liveStats.frames === 0 ? "READY" : liveStats.detections.length ? "REVIEW" : "PASS"}</strong>
                  <span>{liveStats.frames === 0 ? "Start camera to build report" : `${liveScore.toFixed(0)}/100 quality screen`}</span>
                </div>
              </div>
              <div className="live-report-stats">
                <div><span>Frames analyzed</span><strong>{liveStats.frames}</strong></div>
                <div><span>Detected conditions</span><strong>{liveStats.detections.length}</strong></div>
                <div><span>Highest severity</span><strong className={`severity-text ${liveHighestSeverity}`}>{liveHighestSeverity.toUpperCase()}</strong></div>
                <div><span>Max confidence</span><strong>{liveStats.detections.length ? `${Math.round(Math.max(...liveStats.detections.map((d) => d.confidence)) * 100)}%` : "—"}</strong></div>
              </div>
              {liveStats.detections.length ? (
                <div className="live-report-list">
                  {liveStats.detections.map((item) => (
                    <div className="live-report-item" key={item.key}>
                      <div>
                        <span className="category-label">{item.category}</span>
                        <h3>{item.label.replaceAll("_", " ")}</h3>
                      </div>
                      <div className="live-report-meta">
                        <span>{Math.round(item.confidence * 100)}% confidence</span>
                        <span>{item.count} frame{item.count === 1 ? "" : "s"}</span>
                        <b className={`severity-badge ${item.severity}`}>{item.severity}</b>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="live-clean">
                  <span>✓</span>
                  <div><strong>No validated detections</strong><small>Keep the camera on the work area for continued screening. No reliable quality defect has been identified in this session.</small></div>
                </div>
              )}
            </section>

            <div className="info-grid">
              <section className="info-card"><span className="info-icon">AI</span><div><strong>Detection engine</strong><p>{liveInfo?.mode || "Built-in CV baseline"}</p></div><span className="state-good">● Ready</span></section>
              <section className="info-card"><span className="info-icon">5</span><div><strong>Quality categories</strong><p>Cracks · Concrete · Finish · Components · Corrosion</p></div><span className="state-good">● Available</span></section>
            </div>
          </div>
        )}

        {tab === "results" && result && (
          <div>
            <div className="hero result-hero">
              <div>
                <div className="eyebrow">INSPECTION COMPLETE</div>
                <h1>Quality Inspection Result</h1>
                <p>{result.project_id} <span className="hero-separator">•</span> Inspection {result.inspection_id}</p>
              </div>
              <button className="secondary-button" onClick={resetInspection}>← New inspection</button>
            </div>

            <div className="score-grid">
              <section className="score-card score-main">
                <span>AI quality score</span>
                <div className="score-value">{Number(result.quality_score).toFixed(result.quality_score % 1 ? 1 : 0)}<small>/100</small></div>
                <div className="progress"><i style={{ width: `${Math.max(0, Math.min(100, result.quality_score))}%` }} /></div>
                <small className="score-note">{result.finding_count === 0 ? "No validated defects" : "Based on validated findings"}</small>
              </section>
              <section className={`score-card status-card ${statusClass}`}><span>Status</span><strong>{result.status.replaceAll("_", " ")}</strong><small>{result.status === "PASS" ? "Inspection passed" : result.status === "FAIL" ? "Engineering review recommended" : "Review findings before acceptance"}</small></section>
              <section className="score-card"><span>Findings</span><strong>{result.finding_count}</strong><small>Across submitted evidence</small></section>
              <section className="score-card severity-card"><span>Highest severity</span><strong className={`severity-badge ${severity}`}>{severity}</strong><small>{result.risk_required ? "Risk escalation required" : result.finding_count ? "Human review recommended" : "No review triggered"}</small></section>
            </div>

            <div className="result-layout">
              <section>
                <div className="result-heading"><div><h2>Detected findings</h2><p>Validated visual and measurement findings from the Quality Inspection Agent.</p></div><span>{result.confidence ? `${(result.confidence * 100).toFixed(0)}% max confidence` : "Clean inspection"}</span></div>
                {result.findings?.length ? result.findings.map((f) => (
                  <article className="finding-card" key={f.finding_id}>
                    <div className="finding-head">
                      <div><span className="category-label">{f.inspection_category}</span><h3>{f.defect_type.replaceAll("_", " ")}</h3></div>
                      <span className={`severity-badge ${f.severity}`}>{f.severity}</span>
                    </div>
                    <div className="finding-source"><span>Detection source</span><b>{f.source_tool?.replaceAll("_", " ") || "visual inspection"}</b></div>
                    <p className="finding-description">{f.description}</p>
                    <div className="finding-meta"><span>Confidence {(f.confidence * 100).toFixed(0)}%</span><span>{f.source_tool}</span>{f.requires_human_verification && <span>Human verification</span>}</div>
                    <div className="recommendation"><strong>Recommended action</strong><span>{f.recommended_action}</span></div>
                  </article>
                )) : (
                  <div className="clean-result"><div className="clean-icon">✓</div><h3>Inspection passed</h3><p>No validated visible defects or tolerance violations were found in the submitted evidence.</p><div className="clean-stats"><span><b>100/100</b> quality score</span><span><b>0</b> findings</span><span><b>PASS</b> decision</span></div></div>
                )}
              </section>

              <aside className="result-sidebar">
                <section className="side-card"><h3>AI recommendations</h3>{result.recommendations.map((text, i) => <div className="recommendation-item" key={i}><b>{String(i + 1).padStart(2, "0")}</b><span>{text}</span></div>)}</section>
                <section className="side-card"><h3>Inspection context</h3>{[["Site", result.inspection_context?.site_id], ["Zone", result.inspection_context?.zone], ["Area", result.inspection_context?.area], ["Checks", result.categories_requested?.length ? `${result.categories_requested.length} selected` : "—"], ["Risk escalation", result.risk_required ? "Required" : "Not triggered"]].map(([label, value]) => <div className="context-row" key={label}><span>{label}</span><b>{value || "—"}</b></div>)}</section>
                <div className="review-note"><strong>Engineering review</strong><span>AI screening is preliminary. Verify findings against project specifications, measurements, applicable standards and qualified engineering inspection.</span></div>
              </aside>
            </div>
          </div>
        )}
      </main>

      <footer className="footer"><span>Construction Intelligence Hub</span><span>Quality Inspection Agent · v3.2</span></footer>
    </div>
  );
}

function SectionHeader({ number, title, subtitle }) {
  return <div className="section-header"><span className="section-number">{number}</span><div><h2>{title}</h2><p>{subtitle}</p></div></div>;
}

createRoot(document.getElementById("root")).render(<App />);
