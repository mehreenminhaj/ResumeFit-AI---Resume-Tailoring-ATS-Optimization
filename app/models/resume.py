from typing import List, Optional

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


class ExperienceItem(BaseModel):
    id: Optional[str] = None
    role: str = Field(default="", description="Job Title or Position")
    company: str = Field(default="", description="Employer or Company Name")
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current: bool = False
    bullets: List[str] = Field(default_factory=list, description="List of accomplishment bullets")


class EducationItem(BaseModel):
    id: Optional[str] = None
    institution: str = Field(default="", description="College or University")
    degree: str = Field(default="", description="Degree name")
    field: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None


class ProjectItem(BaseModel):
    id: Optional[str] = None
    title: str = Field(default="", description="Project Name")
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    bullets: List[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    full_name: str = Field(default="Candidate", description="Full Name")
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    current_title: Optional[str] = None
    summary: str = Field(default="", description="Professional summary")
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
