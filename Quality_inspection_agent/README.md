# Construction Intelligence Hub — Quality Inspection Agent v3.1

A standalone Quality Inspection Agent designed to be moved into the larger Construction Intelligence Hub later.

## What changed in v3.1

- Professional responsive UI with centered navigation and a cleaner desktop/mobile layout.
- Results page now clearly distinguishes **PASS**, **REVIEW REQUIRED**, and **FAIL**.
- Clean inspections with **zero validated findings score 100/100 and PASS**.
- Low-confidence visual candidates are suppressed instead of being counted as defects.
- Component/installation baseline no longer treats every rectangle or opening as a defect. That category is checklist-driven unless a trained model is supplied.
- Visual penalties are weighted by severity and confidence rather than simply subtracting a fixed penalty for every raw detector candidate.
- Empty measurements do not create failures.
- Live bounding boxes now use the actual frame width/height returned by the backend instead of assuming 1280×720.
- Fixed the camera permission error handler.
- Optional YOLO `.pt` models can be placed in the category model folders.

## Inspection categories

1. Cracks — walls, slabs and linear cracking
2. Concrete defects — obvious void-like anomalies / surface defects
3. Surface / finish — conservative texture irregularity screen
4. Components / installation — measurement/checklist driven without a trained model
5. Corrosion — rust/corrosion color and shape screen

## Important model note

The included visual engines are **prototype CV baselines** so the application runs without trained model files. They are not equivalent to production-trained construction defect models and should not be used to certify structural safety or code compliance.

When trained YOLO models are available, place them here:

```text
models/
├── crack/model.pt
├── concrete/model.pt
├── surface/model.pt
├── component/model.pt
└── corrosion/model.pt
```

The external model is used only when the file exists. Install the Ultralytics package in the backend environment when using `.pt` models.

## Recommended PASS test

Use clear, defect-free photos. Select the categories that are actually relevant to those photos and **leave all measurements blank**.

Expected result:

```text
AI quality score: 100/100
Status: PASS
Findings: 0
Highest severity: NONE
```

A clean image should never fail merely because it contains normal edges, texture, windows or rectangular construction elements.

## Recommended defect test

Use the included sample images:

```text
sample_images/
├── 01_cracked_wall.jpg
├── 02_concrete_defect.jpg
├── 03_rust_component.jpg
├── 04_surface_finish.jpg
└── 05_component.jpg
```

For measurement testing, enter both the measured value and its corresponding tolerance. For example:

```text
Crack width: 2.5 mm
Maximum crack width: 2.0 mm
```

This creates a deterministic measurement nonconformance and requires human verification.

## Windows local run

### Terminal 1 — backend

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — frontend

```bat
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

Backend health:

```text
http://127.0.0.1:8000/health
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Docker

From the project root:

```bat
docker compose up --build
```

Stop it with:

```bat
docker compose down
```

## Live monitor

The browser camera is captured frame-by-frame and sent to the backend about every 700 ms for local development. If `YOLO_LIVE_MODEL_PATH` points to an existing YOLO `.pt` model, the live monitor uses it; otherwise it uses the built-in baseline screen.

For production CCTV/RTSP, use a proper WebRTC/RTSP streaming pipeline instead of browser frame uploads.

## Integration into the main Construction Intelligence Hub

Move only the Quality Agent/backend/model pieces into the main system:

```text
backend/app/quality_agent/  -> backend/agents/quality/
backend/app/api/quality.py   -> main backend API layer
models/<category>/           -> models/quality/<category>/
```

Do **not** copy the standalone frontend into the main project. It is the test UI for this agent.


## v3.2 refinements

- Centered, responsive application header/navigation.
- New Inspection clears project/site/zone/area, notes, selected checks, uploaded files and measurements.
- Finding cards no longer render the broken/annoying "Inspection evidence" image block.
- Live camera uses a robust camera-constraint fallback: rear camera when available, then any camera.
- Live frame requests are serialized to prevent overlapping requests.
- Live Monitor now builds a session report below the camera with frames analyzed, validated conditions, confidence, severity and a quality screen.
- Live baseline detections use the same conservative confidence validation as normal inspection.
- Comprehensive inspections now honor the categories explicitly selected by the user.
- Backend/frontend version is 3.2.0.

### Camera note

For browser camera access, use `http://localhost:5173` during local development. If the app is opened through a non-localhost HTTP address, browsers normally require HTTPS for camera access. Allow camera permission when prompted. If another application is using the camera, close it before starting Live Monitor.
