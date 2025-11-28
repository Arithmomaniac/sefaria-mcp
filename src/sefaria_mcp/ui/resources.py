"""MCP-UI resource factory functions for Sefaria.

This module provides factory functions for creating MCP-UI resources
from Sefaria API responses. These resources can be included in tool
results alongside standard text/JSON responses.

Usage:
    from sefaria_mcp.ui.resources import create_text_viewer_resource
    
    # Create a UI resource from get_text response
    ui_resource = create_text_viewer_resource(
        reference="Genesis 1:1",
        text_data={"he": "...", "text": "...", ...}
    )

Extension Points:
- Add new resource factory functions for other UI components
- Each factory should return a UIResource from mcp-ui-server
- Follow the pattern: create_<component>_resource(...)

For more on MCP-UI resources:
- https://mcpui.dev/guide/server/python/walkthrough
"""

from typing import Any, Dict, Optional, List

from mcp_ui_server import create_ui_resource, UIMetadataKey
from mcp_ui_server.core import UIResource

from .components import get_text_viewer_html


def create_text_viewer_resource(
    reference: str,
    text_data: Dict[str, Any],
    uri_suffix: Optional[str] = None,
) -> UIResource:
    """Create a MCP-UI resource for displaying Sefaria text content.
    
    This factory function takes the response from Sefaria's text API and
    creates a rich interactive UI resource for MCP-UI compatible clients.
    
    Args:
        reference: The Sefaria reference string (e.g., "Genesis 1:1")
        text_data: The optimized text data dictionary from get_text, containing:
            - versions: List of version objects with text content
            - available_versions: List of available version metadata
            - he: Hebrew text (if present in legacy format)
            - text: English text (if present in legacy format)
        uri_suffix: Optional suffix for the URI (defaults to sanitized reference)
    
    Returns:
        UIResource: A MCP-UI resource ready to be included in tool results
    
    Example:
        >>> resource = create_text_viewer_resource(
        ...     reference="Genesis 1:1",
        ...     text_data={"versions": [...], "he": "...", "text": "..."}
        ... )
        >>> # Include in tool result: [resource.to_dict()]
    
    Events the UI Component Will Emit:
        - show_connections: User wants to see text connections/links
        - show_commentaries: User wants to see commentaries
        - copy_reference: User copied the reference to clipboard
    """
    # Extract text content from the text_data
    hebrew_text = None
    english_text = None
    version_title = None
    
    # Try to get text from versions array (preferred format)
    versions = text_data.get("versions", [])
    for version in versions:
        lang = version.get("languageFamilyName", "").lower()
        text = version.get("text", "")
        
        if lang == "hebrew" and text:
            hebrew_text = text
        elif lang == "english" and text:
            english_text = text
            version_title = version.get("versionTitle")
    
    # Fallback to legacy format (he/text fields)
    if hebrew_text is None:
        hebrew_text = text_data.get("he")
    if english_text is None:
        english_text = text_data.get("text")
    
    # Get available versions for reference
    available_versions = text_data.get("available_versions", [])
    
    # Generate the HTML content
    html_content = get_text_viewer_html(
        reference=reference,
        hebrew_text=hebrew_text,
        english_text=english_text,
        version_title=version_title,
        available_versions=available_versions,
    )
    
    # Create a safe URI suffix from the reference
    safe_suffix = uri_suffix or reference.replace(" ", "-").replace(":", "-")
    
    # Create and return the UI resource
    return create_ui_resource({
        "uri": f"ui://sefaria/text/{safe_suffix}",
        "content": {
            "type": "rawHtml",
            "htmlString": html_content
        },
        "encoding": "text",
        "uiMetadata": {
            UIMetadataKey.PREFERRED_FRAME_SIZE: ["900px", "600px"]
        },
        "metadata": {
            "reference": reference,
            "componentType": "text_viewer"
        }
    })


# Additional resource factory functions can be added here
# Example extension point for future components:
#
# def create_search_results_resource(query: str, results: List[Dict]) -> UIResource:
#     """Create a MCP-UI resource for displaying search results."""
#     ...
#
# def create_knowledge_graph_resource(topic: str, connections: Dict) -> UIResource:
#     """Create a MCP-UI resource for displaying a knowledge graph."""
#     ...
