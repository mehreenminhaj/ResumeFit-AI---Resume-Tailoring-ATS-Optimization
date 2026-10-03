import json
import os
import re
from pathlib import Path
from typing import Dict, Any

from app.services.pdf_parser import extract_text_from_pdf
from app.services.docx_parser import extract_text_from_docx
from app.models.resume import ResumeData, ExperienceItem, EducationItem, ProjectItem


def extract_resume_text(file_path: str) -> str:
    """
    Universal resume text extractor handling .pdf, .docx, and text files.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

    raise ValueError(f"Unsupported resume file format: {ext}. Only PDF, DOCX, and TXT are supported.")


def parse_resume_structure(resume_text: str) -> ResumeData:
    """
    Extracts structured ResumeData from raw resume text using LLM or smart heuristic extraction.
    """
    # 1. Try LLM extraction if API key configured
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            from app.services.llm_service import call_llm_json

            prompt = f"""
Analyze this resume and extract structured information.

STRICT INSTRUCTION:
Extract ONLY facts present in the resume. Never invent experience, companies, or skills.

Return valid JSON with exactly these fields:
{{
    "full_name": "Candidate Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "City, State",
    "linkedin": "url or handle",
    "github": "url or handle",
    "current_title": "Current or most recent job title",
    "summary": "Existing summary paragraph",
    "technical_skills": ["python", "sql", "fastapi"],
    "soft_skills": ["leadership", "communication"],
    "experience": [
        {{
            "role": "Software Engineer",
            "company": "Company Name",
            "location": "City, State",
            "start_date": "2021",
            "end_date": "Present",
            "current": true,
            "bullets": ["Accomplished bullet 1", "Accomplished bullet 2"]
        }}
    ],
    "education": [
        {{
            "institution": "University Name",
            "degree": "B.S. in Computer Science",
            "field": "Computer Science",
            "graduation_year": "2021"
        }}
    ],
    "projects": [
        {{
            "title": "Project Name",
            "technologies": ["Python", "FastAPI"],
            "bullets": ["Built high throughput API"]
        }}
    ],
    "certifications": ["AWS Solutions Architect", "etc"]
}}

Resume:
{resume_text[:12000]}
"""
            data = call_llm_json(prompt)
            return ResumeData(**data)
        except Exception as e:
            print(f"LLM Resume extraction failed, falling back to heuristics: {e}")

    # Heuristic fallback if LLM is not available or fails
    lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
    full_name = lines[0] if lines else "Candidate"
    
    # Extract email and phone with regex
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
    phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", resume_text)

    # Common tech keywords
    known_skills = [
        "python", "javascript", "typescript", "react", "node.js", "fastapi", "sql",
        "postgresql", "mongodb", "docker", "aws", "git", "rest api", "html", "css",
        "django", "flask", "c++", "c#", "java", "kubernetes", "linux", "pandas", "numpy"
    ]
    detected_skills = [s for s in known_skills if re.search(rf"\b{re.escape(s)}\b", resume_text, re.I)]

    return ResumeData(
        full_name=full_name,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        summary=lines[1] if len(lines) > 1 else "",
        technical_skills=detected_skills,
        experience=[],
        education=[],
        projects=[]
    )
