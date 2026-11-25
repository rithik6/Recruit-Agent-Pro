from recruit_agent.config import DEFAULT_MODEL, load_settings
from recruit_agent.prompt_builder import build_user_prompt, load_system_prompt
from recruit_agent.report import to_markdown
from recruit_agent.schemas import AnalysisResult


# --- system prompt file ---

def test_system_prompt_file_loads_and_has_key_rules():
    prompt = load_system_prompt()
    assert prompt.startswith("# Role")
    assert "JSON" in prompt  # Groq JSON mode needs the word JSON in the prompt
    assert "untrusted data" in prompt  # prompt-injection rule
    assert "gender" in prompt  # fairness rule
    assert "Never invent" in prompt  # accuracy rule


def test_user_prompt_puts_inputs_inside_delimiters_in_order():
    prompt = build_user_prompt("Data Analyst", "Skills: SQL", "Resume text")
    assert prompt.startswith("Target role: Data Analyst")
    jd_at = prompt.index("<job_description>\nSkills: SQL\n</job_description>")
    resume_at = prompt.index("<resume>\nResume text\n</resume>")
    assert jd_at < resume_at


# --- settings ---

def test_settings_read_from_environment(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test")
    monkeypatch.setenv("GROQ_MODEL", "openai/gpt-oss-20b")
    settings = load_settings(load_env_file=False)
    assert settings.groq_api_key == "gsk_test"
    assert settings.groq_model == "openai/gpt-oss-20b"


def test_settings_defaults_when_env_is_empty(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("GROQ_MODEL", "")
    settings = load_settings(load_env_file=False)
    assert settings.groq_api_key is None
    assert settings.groq_model == DEFAULT_MODEL


# --- downloadable report ---

def test_report_contains_score_gaps_and_all_20_questions(valid_analysis):
    report = to_markdown(AnalysisResult.model_validate(valid_analysis), "Backend Developer")

    assert report.startswith("# Recruit-Agent Pro report: Backend Developer")
    assert "**ATS match score:** 62/100" in report
    assert "1. **Docker**" in report
    assert "1. Behavioral question 1?" in report
    assert "6. Technical question 1?" in report
    assert "20. Scenario question 10?" in report
