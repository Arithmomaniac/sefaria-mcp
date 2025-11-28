# Sefaria MCP Server

A modern [MCP (Model Context Protocol)](https://github.com/ai21labs/model-context-protocol) server for accessing the Jewish library via the Sefaria API.

## What does this server do?

This server exposes the Sefaria Jewish library as a set of 15 MCP tools, allowing LLMs and other MCP clients to:

**Primary Tools:**
- **get_text** - Retrieve Jewish texts by reference (e.g., "Genesis 1:1")
- **text_search** - Search across the entire Jewish library
- **get_current_calendar** - Get situational Jewish calendar information
- **english_semantic_search** - Semantic similarity search on English text embeddings (Currently only works from official Sefaria MCP)

**Core Tools:**
- **get_links_between_texts** - Find cross-references and connections between texts
- **search_in_book** - Search within a specific book or text work
- **search_in_dictionaries** - Search Jewish reference dictionaries

**Support Tools:**
- **get_english_translations** - Retrieve all available English translations for a text
- **get_topic_details** - Retrieve detailed information about topics in Jewish thought
- **clarify_name_argument** - Autocomplete and validate text names, book titles, and topics
- **clarify_search_path_filter** - Convert book names to proper search filter paths

**Structure Tools:**
- **get_text_or_category_shape** - Explore the hierarchical structure of texts and categories
- **get_text_catalogue_info** - Get bibliographic and structural information (index) for a work

**Manuscript Tools:**
- **get_available_manuscripts** - Access historical manuscript metadata and image URLs
- **get_manuscript_image** - Download and process specific manuscript images

All endpoints are optimized for LLM consumption (compact, relevant, and structured responses).

## What is MCP?

MCP (Model Context Protocol) is an open protocol for connecting Large Language Models (LLMs) to external tools, APIs, and knowledge sources. It enables LLMs to retrieve, reference, and interact with structured data and external services in a standardized way. Learn more in the [MCP documentation](https://modelcontextprotocol.io/).

## How to Run

### Prerequisites
- Python 3.10+
- Docker (optional, for containerized deployment)

### Local Development

1. **Install dependencies:**
    ```bash
    pip install -e .
    ```
2. **Run the server:**
    ```bash
    python -m sefaria_mcp.main
    ```
    The server will be available at `http://127.0.0.1:8088/sse` by default.

### Docker

1. **Build the image:**
    ```bash
    docker build -t sefaria-mcp .
    ```
2. **Run the container:**
    ```bash
    docker run -d --name sefaria-mcp -p 8089:8088 sefaria-mcp
    ```
    The server will be available at `http://localhost:8089/sse`.

### Usage
- Connect your MCP-compatible client to the `/sse` endpoint.
- All tool endpoints are available via the MCP protocol.

## Commit Hygiene

This repo uses semantic commits with the `fix`, `feat`, and `chore` keywords.

## MCP-UI Support

This server includes [MCP-UI](https://mcpui.dev/) support for rich interactive UI resources. When using an MCP-UI compatible client (such as [ui-inspector](https://github.com/MCP-UI-Org/mcp-ui) or [LibreChat](https://www.librechat.ai/)), certain tools will return visually rich interactive components alongside the standard JSON responses.

### Supported UI Resources

- **Text Viewer** (`get_text`): Displays Hebrew/English text in a beautiful bilingual panel with:
  - Side-by-side Hebrew and English columns
  - Action buttons for showing connections, commentaries, and copying references
  - Responsive design that adapts to different screen sizes

### How It Works

Tools that support MCP-UI return multiple content items:
1. A standard text/JSON response (for all MCP clients)
2. An MCP-UI resource with rich HTML content (for MCP-UI compatible clients)

This ensures backward compatibility with all MCP clients while providing enhanced experiences for UI-capable clients.

### Previewing UI Resources

To preview UI resources, you can use:
- **ui-inspector**: The official MCP-UI development tool from [MCP-UI-Org](https://github.com/MCP-UI-Org/mcp-ui)
- **LibreChat**: An open-source AI chat platform with MCP-UI support

### Extending UI Resources

The UI module is designed for extensibility. To add new UI components:

1. Create a component template in `src/sefaria_mcp/ui/components/`
2. Add a resource factory function in `src/sefaria_mcp/ui/resources.py`
3. Update the relevant tool to include the new UI resource

See the `text_viewer.py` component for a documented example.

## Acknowledgments

Special thanks to [@Sivan22](https://github.com/Sivan22) for pioneering the first Sefaria MCP server ([mcp-sefaria-server](https://github.com/Sivan22/mcp-sefaria-server)), which inspired this project and the broader effort to make Jewish texts accessible to LLMs and modern AI tools.

## License
MIT
