import json

import pytest

from recruit_agent.guardrails import GuardrailError, parse_model_output


def test_valid_reply_is_parsed(valid_analysis):
    result = parse_model_output(json.dumps(valid_analysis))
    assert result.ats_score == 62
    assert len(result.missing_skills) == 5
    assert len(result.interview_questions.scenario_based) == 10


def test_reply_wrapped_in_markdown_fence_is_parsed(valid_analysis):
    raw = "Here you go:\n```json\n" + json.dumps(valid_analysis) + "\n```"
    assert parse_model_output(raw).ats_score == 62


def test_extra_keys_are_ignored(valid_analysis):
    valid_analysis["unexpected"] = "value"
    assert parse_model_output(json.dumps(valid_analysis)).ats_score == 62


@pytest.mark.parametrize("raw", ["", "   ", "I cannot help with that.", "{not json}"])
def test_empty_or_non_json_reply_is_rejected(raw):
    with pytest.raises(GuardrailError):
        parse_model_output(raw)


@pytest.mark.parametrize("score", [-1, 101, 150])
def test_score_out_of_range_is_rejected(valid_analysis, score):
    valid_analysis["ats_score"] = score
    with pytest.raises(GuardrailError, match="ats_score"):
        parse_model_output(json.dumps(valid_analysis))


def test_wrong_number_of_missing_skills_is_rejected(valid_analysis):
    valid_analysis["missing_skills"] = valid_analysis["missing_skills"][:4]
    with pytest.raises(GuardrailError, match="missing_skills"):
        parse_model_output(json.dumps(valid_analysis))


def test_wrong_number_of_scenario_questions_is_rejected(valid_analysis):
    valid_analysis["interview_questions"]["scenario_based"].pop()
    with pytest.raises(GuardrailError, match="scenario_based"):
        parse_model_output(json.dumps(valid_analysis))


def test_blank_question_is_rejected(valid_analysis):
    valid_analysis["interview_questions"]["behavioral"][0] = "   "
    with pytest.raises(GuardrailError, match="behavioral"):
        parse_model_output(json.dumps(valid_analysis))


def test_missing_required_key_is_rejected(valid_analysis):
    del valid_analysis["interview_questions"]
    with pytest.raises(GuardrailError, match="interview_questions"):
        parse_model_output(json.dumps(valid_analysis))
