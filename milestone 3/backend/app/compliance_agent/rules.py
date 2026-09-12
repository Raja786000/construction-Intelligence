from datetime import date
from dateutil import parser

RANK={"NONE":0,"LOW":1,"MEDIUM":2,"HIGH":3,"CRITICAL":4}
LABEL={
 "permit":"Construction permit","license":"Contractor/license registration",
 "insurance":"Project insurance","workers_compensation":"Workers compensation insurance",
 "inspection_certificate":"Inspection certificate","completion_certificate":"Completion/occupancy certificate",
 "method_statement":"Method statement / SWMS","risk_assessment":"Risk assessment / JHA",
 "environmental_permit":"Environmental permit","material_certificate":"Material/test certificate"
}
DEFAULT=["permit","license","insurance","inspection_certificate"]

def pd(v):
    try: return parser.parse(v).date() if v else None
    except: return None

def f(kind, ftype, title, desc, sev, conf, doc, evidence, action, **meta):
    return {"category":kind,"finding_type":ftype,"title":title,"description":desc,
            "severity":sev,"confidence":conf,"document":doc,"evidence":evidence,
            "recommended_action":action,"human_verification_required":True,"metadata":meta}

def run_rules(docs, required, coverages, min_limit, inspection_date, renewal_window=30):
    today=pd(inspection_date) or date.today()
    found=[]
    present={d["doc_type"] for d in docs if d["doc_type"]!="unknown"}

    for req in required:
        if req not in present:
            found.append(f("compliance","missing_document",f"Missing {LABEL.get(req,req)}",
              f"No recognized evidence was submitted for {LABEL.get(req,req).lower()}.","HIGH",.99,None,
              "No matching document found in the submitted evidence.",
              f"Provide and verify a valid {LABEL.get(req,req).lower()}.",required_type=req))

    for d in docs:
        fields=d.get("fields",{})
        exp=pd(fields.get("expiry_date"))
        if exp:
            days=(exp-today).days
            if days<0:
                sev="CRITICAL" if d["doc_type"]=="insurance" else "HIGH"
                found.append(f("validity","expired_document",f"Expired {LABEL.get(d['doc_type'],d['doc_type'])}",
                  f"The document appears to have expired {abs(days)} day(s) before the inspection date.",sev,.98,
                  d["filename"],f"Expiry date: {fields['expiry_date']}",
                  "Obtain a current document and verify it against the project requirements.",days_from_expiry=days))
            elif days<=renewal_window:
                found.append(f("validity","expiring_soon",f"{LABEL.get(d['doc_type'],d['doc_type'])} expires soon",
                  f"The document expires in approximately {days} day(s).","MEDIUM",.97,d["filename"],
                  f"Expiry date: {fields['expiry_date']}",
                  "Start renewal and record the replacement before the expiry date.",days_to_expiry=days))

        if d["doc_type"]=="insurance":
            if not fields.get("policy_number"):
                found.append(f("insurance","missing_policy_identifier","Insurance policy identifier not extracted",
                  "A policy/certificate identifier could not be confidently extracted.","MEDIUM",.86,d["filename"],
                  "No policy number was extracted.","Verify the original certificate and record the policy/certificate number."))
            if not fields.get("expiry_date"):
                found.append(f("insurance","missing_expiry","Insurance expiry date not extracted",
                  "No reliable expiry/valid-through date was extracted.","HIGH",.94,d["filename"],
                  "Expiry field was not found.","Verify the original certificate and record its dates."))
            if min_limit is not None and fields.get("coverage_limit"):
                try:
                    amount=float(str(fields["coverage_limit"]).replace(",",""))
                    if amount < min_limit:
                        found.append(f("insurance","insufficient_limit","Insurance limit below configured minimum",
                          f"Extracted coverage limit {amount:,.0f} is below the configured minimum {min_limit:,.0f}.",
                          "HIGH",.95,d["filename"],f"Extracted limit: {amount:,.0f}",
                          "Verify the original policy and obtain coverage meeting the project requirement.",
                          extracted_limit=amount,minimum_limit=min_limit))
                except: pass
            if coverages:
                txt=(fields.get("coverage_type") or "").lower()
                for cov in coverages:
                    if cov.lower() not in txt:
                        found.append(f("insurance","coverage_not_confirmed",f"Required coverage not confirmed: {cov}",
                          f"The extracted insurance text did not confidently confirm the required coverage '{cov}'.",
                          "MEDIUM",.75,d["filename"],f"Required: {cov}",
                          "Review the policy wording, endorsements and schedule to confirm this coverage."))

    return found
