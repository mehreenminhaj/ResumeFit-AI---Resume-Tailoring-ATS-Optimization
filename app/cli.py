#!/usr/bin/env python3
"""
Resume Tailoring Assistant - CLI MVP
Command line tool to extract, match, and tailor resumes against job descriptions.
"""

import sys
import os
import argparse
import json
from pathlib import Path

from app.models.resume import ResumeData
from app.models.job import JobDescriptionData
from app.services.resume_analyzer import extract_resume_text, parse_resume_structure
from app.services.jd_analyzer import parse_job_description
from app.services.matcher import calculate_match_analysis
from app.services.llm_service import tailor_resume_content
from app.services.resume_generator import generate_docx_resume
from app.services.report_generator import generate_match_report_markdown


def run_cli():
    parser = argparse.ArgumentParser(
        prog="resumefit",
        description="ResumeFit AI - ATS Resume Tailoring Assistant with Strict Anti-Hallucination Guardrails"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze resume against job description")
    analyze_parser.add_argument("--resume", "-r", required=True, help="Path to resume file (PDF, DOCX, or TXT)")
    analyze_parser.add_argument("--jd", "-j", required=True, help="Path to job description text file")
    analyze_parser.add_argument("--output", "-o", default="outputs", help="Output directory for generated files")
    analyze_parser.add_argument("--export-docx", action="store_true", help="Generate tailored DOCX file")

    # demo command
    demo_parser = subparsers.add_parser("demo", help="Run with built-in sample data")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "demo":
        print("\n" + "=" * 60)
        print("  🚀 ResumeFit AI - Running Pipeline Demo")
        print("=" * 60)
        print("  [1/4] Extracting candidate profile...")
        resume = ResumeData(
            full_name="Jane Doe",
            email="jane.doe@example.com",
            technical_skills=["Python", "SQL", "FastAPI", "PostgreSQL", "Pandas", "Git", "REST APIs", "Docker"]
        )
        print(f"        ✓ Candidate: {resume.full_name} ({len(resume.technical_skills)} skills)")

        print("  [2/4] Parsing job description...")
        jd = JobDescriptionData(
            job_title="Senior Python Backend Engineer",
            company="CloudScale AI",
            required_skills=["Python", "SQL", "FastAPI", "Docker", "AWS", "PostgreSQL"],
            preferred_skills=["Kubernetes", "Redis"]
        )
        print(f"        ✓ Target: {jd.job_title} at {jd.company}")

        print("  [3/4] Running matching engine & anti-hallucination check...")
        analysis = calculate_match_analysis(resume, jd)
        print(f"\n  🎯 ATS Match Score: {analysis.overall_score}%")
        print(f"  ✓ Matched Skills ({len(analysis.matched_skills)}): {', '.join([m.skill for m in analysis.matched_skills])}")
        print(f"  ! Missing Skills ({len(analysis.missing_skills)}): {', '.join([m.skill for m in analysis.missing_skills])}")

        for ms in analysis.missing_skills:
            print(f"    - {ms.skill}: {ms.recommendation}")
            print(f"      🛡️ {ms.do_not_claim_warning}")

        print("\n  [4/4] Generating tailored resume...")
        tailored = tailor_resume_content(resume, jd, analysis)
        out_path = "outputs/sample_tailored_resume.docx"
        generate_docx_resume(resume, tailored, out_path)
        print(f"  ✓ Exported tailored Word document to: {out_path}")
        print("=" * 60 + "\n")
        return

    if args.command == "analyze":
        resume_path = args.resume
        jd_path = args.jd

        if not os.path.exists(resume_path):
            print(f"Error: Resume file '{resume_path}' does not exist.")
            sys.exit(1)
        if not os.path.exists(jd_path):
            print(f"Error: Job description file '{jd_path}' does not exist.")
            sys.exit(1)

        print(f"Reading resume from {resume_path}...")
        resume_text = extract_resume_text(resume_path)
        resume = parse_resume_structure(resume_text)

        with open(jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()
        jd = parse_job_description(jd_text)

        print(f"Comparing {resume.full_name} against {jd.job_title}...")
        analysis = calculate_match_analysis(resume, jd)

        print("\n" + "=" * 50)
        print(f"  Overall ATS Match Score: {analysis.overall_score}%")
        print("=" * 50)
        print(f"  Matched Skills: {len(analysis.matched_skills)}")
        for m in analysis.matched_skills:
            print(f"    ✓ {m.skill}")

        print(f"\n  Missing Skills (Skill Gaps): {len(analysis.missing_skills)}")
        for ms in analysis.missing_skills:
            print(f"    ! {ms.skill} [{ms.importance}]")
            print(f"      Advice: {ms.recommendation}")
            print(f"      Notice: {ms.do_not_claim_warning}")

        tailored = tailor_resume_content(resume, jd, analysis)

        out_dir = Path(args.output)
        out_dir.mkdir(exist_ok=True)

        # Save Report
        report_file = out_dir / f"{resume.full_name.lower().replace(' ', '_')}_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(generate_match_report_markdown(resume, jd, analysis, tailored))
        print(f"\n  ✓ Saved ATS Match Report: {report_file}")

        if args.export_docx:
            docx_file = out_dir / f"{resume.full_name.lower().replace(' ', '_')}_tailored.docx"
            generate_docx_resume(resume, tailored, str(docx_file))
            print(f"  ✓ Saved Tailored Resume: {docx_file}")


if __name__ == "__main__":
    run_cli()
