# 🏗️ Construction Intelligence Hub — Complete Setup & Run Guide

This guide contains **step-by-step instructions** so you and your teammates can easily run the entire project on any PC.

---

## 💻 System Prerequisites

Before starting, ensure your PC has:
1. **Python 3.10 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ **Important during installation**: Check the box **"Add python.exe to PATH"**!
2. **Node.js (v18 or higher)**
   - Download the LTS version from [nodejs.org](https://nodejs.org/) (includes `npm`).
3. **MongoDB (Optional)**
   - If you have MongoDB installed locally (`mongodb://localhost:27017`), the platform will store all data in it.
   - **No MongoDB? No problem!** The backend includes an automatic in-memory fallback database, so it works out-of-the-box on any machine even without MongoDB installed.

---

## ⚡ Method 1: 1-Click Automated Execution (Windows)

We have created two batch scripts to make running the project completely effortless:

### Step 1: Run Setup (First time only)
- In the project root folder, double-click **`setup.bat`** (or open command prompt and run `setup.bat`).
- This will automatically:
  1. Verify Python and Node.js.
  2. Install all backend packages (`fastapi`, `torch`, `ultralytics`, `reportlab`, `scikit-learn`, etc.).
  3. Install all frontend React dependencies (`lucide-react`, `vite`, etc.).
  4. Seed sample data (Metro Bridge Project ₹20 Cr, 7 workers, alerts, weather telemetry).

### Step 2: Launch Platform
- Double-click **`run_hub.bat`**.
- It will automatically:
  1. Start the FastAPI backend server on `http://127.0.0.1:8000`
  2. Start the React Vite frontend server on `http://localhost:5173`
  3. Automatically open your browser to the login screen!

---

## 🛠️ Method 2: Manual Terminal Steps (Windows / macOS / Linux)

If you or your friends prefer running commands in terminals, follow these steps:

### 1. Backend Setup & Run

Open a terminal in the root folder (`construction-Intelligence`):

```bash
# 1. Install backend dependencies
pip install -r requirements.txt

# 2. Seed database with initial project & worker records
python backend/app/db/init_db.py

# 3. Start the FastAPI backend server
python -m uvicorn backend.main:app --port 8000 --reload
```
- **Backend API will run at:** `http://127.0.0.1:8000`
- **Interactive Swagger Docs at:** `http://127.0.0.1:8000/docs`

---

### 2. Frontend Setup & Run

Open a **second terminal** and navigate to the `frontend` folder:

```bash
# 1. Navigate to frontend folder
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start Vite dev server
npm run dev
```
- **Web App will run at:** `http://localhost:5173/`

---

## 🔑 Login & Demo Credentials

Open your browser at `http://localhost:5173/`.  
On the login screen, you can either click the **1-Click Quick Demo** buttons or type:

| Role | Email / Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Site Administrator** | `admin@construction.ai` | `admin123` | Full Access (CRUD, Reports, AI Settings) |
| **Safety Officer** | `safety@construction.ai` | `safety123` | Safety Cam, PPE Alerts, Incident Center |
| **Project Manager** | `manager@construction.ai` | `manager123` | Projects, Milestones, Workers, Budget |

---

## 🧭 How to Test All 10 Integrated Features

Once logged in, use the left navigation sidebar to test each module:

1. **Dashboard**:
   - View high-level metrics: 504 total projects, 68% progress on Metro Bridge Project, 120 workers, 3 PPE violations, ₹1.8 Cr budget used, AI risk score (38.5 / 100).
   - Check the **Live Weather Alert**: `Tomorrow: Heavy Rain (45mm)`.

2. **Project Management**:
   - View Metro Bridge Project (₹20 Cr budget, ABC Construction Ltd).
   - Click **+ Add Project** to add a new project directly into the database.
   - Edit progress or delete projects with live updates.

3. **Worker Management**:
   - View workers list (`W101` Rajesh Kumar, `W102` Sunil Verma, etc.).
   - Click the **Helmet** or **Safety Vest** toggle buttons to instantly change compliance status.
   - Click **+ Register Worker** to add new personnel.

4. **Safety Detection (YOLOv11 AI)**:
   - Powered by `ai_models/safety/best.pt`.
   - **Upload Image/Video**: Drop any site image or test photo to detect `Person`, `Hardhat`, `NO-Hardhat`, `Safety Vest`, `NO-Safety Vest`.
   - **Webcam Mode**: Click *Start Live Webcam* for real-time video stream detection.
   - *Notice*: If any person is detected without a helmet or vest, an alert is automatically generated and pushed to the Alerts Center!

5. **Risk Prediction (ML)**:
   - Test Schedule Delay prediction, Cost Overrun probability, and Equipment Failure risk models.
   - Adjust site factors (e.g. rain forecast, workforce deficit, machinery hours) and click **Run AI Assessment**.

6. **Quality Monitoring (Agent v3.1)**:
   - Select inspection categories: **Cracks & Fissures**, **Concrete Defects**, **Surface & Finish**, **Components**, or **Rust & Corrosion**.
   - Upload a site photo or click run analysis to detect surface defects and structural integrity scores.

7. **Weather Integration**:
   - View live weather telemetry (Temperature, Humidity, Wind speed, Precipitation) and orange alert for tomorrow's rain forecast.

8. **Alerts Notification Center**:
   - Filter alerts by severity (Critical, Warning, Info).
   - Click **Resolve** to close alerts.

9. **Executive Reports & PDF Download**:
   - Select **Daily**, **Weekly**, or **Monthly** executive summary.
   - Click **Generate & Download PDF** to get a generated PDF report with charts and risk breakdowns.

---

## ❓ Troubleshooting & FAQs

### 1. `python` or `npm` is not recognized
- Make sure Python and Node.js are added to your system environment variables (`PATH`).
- Restart your terminal after installing them.

### 2. Port 8000 or 5173 is already in use
- Check if another application or an earlier terminal is running on port 8000 or 5173.
- In Windows, you can kill existing Python processes using:
  ```powershell
  taskkill /F /IM python.exe
  taskkill /F /IM node.exe
  ```

### 3. Webcam not showing in Safety Surveillance
- Ensure your browser allows camera access permissions for `http://localhost:5173`.
