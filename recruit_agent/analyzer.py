"""Runs the analysis: builds the prompt, calls the AI, validates the answer."""

from __future__ import annotations

from typing import Any, Protocol

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from .guardrails import GuardrailError, parse_model_output
from .prompt_builder import build_user_prompt
from .schemas import AnalysisResult


class ChatModel(Protocol):
    def invoke(self, messages: list[BaseMessage]) -> Any: ...


def build_llm(model: str, api_key: str | None, temperature: float) -> ChatModel:
    # Imported here so the rest of this module (and its tests) load quickly.
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_retries=2,
        # JSON mode: Groq rejects replies that are not a JSON object.
        model_kwargs={"response_format": {"type": "json_object"}},
    )


class ResumeAnalyzer:
    def __init__(self, llm: ChatModel, system_prompt: str, max_attempts: int = 2):
        self.llm = llm
        self.system_prompt = system_prompt
        self.max_attempts = max_attempts

    def analyze(self, role: str, job_description: str, resume_text: str) -> AnalysisResult:
        messages: list[BaseMessage] = [
            SystemMessage(self.system_prompt),
            HumanMessage(build_user_prompt(role, job_description, resume_text)),
        ]
        last_error: GuardrailError | None = None

        for _ in range(self.max_attempts):
            reply = self.llm.invoke(messages)
            raw = reply.content if isinstance(reply.content, str) else str(reply.content)
            try:
                return parse_model_output(raw)
            except GuardrailError as exc:
                last_error = exc
                # Show the AI what was wrong and ask once more.
                messages = messages + [
                    AIMessage(raw),
                    HumanMessage(
                        f"Your reply was rejected: {exc} "
                        "Reply again with only the corrected JSON object."
                    ),
                ]

        raise GuardrailError(
            f"The AI gave an invalid answer {self.max_attempts} times. Please try again."
        ) from last_error
