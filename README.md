# Resume Tailoring Assistant (ResumeFit AI)

> **ResumeFit AI** is an AI-powered resume optimization system that analyzes target job descriptions against a candidate's resume, identifies matching and missing skills, detects critical ATS keywords, provides personalized truthful improvement recommendations, and generates tailored resumes while **strictly preventing fabricated or unsupported experience**.

---

## 🎯 What It Does

```text
Resume (PDF/DOCX/TXT)
   ↓
Extract text & structured profile
   ↓
Analyze experience, skills, projects
   ↓
                    ┌───────────────┐
Job Description →   │ Matching      │
                    │ Engine        │
                    └───────┬───────┘
                            ↓
                  Identify requirements
                            ↓
              ┌─────────────┴─────────────┐
              ↓                           ↓
       Matching Skills              Missing Skills
       (Exact + Synonyms)           (Truth Advisory)
              ↓                           ↓
       Tailor Resume              Improvement Tips
              └─────────────┬─────────────┘
                            ↓
                    Generate Outputs
                            ↓
             Tailored Resume (.docx) + ATS Report (.md)
```

### 🛡️ The Strict Anti-Hallucination Rule

The application **never invents experience**:
- If the JD requires **AWS** or **Docker**, and your resume lacks it, ResumeFit AI will **never** pretend you used it professionally.
- Instead, it marks it as a **Missing Skill** with an honest advisory:
  > **Missing Skill:** AWS  
  > **Recommendation:** Consider learning AWS fundamentals or adding personal projects/certifications if you have completed them.  
  > **Strict Rule:** Do NOT claim professional AWS experience.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Document Processing:** PyMuPDF (`fitz`), `python-docx`, `ReportLab`
- **NLP & Matching:** Scikit-learn, Regex tokenizers, Skill Canonical Alias Dictionary
- **AI / LLMs:** Configurable Gemini API (`gemini-2.5-flash`) & OpenAI API (`gpt-4o-mini`)
- **Frontend:** Vanilla HTML5, CSS3 (Modern SaaS Theme), Vanilla JavaScript (Zero TypeScript)
- **Database / Persistence:** SQLite / LocalStorage Application Tracker
- **Testing:** `pytest`, `httpx` (TestClient)

---

## 📁 Project Structure

```text
resume-tailoring-assistant/
│
├── app/
│   ├── main.py                     # FastAPI application & router mounting
│   │
│   ├── api/                        # REST API Endpoints
│   │   ├── __init__.py
│   │   ├── resume.py               # Resume upload & text parsing
│   │   ├── jobs.py                 # Job description analysis & URL scraping
│   │   └── analysis.py             # Match scoring, tailoring & export
│   │
│   ├── services/                   # Business Logic & Algorithms
│   │   ├── __init__.py
│   │   ├── pdf_parser.py           # PyMuPDF text extraction
│   │   ├── docx_parser.py          # python-docx parser
│   │   ├── resume_analyzer.py      # Structured resume extractor
│   │   ├── jd_analyzer.py          # Structured JD requirements extractor
│   │   ├── matcher.py              # Skill alias mapping & weighted ATS scoring
│   │   ├── llm_service.py          # LLM tailoring with anti-hallucination prompts
│   │   ├── resume_generator.py     # python-docx ATS resume builder
│   │   └── report_generator.py     # Markdown report generator
│   │
│   ├── models/                     # Pydantic Schemas
│   │   ├── __init__.py
│   │   ├── resume.py               # ResumeData, ExperienceItem, ProjectItem
│   │   ├── job.py                  # JobDescriptionData, KeywordFrequency
│   │   └── analysis.py             # MatchAnalysisResult, TailoredResumeResult
│   │
│   └── utils/                      # Helper Utilities
│       ├── __init__.py
│       ├── text_cleaner.py         # Whitespace cleaning & keyword counter
│       └── file_validator.py       # Extension and size validation
│
├── frontend/                       # Web User Interface
│   ├── index.html                  # Responsive SaaS Studio & Application Tracker
│   ├── style.css                   # Refined design system & dark mode
│   └── app.js                      # Vanilla JavaScript controller
│
├── uploads/                        # Temporary uploaded resume files
├── outputs/                        # Generated tailored DOCX & reports
│
├── tests/                          # Pytest Unit Test Suite
│   ├── __init__.py
│   ├── test_parser.py              # Text cleaning & validator tests
│   ├── test_matcher.py             # Exact, alias & gap matching tests
│   └── test_api.py                 # FastAPI endpoint integration tests
│
├── .env                            # Environment variables & API keys
├── .gitignore
├── requirements.txt                # Python dependencies
├── README.md
└── run.py                          # Server launcher script
```

---

## 🚀 Getting Started

### 1. Clone & Set Up Virtual Environment

In PowerShell (Windows):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `.env`:
```ini
# Add your Gemini or OpenAI key (Gemini is free and recommended)
GEMINI_API_KEY="your-gemini-api-key"
# or
OPENAI_API_KEY="your-openai-api-key"

LLM_PROVIDER="gemini"
LLM_MODEL="gemini-2.5-flash"
PORT=8000
```

### 3. Run the Application

```bash
python run.py
```

Then open your browser at:
- **Web UI:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Running Unit Tests

Run the full pytest suite:

```bash
pytest tests/ -v
```

---

## 💻 CLI MVP Terminal Mode

In addition to the Web UI, an interactive Terminal MVP is available directly inside the application under the **CLI MVP Terminal** tab!

Available commands:
- `help` - Show all CLI options
- `run demo` - Run the complete end-to-end resume tailoring pipeline with sample data
- `resumefit match` - Inspect matching skills & aliases
- `resumefit gaps` - View missing requirements & strict truth advisories
- `resumefit audit` - Verify zero fabricated claims
- `resumefit export --format docx` - Generate Word document output
- `clear` - Clear terminal screen
