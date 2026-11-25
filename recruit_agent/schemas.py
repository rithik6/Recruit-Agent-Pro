"""The shape the AI's answer must have. Anything else is rejected."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Sentence = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=600)]


class MissingSkill(BaseModel):
    skill: ShortText
    why_it_matters: Sentence


class InterviewQuestions(BaseModel):
    behavioral: list[Sentence] = Field(min_length=5, max_length=5)
    technical_fundamentals: list[Sentence] = Field(min_length=5, max_length=5)
    scenario_based: list[Sentence] = Field(min_length=10, max_length=10)


class AnalysisResult(BaseModel):
    ats_score: int = Field(ge=0, le=100)
    score_summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1500)]
    matched_skills: list[ShortText] = Field(default_factory=list, max_length=20)
    missing_skills: list[MissingSkill] = Field(min_length=5, max_length=5)
    interview_questions: InterviewQuestions
    improvement_tips: list[Sentence] = Field(default_factory=list, max_length=10)
