# MCP Server for BCP Calculator

This guide explains how to use the BCP Calculator as a Model Completion Provider (MCP) server.

## Prerequisites

Before using the MCP server, make sure you have:

1. Installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your API keys for the providers you want to use (OpenAI and/or Anthropic).

## Starting the MCP Server (stdio)

You can start the MCP server locally using stdio transport:

```bash
python run_mcp_server.py
```

This mode is useful for desktop clients that spawn the server process.

## Starting the MCP Server (Streamable HTTP)

To run the MCP server as a standalone HTTP service (remote-friendly):

```bash
python run_mcp_http_server.py --host 0.0.0.0 --port 51617
```

Notes:
- Allowed origins default to "*". You can override with `--allowed-origins` or `MCP_ALLOWED_ORIGINS`.
- The server uses the same provider API keys as the CLI.

## MCP Client Examples

### Stdio Client Configuration

Configure MCP clients (e.g., continue.dev) to call the BCP tool via stdio:

```json
    "bcp": {
        "command": "~/cit/flow/github/flow-ciandt/bcp-agent/venv/bin/python",
        "args": [
            "~/cit/flow/github/flow-ciandt/bcp-agent/run_mcp_server.py"
        ],
        "env": {
            "OPENAI_API_KEY": "${OPENAI_API_KEY}"
        },
        "type": "stdio"
    }
```

### HTTP Client Usage

For HTTP clients, point them to the MCP HTTP server URL. Specific configuration varies by client; consult your MCP client documentation. A common approach is using the MCP Inspector to connect to `http://localhost:51617`.
