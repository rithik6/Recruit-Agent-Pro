"""Builds the messages sent to the AI. The system prompt lives in prompts/system_prompt.md."""

from __future__ import annotations

from pathlib import Path

from .guardrails import sanitize_for_prompt

SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.md"


def load_system_prompt(path: Path = SYSTEM_PROMPT_PATH) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_user_prompt(role: str, job_description: str, resume_text: str) -> str:
    """Wrap the untrusted inputs in delimiters the system prompt tells the AI about."""
    return (
        f"Target role: {sanitize_for_prompt(role)}\n\n"
        f"<job_description>\n{sanitize_for_prompt(job_description)}\n</job_description>\n\n"
        f"<resume>\n{sanitize_for_prompt(resume_text)}\n</resume>\n\n"
        "Analyse the resume against the job description and reply with the JSON object "
        "described in your instructions."
    )
