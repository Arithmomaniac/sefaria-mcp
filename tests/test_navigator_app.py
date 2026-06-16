from sefaria_mcp.apps.navigator import _render_app


def test_render_app_contains_payload_state_and_suggestion_action():
    app = _render_app(
        {
            "current_ref": "Genesis 1:1",
            "text_en": "In the beginning...",
            "text_he": "בראשית...",
            "suggestions": [
                {
                    "candidate_id": 0,
                    "ref": "Rashi on Genesis 1:1:1",
                    "display_title": "Rashi",
                    "category": "Commentary",
                    "rationale": "Start with Rashi.",
                }
            ],
        }
    )

    payload = app.to_json()

    assert payload["state"]["payload"]["current_ref"] == "Genesis 1:1"
    assert payload["state"]["payload"]["suggestions"][0]["display_title"] == "Rashi"
    assert "Rashi on Genesis 1:1:1" in str(payload)
    assert "toolCall" in str(payload)
