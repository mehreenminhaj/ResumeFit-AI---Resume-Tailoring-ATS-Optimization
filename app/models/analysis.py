from typing import List, Optional, Dict, Any

try:
    from pydantic import BaseModel, Field
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self):
            res = {}
            for k, v in self.__dict__.items():
                if isinstance(v, list):
                    res[k] = [item.model_dump() if hasattr(item, "model_dump") else item for item in v]
                elif hasattr(v, "model_dump"):
                    res[k] = v.model_dump()
                else:
                    res[k] = v
            return res

    def Field(*args, default=None, default_factory=None, description=None, **kwargs):
        if default_factory is not None:
            return default_factory()
        return default


class MatchedSkill(BaseModel):
    skill: str = ""
    category: str = "technical"
    match_type: str = "exact"  # exact, alias, semantic
    matched_with: Optional[str] = None
    confidence: float = 1.0


class MissingSkill(BaseModel):
    skill: str = ""
    importance: str = "critical"  # critical, preferred
    recommendation: str = ""
    do_not_claim_warning: str = ""


class KeywordComparison(BaseModel):
    keyword: str = ""
    jd_count: int = 0
    resume_count: int = 0
    found_in_resume: bool = False


class MatchAnalysisResult(BaseModel):
    overall_score: int = 0
    score_breakdown: Dict[str, int] = Field(default_factory=dict)
    matched_skills: List[MatchedSkill] = Field(default_factory=list)
    missing_skills: List[MissingSkill] = Field(default_factory=list)
    keyword_matches: List[KeywordComparison] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    strict_anti_hallucination_verified: bool = True
    compliance_notes: str = ""


class SuggestedChange(BaseModel):
    section: str = ""
    type: str = "reorder"  # reorder, rewrite, highlight, warning
    description: str = ""
    explanation: str = ""


class TailoredResumeResult(BaseModel):
    job_title: str = ""
    company: Optional[str] = None
    tailored_summary: str = ""
    prioritized_skills: Dict[str, List[str]] = Field(default_factory=dict)
    tailored_experience: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_changes: List[SuggestedChange] = Field(default_factory=list)
    verification_audit: Dict[str, Any] = Field(default_factory=dict)
