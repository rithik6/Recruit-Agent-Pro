# Recruit-Agent Pro: High-Performance AI Career Intelligence Pipeline

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg.svg)](https://recruit-agent-pro-sqdtiqm9wodfubdpngzokh.streamlit.app/)

> **Live Production URL:** [https://recruit-agent-pro-sqdtiqm9wodfubdpngzokh.streamlit.app/](https://recruit-agent-pro-sqdtiqm9wodfubdpngzokh.streamlit.app/)

Recruit-Agent Pro is a semantic-aware career intelligence platform designed to bridge the structural gap between unstructured student professional narratives and dynamic industry job role taxonomies. Moving beyond the limitations of legacy keyword-based Applicant Tracking Systems (ATS), this platform leverages state-of-the-art Large Language Models (LLMs) and specialized hardware acceleration to provide real-time, sub-second diagnostic evaluation and synthetic interview preparation materials for early-career professionals.

---

## 🚀 Key Features

* **Semantic Competency Alignment:** Utilizes high-dimensional latent space understanding via Llama 3.1 to score resumes based on core competencies rather than fragile keyword matching.
* **Sub-Second Core Inference:** Achieves speeds of over 1,300 tokens per second by offloading cognitive reasoning tasks to Groq's Language Processing Unit (LPU) architecture.
* **Granular Skill-Gap Diagnostics:** Evaluates candidates against specific job role requirements to pinpoint the top 5 missing technical or conceptual skills.
* **Personalized Synthetic Interview Kit:** Generates a structured 20-question repository tailored directly to the candidate's discovered skill gaps, categorized into:
  * 5 Behavioral Questions
  * 5 Technical Fundamentals
  * 10 Scenario-Based Advanced Questions

---

## 🛠️ Tech Stack & Architecture

* **Core Engine:** Meta AI's `Llama 3.1 (8B-Instant)`
* **Hardware Acceleration:** Groq LPU (Language Processing Unit) Cloud Infrastructure
* **Orchestration Layer:** LangChain (Prompt Engineering & Zero-Shot Inference Chains)
* **Document Processing:** PyMuPDF (Coordinate-aware structural PDF text extraction)
* **User Interface:** Streamlit Dashboard

---

## 📂 Project Structure

```text
Recruit-Agent-Pro/
│
├── app.py                # Main Streamlit application and UI logic
├── main.py               # Core processing routines and inference orchestration
├── requirements.txt      # Production dependencies and library constraints
├── .gitignore            # Git exclusion rules (safeguarding virtual environments and API keys)
└── README.md             # System documentation