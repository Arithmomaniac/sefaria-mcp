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
- **suggest_next_sources** - Suggest up to three validated linked sources to study next from a starting reference
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

**MCP App POC:**
- **browse_suggested_sources** - Opens a minimal MCP App UI for a reference, showing the current text and three clickable suggested next sources. The app uses the same server-side lookup pipeline as `suggest_next_sources` and keeps navigation bounded to click-through plus back.

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
    Set `SEFARIA_MCP_PORT` to override the SSE/API port (e.g., `SEFARIA_MCP_PORT=8089 python -m sefaria_mcp.main`).
    Prometheus metrics bind separately on `SEFARIA_MCP_METRICS_PORT` (default `9090`).

### Bounded sampling/UI MVP smoke test

The MVP intentionally keeps sampling and UI bounded:

1. The server fetches the current text and first-hop Sefaria links in code.
2. `suggest_next_sources` makes one guarded sampling request to rank server-provided candidate IDs. If sampling is unavailable, it returns deterministic fallback suggestions.
3. `browse_suggested_sources` renders a small MCP App with the current text and three suggested next sources.

Exercise the server locally:

```bash
python -m sefaria_mcp.main
```

Then connect an MCP client to `http://127.0.0.1:8088/sse` and call:

```text
get_text(reference="Genesis 1:1", version_language="both")
get_links_between_texts(reference="Genesis 1:1", with_text="0")
suggest_next_sources(reference="Genesis 1:1", question="classic commentaries")
browse_suggested_sources(reference="Genesis 1:1")
```

The expected fallback suggestions for `Genesis 1:1` should include classic linked commentaries such as Rashi, Ramban, and Ibn Ezra. Sampling-capable clients may reorder or explain suggestions differently, but returned candidate IDs are validated server-side.

### Docker

1. **Build the image:**
    ```bash
    docker build -t sefaria-mcp .
    ```
2. **Run the container:**
    ```bash
    docker run -d --name sefaria-mcp \
        -e SEFARIA_MCP_PORT=8089 \
        -e SEFARIA_MCP_METRICS_PORT=9090 \
        -p 8089:8089 \
        -p 9090:9090 \
        sefaria-mcp
    ```
    The server will be available at `http://localhost:8089/sse` and metrics at `http://localhost:9090/` (adjust the port mappings as needed).

### Usage
- Connect your MCP-compatible client to the `/sse` endpoint.
- All tool endpoints are available via the MCP protocol.

### Monitoring
- Prometheus metrics are exposed via the standalone HTTP server started on `SEFARIA_MCP_METRICS_PORT` (defaults to `9090`).
- Scrape `http://localhost:9090/` (or your configured host/port). Metrics include:
  - `mcp_tool_calls_total{tool_name,status}` – call counts per tool and status.
  - `mcp_tool_duration_seconds{tool_name}` – histogram of per-call durations.
  - `mcp_tool_payload_bytes{tool_name}` – histogram of response payload sizes.
  - `mcp_errors_total{tool_name,error_type}` – per-tool error counts.
  - `mcp_active_connections` – current SSE connection gauge.
  - Standard FastAPI instrumentation (request rate, latency, status codes, in-progress requests, etc.) from `prometheus_fastapi_instrumentator`.

## Commit Hygiene

This repo uses semantic commits with the `fix`, `feat`, and `chore` keywords.
## Acknowledgments

Special thanks to [@Sivan22](https://github.com/Sivan22) for pioneering the first Sefaria MCP server ([mcp-sefaria-server](https://github.com/Sivan22/mcp-sefaria-server)), which inspired this project and the broader effort to make Jewish texts accessible to LLMs and modern AI tools.

## License
MIT
