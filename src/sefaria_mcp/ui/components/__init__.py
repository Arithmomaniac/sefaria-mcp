"""MCP-UI component templates for Sefaria.

This subpackage contains the HTML/JS templates for various UI components 
that can be rendered by MCP-UI compatible clients.

Components:
- text_viewer: Bilingual Hebrew/English text viewer with interactive actions

To add a new component:
1. Create a new module (e.g., `my_component.py`)
2. Define a function that returns the HTML template as a string
3. Export the function from this __init__.py
4. Create a corresponding resource factory in `../resources.py`
"""

from .text_viewer import get_text_viewer_html

__all__ = ["get_text_viewer_html"]
