#!/usr/bin/env python3
"""
BCP Calculator - Standalone MCP HTTP Server

Runs the MCP server using Streamable HTTP transport without changing existing API capabilities.
"""

import argparse
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from src.bcp.bcp_calculator import BCPCalculator
from src.bcp.logger import setup_logger


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the BCP MCP HTTP server.")
    parser.add_argument("--host", type=str, default=os.environ.get("MCP_HTTP_HOST", "0.0.0.0"), help="Host to bind the MCP server (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("MCP_HTTP_PORT", "51617")), help="Port to bind the MCP server (default: 51617)")
    parser.add_argument("--allowed-origins", type=str, default=os.environ.get("MCP_ALLOWED_ORIGINS", "*"), help="Comma-separated list of allowed origins for CORS (default: *)")
    return parser.parse_args()


def build_server(logger: logging.Logger) -> FastMCP:
    mcp = FastMCP("bcp-calculator-mcp")

    @mcp.tool()
    async def calculate_bcp(story_content: str, provider: str = "openai") -> dict:
        """Calculate BCP via MCP tool."""
        calculator = BCPCalculator(logger, provider_name=provider)
        result = calculator.calculate_bcp(story_content)
        return {"result": result}

    return mcp


def main() -> None:
    load_dotenv()
    args = parse_arguments()

    logger = setup_logger(logging.INFO)
    logger.info(f"Starting MCP HTTP Server on {args.host}:{args.port}")
    logger.info(f"Allowed origins: {args.allowed_origins}")

    # Configure server bind settings via FastMCP constructor arguments
    mcp = FastMCP(
        "bcp-calculator-mcp",
        host=args.host,
        port=args.port,
        streamable_http_path="/mcp",
    )

    def apply_provider_overrides(
        provider: str | None,
        api_key: str | None = None,
        model_name: str | None = None,
        flow_client_id: str | None = None,
        flow_client_secret: str | None = None,
        flow_base_url: str | None = None,
        flow_tenant: str | None = None,
        flow_agent: str | None = None,
    ) -> None:
        """Apply provider-related overrides by setting environment variables."""
        p = (provider or os.environ.get("BCP_PROVIDER") or "openai").lower()
        if p == "openai":
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
            if model_name:
                os.environ["OPENAI_MODEL_NAME"] = model_name
        elif p == "claude":
            if api_key:
                os.environ["ANTHROPIC_API_KEY"] = api_key
            if model_name:
                os.environ["ANTHROPIC_MODEL_NAME"] = model_name
        elif p in ("flow-openai", "flow"):
            if flow_client_id:
                os.environ["FLOW_CLIENT_ID"] = flow_client_id
            if flow_client_secret:
                os.environ["FLOW_CLIENT_SECRET"] = flow_client_secret
            if flow_base_url:
                os.environ["FLOW_BASE_URL"] = flow_base_url
            if flow_tenant:
                os.environ["FLOW_TENANT"] = flow_tenant
            if flow_agent:
                os.environ["FLOW_AGENT"] = flow_agent
            if model_name:
                os.environ["FLOW_MODEL_NAME"] = model_name
        elif p == "flow-bedrock":
            if flow_client_id:
                os.environ["FLOW_CLIENT_ID"] = flow_client_id
            if flow_client_secret:
                os.environ["FLOW_CLIENT_SECRET"] = flow_client_secret
            if flow_base_url:
                os.environ["FLOW_BASE_URL"] = flow_base_url
            if flow_tenant:
                os.environ["FLOW_TENANT"] = flow_tenant
            if flow_agent:
                os.environ["FLOW_AGENT"] = flow_agent
            if model_name:
                os.environ["FLOW_BEDROCK_MODEL_NAME"] = model_name
        # No else: unsupported provider handled downstream by BCPCalculator

    @mcp.tool()
    async def calculate_bcp(
        story_content: str,
        provider: str | None = None,
        api_key: str | None = None,
        model_name: str | None = None,
        flow_client_id: str | None = None,
        flow_client_secret: str | None = None,
        flow_base_url: str | None = None,
        flow_tenant: str | None = None,
        flow_agent: str | None = None,
    ) -> dict:
        """Calculate BCP via MCP tool.
        - provider: optional. If not provided, defaults to env BCP_PROVIDER or 'openai'.
        - api_key: optional provider API key override (OPENAI_API_KEY or ANTHROPIC_API_KEY).
        - model_name: optional model name override for the selected provider.
        - flow_*: optional Flow overrides if provider is flow-openai or flow-bedrock.
        """
        effective_provider = (provider or os.environ.get("BCP_PROVIDER") or "openai").lower()
        apply_provider_overrides(effective_provider, api_key, model_name, flow_client_id, flow_client_secret, flow_base_url, flow_tenant, flow_agent)
        calculator = BCPCalculator(logger, provider_name=effective_provider)
        result = calculator.calculate_bcp(story_content)
        return {"result": result}

    # Run using streamable HTTP transport
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
