from langgraph.graph import StateGraph, START, END
from app.compliance_agent.state import ComplianceState
from app.compliance_agent.extractors import extract_text, classify
from app.compliance_agent.rules import run_rules, DEFAULT, RANK

def receive(s): return {"documents":s["request"].get("documents",[]),"errors":[]}
def extract(s):
    out=[]; errors=list(s.get("errors",[]))
    for d in s["documents"]:
        try:
            text,method=extract_text(d["path"])
            typ,fields,preview=classify(text,d["filename"])
            out.append({**d,"doc_type":typ,"extraction_method":method,"fields":fields,"text_preview":preview[:700]})
            if method=="ocr_unavailable":
                errors.append(f"OCR unavailable for image document '{d['filename']}'. Manual review is required for text on this image.")
        except Exception as e:
            errors.append(f"Could not extract '{d['filename']}': {e}")
    return {"extracted":out,"errors":errors}
def classify_node(s): return {"classified":s["extracted"]}
def evaluate(s):
    r=s["request"]
    return {"findings":run_rules(s["classified"],r.get("required_documents") or DEFAULT,
      r.get("required_coverages") or [],r.get("minimum_liability_limit"),
      r.get("inspection_date"),r.get("renewal_window_days",30))}
def finalize(s):
    fs=s.get("findings",[]); errors=s.get("errors",[])
    penalty=sum({"LOW":4,"MEDIUM":12,"HIGH":25,"CRITICAL":40}.get(x["severity"],0) for x in fs)
    score=max(0,min(100,round(100-penalty,1)))
    rank=max([RANK.get(x["severity"],0) for x in fs] or [0])
    sev=["NONE","LOW","MEDIUM","HIGH","CRITICAL"][rank]
    status="FAIL" if sev=="CRITICAL" else ("REVIEW_REQUIRED" if fs or errors else "PASS")
    rec=[]
    if not fs and not errors:
        rec.append("All configured baseline checks passed. Confirm originals and jurisdiction-specific requirements before final approval.")
    for x in fs:
        if x["recommended_action"] not in rec: rec.append(x["recommended_action"])
    if errors: rec.append("Resolve extraction/OCR issues and manually verify affected documents.")
    return {"score":score,"status":status,"highest_severity":sev,"recommendations":rec}
def build_graph():
    g=StateGraph(ComplianceState)
    for n,fn in [("receive",receive),("extract",extract),("classify",classify_node),("evaluate",evaluate),("finalize",finalize)]: g.add_node(n,fn)
    for a,b in [(START,"receive"),("receive","extract"),("extract","classify"),("classify","evaluate"),("evaluate","finalize"),("finalize",END)]: g.add_edge(a,b)
    return g.compile()
