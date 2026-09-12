import uuid

RULES = [
    ("crack_width_mm","crack","crack_width_max_mm",lambda a,b:a>b,"Crack width exceeds the configured maximum.","high"),
    ("concrete_cover_mm","concrete","concrete_cover_min_mm",lambda a,b:a<b,"Concrete cover is below the configured minimum.","high"),
    ("surface_finish_score","surface","surface_finish_min_score",lambda a,b:a<b,"Surface finish score is below the configured minimum.","medium"),
    ("component_alignment_mm","component","component_alignment_max_mm",lambda a,b:a>b,"Component alignment error exceeds the configured maximum.","medium"),
    ("corrosion_depth_mm","corrosion","corrosion_depth_max_mm",lambda a,b:a>b,"Corrosion depth exceeds the configured maximum.","high"),
]

def run_measurement_checks(measurements, categories):
    out=[]
    for value_key, category, tolerance_key, predicate, description, severity in RULES:
        if categories and category not in categories:
            continue
        if value_key not in measurements or tolerance_key not in measurements:
            continue
        value=float(measurements[value_key]); tol=float(measurements[tolerance_key])
        if predicate(value,tol):
            out.append({
                "finding_id":str(uuid.uuid4()),
                "inspection_category":category,
                "defect_type":"measurement_nonconformance",
                "description":description,
                "confidence":1.0,
                "severity":severity,
                "evidence":f"{value_key}={value}; {tolerance_key}={tol}",
                "image_id":None,
                "bounding_boxes":[],
                "measurements":{value_key:value,tolerance_key:tol},
                "source_tool":"measurement_checklist",
                "requires_human_verification":True,
                "recommended_action":"Verify the measurement against approved drawings, specifications and applicable acceptance criteria."
            })
    return out
