import json

from sefaria_mcp.logic import _build_link_candidates
from sefaria_mcp.models import LookupContext, SamplingChoice, SamplingChoiceResult
from sefaria_mcp.suggestions import (
    build_sampling_prompt,
    deterministic_suggestions,
    suggestions_from_sampling,
)


def test_build_link_candidates_prioritizes_classic_commentaries():
    links = [
        {"sourceRef": "Abarbanel on Torah, Genesis 1:1", "category": "Commentary", "type": "commentary", "collectiveTitle": {"en": "Abarbanel"}, "sourceHasEn": True},
        {"sourceRef": "Rashi on Genesis 1:1:1", "category": "Commentary", "type": "commentary", "collectiveTitle": {"en": "Rashi"}, "sourceHasEn": True},
        {"sourceRef": "Ramban on Genesis 1:1:1", "category": "Commentary", "type": "commentary", "collectiveTitle": {"en": "Ramban"}, "sourceHasEn": True},
        {"sourceRef": "Berakhot 2a", "category": "Talmud", "type": "quotation", "sourceHasEn": True},
    ]

    candidates = _build_link_candidates(links, max_candidates=3)

    assert [candidate.display_name_en for candidate in candidates] == ["Rashi", "Ramban", "Abarbanel"]
    assert [candidate.id for candidate in candidates] == [0, 1, 2]


def test_deterministic_suggestions_clamps_and_deduplicates_titles():
    context = LookupContext(
        current_ref="Genesis 1:1",
        candidates=_build_link_candidates(
            [
                {"sourceRef": "Rashi on Genesis 1:1:1", "category": "Commentary", "collectiveTitle": {"en": "Rashi"}, "sourceHasEn": True},
                {"sourceRef": "Rashi on Genesis 1:1:2", "category": "Commentary", "collectiveTitle": {"en": "Rashi"}, "sourceHasEn": True},
                {"sourceRef": "Ramban on Genesis 1:1:1", "category": "Commentary", "collectiveTitle": {"en": "Ramban"}, "sourceHasEn": True},
                {"sourceRef": "Ibn Ezra on Genesis 1:1:1", "category": "Commentary", "collectiveTitle": {"en": "Ibn Ezra"}, "sourceHasEn": True},
            ],
            max_candidates=10,
        ),
    )

    result = deterministic_suggestions(context, max_suggestions=99)

    assert len(result.suggestions) == 3
    assert result.fallback_used is True
    assert [suggestion.display_title for suggestion in result.suggestions] == ["Rashi", "Ramban", "Ibn Ezra"]


def test_sampling_validation_drops_invalid_candidate_ids():
    context = LookupContext(
        current_ref="Genesis 1:1",
        candidates=_build_link_candidates(
            [
                {"sourceRef": "Rashi on Genesis 1:1:1", "category": "Commentary", "collectiveTitle": {"en": "Rashi"}, "sourceHasEn": True},
                {"sourceRef": "Ramban on Genesis 1:1:1", "category": "Commentary", "collectiveTitle": {"en": "Ramban"}, "sourceHasEn": True},
            ],
            max_candidates=10,
        ),
    )
    sampling = SamplingChoiceResult(
        choices=[
            SamplingChoice(candidate_id=1, rationale="Deepens the verse."),
            SamplingChoice(candidate_id=42, rationale="Invalid."),
        ],
        guardrail_note="Study guidance only.",
    )

    result = suggestions_from_sampling(context, sampling)

    assert result.fallback_used is False
    assert [suggestion.ref for suggestion in result.suggestions] == ["Ramban on Genesis 1:1:1"]
    assert result.errors == ["Dropped invalid candidate_id 42"]


def test_sampling_prompt_contains_guards_and_candidate_ids():
    context = LookupContext(
        current_ref="Genesis 1:1",
        text_en="In the beginning...",
        candidates=_build_link_candidates(
            [
                {"sourceRef": "Rashi on Genesis 1:1:1", "category": "Commentary", "collectiveTitle": {"en": "Rashi"}, "sourceHasEn": True},
            ],
            max_candidates=10,
        ),
    )

    prompt = build_sampling_prompt(context, question="classic commentaries")

    assert "not halakhic or professional advice" in prompt
    assert "Choose only from the candidate IDs" in prompt
    assert "id=0" in prompt
    assert "Rashi on Genesis 1:1:1" in prompt


def test_sampling_choice_result_json_contract():
    payload = {"choices": [{"candidate_id": 0, "rationale": "Start here."}]}

    result = SamplingChoiceResult.model_validate_json(json.dumps(payload))

    assert result.choices[0].candidate_id == 0
