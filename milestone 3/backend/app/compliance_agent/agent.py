from uuid import uuid4
from datetime import datetime, timezone
from app.compliance_agent.graph import build_graph
from app.compliance_agent.rules import DEFAULT, LABEL

class ComplianceInsuranceAgent:
    def __init__(self): self.graph=build_graph()

    def capabilities(self):
        return {
          "agent":"compliance_insurance_agent","milestone":3,"version":"2.0.0",
          "checks":["missing records","document recognition","expiry/renewal","insurance policy extraction",
                    "coverage confirmation","configured minimum liability limit","extraction quality"],
          "supported_files":["pdf","docx","txt","md","csv","xlsx","png","jpg","jpeg","webp"],
          "default_required_documents":DEFAULT,
          "document_types":LABEL,
          "note":"Baseline, jurisdiction-agnostic screening. Professional verification is required."
        }

    def inspect(self,request):
        s=self.graph.invoke({"request":request})
        docs=s.get("classified",[]); fs=s.get("findings",[])
        return {
          "agent":"compliance_insurance_agent","event_type":"compliance_inspection_completed",
          "project_id":request["project_id"],"inspection_id":str(uuid4()),
          "project_name":request.get("project_name",""),"site_id":request.get("site_id",""),
          "jurisdiction":request.get("jurisdiction",""),"project_type":request.get("project_type",""),
          "compliance_score":s.get("score",0),"status":s.get("status","REVIEW_REQUIRED"),
          "highest_severity":s.get("highest_severity","NONE"),
          "documents_received":len(request.get("documents",[])),
          "documents_recognized":sum(d.get("doc_type")!="unknown" for d in docs),
          "findings_count":len(fs),"findings":fs,
          "document_register":[{
            "document_id":d["document_id"],"filename":d["filename"],"document_type":d["doc_type"],
            "extraction_method":d["extraction_method"],"fields":d["fields"],"url":d["url"],
            "size_bytes":d.get("size_bytes",0)
          } for d in docs],
          "recommendations":s.get("recommendations",[]),
          "warnings":[
            "This is preliminary compliance/insurance screening, not legal advice or proof of compliance.",
            "Verify jurisdiction-specific requirements, policy wording, endorsements, limits and original documents."
          ],
          "errors":s.get("errors",[]),"created_at":datetime.now(timezone.utc).isoformat()
        }
