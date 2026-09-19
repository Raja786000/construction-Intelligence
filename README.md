# 🏗️ Construction Intelligence Hub — Unified AI Platform

Enterprise Construction Intelligence & Site Surveillance platform integrating YOLOv11 computer vision, MongoDB project & worker management, predictive risk machine learning, live weather telemetry, quality defect inspection, and automated PDF reporting.

---

## ⚡ Quick Start (Windows)

1. **One-Time Setup**: Double-click [`setup.bat`](./setup.bat)
2. **Start Platform**: Double-click [`run_hub.bat`](./run_hub.bat)
3. Open **`http://localhost:5173/`** in your browser!

👉 **For complete step-by-step instructions, troubleshooting, and manual terminal commands, read [HOW_TO_RUN.md](./HOW_TO_RUN.md).**

---

## 🔑 Demo Logins
- **Admin**: `admin@construction.ai` / `admin123`
- **Safety Officer**: `safety@construction.ai` / `safety123`
- **Project Manager**: `manager@construction.ai` / `manager123`
*(Or click the 1-click demo buttons on the login modal)*

---

## 🚀 Architecture & Modules
- **Frontend**: Vite + React 19 + Dark Glassmorphic Theme + Lucide Icons
- **Backend**: FastAPI + Uvicorn (48 REST Endpoints)
- **Computer Vision**: Ultralytics YOLOv11 (`ai_models/safety/best.pt`) with webcam & file inference
- **Database**: MongoDB / pymongo with automatic in-memory fallback
- **Quality Agent**: Visual inspection for cracks, concrete defects, surface finish, and corrosion
- **Risk ML**: Schedule delay, cost overrun, and equipment failure prediction
- **Reporting**: Daily, Weekly, Monthly consolidation with ReportLab PDF export