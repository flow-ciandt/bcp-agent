#!/usr/bin/env python3
"""
Run Provider Comparison

This script is a convenient wrapper to run the provider comparison tool.
"""

import sys
import os
import argparse
from pathlib import Path

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run BCP provider comparison on test stories."
    )
    parser.add_argument(
        "--stories-dir",
        type=str,
        default="tests/data",
        help="Directory containing user story files (default: tests/data)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="tests/results",
        help="Directory to save results (default: tests/results)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "csv", "excel"],
        default="excel",
        help="Output format for comparison (default: excel)"
    )
    return parser.parse_args()

def main():
    """Main entry point for the wrapper script."""
    args = parse_arguments()
    
    # Ensure paths exist
    stories_dir = Path(args.stories_dir)
    output_dir = Path(args.output_dir)
    
    if not stories_dir.exists():
        print(f"Error: Stories directory '{stories_dir}' does not exist.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Build command to run the comparison script
    command = [
        "python",
        os.path.join("tests", "compare_providers.py"),
        f"--stories-dir={args.stories_dir}",
        f"--output-dir={args.output_dir}",
        f"--log-level={args.log_level}",
        f"--format={args.format}"
    ]
    
    # Execute the comparison script
    print(f"Running comparison with command: {' '.join(command)}")
    os.execvp("python", command)

if __name__ == "__main__":
    main()