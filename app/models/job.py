from typing import List, Optional, Dict

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


class KeywordFrequency(BaseModel):
    word: str = ""
    count: int = 0


class JobDescriptionData(BaseModel):
    job_title: str = Field(default="Target Role", description="Job Title")
    company: Optional[str] = None
    experience_level: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    experience_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    keywords: List[KeywordFrequency] = Field(default_factory=list)
    raw_text: Optional[str] = None
