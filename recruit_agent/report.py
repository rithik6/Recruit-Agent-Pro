"""Turns an AnalysisResult into a Markdown report for download."""

from __future__ import annotations

from .schemas import AnalysisResult


def to_markdown(result: AnalysisResult, role: str) -> str:
    lines = [
        f"# Recruit-Agent Pro report: {role}",
        "",
        f"**ATS match score:** {result.ats_score}/100",
        "",
        result.score_summary,
        "",
    ]

    if result.matched_skills:
        lines += ["## Matched skills", "", ", ".join(result.matched_skills), ""]

    lines += ["## Top 5 missing skills", ""]
    lines += [
        f"{i}. **{gap.skill}**: {gap.why_it_matters}"
        for i, gap in enumerate(result.missing_skills, start=1)
    ]
    lines.append("")

    if result.improvement_tips:
        lines += ["## How to close the gaps", ""]
        lines += [f"- {tip}" for tip in result.improvement_tips]
        lines.append("")

    lines += ["## 20 interview questions", ""]
    number = 1
    for title, questions in question_sections(result):
        lines += [f"### {title}", ""]
        for question in questions:
            lines.append(f"{number}. {question}")
            number += 1
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def question_sections(result: AnalysisResult) -> list[tuple[str, list[str]]]:
    q = result.interview_questions
    return [
        ("Behavioral", q.behavioral),
        ("Technical fundamentals", q.technical_fundamentals),
        ("Scenario-based (advanced)", q.scenario_based),
    ]
