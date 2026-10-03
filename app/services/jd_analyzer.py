import os
from typing import Dict, Any, List
from app.models.job import JobDescriptionData, KeywordFrequency
from app.utils.text_cleaner import extract_keywords_from_text


def parse_job_description(jd_text: str) -> JobDescriptionData:
    """
    Analyzes job description to extract required skills, preferred skills,
    experience level, and ATS keywords.
    """
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            from app.services.llm_service import call_llm_json

            prompt = f"""
Analyze the following job description.

Return valid JSON with exactly these fields:
{{
    "job_title": "Job Title",
    "company": "Company Name if found",
    "experience_level": "e.g. Senior / Mid / 3+ years",
    "required_skills": ["python", "sql", "fastapi"],
    "preferred_skills": ["docker", "aws"],
    "soft_skills": ["collaboration", "problem solving"],
    "education": ["Bachelor's in CS or equivalent"],
    "experience_requirements": ["3+ years in backend engineering"],
    "responsibilities": ["Design and maintain scalable microservices"]
}}

Job Description:
{jd_text[:12000]}
"""
            data = call_llm_json(prompt)
            kw_counts = extract_keywords_from_text(jd_text, top_n=25)
            keywords = [KeywordFrequency(word=w, count=c) for w, c in kw_counts.items()]

            return JobDescriptionData(
                job_title=data.get("job_title", "Target Role"),
                company=data.get("company"),
                experience_level=data.get("experience_level"),
                required_skills=data.get("required_skills", []),
                preferred_skills=data.get("preferred_skills", []),
                soft_skills=data.get("soft_skills", []),
                education=data.get("education", []),
                experience_requirements=data.get("experience_requirements", []),
                responsibilities=data.get("responsibilities", []),
                keywords=keywords,
                raw_text=jd_text
            )
        except Exception as e:
            print(f"LLM JD extraction failed, using heuristic: {e}")

    # Heuristic fallback
    kw_counts = extract_keywords_from_text(jd_text, top_n=25)
    keywords = [KeywordFrequency(word=w, count=c) for w, c in kw_counts.items()]

    common_tech = ["python", "sql", "fastapi", "docker", "aws", "postgresql", "react", "git", "rest api"]
    found_req = [t for t in common_tech if t in jd_text.lower()]

    return JobDescriptionData(
        job_title="Target Position",
        required_skills=found_req[:4],
        preferred_skills=found_req[4:],
        keywords=keywords,
        raw_text=jd_text
    )
