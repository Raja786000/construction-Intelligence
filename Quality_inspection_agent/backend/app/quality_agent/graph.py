import uuid
from datetime import datetime, timezone
from langgraph.graph import StateGraph, END
from .state import QualityState
from .tools.checklist import run_measurement_checks

# Visual baseline detections are intentionally conservative. Structured measurement
# violations are deterministic and therefore receive full weight.
VISUAL_THRESHOLD = {
    "crack": .76,
    "concrete": .80,
    "surface": .84,
    "component": .82,
    "corrosion": .78,
}
SEVERITY_ORDER={"none":0,"low":1,"medium":2,"high":3,"critical":4}

# Maximum contribution per finding before confidence scaling.
PENALTY={"low":5,"medium":15,"high":30,"critical":50}

def _score_penalty(f):
    if f.get("source_tool") == "measurement_checklist":
        return PENALTY.get(f.get("severity"), 0)
    conf=float(f.get("confidence",0))
    return PENALTY.get(f.get("severity"), 0) * min(1.0, max(0.0, conf))

def build_graph(detectors):
    g=StateGraph(QualityState)

    def receive(s):
        return {"inspection_id":str(uuid.uuid4()),"errors":[],"warnings":[]}

    def validate(s):
        req=s["request"]
        errors=[]
        if not req.get("project_id"):
            errors.append("Project ID is required.")
        if not req.get("images") and not req.get("measurements"):
            errors.append("Add at least one image or one structured measurement.")
        cats=req.get("inspection_categories") or []
        if req.get("inspection_mode") != "checklist" and req.get("images") and not cats:
            errors.append("Select at least one quality check for image inspection.")
        return {"errors":errors}

    def inspect(s):
        req=s["request"]
        if s.get("errors"):
            return {"findings":[]}
        cats=set(req.get("inspection_categories") or [])
        mode=req.get("inspection_mode","comprehensive")
        # Comprehensive and targeted modes both inspect the checks the user
        # explicitly selected. Quick scan intentionally stays crack-only.
        selected=detectors
        if mode in {"comprehensive", "targeted"}:
            selected=[d for d in detectors if d.category in cats]
        elif mode=="checklist":
            selected=[]
        elif mode=="quick":
            selected=[d for d in detectors if d.category=="crack"]
        findings=[]
        warnings=[]
        for path in req.get("images",[]):
            for d in selected:
                try:
                    candidates=d.detect(path)
                    for f in candidates:
                        # Only validated visual candidates contribute to the result.
                        threshold=VISUAL_THRESHOLD.get(f.get("inspection_category"), .80)
                        if f.get("source_tool")=="measurement_checklist" or float(f.get("confidence",0))>=threshold:
                            findings.append(f)
                        else:
                            warnings.append(f"Low-confidence {d.category} visual candidate suppressed.")
                except Exception as exc:
                    warnings.append(f"{d.key}: {exc}")
        findings.extend(run_measurement_checks(req.get("measurements",{}),cats))
        return {"findings":findings,"warnings":warnings}

    def finalize(s):
        findings=s.get("findings",[])
        seen=set(); clean=[]
        for f in findings:
            key=(f["inspection_category"],f["defect_type"],f.get("image_id"),f["source_tool"],f["evidence"])
            if key in seen:
                continue
            seen.add(key)
            if not f.get("finding_id"):
                f["finding_id"]=str(uuid.uuid4())
            clean.append(f)
        findings=clean

        penalty=sum(_score_penalty(f) for f in findings)
        score=round(max(0.0, min(100.0, 100.0-penalty)), 1)
        severity=max((f.get("severity","none") for f in findings),key=lambda x:SEVERITY_ORDER.get(x,0),default="none")
        if not findings:
            status="PASS"
        elif severity in {"high","critical"}:
            status="FAIL"
        else:
            status="REVIEW_REQUIRED"

        rec=[]
        for f in findings:
            a=f.get("recommended_action")
            if a and a not in rec:
                rec.append(a)
        if not rec:
            rec=["No validated visual defects or tolerance violations were found. Continue routine qualified inspection."]

        result={
            "agent":"quality_inspection_agent",
            "event_type":"quality_inspection_completed",
            "inspection_id":s["inspection_id"],
            "project_id":s["request"]["project_id"],
            "inspection_context":{
                "site_id":s["request"].get("site_id"),
                "zone":s["request"].get("zone"),
                "area":s["request"].get("area")
            },
            "inspection_mode":s["request"].get("inspection_mode"),
            "categories_requested":s["request"].get("inspection_categories",[]),
            "description":s["request"].get("description"),
            "quality_score":score,
            "status":status,
            "severity":severity,
            "finding_count":len(findings),
            "confidence":round(max((float(f.get("confidence",0)) for f in findings),default=0),3),
            "risk_required":severity in {"high","critical"},
            "findings":findings,
            "recommendations":rec,
            "errors":s.get("errors",[]),
            "warnings":s.get("warnings",[]),
            "created_at":datetime.now(timezone.utc).isoformat()
        }
        return {"final_result":result}

    g.add_node("receive",receive)
    g.add_node("validate",validate)
    g.add_node("inspect",inspect)
    g.add_node("finalize",finalize)
    g.set_entry_point("receive")
    g.add_edge("receive","validate")
    g.add_edge("validate","inspect")
    g.add_edge("inspect","finalize")
    g.add_edge("finalize",END)
    return g.compile()
