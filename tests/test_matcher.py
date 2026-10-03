import pytest
from app.models.resume import ResumeData, ExperienceItem, ProjectItem
from app.models.job import JobDescriptionData, KeywordFrequency
from app.services.matcher import calculate_match_analysis, normalize_skill, SKILL_ALIASES


def test_normalize_skill_aliases():
    assert normalize_skill("postgres") == "postgresql"
    assert normalize_skill("PostgreSQL") == "postgresql"
    assert normalize_skill("js") == "javascript"
    assert normalize_skill("React.js") == "react"
    assert normalize_skill("fastapi") == "fastapi"


def test_calculate_match_analysis_exact_and_missing():
    resume = ResumeData(
        full_name="Jane Doe",
        summary="Backend developer building scalable web services",
        technical_skills=["Python", "SQL", "FastAPI", "Pandas", "Git"],
        experience=[
            ExperienceItem(
                role="Software Engineer",
                company="Tech Corp",
                bullets=["Built RESTful APIs using FastAPI and PostgreSQL"]
            )
        ]
    )

    jd = JobDescriptionData(
        job_title="Senior Python Backend Engineer",
        required_skills=["Python", "SQL", "FastAPI", "Docker", "AWS", "PostgreSQL"],
        preferred_skills=["Kubernetes", "Redis"],
        keywords=[
            KeywordFrequency(word="python", count=5),
            KeywordFrequency(word="fastapi", count=4),
            KeywordFrequency(word="docker", count=3)
        ]
    )

    analysis = calculate_match_analysis(resume, jd)

    # Matched skills should include Python, SQL, FastAPI, and PostgreSQL (via experience mention/alias)
    matched_names = {m.skill.lower() for m in analysis.matched_skills}
    assert "python" in matched_names
    assert "sql" in matched_names
    assert "fastapi" in matched_names

    # Missing skills should identify Docker and AWS with strict warnings
    missing_names = {m.skill.lower() for m in analysis.missing_skills}
    assert "docker" in missing_names
    assert "aws" in missing_names

    # Check that warning prevents fabrication
    docker_missing = next(m for m in analysis.missing_skills if m.skill.lower() == "docker")
    assert "Do not fabricate" in docker_missing.do_not_claim_warning


def test_truth_compliance_verified():
    resume = ResumeData(full_name="Bob Smith", technical_skills=["Python"])
    jd = JobDescriptionData(job_title="Developer", required_skills=["Python", "AWS"])

    analysis = calculate_match_analysis(resume, jd)
    assert analysis.strict_anti_hallucination_verified is True
    assert analysis.overall_score >= 15
