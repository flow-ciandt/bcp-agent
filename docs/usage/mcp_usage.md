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

## Starting the MCP Server

You can start the MCP server using the provided script:

```bash
python run_mcp_server.py
```

Once started, you can use a MCP client to interact with the server.

## MCP Client Example

Here is a simple example of how to use a MCP client to send a user story to the MCP server and receive the calculated BCP.

### MCP Client Configuration

You can configure MCP clients like continue.dev or copilot chat to call the bcp calculation tool adding something like this to the MCP configuration file:

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
