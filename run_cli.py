#!/usr/bin/env python3
"""
BCP Calculator - Main Entry Point

This script is a wrapper around the main application module.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run the main function from the actual module
from src.main import main

if __name__ == "__main__":
    main()