# MCP Client

A Python-based client that connects generic LLMs (Ollama, OpenRouter, OpenAI) to [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers.

This tool allows you to chat with an LLM that is augmented with tools provided by an MCP server.

## Features

- **Generic LLM Support**: Connect to Ollama, OpenRouter, or OpenAI.
- **MCP Tool Integration**: Automatically discovers and uses tools exposed by MCP servers.
- **Interactive CLI**: Rich text chat interface with markdown support.
- **Configurable**: Use environment variables, CLI flags, or a TOML config file.

## Installation

Requires Python 3.10 or higher.

1.  Clone the repository:

    ```bash
    git clone https://github.com/fluxkraken/mcp-client.git
    cd mcp-client
    ```

2.  Install dependencies:
    ```bash
    pip install -e .
    ```

## Usage

### quick Start (Ollama + Local MCP Server)

Assuming you have an MCP server running at `http://localhost:8000/sse` and Ollama running locally:

```bash
mcp-client --provider ollama --model llama3 --mcp-url http://localhost:8000/sse
```

### Configuration File (Recommended)

You can define your settings in a `config.toml` file to avoid typing flags every time.

Create `mcp_config.toml`:

```toml
[llm_provider]
provider = "openrouter"
model = "anthropic/claude-3.5-sonnet"
api_key = "sk-or-v1-..."  # Or set OPENROUTER_API_KEY env var

[mcp_server]
url = "http://localhost:8000/sse"
```

Run with the config:

```bash
mcp-client --config mcp_config.toml
```

### CLI Options

| Flag             | Description                                     | Default         |
| ---------------- | ----------------------------------------------- | --------------- |
| `--config`, `-c` | Path to TOML config file                        | None            |
| `--provider`     | LLM Provider (`openai`, `openrouter`, `ollama`) | `openai`        |
| `--model`        | Model name (e.g., `gpt-4`, `llama3`)            | `gpt-3.5-turbo` |
| `--mcp-url`      | URL of the MCP Server (SSE endpoint)            | Required        |
| `--api-key`      | API Key (overrides env var `LLM_API_KEY`)       | None            |

### Environment Variables

- `OPENAI_API_KEY`: For OpenAI provider.
- `OPENROUTER_API_KEY`: For OpenRouter provider.
- `OLLAMA_URL`: Base URL for Ollama (default: `http://localhost:11434`)
