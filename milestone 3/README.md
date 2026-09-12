# Construction Compliance & Insurance Intelligence — Milestone 3 Professional

This is a standalone Milestone 3 agent for later integration into the Construction Intelligence Hub.

## What changed from the basic version

This version accepts more than PDFs:

- PDF
- DOCX
- XLSX
- CSV
- TXT
- Markdown
- JPG/JPEG
- PNG
- WEBP

It also adds:

- Project-type presets
- Custom required-document scope
- Insurance coverage requirements
- Minimum liability limit checking
- Configurable renewal-alert window
- Document register
- Structured field extraction
- Expiry/renewal screening
- Missing-document detection
- Unknown-document review
- Findings with confidence/severity
- Compliance score and status
- LangGraph orchestration
- Responsive enterprise-style UI
- Sample documents for PASS, expiry and low-limit testing

## Run

Backend:
```bat
cd construction-compliance-insurance-agent-milestone-3-pro\backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Frontend in a second terminal:
```bat
cd construction-compliance-insurance-agent-milestone-3-pro\frontend
npm install
npm run dev
```

Open:
http://localhost:5173

Swagger:
http://127.0.0.1:8000/docs

## Test 1 — PASS

Project type: Commercial.

Required:
- Construction permit
- Contractor/license registration
- Project insurance
- Inspection certificate

Upload:
- 01_construction_permit.pdf
- 02_contractor_license.pdf
- 03_insurance_certificate.pdf
- 04_inspection_certificate.pdf

Leave minimum liability blank for the first test.

Expected:
100/100, PASS, 0 findings.

## Test 2 — Expired insurance

Use the same required records but replace the valid insurance PDF with:
06? No — use `05_expired_insurance_for_testing.pdf`.

Expected:
Expired insurance finding, CRITICAL severity, non-PASS status.

## Test 3 — Minimum insurance limit

Set:
Minimum liability limit = 5000000

Upload `06_low_limit_insurance_for_testing.pdf` as the insurance evidence.

Expected:
Insurance limit below configured minimum.

## Important

The baseline extraction and rules are not a legal compliance determination. Jurisdiction-specific requirements, permit scope, policy wording, endorsements, named insureds, exclusions, limits and original documents must be verified by qualified professionals.

For image OCR, install a system OCR engine such as Tesseract separately and ensure the Python OCR packages are available, or replace the extractor with your enterprise OCR provider.
