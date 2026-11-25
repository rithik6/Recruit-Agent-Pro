"""Extract plain text from an uploaded PDF."""

from __future__ import annotations

import pymupdf

from .guardrails import GuardrailError


class PDFExtractionError(GuardrailError):
    """The PDF could not be read safely. The message is safe to show users."""


def extract_text_from_pdf(data: bytes, *, max_pages: int) -> str:
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as exc:  # pymupdf raises several error types for broken files
        raise PDFExtractionError(
            "This file could not be opened as a PDF. Please upload a valid PDF."
        ) from exc

    with doc:
        if doc.needs_pass:
            raise PDFExtractionError(
                "This PDF is password-protected. Please upload an unlocked copy."
            )
        if doc.page_count > max_pages:
            raise PDFExtractionError(
                f"This PDF has {doc.page_count} pages. Resumes are limited to {max_pages} pages."
            )
        return "\n".join(page.get_text() for page in doc).strip()
