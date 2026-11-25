"""Recruit-Agent Pro: Streamlit UI.

This file only draws the page. The logic lives in the `recruit_agent` package
and the AI's instructions live in `prompts/system_prompt.md`.
"""

import hashlib
import re

import streamlit as st

from recruit_agent.analyzer import ResumeAnalyzer, build_llm
from recruit_agent.config import load_settings
from recruit_agent.guardrails import (
    GuardrailError,
    check_file_size,
    check_job_description,
    check_resume_text,
    redact_pii,
)
from recruit_agent.job_roles import JOB_ROLES
from recruit_agent.pdf_parser import extract_text_from_pdf
from recruit_agent.prompt_builder import load_system_prompt
from recruit_agent.report import question_sections, to_markdown
from recruit_agent.schemas import AnalysisResult

PLACEHOLDER_ROLE = "Select a Role"
CUSTOM_ROLE_LABEL = "Custom role (see job description)"

st.set_page_config(page_title="Recruit-Agent Pro", page_icon="💼", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    .stExpander { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

settings = load_settings()


@st.cache_resource(show_spinner=False)
def get_analyzer(model: str, api_key: str, temperature: float) -> ResumeAnalyzer:
    return ResumeAnalyzer(build_llm(model, api_key, temperature), load_system_prompt())


def render_results(result: AnalysisResult, role: str, warnings: list[str], resume_for_ai: str, redactions: int) -> None:
    for warning in warnings:
        st.warning(f"⚠️ {warning}")

    tab1, tab2, tab3 = st.tabs(["📊 Analysis Report", "❓ 20 Interview Questions", "📄 Resume Preview"])

    with tab1:
        st.subheader("ATS Scoring & Skill Gaps")
        col1, col2 = st.columns([1, 3])
        col1.metric("ATS Match Score", f"{result.ats_score}%")
        col2.progress(result.ats_score)
        col2.write(result.score_summary)

        if result.matched_skills:
            st.markdown("**✅ Matched skills:** " + ", ".join(result.matched_skills))

        st.markdown("#### 🧩 Top 5 Missing Skills")
        st.markdown("\n".join(
            f"{i}. **{gap.skill}**: {gap.why_it_matters}"
            for i, gap in enumerate(result.missing_skills, start=1)
        ))

        if result.improvement_tips:
            st.markdown("#### 🚀 How to Close the Gaps")
            st.markdown("\n".join(f"- {tip}" for tip in result.improvement_tips))

        safe_role = re.sub(r"[^A-Za-z0-9]+", "_", role).strip("_") or "Report"
        st.download_button(
            label="📥 Download Full Report",
            data=to_markdown(result, role),
            file_name=f"Analysis_{safe_role}.md",
            mime="text/markdown",
        )

    with tab2:
        st.subheader("Tailored Interview Preparation")
        st.success("These questions are generated based on your specific gaps and experience.")
        number = 1
        for title, questions in question_sections(result):
            st.markdown(f"#### {title}")
            st.markdown("\n".join(f"{number + i}. {q}" for i, q in enumerate(questions)))
            number += len(questions)

    with tab3:
        st.subheader("Parsed Text Content")
        st.caption(
            f"🔒 Emails and phone numbers are removed before the text is sent to the AI "
            f"({redactions} removed)."
        )
        st.text_area("What the AI sees:", resume_for_ai, height=500, disabled=True)


with st.sidebar:
    st.title("⚙️ Control Panel")
    st.subheader("Target Settings")

    selected_role = st.selectbox("🎯 Target Job Role", options=[PLACEHOLDER_ROLE, *JOB_ROLES])

    if selected_role != PLACEHOLDER_ROLE:
        job_description = JOB_ROLES[selected_role]
        st.info(f"Targeting: **{selected_role}**")
    else:
        job_description = st.text_area("Or paste a custom Job Description here:")

    uploaded_resume = st.file_uploader("📤 Upload Resume (PDF)", type="pdf")

    st.markdown("---")
    analyze_clicked = st.button("🔍 Run Full Analysis")

st.title("💼 Recruit-Agent Pro: Intelligence Dashboard")

if not settings.groq_api_key:
    st.error(
        "GROQ_API_KEY is not set. Create a key at https://console.groq.com/keys, "
        "then put `GROQ_API_KEY=your_key` in a `.env` file next to app.py "
        "(or in Streamlit Cloud: App settings → Secrets)."
    )
    st.stop()

if not uploaded_resume:
    st.warning("👈 Use the sidebar on the left to select a role and upload your resume.")
    st.stop()

# --- Input guardrails: file, PDF and resume text ---
pdf_bytes = uploaded_resume.getvalue()
try:
    check_file_size(len(pdf_bytes), settings.max_pdf_mb)
    resume = check_resume_text(
        extract_text_from_pdf(pdf_bytes, max_pages=settings.max_pdf_pages),
        min_chars=settings.min_resume_chars,
        max_chars=settings.max_resume_chars,
    )
except GuardrailError as exc:
    st.error(f"🚫 {exc}")
    st.stop()

resume_for_ai, redactions = redact_pii(resume.text)
role_label = selected_role if selected_role != PLACEHOLDER_ROLE else CUSTOM_ROLE_LABEL
run_key = hashlib.sha256(
    pdf_bytes + role_label.encode() + (job_description or "").encode()
).hexdigest()

if analyze_clicked:
    try:
        jd = check_job_description(
            job_description, min_chars=settings.min_jd_chars, max_chars=settings.max_jd_chars
        )
    except GuardrailError as exc:
        st.error(f"🚫 {exc}")
        st.stop()

    with st.spinner("🤖 AI is deep-scanning your resume..."):
        try:
            analyzer = get_analyzer(settings.groq_model, settings.groq_api_key, settings.temperature)
            result = analyzer.analyze(role_label, jd.text, resume_for_ai)
        except GuardrailError as exc:
            st.error(f"🚫 {exc}")
            st.stop()
        except Exception as exc:  # network, auth or rate-limit errors from Groq
            st.error(f"An error occurred while contacting the AI service: {exc}")
            st.stop()

    # Keep the result so it survives reruns (e.g. clicking the download button).
    st.session_state["analysis"] = {
        "key": run_key,
        "result": result,
        "warnings": resume.warnings + jd.warnings,
    }

saved = st.session_state.get("analysis")
if saved and saved["key"] == run_key:
    render_results(saved["result"], role_label, saved["warnings"], resume_for_ai, redactions)
else:
    st.write("### Ready to Analyze")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Target Role:** {role_label}")
        st.write(f"**File:** {uploaded_resume.name}")
        if redactions:
            st.write(f"🔒 {redactions} email/phone number(s) will be hidden from the AI.")
    with col2:
        st.info("Click the 'Run Full Analysis' button in the sidebar to begin.")

    for warning in resume.warnings:
        st.warning(f"⚠️ {warning}")

    with st.expander("👀 View Extracted Resume Text"):
        st.text(resume_for_ai[:1000] + ("..." if len(resume_for_ai) > 1000 else ""))
