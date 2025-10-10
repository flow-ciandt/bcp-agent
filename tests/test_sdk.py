"""
BCP Calculator Test Script

This script demonstrates three different ways to use the BCP Calculator:
1. Direct SDK usage
2. CLI usage via subprocess
3. API usage via HTTP requests
"""

import json
import os
import subprocess
import time
from pathlib import Path
import logging

import requests
from bcp.bcp_calculator import BCPCalculator
from bcp.logger import setup_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define a test story
TEST_STORY = """
As a user, I want to reset my password so that I can regain access to my account.

Acceptance Criteria:
1. User can request a password reset via email
2. User receives a reset link that expires in 24 hours
3. User can set a new password that meets security requirements
"""

def test_sdk_direct():
    """Test using the SDK directly."""
    print("\n=== Testing Direct SDK Usage ===")

    # Initialize provider and calculator
    #provider = OpenAIProvider()
    log_level = getattr(logging, "DEBUG")
    logger = setup_logger(log_level)

    calculator = BCPCalculator(logger=logger, provider_name="flow-openai")

    # Calculate BCP
    result = calculator.calculate_bcp(TEST_STORY)

    # Print results
    print(f"Total BCP: {result['total_bcp']}")

    return result

def main():
    """Run all tests."""
    # Test SDK directly
    sdk_result = test_sdk_direct()

    print(f"SDK Total BCP: {sdk_result['total_bcp']}")

if __name__ == "__main__":
    main()
