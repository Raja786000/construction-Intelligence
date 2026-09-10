# Agentic AI for Safety Monitoring with Construction Risk Analysis
> **Agentic Construction Risk Intelligence Platform & Construction Intelligence Hub**

![Platform License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-v0.110.0-009688.svg)
![YOLO Architecture](https://img.shields.io/badge/YOLO-v8%2Fv11-orange.svg)

An advanced, AI-powered construction risk intelligence platform that centralizes project data and uses autonomous AI agents, computer vision, and machine learning to identify, predict, and mitigate construction risks throughout the project lifecycle.

---

## 🌟 Executive Summary & Objectives

Unlike traditional monitoring systems that rely on manual site inspections and reactive decision-making, the **Construction Intelligence Hub** continuously ingests data from Building Information Modeling (BIM), IoT structural/vibration sensors, site imagery, project schedules, and meteorological forecasts to provide real-time risk intelligence.

### Key Platform Objectives:
- 📊 **Real-time Construction Progress Monitoring**: Live tracking of site zones, worker counts, and active tasks.
- 🔮 **Predictive Delay & Budget Analytics**: Machine learning models predicting completion delays and cost overrun variances.
- 🦺 **AI-Powered Computer Vision Safety Monitoring**: Detection of PPE violations (`Hardhat`, `Safety Vest`, `Mask`, `Harness`) and site hazards (`Fire`, `Smoke`).
- 🏗️ **Resource & Machinery Optimization**: Predictive breakdown risk scoring based on IoT vibration sensor telemetry.
- 🤖 **Autonomous Multi-Agent Collaboration**: 6 domain-specific agents (`Safety`, `Weather`, `Cost`, `Schedule`, `Resource`, `Quality`) communicating to synthesize joint mitigation workflows.
- 💬 **AI Risk Assistant Copilot**: Context-aware conversational AI assistant generating natural language risk explanations and audit reports.

---

## 🏗️ System Architecture & 15 Core Domain Entities

```
 ┌──────────────────────────────────────────────────────────────────────────┐
 │                        INTERACTIVE DASHBOARD UI                          │
 │      Executive Overview | CV Safety Studio | Agent Hub | AI Assistant     │
 └────────────────────────────────────┬─────────────────────────────────────┘
                                      │ REST API / WebSockets
 ┌────────────────────────────────────▼─────────────────────────────────────┐
 │                            FASTAPI BACKEND ENGINE                        │
 ├───────────────────┬──────────────────────┬───────────────────────────────┤
 │  CV Safety Engine │  Predictive ML Engine│ Autonomous Agent Ensemble     │
 │  - Hardhat / Vest │  - Schedule Delays   │ - Safety Agent   - Cost Agent │
 │  - Fire / Smoke   │  - Cost Overruns     │ - Weather Agent  - Resource   │
 │  - Annotator      │  - Machinery Health  │ - Schedule Agent - Quality    │
 └───────────────────┴──────────────────────┴───────────────────────────────┘
                                      │
 ┌────────────────────────────────────▼─────────────────────────────────────┐
 │                         SQLITE DOMAIN DATABASE                           │
 └──────────────────────────────────────────────────────────────────────────┘
```

### 15 Core Domain Entities

| Entity | Description |
| :--- | :--- |
| **Project** | Project ID, name, location, client, total budget, spent funds, start/end dates, composite risk score. |
| **Construction Site** | Site zones, active worker density, ambient weather status, location specs. |
| **Risk** | Identified risk items, category (Safety/Delay/Cost), severity, probability, mitigation plan. |
| **AI Agent** | Specialized autonomous agents (`Safety`, `Weather`, `Cost`, `Schedule`, `Resource`, `Quality`). |
| **Worker** | Worker ID, trade, assigned task, certification, and PPE compliance log. |
| **Equipment** | Machinery status, operating hours, maintenance schedule, vibration telemetry, failure risk. |
| **Material** | Inventory levels, required quantities, supply chain shortage risk, quality grade. |
| **Task** | Construction activities, planned vs actual completion dates, dependencies, delay days. |
| **Safety Incident** | Logged accidents, PPE violations, hazard events, corrective actions taken. |
| **Weather Data** | Forecast temperature, rainfall (mm), wind speed, severe storm alert levels. |
| **Cost Record** | Expense categories, planned vs actual costs, budget variance, overrun probability. |
| **Schedule** | Planned milestones, completed milestones, target completion date, forecast delay days. |
| **Sensor Data** | IoT readings (tower crane vibration, structural strain microstrain, dust PM10). |
| **Alert** | AI-generated risk alerts, severity rating, recipient agent, resolution status. |
| **Report** | Automatically generated daily, weekly, and monthly project audit reports. |

---

## 🦺 Computer Vision & Dataset Integration

The platform includes dual-mode Computer Vision safety detection:
- **PyTorch / Ultralytics Mode**: Runs custom-trained YOLO weights (`yolo11n.pt`) when GPU/weights are available.
- **Simulated Production Mode**: Instant zero-dependency fallback for demonstration without downloading heavy CUDA binaries.

### Supported Datasets:
1. **Kaggle PPE Kit Detection**: [Dataset Link](https://www.kaggle.com/code/sajjadalishah/ppe-kit-detection-construction-site-safety)
2. **Roboflow Construction Site Safety Dataset**: [Dataset Link](https://www.kaggle.com/datasets/snehilsanyal/construction-site-safety-image-dataset-roboflow)

### Training Custom YOLO Model:
```bash
python scripts/train_ppe_yolo.py --dataset_dir ./datasets/construction_safety --epochs 50
```

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.9 or higher
- Modern web browser (Chrome, Edge, Firefox)

### Step 1: Clone or Extract Repository
```bash
cd advanced_construction_risk
```

### Step 2: Install Required Dependencies
```bash
pip install fastapi uvicorn opencv-python numpy pydantic ultralytics
```

### Step 3: Launch Platform & Dashboard
Run the single starter command:
```bash
python run.py
```
This command initializes the SQLite database, populates seed data for all 15 entities, launches the FastAPI server at `http://127.0.0.1:8000`, and opens the interactive dashboard in your browser!

---

## 🛠️ API Reference Endpoints

- `GET /api/dashboard/stats`: Returns live executive metrics, PPE compliance rate, and weather alerts.
- `POST /api/safety/analyze`: Accepts image uploads and returns annotated frames with PPE bounding boxes.
- `GET /api/agents/collaborate`: Executes multi-agent evaluation cycle and inter-agent message pipeline.
- `POST /api/predictive/schedule-delay`: Runs ML schedule delay prediction model.
- `POST /api/predictive/cost-overrun`: Runs ML cost overrun estimation model.
- `GET /api/entities/{entity_type}`: Returns tabular data for any of the 15 project entities.
- `POST /api/assistant/chat`: Interacts with the context-aware AI Risk Assistant Copilot.
- `GET /api/reports/generate`: Generates an executive risk audit report.

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
