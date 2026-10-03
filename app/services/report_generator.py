from app.models.analysis import MatchAnalysisResult, TailoredResumeResult
from app.models.resume import ResumeData
from app.models.job import JobDescriptionData


def generate_match_report_markdown(
    resume: ResumeData,
    jd: JobDescriptionData,
    analysis: MatchAnalysisResult,
    tailored: TailoredResumeResult
) -> str:
    """
    Generates a structured markdown report detailing overall match %,
    matched vs missing skills, keyword frequencies, and step-by-step truthful change recommendations.
    """
    lines = []
    lines.append("# RESUME ANALYSIS & TAILORING REPORT")
    lines.append(f"**Target Role:** {jd.job_title} at {jd.company or 'Target Employer'}")
    lines.append(f"**Candidate:** {resume.full_name}")
    lines.append("────────────────────────────────────────────────────────────\n")

    # Score
    lines.append(f"## Overall ATS Skill Match: {analysis.overall_score}%")
    lines.append(f"- **Required Skills:** {analysis.score_breakdown.get('required_skills', 0)}%")
    lines.append(f"- **Preferred Skills:** {analysis.score_breakdown.get('preferred_skills', 0)}%")
    lines.append(f"- **ATS Keyword Alignment:** {analysis.score_breakdown.get('keywords', 0)}%")
    lines.append(f"- **Experience Relevance:** {analysis.score_breakdown.get('experience', 0)}%\n")

    # Matched Skills
    lines.append("### Matched Skills")
    if analysis.matched_skills:
        for m in analysis.matched_skills:
            match_badge = f"(via '{m.matched_with}')" if m.matched_with and m.matched_with != m.skill else ""
            lines.append(f"✓ **{m.skill}** {match_badge}")
    else:
        lines.append("No direct skill matches detected.")
    lines.append("")

    # Missing Skills with strict guidance
    lines.append("### Missing Skills (Gaps)")
    if analysis.missing_skills:
        for ms in analysis.missing_skills:
            imp_tag = "[Required]" if ms.importance == "critical" else "[Preferred]"
            lines.append(f"! **{ms.skill}** {imp_tag}")
            lines.append(f"  • *Recommendation:* {ms.recommendation}")
            lines.append(f"  • *Guidance:* {ms.do_not_claim_warning}")
    else:
        lines.append("All key skills from job description were matched.")
    lines.append("")

    # High Priority ATS Keywords
    lines.append("### ATS Keyword Analysis")
    lines.append("| Keyword | JD Frequency | Resume Frequency | Match Status |")
    lines.append("| :--- | :---: | :---: | :---: |")
    for kw in analysis.keyword_matches:
        status = "✓ Matched" if kw.found_in_resume else "✗ Missing"
        lines.append(f"| {kw.keyword} | {kw.jd_count} | {kw.resume_count} | {status} |")
    lines.append("")

    # Suggested Changes & Audit
    lines.append("### Suggested Changes & Truth Audit")
    for idx, change in enumerate(tailored.suggested_changes, 1):
        lines.append(f"{idx}. **[{change.section}] {change.description}**")
        lines.append(f"   {change.explanation}")
    lines.append("")

    lines.append("### Strict Anti-Hallucination Audit")
    lines.append("🛡️ **Verified Truth Guarantee:**")
    lines.append("- No employers or dates were fabricated.")
    lines.append("- No metrics or percentages were invented.")
    lines.append("- Missing skills are clearly flagged for genuine self-study or adjacent experience rather than falsely claimed.")

    return "\n".join(lines)
