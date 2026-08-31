from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import tempfile

from app.db.connection import db
from app.reports.pdf_generator import generate_report_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/{report_id}/pdf")
def download_report_pdf(report_id: str):
    try:
        # Load from MongoDB
        report = db["reports"].find_one({"_id": report_id})
        if not report:
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found.")

        # Create temporary file path
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, f"{report_id}.pdf")
        
        # Generate the PDF
        generate_report_pdf(report, pdf_path)
        
        # Return FileResponse
        return FileResponse(
            path=pdf_path,
            filename=f"{report_id}.pdf",
            media_type="application/pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")
