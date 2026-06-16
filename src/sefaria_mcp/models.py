from pydantic import BaseModel, Field


class LinkCandidate(BaseModel):
    id: int
    ref: str
    category: str = ""
    link_type: str = ""
    source_ref: str | None = None
    source_he_ref: str | None = None
    display_name_en: str | None = None
    display_name_he: str | None = None
    has_english: bool = False
    snippet_en: str | None = None
    snippet_he: str | None = None


class LookupContext(BaseModel):
    current_ref: str
    text_en: str | None = None
    text_he: str | None = None
    candidates: list[LinkCandidate] = Field(default_factory=list)


class SamplingChoice(BaseModel):
    candidate_id: int
    rationale: str


class SamplingChoiceResult(BaseModel):
    choices: list[SamplingChoice] = Field(default_factory=list)
    guardrail_note: str | None = None


class SuggestedSource(BaseModel):
    candidate_id: int
    ref: str
    display_title: str
    category: str
    rationale: str


class SuggestedSourcesResult(BaseModel):
    current_ref: str
    question: str | None = None
    guardrail_note: str | None = None
    suggestions: list[SuggestedSource] = Field(default_factory=list)
    fallback_used: bool = False
    errors: list[str] = Field(default_factory=list)
