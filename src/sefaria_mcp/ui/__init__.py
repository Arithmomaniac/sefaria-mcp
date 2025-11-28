"""MCP-UI integration module for Sefaria MCP Server.

This module provides rich interactive UI resources for MCP clients that support MCP-UI.
These UI resources complement the standard text/JSON responses, enabling visual 
rendering of Jewish texts, search panels, and other interactive components.

Extension Points:
- Add new UI components in the `components` subpackage
- Add resource factory functions in `resources.py`
- Register new UI-enabled tools by following the `get_text` pattern in tools.py

For more information on MCP-UI:
- https://mcpui.dev/
- https://github.com/MCP-UI-Org/mcp-ui
"""

from .resources import create_text_viewer_resource

__all__ = ["create_text_viewer_resource"]
