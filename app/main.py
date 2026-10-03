import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.resume import router as resume_router
from app.api.jobs import router as jobs_router
from app.api.analysis import router as analysis_router

app = FastAPI(
    title="Resume Tailoring Assistant (ResumeFit AI)",
    description="Intelligent ATS Resume Tailoring System with Strict Anti-Hallucination Guardrails",
    version="1.0.0"
)

# Enable CORS for local development & frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(resume_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")

# Mount frontend directory for static UI serving if it exists
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "Resume Tailoring Assistant",
        "version": "1.0.0"
    }
