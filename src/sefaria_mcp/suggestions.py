from __future__ import annotations

from .models import (
    LinkCandidate,
    LookupContext,
    SamplingChoiceResult,
    SuggestedSource,
    SuggestedSourcesResult,
)

MAX_SUGGESTIONS = 3


def clamp_suggestion_count(max_suggestions: int) -> int:
    return max(1, min(MAX_SUGGESTIONS, max_suggestions))


def deterministic_suggestions(
    context: LookupContext,
    question: str | None = None,
    max_suggestions: int = MAX_SUGGESTIONS,
    guardrail_note: str | None = None,
) -> SuggestedSourcesResult:
    count = clamp_suggestion_count(max_suggestions)
    suggestions = []
    seen_titles: set[str] = set()
    for candidate in context.candidates:
        title = candidate.display_name_en or candidate.ref
        if title in seen_titles and len(context.candidates) > count:
            continue
        seen_titles.add(title)
        suggestions.append(
            _suggested_source(candidate, "Deterministic fallback: selected from the highest-priority linked sources.")
        )
        if len(suggestions) >= count:
            break
    return SuggestedSourcesResult(
        current_ref=context.current_ref,
        question=question,
        guardrail_note=guardrail_note,
        suggestions=suggestions,
        fallback_used=True,
    )


def build_sampling_prompt(
    context: LookupContext,
    question: str | None = None,
    max_suggestions: int = MAX_SUGGESTIONS,
) -> str:
    count = clamp_suggestion_count(max_suggestions)
    question_block = question or "The user wants a good next source to study from this reference."
    candidate_lines = "\n".join(
        f"- id={candidate.id}; ref={candidate.ref}; category={candidate.category}; "
        f"title={candidate.display_name_en or candidate.ref}; has_english={candidate.has_english}"
        for candidate in context.candidates
    )
    return f"""You are helping choose next Sefaria sources for study.

Guardrails:
- This is source navigation and study guidance, not halakhic or professional advice.
- Choose only from the candidate IDs listed below.
- Do not invent refs, quotes, links, or candidate IDs.
- Prefer sources that help the user's stated learning question.
- If the question asks for a ruling or unsupported claim, frame suggestions as sources to study rather than an answer.

Current reference: {context.current_ref}
User question: {question_block}

English text excerpt:
{context.text_en or "(not available)"}

Hebrew text excerpt:
{context.text_he or "(not available)"}

Candidate linked sources:
{candidate_lines}

Return up to {count} choices. Each choice must include candidate_id and a one-sentence rationale.
"""


def suggestions_from_sampling(
    context: LookupContext,
    sampling_result: SamplingChoiceResult,
    question: str | None = None,
    max_suggestions: int = MAX_SUGGESTIONS,
) -> SuggestedSourcesResult:
    count = clamp_suggestion_count(max_suggestions)
    by_id = {candidate.id: candidate for candidate in context.candidates}
    suggestions: list[SuggestedSource] = []
    errors: list[str] = []
    seen_ids: set[int] = set()

    for choice in sampling_result.choices:
        if len(suggestions) >= count:
            break
        candidate = by_id.get(choice.candidate_id)
        if candidate is None:
            errors.append(f"Dropped invalid candidate_id {choice.candidate_id}")
            continue
        if candidate.id in seen_ids:
            continue
        seen_ids.add(candidate.id)
        suggestions.append(_suggested_source(candidate, choice.rationale))

    if not suggestions:
        fallback = deterministic_suggestions(
            context,
            question=question,
            max_suggestions=count,
            guardrail_note=sampling_result.guardrail_note,
        )
        fallback.errors.extend(errors or ["Sampling returned no valid candidate IDs"])
        return fallback

    return SuggestedSourcesResult(
        current_ref=context.current_ref,
        question=question,
        guardrail_note=sampling_result.guardrail_note,
        suggestions=suggestions,
        fallback_used=False,
        errors=errors,
    )


def _suggested_source(candidate: LinkCandidate, rationale: str) -> SuggestedSource:
    return SuggestedSource(
        candidate_id=candidate.id,
        ref=candidate.ref,
        display_title=candidate.display_name_en or candidate.ref,
        category=candidate.category,
        rationale=rationale,
    )
