from __future__ import annotations

import json

from fastmcp import Context, FastMCP, FastMCPApp
from prefab_ui.actions import CallTool, SetState
from prefab_ui.app import PrefabApp
from prefab_ui.components import Button, Card, CardContent, CardHeader, CardTitle, Column, Heading, Markdown, Row, Text

from ..logic import get_suggestion_lookup_context
from ..models import LookupContext
from ..suggestions import deterministic_suggestions


def register_suggested_sources_app(mcp: FastMCP) -> None:
    app = FastMCPApp("Sefaria Suggested Sources")

    @app.tool()
    async def load_suggested_source(reference: str, ctx: Context) -> dict:
        """Load a Sefaria reference and deterministic next-source suggestions."""
        return await _build_payload(ctx, reference)

    @app.ui()
    async def browse_suggested_sources(reference: str = "Genesis 1:1", ctx: Context | None = None) -> PrefabApp:
        """Open a minimal Sefaria UI showing a ref and three suggested next sources."""
        if ctx is None:
            raise ValueError("Context is required to browse suggested sources.")

        payload = await _build_payload(ctx, reference)
        return _render_app(payload)

    mcp.add_provider(app)


async def _build_payload(ctx: Context, reference: str) -> dict:
    context_json = await get_suggestion_lookup_context(ctx.log, reference, max_candidates=12)
    context = LookupContext.model_validate_json(context_json)
    suggestions = deterministic_suggestions(context)
    return {
        "current_ref": context.current_ref,
        "text_en": context.text_en or "",
        "text_he": context.text_he or "",
        "suggestions": [source.model_dump() for source in suggestions.suggestions],
    }


def _render_app(payload: dict) -> PrefabApp:
    suggestion_cards = []
    for suggestion in payload["suggestions"]:
        ref = suggestion["ref"]
        suggestion_cards.append(
            Card(
                children=[
                    CardHeader(
                        children=[
                            CardTitle(f"{suggestion['display_title']} · {suggestion['category']}")
                        ]
                    ),
                    CardContent(
                        children=[
                            Text(content=ref),
                            Text(content=suggestion["rationale"]),
                            Button(
                                "Open source",
                                onClick=[
                                    SetState("previous_payload", "{{ payload }}"),
                                    CallTool(
                                        "load_suggested_source",
                                        arguments={"reference": ref},
                                        on_success=SetState("payload", "{{ $result }}"),
                                    ),
                                ],
                            ),
                        ]
                    ),
                ]
            )
        )

    return PrefabApp(
        title="Sefaria Suggested Sources",
        state={"payload": payload, "previous_payload": payload},
        view=Column(
            gap=4,
            children=[
                Heading("Sefaria Suggested Sources"),
                Row(
                    children=[
                        Button("Back", onClick=SetState("payload", "{{ previous_payload }}")),
                        Text(content="Current ref: {{ payload.current_ref }}"),
                    ]
                ),
                Card(
                    children=[
                        CardHeader(children=[CardTitle("Current text")]),
                        CardContent(
                            children=[
                                Markdown("**Hebrew**\n\n{{ payload.text_he }}"),
                                Markdown("**English**\n\n{{ payload.text_en }}"),
                            ]
                        ),
                    ]
                ),
                Heading("Suggested next sources", level=2),
                Column(gap=3, children=suggestion_cards),
            ],
        ),
    )
