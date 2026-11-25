import pytest

from recruit_agent.guardrails import GuardrailError
from recruit_agent.pdf_parser import PDFExtractionError, extract_text_from_pdf


def test_text_is_extracted_from_valid_pdf(make_pdf):
    text = extract_text_from_pdf(make_pdf(), max_pages=5)
    assert "Alex Sample" in text
    assert "PostgreSQL" in text


def test_pdf_without_text_returns_empty_string(make_pdf):
    assert extract_text_from_pdf(make_pdf(lines=[]), max_pages=5) == ""


@pytest.mark.parametrize("data", [b"", b"this is not a pdf"])
def test_invalid_file_is_rejected(data):
    with pytest.raises(PDFExtractionError, match="valid PDF"):
        extract_text_from_pdf(data, max_pages=5)


def test_too_many_pages_is_rejected(make_pdf):
    with pytest.raises(PDFExtractionError, match="3 pages"):
        extract_text_from_pdf(make_pdf(pages=3), max_pages=2)


def test_password_protected_pdf_is_rejected(make_pdf):
    with pytest.raises(PDFExtractionError, match="password-protected"):
        extract_text_from_pdf(make_pdf(password="secret"), max_pages=5)


def test_pdf_errors_are_guardrail_errors():
    assert issubclass(PDFExtractionError, GuardrailError)
