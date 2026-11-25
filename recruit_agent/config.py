"""Settings for the app.

Secrets come from environment variables: a local `.env` file, or the Secrets
page on Streamlit Cloud (which exposes top-level secrets as env vars).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# llama-3.1-8b-instant was shut down by Groq on 2026-08-16.
DEFAULT_MODEL = "openai/gpt-oss-120b"


@dataclass(frozen=True)
class Settings:
    groq_api_key: str | None
    groq_model: str = DEFAULT_MODEL
    temperature: float = 0.3

    # Guardrail limits
    max_pdf_mb: int = 5  # keep in sync with .streamlit/config.toml
    max_pdf_pages: int = 10
    min_resume_chars: int = 200
    max_resume_chars: int = 15_000
    min_jd_chars: int = 30
    max_jd_chars: int = 5_000


def load_settings(load_env_file: bool = True) -> Settings:
    """Read settings from the environment (and `.env`, unless disabled for tests)."""
    if load_env_file:
        load_dotenv()
    return Settings(
        groq_api_key=os.getenv("GROQ_API_KEY") or None,
        groq_model=os.getenv("GROQ_MODEL") or DEFAULT_MODEL,
    )
