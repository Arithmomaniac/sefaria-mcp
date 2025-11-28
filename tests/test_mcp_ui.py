"""Tests for MCP-UI resource creation in Sefaria MCP Server."""

import json
import pytest
from mcp.types import TextContent
from mcp_ui_server.core import UIResource

from sefaria_mcp.ui import create_text_viewer_resource
from sefaria_mcp.ui.components import get_text_viewer_html


class TestTextViewerComponent:
    """Tests for the text viewer HTML component."""

    def test_get_text_viewer_html_basic(self):
        """Test that get_text_viewer_html returns valid HTML."""
        html = get_text_viewer_html(
            reference="Genesis 1:1",
            hebrew_text="בְּרֵאשִׁית בָּרָא אֱלֹהִים",
            english_text="In the beginning God created",
        )
        
        assert isinstance(html, str)
        assert "<!DOCTYPE html>" in html
        assert "Genesis 1:1" in html
        assert "בְּרֵאשִׁית" in html
        assert "In the beginning" in html

    def test_get_text_viewer_html_escapes_special_chars(self):
        """Test that HTML special characters are escaped."""
        html = get_text_viewer_html(
            reference="Test <script>alert('xss')</script>",
            hebrew_text="<script>bad</script>",
            english_text="<script>bad</script>",
        )
        
        # Script tags should be escaped, not rendered
        assert "<script>" not in html or "&lt;script&gt;" in html
        assert "alert('xss')" not in html or "alert(&#x27;xss&#x27;)" in html or "alert(\\'xss\\')" in html

    def test_get_text_viewer_html_handles_missing_text(self):
        """Test that missing text is handled gracefully."""
        html = get_text_viewer_html(
            reference="Genesis 1:1",
            hebrew_text=None,
            english_text=None,
        )
        
        assert isinstance(html, str)
        assert "Genesis 1:1" in html
        assert "No Hebrew text available" in html
        assert "No English text available" in html

    def test_get_text_viewer_html_handles_list_text(self):
        """Test that list-format text is formatted correctly."""
        html = get_text_viewer_html(
            reference="Genesis 1:1-3",
            hebrew_text=["Verse 1 hebrew", "Verse 2 hebrew"],
            english_text=["Verse 1 english", "Verse 2 english"],
        )
        
        assert "Verse 1 hebrew" in html
        assert "Verse 2 hebrew" in html
        assert "Verse 1 english" in html
        assert "Verse 2 english" in html

    def test_get_text_viewer_html_includes_version_title(self):
        """Test that version title is displayed when provided."""
        html = get_text_viewer_html(
            reference="Genesis 1:1",
            hebrew_text="בראשית",
            english_text="In the beginning",
            version_title="The Koren Jerusalem Bible",
        )
        
        assert "The Koren Jerusalem Bible" in html

    def test_get_text_viewer_html_includes_action_buttons(self):
        """Test that action buttons are present."""
        html = get_text_viewer_html(
            reference="Genesis 1:1",
            hebrew_text="בראשית",
            english_text="In the beginning",
        )
        
        assert "Show Connections" in html
        assert "Show Commentaries" in html
        assert "Copy Reference" in html

    def test_get_text_viewer_html_includes_event_handling(self):
        """Test that JavaScript event handlers are present."""
        html = get_text_viewer_html(
            reference="Genesis 1:1",
            hebrew_text="בראשית",
            english_text="In the beginning",
        )
        
        assert "sendIntent" in html
        assert "postMessage" in html
        assert "show_connections" in html
        assert "show_commentaries" in html


class TestCreateTextViewerResource:
    """Tests for the text viewer resource factory."""

    def test_create_text_viewer_resource_basic(self):
        """Test basic resource creation."""
        text_data = {
            "versions": [
                {"languageFamilyName": "Hebrew", "text": "בראשית", "versionTitle": "Hebrew Source"},
                {"languageFamilyName": "English", "text": "In the beginning", "versionTitle": "JPS 1917"},
            ],
            "ref": "Genesis 1:1",
        }
        
        resource = create_text_viewer_resource(
            reference="Genesis 1:1",
            text_data=text_data,
        )
        
        assert isinstance(resource, UIResource)
        assert resource.type == "resource"
        assert resource.resource is not None

    def test_create_text_viewer_resource_uri_format(self):
        """Test that URI is formatted correctly."""
        text_data = {"versions": [], "ref": "Genesis 1:1"}
        
        resource = create_text_viewer_resource(
            reference="Genesis 1:1",
            text_data=text_data,
        )
        
        uri = str(resource.resource.uri)
        assert uri.startswith("ui://sefaria/text/")
        assert "Genesis" in uri

    def test_create_text_viewer_resource_with_legacy_format(self):
        """Test resource creation with legacy he/text format."""
        text_data = {
            "he": "בראשית ברא אלהים",
            "text": "In the beginning God created",
            "ref": "Genesis 1:1",
        }
        
        resource = create_text_viewer_resource(
            reference="Genesis 1:1",
            text_data=text_data,
        )
        
        assert isinstance(resource, UIResource)
        # Verify content was processed
        html_content = resource.resource.text
        assert "בראשית" in html_content
        assert "In the beginning" in html_content

    def test_create_text_viewer_resource_mime_type(self):
        """Test that MIME type is text/html."""
        text_data = {"versions": [], "ref": "Genesis 1:1"}
        
        resource = create_text_viewer_resource(
            reference="Genesis 1:1",
            text_data=text_data,
        )
        
        assert resource.resource.mimeType == "text/html"

    def test_create_text_viewer_resource_custom_uri_suffix(self):
        """Test custom URI suffix."""
        text_data = {"versions": [], "ref": "Test"}
        
        resource = create_text_viewer_resource(
            reference="Test",
            text_data=text_data,
            uri_suffix="custom-suffix-123",
        )
        
        uri = str(resource.resource.uri)
        assert "custom-suffix-123" in uri


class TestGetTextToolIntegration:
    """Integration tests for the get_text tool with MCP-UI resources."""

    def test_text_data_structure_for_ui_resource(self):
        """Test that typical get_text response structure works for UI resource creation."""
        # Simulate a typical response from the Sefaria API (post-optimization)
        text_data = {
            "ref": "Genesis 1:1",
            "versions": [
                {
                    "text": "In the beginning God created the heaven and the earth.",
                    "versionTitle": "JPS 1917",
                    "languageFamilyName": "English",
                    "versionSource": "https://www.sefaria.org/",
                },
                {
                    "text": "בְּרֵאשִׁ֖ית בָּרָ֣א אֱלֹהִ֑ים אֵ֥ת הַשָּׁמַ֖יִם וְאֵ֥ת הָאָֽרֶץ׃",
                    "versionTitle": "Tanach with Ta'amei Hamikra",
                    "languageFamilyName": "Hebrew",
                    "versionSource": "https://www.sefaria.org/",
                },
            ],
            "available_versions": [
                {"versionTitle": "JPS 1917", "languageFamilyName": "English"},
                {"versionTitle": "Tanach with Ta'amei Hamikra", "languageFamilyName": "Hebrew"},
            ],
        }
        
        resource = create_text_viewer_resource(
            reference="Genesis 1:1",
            text_data=text_data,
        )
        
        assert isinstance(resource, UIResource)
        html_content = resource.resource.text
        
        # Verify both languages are present
        assert "בְּרֵאשִׁ֖ית" in html_content
        assert "In the beginning" in html_content
        assert "JPS 1917" in html_content

    def test_empty_versions_handled_gracefully(self):
        """Test that empty versions list doesn't cause errors."""
        text_data = {
            "ref": "Unknown Reference",
            "versions": [],
        }
        
        resource = create_text_viewer_resource(
            reference="Unknown Reference",
            text_data=text_data,
        )
        
        assert isinstance(resource, UIResource)
        html_content = resource.resource.text
        assert "Unknown Reference" in html_content


class TestMCPUIResourceStructure:
    """Tests verifying the MCP-UI resource structure matches protocol expectations."""

    def test_resource_is_embedded_resource_type(self):
        """Verify resource has correct embedded resource structure."""
        from mcp.types import EmbeddedResource
        
        text_data = {"versions": [], "ref": "Test"}
        resource = create_text_viewer_resource(reference="Test", text_data=text_data)
        
        # UIResource should inherit from EmbeddedResource
        assert isinstance(resource, EmbeddedResource)

    def test_resource_can_be_serialized(self):
        """Verify resource can be serialized to dict/JSON."""
        text_data = {"versions": [], "ref": "Test"}
        resource = create_text_viewer_resource(reference="Test", text_data=text_data)
        
        # Should be serializable
        serialized = resource.model_dump()
        assert isinstance(serialized, dict)
        assert "type" in serialized
        assert "resource" in serialized
        assert serialized["type"] == "resource"

    def test_text_content_structure(self):
        """Verify TextContent has correct structure for mixed responses."""
        content = TextContent(type="text", text='{"ref": "Genesis 1:1"}')
        
        serialized = content.model_dump()
        assert serialized["type"] == "text"
        assert serialized["text"] == '{"ref": "Genesis 1:1"}'
