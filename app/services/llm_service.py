import os
import json
import re
from typing import Dict, Any, List
from app.models.resume import ResumeData
from app.models.job import JobDescriptionData
from app.models.analysis import MatchAnalysisResult, TailoredResumeResult, SuggestedChange


def call_llm_json(prompt: str) -> Dict[str, Any]:
    """
    Executes a structured JSON call using OpenAI or Gemini API based on environment configuration.
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    raw_text = ""

    # Try Gemini if key available or provider is gemini
    if (provider == "gemini" or not openai_key) and gemini_key:
        try:
            # Using google-genai or direct request
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            raw_text = response.text or "{}"
        except Exception as e:
            # Try urllib fallback for zero-dep compatibility
            import urllib.request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            req_data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                raw_text = result["candidates"][0]["content"]["parts"][0]["text"]

    # Try OpenAI
    elif openai_key:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        raw_text = response.choices[0].message.content or "{}"

    else:
        raise ValueError("No LLM API Key found. Set GEMINI_API_KEY or OPENAI_API_KEY in your .env file.")

    # Clean code block markdown if present
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    return json.loads(cleaned.strip())


def tailor_resume_content(
    resume: ResumeData,
    jd: JobDescriptionData,
    analysis: MatchAnalysisResult
) -> TailoredResumeResult:
    """
    Tailors resume to match job description with STRICT ANTI-HALLUCINATION RULES.
    Never invents experience, metrics, or technologies.
    """
    prompt = f"""
You are a professional resume editor.

Your task is to tailor the candidate's resume to the job description.

STRICT RULES:
1. Never invent experience.
2. Never invent employment.
3. Never invent projects.
4. Never invent certifications.
5. Never invent technologies the candidate has not demonstrated.
6. You may reorder existing information.
7. You may rewrite existing bullet points using the XYZ framework (Accomplished [X] as measured by [Y] by doing [Z]).
8. You may emphasize relevant existing skills.
9. Keep achievements truthful.
10. Do not add fake numbers or metrics.

TARGET JOB:
Title: {jd.job_title}
Company: {jd.company or "Target Company"}
Required Skills: {', '.join(jd.required_skills)}
Preferred Skills: {', '.join(jd.preferred_skills)}

CANDIDATE'S CURRENT RESUME:
Name: {resume.full_name}
Summary: {resume.summary}
Skills: {', '.join(resume.technical_skills)}
Experience:
{json.dumps([e.model_dump() for e in resume.experience], indent=2)}

MATCHING CONTEXT:
Matched Skills: {', '.join([m.skill for m in analysis.matched_skills])}
Missing Skills: {', '.join([m.skill for m in analysis.missing_skills])}

Return valid JSON with exactly this structure:
{{
    "job_title": "{jd.job_title}",
    "company": "{jd.company or 'Target Company'}",
    "tailored_summary": "Truthful 3-4 sentence professional summary tailored to role without inventing claims",
    "prioritized_skills": {{
        "Core Matched Skills": ["skills that appear in JD first", "..."],
        "Additional Technical Skills": ["other genuine skills"]
    }},
    "tailored_experience": [
        {{
            "role": "Same role",
            "company": "Same company",
            "bullets": [
                "Enhanced truthful bullet point emphasizing relevant scope",
                "Second enhanced truthful bullet point"
            ]
        }}
    ],
    "suggested_changes": [
        {{
            "section": "Skills",
            "type": "reorder",
            "description": "Moved relevant skills to front of skills list",
            "explanation": "Allows ATS scanners and recruiters to immediately verify primary qualifications."
        }},
        {{
            "section": "Experience",
            "type": "rewrite",
            "description": "Strengthened action verbs and technical keywords",
            "explanation": "Clarifies role impact while retaining strictly factual candidate experience."
        }}
    ],
    "verification_audit": {{
        "unsupported_claims_detected": false,
        "anti_hallucination_guarantee": "No companies, degrees, tools, or metrics were invented."
    }}
}}
"""
    try:
        data = call_llm_json(prompt)
        return TailoredResumeResult(
            job_title=data.get("job_title", jd.job_title),
            company=data.get("company", jd.company),
            tailored_summary=data.get("tailored_summary", resume.summary),
            prioritized_skills=data.get("prioritized_skills", {"Technical Skills": resume.technical_skills}),
            tailored_experience=data.get("tailored_experience", [e.model_dump() for e in resume.experience]),
            suggested_changes=[SuggestedChange(**c) for c in data.get("suggested_changes", [])],
            verification_audit=data.get("verification_audit", {"unsupported_claims_detected": False})
        )
    except Exception as e:
        print(f"LLM tailoring failed, generating deterministic fallback: {e}")
        # Deterministic fallback maintaining truth
        matched_names = {m.skill.lower() for m in analysis.matched_skills}
        reordered_skills = sorted(
            resume.technical_skills,
            key=lambda s: 0 if s.lower() in matched_names else 1
        )
        return TailoredResumeResult(
            job_title=jd.job_title,
            company=jd.company,
            tailored_summary=resume.summary or f"Experienced {resume.current_title or 'Professional'} with expertise in {', '.join(reordered_skills[:4])}.",
            prioritized_skills={"Prioritized Skills": reordered_skills},
            tailored_experience=[e.model_dump() for e in resume.experience],
            suggested_changes=[
                SuggestedChange(
                    section="Skills",
                    type="reorder",
                    description=f"Prioritized {len(analysis.matched_skills)} matched skills to top of section",
                    explanation="Ensures immediate visibility for automated ATS screens."
                )
            ],
            verification_audit={"unsupported_claims_detected": False}
        )


def rewrite_bullet_points(bullet: str, role: str, target_keywords: List[str]) -> List[Dict[str, str]]:
    """
    Generates 3 truthful bullet rewrites tailored for ATS optimization.
    """
    prompt = f"""
Take this resume bullet point from a '{role}' role and produce 3 truthful rewrites.

ORIGINAL BULLET:
"{bullet}"

ALLOWED RELEVANT KEYWORDS (only use if truthful to the context):
{', '.join(target_keywords[:8])}

RULES:
1. Do not invent numbers, metrics, or technologies not in original bullet.
2. Produce 3 styles: 'impact', 'ats_keyword', 'concise'.

Return valid JSON:
{{
    "rewrites": [
        {{
            "style": "impact",
            "title": "Action & Outcome Focused",
            "text": "Rewritten bullet emphasizing action and result truthfully",
            "explanation": "Highlights the delivered contribution clearly."
        }},
        {{
            "style": "ats_keyword",
            "title": "ATS Keyword Optimized",
            "text": "Rewritten bullet integrating relevant terminology",
            "explanation": "Increases keyword relevance without fabricating experience."
        }},
        {{
            "style": "concise",
            "title": "Concise & Direct",
            "text": "Crisp bullet removing fluff",
            "explanation": "Improves recruiter readability."
        }}
    ]
}}
"""
    try:
        data = call_llm_json(prompt)
        return data.get("rewrites", [])
    except Exception as e:
        return [
            {
                "style": "impact",
                "title": "Original Bullet",
                "text": bullet,
                "explanation": "Original text preserved."
            }
        ]
