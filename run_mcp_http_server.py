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

    mcp = build_server(logger)

    # Note: FastMCP supports 'http' transport. CORS and headers are controlled by SDK options.
    # If the SDK exposes explicit parameters for CORS, pass them here.
    # For now, we simply run with http transport and default settings.
    mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
