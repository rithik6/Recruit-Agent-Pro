"""Setup check: is GROQ_API_KEY set, and does the configured model answer?

Run:  python check.py
"""

import sys

from recruit_agent.analyzer import build_llm
from recruit_agent.config import load_settings


def main() -> int:
    settings = load_settings()
    if not settings.groq_api_key:
        print("❌ GROQ_API_KEY is not set. Copy .env.example to .env and add your key.")
        return 1
    print(f"✅ Found GROQ_API_KEY (starts with {settings.groq_api_key[:5]}...).")

    llm = build_llm(settings.groq_model, settings.groq_api_key, settings.temperature)
    try:
        reply = llm.invoke('Reply with exactly this JSON: {"status": "ok"}').content
    except Exception as exc:
        print(f"❌ Call to model '{settings.groq_model}' failed: {exc}")
        return 1

    print(f"✅ Model '{settings.groq_model}' answered: {reply.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
