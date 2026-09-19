from fastapi import APIRouter, UploadFile, File
import shutil
import os
import cv2
import numpy as np
import base64

from app.graphs.safety_graph import graph
from app.graphs.video_safety_graph import video_graph

from app.services.incident_service import ViolationTracker

from app.services.safety_service import (
    detect_video,
    detect_live_frame
)


router = APIRouter(
    prefix="/safety",
    tags=["Safety Monitoring"]
)


# ==========================================
# LIVE VIOLATION TRACKER
# ==========================================

live_tracker = ViolationTracker()


# ==========================================
# IMAGE DETECTION
# ==========================================

@router.post("/detect")
async def detect_safety(
    file: UploadFile = File(...)
):

    upload_dir = "uploads/images"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    image_path = os.path.join(
        upload_dir,
        file.filename
    )

    with open(
        image_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    print("Calling detect()...")

    result = graph.invoke(
        {
            "image_path": image_path,
            "output_image": "",
            "detections": {},
            "risk_level": "",
            "recommendation": "",
            "report": ""
        }
    )

    output_raw = str(result.get("output_image", "")).replace("\\", "/")
    if "/runs/" in output_raw:
        image_url = f"http://127.0.0.1:8000/results/{output_raw.split('/runs/')[-1]}"
    elif "runs/" in output_raw:
        image_url = f"http://127.0.0.1:8000/results/{output_raw.split('runs/')[-1]}"
    elif output_raw:
        image_url = f"http://127.0.0.1:8000/results/{os.path.basename(output_raw)}"
    else:
        image_url = ""

    # Auto-generate Alert in MongoDB if safety violation detected (Note #5 & #8)
    detections = result.get("detections", {})
    no_hardhat = detections.get("NO-Hardhat", 0)
    no_vest = detections.get("NO-Safety Vest", 0)

    generated_alert = None
    if no_hardhat > 0 or no_vest > 0:
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        v_types = []
        if no_hardhat > 0: v_types.append(f"{no_hardhat} person(s) without Hardhat")
        if no_vest > 0: v_types.append(f"{no_vest} person(s) without Safety Vest")
        v_summary = " and ".join(v_types)

        alert_doc = {
            "_id": f"ALT-PPE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "id": f"ALT-PPE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": "PPE Violation Detected by YOLOv11",
            "message": f"Visual safety inspection detected {v_summary} in active work area.",
            "severity": "CRITICAL" if no_hardhat > 0 else "HIGH",
            "source_agent": "Safety Agent (YOLOv11)",
            "is_resolved": False,
            "created_at": now_str
        }
        try:
            from app.db.connection import db
            db["alerts"].insert_one(alert_doc)
            generated_alert = alert_doc
            print(f"Safety Violation Alert logged to DB: {alert_doc['title']}")
        except Exception as e:
            print(f"Failed to log safety alert to DB: {e}")

    return {

        "message":
            "AI Safety Analysis Completed",

        "filename":
            file.filename,

        "output_image":
            image_url,

        "detections":
            result["detections"],

        "risk_level":
            result["risk_level"],

        "recommendation":
            result["recommendation"],

        "report":
            result["report"],

        "alert_generated":
            generated_alert
    }


# ==========================================
# VIDEO DETECTION
# ==========================================

@router.post("/video-detect")
async def detect_video_safety(
    file: UploadFile = File(...)
):

    upload_dir = "uploads/videos"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    video_path = os.path.join(
        upload_dir,
        file.filename
    )

    with open(
        video_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    print(
        "Processing video:",
        video_path
    )

    # ======================================
    # STEP 1: YOLO VIDEO DETECTION
    # ======================================

    video_result = detect_video(
        video_path
    )


    # ======================================
    # STEP 2: VIDEO SAFETY AI GRAPH
    # ======================================

    graph_result = video_graph.invoke(
        {
            "image_path": "",

            "output_image": "",

            "detections":
                video_result["detections"],

            "risk_level":
                video_result["risk_level"],

            "recommendation": "",

            "report": "",

            "compliance_score":
                video_result[
                    "compliance_score"
                ],

            "analyzed_frames":
                video_result[
                    "analyzed_frames"
                ],

            "violation_frames":
                video_result[
                    "violation_frames"
                ]
        }
    )


    # ======================================
    # STEP 3: RESPONSE
    # ======================================

    return {

        "message":
            "AI Video Safety Analysis Completed",

        "filename":
            file.filename,

        "output_video":
            video_result[
                "output_video"
            ],

        "detections":
            video_result[
                "detections"
            ],

        "compliance_score":
            video_result[
                "compliance_score"
            ],

        "risk_level":
            graph_result[
                "risk_level"
            ],

        "analyzed_frames":
            video_result[
                "analyzed_frames"
            ],

        "violation_frames":
            video_result[
                "violation_frames"
            ],

        "recommendation":
            graph_result[
                "recommendation"
            ],

        "report":
            graph_result[
                "report"
            ]
    }


# ==========================================
# LIVE WEBCAM DETECTION
# ==========================================

from pydantic import BaseModel
from typing import Optional

class LiveDetectPayload(BaseModel):
    image: str

@router.post("/detect-live")
@router.post("/live-detect")
async def live_detect_endpoint(payload: LiveDetectPayload):
    try:
        # STEP 1: PARSE BASE64 IMAGE
        img_data = payload.image
        if "," in img_data:
            img_data = img_data.split(",", 1)[1]

        image_bytes = base64.b64decode(img_data)
        np_array = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if frame is None:
            return {
                "error": "Unable to decode frame",
                "detections": {},
                "risk_level": "LOW"
            }

        # STEP 2: YOLO DETECTION
        result = detect_live_frame(frame)
        detections = result.get("detections", {})

        # STEP 3: PERSISTENT VIOLATION TRACKING
        incident_result = live_tracker.update(detections) if live_tracker else {
            "violation": False,
            "confirmed": False,
            "incident": False
        }

        # STEP 4: ENCODE ANNOTATED FRAME TO BASE64
        annotated_frame = result.get("frame", frame)
        success, encoded_image = cv2.imencode(".jpg", annotated_frame)
        image_base64 = ""
        if success:
            image_base64 = base64.b64encode(encoded_image.tobytes()).decode("utf-8")

        # STEP 5: CALCULATE RISK LEVEL
        no_hardhat = detections.get("NO-Hardhat", 0)
        no_vest = detections.get("NO-Safety Vest", 0)
        persons = detections.get("Person", 0)
        hardhats = detections.get("Hardhat", 0)
        vests = detections.get("Safety Vest", 0)

        risk_level = "LOW"
        if no_hardhat > 0 or no_vest > 0:
            risk_level = "HIGH"
        elif persons > 0 and (hardhats < persons or vests < persons):
            risk_level = "MEDIUM"

        # STEP 6: AUTO-GENERATE ALERT IF VIOLATION PERSISTS
        generated_alert = None
        if no_hardhat > 0 or no_vest > 0:
            from datetime import datetime
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            v_types = []
            if no_hardhat > 0: v_types.append(f"{no_hardhat} person(s) without Hardhat")
            if no_vest > 0: v_types.append(f"{no_vest} person(s) without Safety Vest")
            v_summary = " and ".join(v_types)

            alert_doc = {
                "_id": f"ALT-LIVE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "id": f"ALT-LIVE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "title": "Live Camera: PPE Violation Detected",
                "message": f"Real-time surveillance detected {v_summary}.",
                "severity": "CRITICAL" if no_hardhat > 0 else "HIGH",
                "source_agent": "Live Safety Cam (YOLOv11)",
                "is_resolved": False,
                "created_at": now_str
            }
            try:
                from app.db.connection import db
                db["alerts"].insert_one(alert_doc)
                generated_alert = alert_doc
            except Exception as e:
                pass

        return {
            "detections": detections,
            "image": f"data:image/jpeg;base64,{image_base64}",
            "risk_level": risk_level,
            "violation": incident_result.get("violation", False),
            "confirmed_violation": incident_result.get("confirmed", False),
            "incident": incident_result.get("incident", False),
            "alert_generated": generated_alert
        }

    except Exception as e:
        print("LIVE DETECTION ERROR:", e)
        return {
            "error": str(e),
            "detections": {},
            "risk_level": "LOW"
        }