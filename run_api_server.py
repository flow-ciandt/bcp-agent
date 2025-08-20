#!/usr/bin/env python3
"""
BCP Calculator API Server

This script starts the FastAPI server for the BCP Calculator API.
"""

import uvicorn
from dotenv import load_dotenv
import os
import argparse


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Start the BCP Calculator API server."
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development mode)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Override with environment variables if available
    host = os.environ.get("API_HOST", args.host)
    port = int(os.environ.get("API_PORT", args.port))
    reload = args.reload
    
    print(f"Starting BCP Calculator API server on {host}:{port}")
    uvicorn.run(
        "src.api.server:app", 
        host=host, 
        port=port, 
        reload=reload
    )