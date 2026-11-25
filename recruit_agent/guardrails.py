"""Guardrails for Recruit-Agent Pro.

Input guardrails (run before anything is sent to the AI):
- check_file_size: rejects empty or oversized uploads.
- check_resume_text: rejects empty, scanned or tiny resumes, trims very long
  ones, and warns when the text does not look like a resume.
- check_job_description: rejects empty, too-short or too-long job descriptions.
- detect_prompt_injection: flags text that tries to give the AI instructions.
- redact_pii: replaces emails and phone numbers so they never leave the app.
- sanitize_for_prompt: stops user text from closing the <resume> or
  <job_description> blocks in the prompt.

Output guardrail (run on the AI's reply):
- parse_model_output: the reply must be JSON that matches AnalysisResult.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from pydantic import ValidationError

from .schemas import AnalysisResult


class GuardrailError(ValueError):
    """An input or output failed a guardrail. The message is safe to show users."""


@dataclass
class CheckedText:
    """Text that passed a guardrail, plus any non-blocking warnings."""

    text: str
    warnings: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Input guardrails
# --------------------------------------------------------------------------

def check_file_size(size_bytes: int, max_mb: int) -> None:
    if size_bytes <= 0:
        raise GuardrailError("The uploaded file is empty.")
    if size_bytes > max_mb * 1024 * 1024:
        raise GuardrailError(
            f"The file is {size_bytes / (1024 * 1024):.1f} MB. The limit is {max_mb} MB."
        )


RESUME_KEYWORDS = (
    "experience", "education", "skills", "projects", "employment", "internship",
    "certification", "university", "college", "degree", "summary", "objective",
)
MIN_RESUME_KEYWORDS = 2


def _normalise_whitespace(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def check_resume_text(text: str, *, min_chars: int, max_chars: int) -> CheckedText:
    cleaned = _normalise_whitespace(text or "")
    if not cleaned:
        raise GuardrailError(
            "No text could be read from this PDF. If it is a scanned image, "
            "export it again as a text-based PDF."
        )
    if len(cleaned) < min_chars:
        raise GuardrailError(
            f"Only {len(cleaned)} characters of text were found, and a resume needs at "
            f"least {min_chars}. If it is a scanned image, export it as a text-based PDF."
        )

    warnings: list[str] = []
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars]
        warnings.append(
            f"The resume is very long, so only the first {max_chars:,} characters were analysed."
        )

    lowered = cleaned.lower()
    if sum(word in lowered for word in RESUME_KEYWORDS) < MIN_RESUME_KEYWORDS:
        warnings.append(
            "This document doesn't look like a resume (no sections such as Experience, "
            "Education or Skills were found), so the results may be unreliable."
        )

    warnings.extend(_injection_warnings(cleaned, source="resume"))
    return CheckedText(cleaned, warnings)


def check_job_description(text: str, *, min_chars: int, max_chars: int) -> CheckedText:
    cleaned = _normalise_whitespace(text or "")
    if not cleaned:
        raise GuardrailError("Select a target role or paste a job description.")
    if len(cleaned) < min_chars:
        raise GuardrailError(
            f"The job description is too short ({len(cleaned)} characters). Please describe "
            f"the role and its skills in at least {min_chars} characters."
        )
    if len(cleaned) > max_chars:
        raise GuardrailError(
            f"The job description is {len(cleaned):,} characters. "
            f"Please shorten it to {max_chars:,} or fewer."
        )
    return CheckedText(cleaned, _injection_warnings(cleaned, source="job description"))


_INJECTION_PATTERNS = [
    # "ignore all previous instructions", "disregard the above rules"
    r"\b(ignore|disregard|forget|override)\s+"
    r"(?:(?:all|any|of|the|your|these|those|previous|prior|above|earlier|preceding|system|original)\s+){0,4}"
    r"(instructions?|prompts?|rules|guidelines|directions)\b",
    # "you are now a ..."
    r"\byou\s+are\s+now\b",
    # "reveal your system prompt"
    r"\b(reveal|print|show|repeat|output)\s+(me\s+)?(your|the)\s+(system\s+)?(prompt|instructions)\b",
    # "give this candidate a score of 100%"
    r"\b(give|assign|award|rate|score)\b[^.\n]{0,30}\b(candidate|resume|applicant|me|this)\b"
    r"[^.\n]{0,30}\b100\b",
    # fake chat-role tags such as <system> or </assistant>
    r"<\s*/?\s*(system|assistant|instructions?)\s*>",
    # "New instructions:"
    r"\bnew\s+instructions?\s*:",
]
_INJECTION_RE = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def detect_prompt_injection(text: str) -> list[str]:
    """Return the phrases in `text` that look like instructions aimed at the AI."""
    return [m.group(0) for regex in _INJECTION_RE for m in regex.finditer(text)]


def _injection_warnings(text: str, *, source: str) -> list[str]:
    matches = detect_prompt_injection(text)
    if not matches:
        return []
    return [
        f'The {source} contains text that tries to instruct the AI (e.g. "{matches[0][:60]}"). '
        "It was treated as plain text and not followed."
    ]


_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
# A run of digits with optional +, spaces, dots, dashes and brackets. It is only
# treated as a phone number if it holds 10-15 digits, so years ("2019 - 2023")
# and short numbers are left alone.
_PHONE_CANDIDATE_RE = re.compile(r"(?<![\w+])\+?\(?\d[\d \t().-]{7,}\d(?!\w)")


def redact_pii(text: str) -> tuple[str, int]:
    """Replace emails and phone numbers. Returns (redacted_text, how_many_replaced)."""
    text, emails = _EMAIL_RE.subn("[EMAIL]", text)
    phones = 0

    def _replace_phone(match: re.Match[str]) -> str:
        nonlocal phones
        digits = sum(ch.isdigit() for ch in match.group(0))
        if 10 <= digits <= 15:
            phones += 1
            return "[PHONE]"
        return match.group(0)

    text = _PHONE_CANDIDATE_RE.sub(_replace_phone, text)
    return text, emails + phones


_DELIMITER_RE = re.compile(r"<\s*/?\s*(resume|job_description)\s*>", re.IGNORECASE)


def sanitize_for_prompt(text: str) -> str:
    """Remove our own prompt delimiters from user text so it can't break out of them."""
    return _DELIMITER_RE.sub("", text)


# --------------------------------------------------------------------------
# Output guardrail
# --------------------------------------------------------------------------

def parse_model_output(raw: str) -> AnalysisResult:
    """Parse and validate the AI's reply. Raises GuardrailError if it is unusable."""
    if not raw or not raw.strip():
        raise GuardrailError("The AI returned an empty reply.")

    # Tolerate ```json fences or stray text around the object.
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end < start:
        raise GuardrailError("The AI reply was not JSON.")

    try:
        data = json.loads(raw[start : end + 1])
    except json.JSONDecodeError as exc:
        raise GuardrailError(f"The AI reply was not valid JSON ({exc.msg}).") from exc

    try:
        return AnalysisResult.model_validate(data)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in err['loc'])}: {err['msg']}"
            for err in exc.errors()[:5]
        )
        raise GuardrailError(f"The AI reply did not match the expected format ({problems}).") from exc
