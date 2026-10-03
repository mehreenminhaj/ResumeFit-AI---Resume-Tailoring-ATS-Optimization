from fastapi import APIRouter, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.job import JobDescriptionData
from app.services.jd_analyzer import parse_job_description

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobUrlRequest(BaseModel):
    url: str


@router.post("/parse")
async def analyze_job(job_description: str = Form(...)):
    """
    Parses and extracts requirements, skills, and ATS keywords from job description text.
    """
    if len(job_description.strip()) < 20:
        raise HTTPException(status_code=400, detail="Job description text is too short")

    try:
        jd_data = parse_job_description(job_description)
        return jd_data.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze job description: {str(e)}")


@router.post("/fetch-url")
async def fetch_job_from_url(payload: JobUrlRequest):
    """
    Fetches job description text from a job posting URL.
    """
    import urllib.request
    import re

    try:
        req = urllib.request.Request(
            payload.url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # Strip scripts, styles, and tags
        text = re.sub(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", " ", html, flags=re.I)
        text = re.sub(r"<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>", " ", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        jd_data = parse_job_description(text[:8000])
        return jd_data.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job description from URL: {str(e)}")
