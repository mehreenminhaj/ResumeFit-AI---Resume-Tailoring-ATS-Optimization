import os
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.models.resume import ResumeData
from app.models.job import JobDescriptionData
from app.models.analysis import MatchAnalysisResult, TailoredResumeResult
from app.services.matcher import calculate_match_analysis
from app.services.llm_service import tailor_resume_content, rewrite_bullet_points
from app.services.resume_generator import generate_docx_resume, generate_pdf_resume
from app.services.report_generator import generate_match_report_markdown

router = APIRouter(prefix="/analysis", tags=["Analysis"])
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


class MatchRequest(BaseModel):
    resume: ResumeData
    job_description: JobDescriptionData


class TailorRequest(BaseModel):
    resume: ResumeData
    job_description: JobDescriptionData
    analysis: MatchAnalysisResult


class RewriteBulletRequest(BaseModel):
    bullet: str
    role: str
    keywords: List[str] = []


class ExportRequest(BaseModel):
    resume: ResumeData
    tailored: TailoredResumeResult
    format: str = "docx"  # docx, pdf, or md


@router.post("/match", response_model=MatchAnalysisResult)
async def analyze_match(payload: MatchRequest):
    """
    Computes deterministic match, alias mappings, missing skills, and ATS alignment.
    """
    try:
        return calculate_match_analysis(payload.resume, payload.job_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Match analysis failed: {str(e)}")


@router.post("/tailor", response_model=TailoredResumeResult)
async def tailor_resume(payload: TailorRequest):
    """
    Generates a tailored resume with truthful XYZ bullets and prioritized skills.
    Never invents experience or skills.
    """
    try:
        return tailor_resume_content(payload.resume, payload.job_description, payload.analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tailoring failed: {str(e)}")


@router.post("/rewrite-bullet")
async def rewrite_single_bullet(payload: RewriteBulletRequest):
    """
    Provides 3 truthful variations of a bullet point for interactive tailoring.
    """
    try:
        rewrites = rewrite_bullet_points(payload.bullet, payload.role, payload.keywords)
        return {"rewrites": rewrites}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bullet rewriting failed: {str(e)}")


@router.post("/export")
async def export_tailored_resume(payload: ExportRequest):
    """
    Exports the tailored resume as DOCX, PDF, or Markdown.
    """
    safe_name = payload.resume.full_name.lower().replace(" ", "_")

    if payload.format.lower() == "docx":
        file_path = str(OUTPUT_DIR / f"{safe_name}_tailored.docx")
        generate_docx_resume(payload.resume, payload.tailored, file_path)
        return FileResponse(
            path=file_path,
            filename=f"{safe_name}_tailored_resume.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    elif payload.format.lower() == "pdf":
        file_path = str(OUTPUT_DIR / f"{safe_name}_tailored.pdf")
        generate_pdf_resume(payload.resume, payload.tailored, file_path)
        return FileResponse(
            path=file_path,
            filename=f"{safe_name}_tailored_resume.pdf",
            media_type="application/pdf"
        )

    elif payload.format.lower() == "md":
        report_md = generate_match_report_markdown(
            payload.resume,
            JobDescriptionData(job_title=payload.tailored.job_title),
            MatchAnalysisResult(
                overall_score=85,
                score_breakdown={},
                matched_skills=[],
                missing_skills=[],
                keyword_matches=[],
                strengths=[],
                gaps=[],
                compliance_notes="Generated"
            ),
            payload.tailored
        )
        return Response(
            content=report_md,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={safe_name}_report.md"}
        )

    raise HTTPException(status_code=400, detail="Invalid format. Supported: docx, pdf, md")
