#!/usr/bin/env python3
"""
BCP Calculator - Command Line Interface

This script provides a CLI for calculating Business Complexity Points (BCP)
of user stories using a series of predefined prompts and multiple LLM providers.
"""

import argparse
import json
import logging
import sys
import os
from typing import Dict, Any
from dotenv import load_dotenv

from bcp import BCPCalculator, setup_logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Calculate Business Complexity Points (BCP) for a user story."
    )
    parser.add_argument(
        "story_file",
        type=str,
        help="Path to the user story markdown file"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to save the output results (default: print to stdout)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "claude", "flow"],
        default="openai",
        help="LLM provider to use (default: openai)"
    )
    return parser.parse_args()

def read_story_file(file_path: str, logger: logging.Logger) -> str:
    """Read content from a story file."""
    # Check if story file exists
    if not os.path.isfile(file_path):
        logger.error(f"Story file not found: {file_path}")
        sys.exit(1)
    
    # Read story content
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading story file: {str(e)}")
        sys.exit(1)

def calculate_bcp_for_story(story_content: str, provider: str, logger: logging.Logger) -> Dict[str, Any]:
    """Calculate BCP for a given story."""
    try:
        # Initialize BCP calculator with selected provider
        calculator = BCPCalculator(logger, provider_name=provider)
        
        # Calculate BCP
        return calculator.calculate_bcp(story_content)
    except Exception as e:
        logger.error(f"Error calculating BCP: {str(e)}")
        sys.exit(1)

def save_or_print_results(results: Dict[str, Any], output_format: str, output_file: str = None, logger: logging.Logger = None) -> None:
    """Save results to file or print to stdout."""
    # Format results based on specified format
    formatted_results = format_results_json(results) if output_format == "json" else format_results_text(results)
    
    # Output to file or stdout
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(formatted_results)
            if logger:
                logger.info(f"Results saved to {output_file}")
        except Exception as e:
            if logger:
                logger.error(f"Error saving results to {output_file}: {str(e)}")
            sys.exit(1)
    else:
        print(formatted_results)

def main():
    """Main entry point for the BCP Calculator CLI."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    logger = setup_logger(log_level)
    
    # Read story content
    story_content = read_story_file(args.story_file, logger)
    
    # Calculate BCP
    results = calculate_bcp_for_story(story_content, args.provider, logger)
    
    # Output results
    save_or_print_results(results, args.format, args.output_file, logger)

def format_results_json(results: Dict[str, Any]) -> str:
    """Format the results as JSON."""
    # Create a structured JSON output
    json_output = {
        "story_name": results.get("story_name", "Unknown"),
        "total_bcp": results.get("total_bcp", 0),
        "components": results.get("breakdown", {}),
        "steps": {}
    }
    
    # Extract maturity and invest scores
    maturity_score = 0
    invest_score = 0
    
    # Add step results with extracted data
    for step_name, step_result in results["steps"].items():
        if isinstance(step_result, dict):
            # Extract useful information from step result
            step_data = {
                "assessment": step_result.get("assessment", step_result.get("description", "")),
                "score": step_result.get("score", step_result.get("total", 0)),
                "classification": step_result.get("classification", ""),
                "raw_response": step_result.get("raw_response", "")
            }
            json_output["steps"][step_name] = step_data
            
            # Capture maturity and invest scores
            if step_name == "Story Maturity Complexity":
                maturity_score = step_result.get("score", 0)
            elif step_name == "Story INVEST Maturity":
                invest_score = step_result.get("score", 0)
        else:
            json_output["steps"][step_name] = {"raw_response": str(step_result)}
    
    # Add maturity and invest scores to root
    json_output["score"] = {
        "maturity": maturity_score,
        "invest": invest_score
    }
    
    return json.dumps(json_output, indent=2, ensure_ascii=False)

def format_results_text(results: Dict[str, Any]) -> str:
    """Format the results as text (legacy format)."""
    output = []
    
    # Add step results
    for step_name, step_result in results["steps"].items():
        output.append(f"=== {step_name} ===")
        output.append(str(step_result))
        output.append("")
    
    # Add final BCP
    output.append("=== FINAL BUSINESS COMPLEXITY POINTS ===")
    output.append(f"Total BCP: {results['total_bcp']}")
    output.append("")
    
    # Add breakdown
    output.append("=== BCP BREAKDOWN ===")
    for component, score in results["breakdown"].items():
        output.append(f"{component}: {score}")
    
    return "\n".join(output)

if __name__ == "__main__":
    main()