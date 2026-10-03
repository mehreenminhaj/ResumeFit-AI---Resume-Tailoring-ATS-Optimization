import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.resume import ResumeData
from app.services.resume_analyzer import extract_resume_text, parse_resume_structure
from app.utils.file_validator import validate_file_extension

router = APIRouter(prefix="/resume", tags=["Resume"])
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Uploads a resume file (.pdf, .docx, .txt), validates, and extracts text and structured data.
    """
    valid, err_msg = validate_file_extension(file.filename)
    if not valid:
        raise HTTPException(status_code=400, detail=err_msg)

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = extract_resume_text(str(file_path))
        structured = parse_resume_structure(text)
        return {
            "filename": file.filename,
            "character_count": len(text),
            "raw_text": text,
            "resume_data": structured.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")


@router.post("/parse-text")
async def parse_text_resume(resume_text: str = Form(...)):
    """
    Parses plain text resume into structured format.
    """
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text cannot be empty")

    structured = parse_resume_structure(resume_text)
    return {
        "character_count": len(resume_text),
        "raw_text": resume_text,
        "resume_data": structured.model_dump()
    }
