import { useEffect, useRef, useState } from "react";
import { API_BASE_URL } from "../api/client";

export default function LiveMonitoring() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  const [monitoring, setMonitoring] = useState(false);
  const [loading, setLoading] = useState(false);
  const [detections, setDetections] = useState({});
  const [annotatedImage, setAnnotatedImage] = useState(null);
  const [error, setError] = useState("");

  // ================================
  // START CAMERA
  // ================================

  const startCamera = async () => {
    try {
      setError("");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setMonitoring(true);
    } catch (err) {
      console.error("Camera error:", err);

      setError(
        "Unable to access camera. Please allow camera permission in your browser."
      );
    }
  };

  // ================================
  // STOP CAMERA
  // ================================

  const stopCamera = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });

      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setMonitoring(false);
    setLoading(false);
  };

  // ================================
  // CAPTURE FRAME + YOLO DETECTION
  // ================================

  const captureAndDetect = async () => {
    if (!videoRef.current || !canvasRef.current) {
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (video.readyState < 2) {
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );

    canvas.toBlob(
      async (blob) => {
        if (!blob) {
          return;
        }

        const formData = new FormData();

        formData.append(
          "file",
          blob,
          "webcam_frame.jpg"
        );

        try {
          setLoading(true);

          const response = await fetch(
            `${API_BASE_URL}/safety/live-detect`,
            {
              method: "POST",
              body: formData,
            }
          );

          if (!response.ok) {
            throw new Error(
              "Live detection failed"
            );
          }

          const data = await response.json();

          if (data.error) {
            throw new Error(data.error);
          }

          // Update detections
          setDetections(
            data.detections || {}
          );

          // Update annotated image
          if (data.image) {
            setAnnotatedImage(
              `data:image/jpeg;base64,${data.image}`
            );
          }

        } catch (err) {
          console.error(
            "Detection error:",
            err
          );

          setError(
            "AI detection failed."
          );

        } finally {
          setLoading(false);
        }
      },
      "image/jpeg",
      0.8
    );
  };

  // ================================
  // START / STOP DETECTION LOOP
  // ================================

  useEffect(() => {
    if (monitoring) {
      intervalRef.current = setInterval(() => {
        captureAndDetect();
      }, 500);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(
          intervalRef.current
        );

        intervalRef.current = null;
      }
    };
  }, [monitoring]);

  // ================================
  // CLEANUP CAMERA
  // ================================

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  // ================================
  // DETECTION VALUES
  // ================================

  const persons =
    detections["Person"] || 0;

  const hardhats =
    detections["Hardhat"] || 0;

  const vests =
    detections["Safety Vest"] || 0;

  const noHardhat =
    detections["NO-Hardhat"] || 0;

  const noVest =
    detections["NO-Safety Vest"] || 0;

  // ================================
  // RISK CALCULATION
  // ================================

  let risk = "LOW";

  if (
    noHardhat > 0 ||
    noVest > 0
  ) {
    risk = "HIGH";
  } else if (
    persons > 0 &&
    (
      hardhats < persons ||
      vests < persons
    )
  ) {
    risk = "MEDIUM";
  }

  // ================================
  // COMPLIANCE
  // ================================

  let compliance = 100;

  if (persons > 0) {
    let compliantWorkers = 0;

    if (
      hardhats >= persons &&
      vests >= persons
    ) {
      compliantWorkers = persons;
    } else {
      compliantWorkers = Math.min(
        hardhats,
        vests
      );
    }

    compliance = Math.round(
      (compliantWorkers / persons) * 100
    );
  }

  // ================================
  // UI
  // ================================

  return (
    <div className="card shadow p-4 mt-5">

      {/* ================================
          TITLE
      ================================= */}

      <h2 className="text-center mb-4">
        🔴 Live Safety Monitoring
      </h2>


      {/* ================================
          CAMERA + AI DETECTION
      ================================= */}

      <div className="row g-4">

        {/* CAMERA */}

        <div className="col-md-6">

          <div className="card p-3 h-100">

            <h4 className="text-center mb-3">
              📷 Live Camera
            </h4>

            <video
              ref={videoRef}
              autoPlay
              muted
              playsInline
              className="img-fluid rounded"
              style={{
                width: "100%",
                background: "#111",
                minHeight: "300px",
                objectFit: "cover",
              }}
            />

            <div className="text-center mt-3">

              {!monitoring ? (

                <button
                  className="btn btn-success"
                  onClick={startCamera}
                >
                  ▶ Start Live Monitoring
                </button>

              ) : (

                <button
                  className="btn btn-danger"
                  onClick={stopCamera}
                >
                  ⏹ Stop Monitoring
                </button>

              )}

            </div>

          </div>

        </div>


        {/* AI DETECTION */}

        <div className="col-md-6">

          <div className="card p-3 h-100">

            <h4 className="text-center mb-3">
              🤖 AI Detection
            </h4>

            {annotatedImage ? (

              <img
                src={annotatedImage}
                alt="AI Detection"
                className="img-fluid rounded"
                style={{
                  width: "100%",
                  minHeight: "300px",
                  objectFit: "cover",
                }}
              />

            ) : (

              <div
                className="d-flex align-items-center justify-content-center"
                style={{
                  minHeight: "300px",
                  background: "#f5f5f5",
                  borderRadius: "10px",
                }}
              >

                <p className="text-muted">
                  Start monitoring to begin AI detection
                </p>

              </div>

            )}

            {loading && (

              <p className="text-center mt-2">
                🤖 AI analyzing...
              </p>

            )}

          </div>

        </div>

      </div>


      {/* ================================
          DETECTION SUMMARY
      ================================= */}

      <div className="card shadow p-3 mt-4">

        <h4 className="text-center mb-3">
          Detection Summary
        </h4>

        <div className="row g-3 text-center">

          {/* PERSON */}

          <div className="col-6 col-md-3">

            <div className="border rounded p-3">

              <strong>
                Person
              </strong>

              <div className="text-primary fs-4">
                {persons}
              </div>

            </div>

          </div>


          {/* HARDHAT */}

          <div className="col-6 col-md-3">

            <div className="border rounded p-3">

              <strong>
                Hardhat
              </strong>

              <div className="text-primary fs-4">
                {hardhats}
              </div>

            </div>

          </div>


          {/* SAFETY VEST */}

          <div className="col-6 col-md-3">

            <div className="border rounded p-3">

              <strong>
                Safety Vest
              </strong>

              <div className="text-primary fs-4">
                {vests}
              </div>

            </div>

          </div>


          {/* NO VEST */}

          <div className="col-6 col-md-3">

            <div className="border rounded p-3">

              <strong>
                NO-Safety Vest
              </strong>

              <div className="text-danger fs-4">
                {noVest}
              </div>

            </div>

          </div>


          {/* NO HARDHAT */}

          <div className="col-6 col-md-3">

            <div className="border rounded p-3">

              <strong>
                NO-Hardhat
              </strong>

              <div className="text-danger fs-4">
                {noHardhat}
              </div>

            </div>

          </div>

        </div>

      </div>


      {/* ================================
          COMPLIANCE SCORE
      ================================= */}

      <div className="card shadow p-4 mt-4 text-center">

        <h4>
          Compliance Score
        </h4>

        <div
          style={{
            fontSize: "42px",
            fontWeight: "bold",
            color:
              compliance >= 90
                ? "green"
                : compliance >= 70
                ? "orange"
                : "red",
          }}
        >
          {compliance}%
        </div>

        <p className="text-muted mb-0">
          Live PPE compliance
        </p>

      </div>


      {/* ================================
          RISK
      ================================= */}

      <div className="card shadow p-4 mt-4 text-center">

        <h4>
          Overall Risk
        </h4>

        <span
          className={`badge ${
            risk === "LOW"
              ? "bg-success"
              : risk === "MEDIUM"
              ? "bg-warning text-dark"
              : "bg-danger"
          }`}
          style={{
            fontSize: "1.2rem",
            padding: "10px 20px",
          }}
        >
          {risk}
        </span>


        {/* ================================
            SAFETY VIOLATION
        ================================= */}

        {(noHardhat > 0 || noVest > 0) && (

          <div className="alert alert-danger mt-4 mb-0">

            <h5 className="mb-2">
              ⚠️ SAFETY VIOLATION
            </h5>

            <p className="mb-2">
              Worker is missing required PPE.
            </p>

            {noHardhat > 0 && (

              <p className="mb-1">
                ❌ Hardhat violation detected
              </p>

            )}

            {noVest > 0 && (

              <p className="mb-1">
                ❌ Safety vest violation detected
              </p>

            )}

          </div>

        )}


        {/* ================================
            SAFE MESSAGE
        ================================= */}

        {risk === "LOW" &&
          persons > 0 && (

          <div className="alert alert-success mt-4 mb-0">

            <h5 className="mb-2">
              ✅ SAFETY COMPLIANT
            </h5>

            <p className="mb-0">
              Required PPE detected on the worker.
            </p>

          </div>

        )}

      </div>


      {/* ================================
          ERROR
      ================================= */}

      {error && (

        <div className="alert alert-danger mt-4 text-center">
          {error}
        </div>

      )}


      {/* ================================
          HIDDEN CANVAS
      ================================= */}

      <canvas
        ref={canvasRef}
        style={{
          display: "none",
        }}
      />

    </div>
  );
}