from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_parse_text_resume():
    sample_text = """
    Jane Developer
    jane@example.com | 555-123-4567 | San Francisco, CA
    SUMMARY
    Senior Backend Developer with 5 years in Python and cloud architecture.
    SKILLS
    Python, FastAPI, Docker, PostgreSQL, Redis, Git
    EXPERIENCE
    Software Engineer - Acme Corp (2020 - Present)
    • Architected microservices serving 10M daily requests using FastAPI and Postgres.
    """
    response = client.post("/api/resume/parse-text", data={"resume_text": sample_text})
    assert response.status_code == 200
    data = response.json()
    assert "resume_data" in data
    assert data["resume_data"]["full_name"] != ""


def test_match_endpoint():
    payload = {
        "resume": {
            "full_name": "Jane Developer",
            "summary": "Experienced Python engineer",
            "technical_skills": ["Python", "FastAPI", "SQL"],
            "experience": []
        },
        "job_description": {
            "job_title": "Backend Python Lead",
            "required_skills": ["Python", "FastAPI", "AWS"],
            "preferred_skills": ["Docker"]
        }
    }
    response = client.post("/api/analysis/match", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["overall_score"] > 0
    assert len(res["matched_skills"]) >= 2
    assert any(m["skill"] == "AWS" for m in res["missing_skills"])
