"""Text Viewer component for bilingual Hebrew/English text display.

This component renders Sefaria text responses in a visually rich panel with:
- Title/reference display
- Bilingual (Hebrew/English) columns or panels
- Interactive action buttons (Show connections, Show commentaries, Copy reference)

The component emits MCP-UI events when users interact with the buttons,
allowing the MCP client to handle actions appropriately.

Example Usage:
    from sefaria_mcp.ui.components import get_text_viewer_html
    
    html = get_text_viewer_html(
        reference="Genesis 1:1",
        hebrew_text="בְּרֵאשִׁית בָּרָא אֱלֹהִים...",
        english_text="In the beginning God created...",
        version_title="The Koren Jerusalem Bible"
    )

Extension Points:
- Add new action buttons by modifying the action_buttons section
- Customize styling by modifying the CSS in the template
- Add new event types by extending the sendIntent function
"""

from typing import Optional, List
import html as html_escape


def _escape(text: str) -> str:
    """Safely escape HTML content."""
    if text is None:
        return ""
    return html_escape.escape(str(text))


def _format_text_content(text) -> str:
    """Format text content for display, handling both strings and lists."""
    if text is None:
        return ""
    if isinstance(text, list):
        # Handle nested lists (e.g., for multi-verse content)
        formatted_parts = []
        for item in text:
            if isinstance(item, list):
                formatted_parts.append(_format_text_content(item))
            elif item:
                formatted_parts.append(_escape(str(item)))
        return "<br>".join(formatted_parts)
    return _escape(str(text))


def get_text_viewer_html(
    reference: str,
    hebrew_text: Optional[str] = None,
    english_text: Optional[str] = None,
    version_title: Optional[str] = None,
    available_versions: Optional[List[dict]] = None,
) -> str:
    """Generate the HTML template for the text viewer component.
    
    Args:
        reference: The Sefaria reference (e.g., "Genesis 1:1")
        hebrew_text: The Hebrew source text (can be string or list)
        english_text: The English translation (can be string or list)
        version_title: The title of the translation version
        available_versions: List of available version metadata
    
    Returns:
        HTML string for the text viewer component
    
    Events Emitted (via postMessage):
        - show_connections: Request to show connections/links for the reference
        - show_commentaries: Request to show commentaries for the reference
        - copy_reference: Request to copy the reference to clipboard
    """
    # Format the text content
    hebrew_html = _format_text_content(hebrew_text) if hebrew_text else "<em>No Hebrew text available</em>"
    english_html = _format_text_content(english_text) if english_text else "<em>No English text available</em>"
    
    # Build version info display
    version_display = ""
    if version_title:
        version_display = f'<span class="version-info">Translation: {_escape(version_title)}</span>'
    
    # Escape the reference for use in JavaScript
    safe_reference = _escape(reference).replace("'", "\\'")
    
    return f'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sefaria Text Viewer - {_escape(reference)}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 16px;
            background: #fafafa;
            color: #333;
            line-height: 1.6;
        }}
        
        .text-viewer {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
            color: white;
            padding: 16px 20px;
        }}
        
        .reference {{
            font-size: 1.5em;
            font-weight: 600;
            margin: 0 0 4px 0;
        }}
        
        .version-info {{
            font-size: 0.85em;
            opacity: 0.85;
        }}
        
        .text-container {{
            display: flex;
            flex-wrap: wrap;
        }}
        
        .text-column {{
            flex: 1;
            min-width: 280px;
            padding: 20px;
        }}
        
        .hebrew-column {{
            direction: rtl;
            text-align: right;
            border-left: 1px solid #e2e8f0;
            background: #f8fafc;
        }}
        
        .english-column {{
            direction: ltr;
            text-align: left;
        }}
        
        .column-label {{
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #718096;
            margin-bottom: 12px;
            font-weight: 600;
        }}
        
        .text-content {{
            font-size: 1.1em;
            line-height: 1.8;
        }}
        
        .hebrew-column .text-content {{
            font-family: "SBL Hebrew", "Ezra SIL", "Frank Ruehl CLM", "Taamey Frank CLM", serif;
            font-size: 1.25em;
        }}
        
        .actions {{
            border-top: 1px solid #e2e8f0;
            padding: 12px 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            background: #f7fafc;
        }}
        
        .action-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border: 1px solid #cbd5e0;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            color: #4a5568;
            transition: all 0.2s ease;
        }}
        
        .action-btn:hover {{
            background: #edf2f7;
            border-color: #a0aec0;
            color: #2d3748;
        }}
        
        .action-btn:active {{
            transform: translateY(1px);
        }}
        
        .action-btn svg {{
            width: 16px;
            height: 16px;
        }}
        
        .status-message {{
            padding: 8px 16px;
            margin: 10px 20px;
            background: #e6fffa;
            border: 1px solid #81e6d9;
            border-radius: 4px;
            color: #234e52;
            font-size: 0.9em;
            display: none;
        }}
        
        .status-message.visible {{
            display: block;
        }}
        
        @media (max-width: 600px) {{
            .text-container {{
                flex-direction: column;
            }}
            
            .hebrew-column {{
                border-left: none;
                border-bottom: 1px solid #e2e8f0;
            }}
        }}
    </style>
</head>
<body>
    <div class="text-viewer">
        <div class="header">
            <h1 class="reference">{_escape(reference)}</h1>
            {version_display}
        </div>
        
        <div class="text-container">
            <div class="text-column english-column">
                <div class="column-label">English</div>
                <div class="text-content">{english_html}</div>
            </div>
            <div class="text-column hebrew-column">
                <div class="column-label">עברית</div>
                <div class="text-content">{hebrew_html}</div>
            </div>
        </div>
        
        <div id="status" class="status-message"></div>
        
        <div class="actions">
            <button class="action-btn" onclick="sendIntent('show_connections')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                </svg>
                Show Connections
            </button>
            <button class="action-btn" onclick="sendIntent('show_commentaries')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                Show Commentaries
            </button>
            <button class="action-btn" onclick="copyReference()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                Copy Reference
            </button>
        </div>
    </div>
    
    <script>
        const reference = '{safe_reference}';
        
        function showStatus(message) {{
            const status = document.getElementById('status');
            status.textContent = message;
            status.classList.add('visible');
            setTimeout(() => status.classList.remove('visible'), 3000);
        }}
        
        function sendIntent(intent, additionalParams = {{}}) {{
            const payload = {{
                intent: intent,
                params: {{
                    reference: reference,
                    ...additionalParams
                }}
            }};
            
            showStatus(`Action: ${{intent}} for ${{reference}}`);
            
            // Send the intent to the parent frame (MCP-UI host)
            if (window.parent && window.parent !== window) {{
                window.parent.postMessage({{
                    type: 'intent',
                    payload: payload
                }}, '*');
            }}
            
            // Also log for debugging
            console.log('MCP-UI Intent:', payload);
        }}
        
        function copyReference() {{
            navigator.clipboard.writeText(reference)
                .then(() => {{
                    showStatus('Reference copied to clipboard!');
                    sendIntent('copy_reference', {{ copied: true }});
                }})
                .catch(err => {{
                    showStatus('Failed to copy reference');
                    console.error('Copy failed:', err);
                }});
        }}
    </script>
</body>
</html>'''
