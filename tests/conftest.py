"""Shared test helpers. No test here calls the real Groq API."""

import copy

import pymupdf
import pytest

RESUME_LINES = [
    "Alex Sample - Backend Developer",
    "Summary: 2 years building REST APIs in Python.",
    "Skills: Python, Django, Flask, PostgreSQL, Git, Linux",
    "Experience: Junior Developer, Example Corp (2024-2026)",
    "Built Django REST APIs for an internal inventory tool.",
    "Education: B.Tech Computer Science, 2024",
]

VALID_ANALYSIS = {
    "ats_score": 62,
    "score_summary": "Solid Python and Django experience, but no Docker or Redis.",
    "matched_skills": ["Python", "Django", "PostgreSQL"],
    "missing_skills": [
        {"skill": "Docker", "why_it_matters": "The team ships every service in containers."},
        {"skill": "Redis", "why_it_matters": "Used for caching and queues."},
        {"skill": "FastAPI", "why_it_matters": "New services are written in FastAPI."},
        {"skill": "CI/CD", "why_it_matters": "Engineers own their deployment pipelines."},
        {"skill": "Testing", "why_it_matters": "Code must ship with automated tests."},
    ],
    "interview_questions": {
        "behavioral": [f"Behavioral question {i}?" for i in range(1, 6)],
        "technical_fundamentals": [f"Technical question {i}?" for i in range(1, 6)],
        "scenario_based": [f"Scenario question {i}?" for i in range(1, 11)],
    },
    "improvement_tips": ["Containerise a Django project with Docker."],
}


def _make_pdf(lines=RESUME_LINES, *, pages=1, password=None) -> bytes:
    doc = pymupdf.open()
    for _ in range(pages):
        page = doc.new_page()
        y = 72
        for line in lines:
            page.insert_text((72, y), line, fontsize=11)
            y += 16
    if password:
        return doc.tobytes(
            encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw=password, user_pw=password
        )
    return doc.tobytes()


@pytest.fixture
def make_pdf():
    return _make_pdf


@pytest.fixture
def valid_analysis():
    return copy.deepcopy(VALID_ANALYSIS)


@pytest.fixture
def resume_text():
    return "\n".join(RESUME_LINES)
