"""Report Generation — API Routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid, os

from database.connection import get_db
from models.orm_models import Report

router = APIRouter()


class ReportRequest(BaseModel):
    title: str
    report_type: str  # FRAUD | CUSTOMER | NETWORK | SCENARIO | EXECUTIVE
    parameters: Optional[dict] = {}
    user_id: Optional[str] = None


@router.post("/generate")
async def generate_report(req: ReportRequest, db: Session = Depends(get_db)):
    """Trigger PDF report generation."""
    report_id = str(uuid.uuid4())
    file_path = f"/tmp/finsentinel_report_{report_id}.pdf"

    # In production: call a Celery task for async PDF generation
    # from tasks.report_tasks import generate_pdf_report
    # generate_pdf_report.delay(report_id, req.dict())

    report = Report(
        report_id=uuid.UUID(report_id),
        user_id=req.user_id,
        title=req.title,
        report_type=req.report_type,
        parameters=req.parameters,
        file_path=file_path,
    )
    db.add(report)
    db.commit()

    return {
        "report_id": report_id,
        "title": req.title,
        "status": "queued",
        "message": "Report generation queued. Check /reports/{id}/status for progress.",
    }


@router.get("/")
async def list_reports(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Report)
    if user_id:
        query = query.filter(Report.user_id == user_id)
    reports = query.order_by(Report.generated_at.desc()).limit(50).all()
    return [
        {
            "report_id": str(r.report_id),
            "title": r.title,
            "report_type": r.report_type,
            "generated_at": r.generated_at.isoformat(),
            "available": os.path.exists(r.file_path) if r.file_path else False,
        }
        for r in reports
    ]


@router.get("/{report_id}/download")
async def download_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.report_id == uuid.UUID(report_id)).first()
    if not report:
        raise HTTPException(404, "Report not found")
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(404, "Report file not yet available")
    return FileResponse(report.file_path, media_type="application/pdf", filename=f"{report.title}.pdf")
