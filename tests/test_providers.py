#!/usr/bin/env python3
"""
Test script for LLM providers integration.
"""

import os
import logging
import argparse
from dotenv import load_dotenv

from llm_providers import get_provider
from logger import setup_logger

def main():
    """Main entry point for the test script."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Test LLM providers integration."
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "claude"],
        default="openai",
        help="LLM provider to test (default: openai)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    args = parser.parse_args()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    logger = setup_logger(log_level)
    
    try:
        # Get the provider
        provider = get_provider(args.provider, logger)
        
        # Test prompt
        prompt = "Summarize the key features of agile development in 3 bullet points."
        
        # Send the prompt to the LLM
        print(f"Testing {args.provider} provider...")
        response = provider.invoke(prompt)
        
        # Print the response
        print("\nResponse:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        print(f"\n{args.provider} provider test completed successfully.")
        
    except Exception as e:
        logger.error(f"Error testing {args.provider} provider: {str(e)}")
        
if __name__ == "__main__":
    main()