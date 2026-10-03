export interface ExperienceItem {
  id: string;
  role: string;
  company: string;
  location?: string;
  startDate?: string;
  endDate?: string;
  current?: boolean;
  bullets: string[];
}

export interface EducationItem {
  id: string;
  institution: string;
  degree: string;
  field?: string;
  graduationYear?: string;
  gpa?: string;
}

export interface ProjectItem {
  id: string;
  title: string;
  description?: string;
  technologies: string[];
  bullets: string[];
}

export interface ResumeData {
  fullName: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  website?: string;
  currentTitle?: string;
  summary: string;
  technicalSkills: string[];
  softSkills: string[];
  experience: ExperienceItem[];
  education: EducationItem[];
  projects: ProjectItem[];
  certifications: string[];
}

export interface JobDescriptionData {
  jobTitle: string;
  company?: string;
  experienceLevel?: string;
  requiredSkills: string[];
  preferredSkills: string[];
  softSkills: string[];
  educationRequirements: string[];
  experienceRequirements: string[];
  responsibilities: string[];
  keywords: { word: string; count: number }[];
  rawText: string;
}

export interface SkillMatchResult {
  skill: string;
  category: 'technical' | 'soft' | 'tool';
  matchType: 'exact' | 'alias' | 'semantic';
  matchedWith?: string;
  confidence: number;
}

export interface MissingSkillItem {
  skill: string;
  importance: 'critical' | 'preferred';
  recommendation: string;
  doNotClaimWarning: string;
}

export interface KeywordMatch {
  keyword: string;
  jobCount: number;
  resumeCount: number;
  foundInResume: boolean;
}

export interface MatchAnalysis {
  overallScore: number;
  breakdown: {
    requiredSkillsScore: number;
    experienceScore: number;
    keywordScore: number;
    educationScore: number;
  };
  matchedSkills: SkillMatchResult[];
  missingSkills: MissingSkillItem[];
  keywordMatches: KeywordMatch[];
  strengths: string[];
  gaps: string[];
  truthCompliance: {
    verifiedCandidateSkillsCount: number;
    fabricatedRiskItemsDetected: number;
    complianceNote: string;
  };
}

export interface TailoredBulletItem {
  originalBullet: string;
  tailoredBullet: string;
  role: string;
  company: string;
  highlightedKeywords: string[];
  explanation: string;
}

export interface TailoredResumeData {
  jobTitle: string;
  targetCompany?: string;
  tailoredSummary: string;
  prioritizedSkills: {
    category: string;
    skills: string[];
  }[];
  tailoredExperience: {
    id: string;
    role: string;
    company: string;
    bullets: string[];
  }[];
  tailoredProjects: ProjectItem[];
  suggestedChanges: {
    section: string;
    type: 'reorder' | 'rewrite' | 'highlight' | 'warning';
    description: string;
    explanation: string;
  }[];
  verificationAudit: {
    inventedExperienceFound: boolean;
    auditSummary: string;
    honestGuidance: string[];
  };
}

export interface ApplicationRecord {
  id: string;
  jobTitle: string;
  company: string;
  dateApplied: string;
  matchScore: number;
  status: 'saved' | 'tailored' | 'applied' | 'interviewing' | 'offer' | 'archived';
  missingSkillsCount: number;
  resumeVersionName: string;
  notes?: string;
}
