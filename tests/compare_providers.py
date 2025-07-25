#!/usr/bin/env python3
"""
Compare BCP Calculator Results Between Providers

This script processes a set of user stories with both OpenAI and Claude providers,
then generates a comparison report of the results.
"""

import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bcp import BCPCalculator, setup_logger

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Compare BCP calculation results between providers."
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

def process_story(story_path: str, provider: str, logger: logging.Logger) -> Dict[str, Any]:
    """
    Process a single story with the specified provider.
    
    Args:
        story_path: Path to the story file
        provider: Provider name ('openai' or 'claude')
        logger: Logger instance
        
    Returns:
        Dictionary with results
    """
    logger.info(f"Processing {os.path.basename(story_path)} with {provider}")
    
    try:
        # Read story content
        with open(story_path, 'r', encoding='utf-8') as file:
            story_content = file.read()
        
        # Initialize calculator with provider
        calculator = BCPCalculator(logger, provider_name=provider)
        
        # Calculate BCP
        start_time = time.time()
        results = calculator.calculate_bcp(story_content)
        end_time = time.time()
        
        # Add processing time to results
        results["processing_time"] = end_time - start_time
        results["provider"] = provider
        results["story_file"] = os.path.basename(story_path)
        
        logger.info(f"Completed {os.path.basename(story_path)} with {provider} in {end_time - start_time:.2f} seconds")
        return results
    
    except Exception as e:
        logger.error(f"Error processing {os.path.basename(story_path)} with {provider}: {str(e)}")
        return {
            "story_name": os.path.basename(story_path),
            "error": str(e),
            "provider": provider,
            "story_file": os.path.basename(story_path)
        }

def generate_comparison(results: List[Dict[str, Any]], output_dir: str, output_format: str, logger: logging.Logger):
    """
    Generate a comparison report from the results.
    
    Args:
        results: List of result dictionaries
        output_dir: Directory to save output files
        output_format: Output format (json, csv, or excel)
        logger: Logger instance
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract key metrics for comparison
    comparison_data = []
    for result in results:
        provider = result.get("provider", "unknown")
        story_file = result.get("story_file", "unknown")
        story_name = result.get("story_name", "Unknown")
        total_bcp = result.get("total_bcp", 0)
        processing_time = result.get("processing_time", 0)
        
        # Extract component scores
        components = result.get("breakdown", {})
        business_rules = components.get("Business Rules", 0)
        ui_elements = components.get("UI Elements", 0)
        external_integrations = components.get("External Integrations", 0)
        
        # Add to comparison data
        comparison_data.append({
            "Story": story_name,
            "File": story_file,
            "Provider": provider,
            "Total BCP": total_bcp,
            "Business Rules": business_rules,
            "UI Elements": ui_elements,
            "External Integrations": external_integrations,
            "Processing Time (s)": processing_time
        })
    
    # Create a DataFrame
    df = pd.DataFrame(comparison_data)
    
    # Save results based on format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_format == "json":
        output_file = os.path.join(output_dir, f"comparison_results_{timestamp}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_data, f, indent=2)
    elif output_format == "csv":
        output_file = os.path.join(output_dir, f"comparison_results_{timestamp}.csv")
        df.to_csv(output_file, index=False)
    elif output_format == "excel":
        output_file = os.path.join(output_dir, f"comparison_results_{timestamp}.xlsx")
        
        # Create a pivot table comparing providers
        pivot_df = df.pivot_table(
            index="File",
            columns="Provider",
            values=["Total BCP", "Business Rules", "UI Elements", "External Integrations", "Processing Time (s)"],
            aggfunc='mean'
        )
        
        # Calculate differences
        if "openai" in df["Provider"].values and "claude" in df["Provider"].values:
            diff_df = pd.DataFrame()
            for metric in ["Total BCP", "Business Rules", "UI Elements", "External Integrations", "Processing Time (s)"]:
                if (metric, "openai") in pivot_df.columns and (metric, "claude") in pivot_df.columns:
                    diff_df[f"{metric} Diff"] = pivot_df[metric, "openai"] - pivot_df[metric, "claude"]
                    diff_df[f"{metric} % Diff"] = ((pivot_df[metric, "openai"] / pivot_df[metric, "claude"]) - 1) * 100
            
            # Create Excel writer
            with pd.ExcelWriter(output_file) as writer:
                df.to_excel(writer, sheet_name="Raw Data", index=False)
                pivot_df.to_excel(writer, sheet_name="Provider Comparison")
                diff_df.to_excel(writer, sheet_name="Differences")
                
                # Create charts
                create_comparison_charts(df, output_dir, timestamp)
        else:
            df.to_excel(output_file, index=False)
    
    logger.info(f"Comparison report saved to {output_file}")

def create_comparison_charts(df: pd.DataFrame, output_dir: str, timestamp: str):
    """
    Create charts comparing provider results.
    
    Args:
        df: DataFrame with comparison data
        output_dir: Directory to save charts
        timestamp: Timestamp for file naming
    """
    # Create a directory for charts
    charts_dir = os.path.join(output_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)
    
    # 1. Total BCP comparison by story
    plt.figure(figsize=(12, 8))
    pivot_total = df.pivot(index="File", columns="Provider", values="Total BCP")
    pivot_total.plot(kind="bar")
    plt.title("Total BCP Comparison by Story")
    plt.xlabel("Story")
    plt.ylabel("Total BCP")
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, f"total_bcp_comparison_{timestamp}.png"))
    
    # 2. Processing time comparison
    plt.figure(figsize=(12, 8))
    pivot_time = df.pivot(index="File", columns="Provider", values="Processing Time (s)")
    pivot_time.plot(kind="bar")
    plt.title("Processing Time Comparison by Story")
    plt.xlabel("Story")
    plt.ylabel("Time (seconds)")
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, f"processing_time_comparison_{timestamp}.png"))
    
    # 3. Component breakdown comparison (average across all stories)
    components = ["Business Rules", "UI Elements", "External Integrations"]
    provider_components = df.groupby("Provider")[components].mean()
    
    plt.figure(figsize=(10, 6))
    provider_components.plot(kind="bar")
    plt.title("Average Component Scores by Provider")
    plt.xlabel("Provider")
    plt.ylabel("Average Score")
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, f"component_comparison_{timestamp}.png"))

def main():
    """Main entry point for the comparison script."""
    # Load environment variables
    load_dotenv()
    
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = getattr(logging, args.log_level)
    logger = setup_logger(log_level)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get list of story files
    story_dir = Path(args.stories_dir)
    story_files = list(story_dir.glob("*.md"))
    
    if not story_files:
        logger.error(f"No story files found in {args.stories_dir}")
        sys.exit(1)
    
    # Process each story with both providers
    results = []
    
    for story_file in story_files:
        # Process with OpenAI
        openai_result = process_story(str(story_file), "openai", logger)
        results.append(openai_result)
        
        # Process with Claude
        claude_result = process_story(str(story_file), "claude", logger)
        results.append(claude_result)
        
        # Save individual results
        story_name = os.path.splitext(story_file.name)[0]
        
        # Save OpenAI result
        with open(os.path.join(args.output_dir, f"{story_name}_openai.json"), 'w', encoding='utf-8') as f:
            json.dump(openai_result, f, indent=2)
        
        # Save Claude result
        with open(os.path.join(args.output_dir, f"{story_name}_claude.json"), 'w', encoding='utf-8') as f:
            json.dump(claude_result, f, indent=2)
    
    # Generate comparison report
    generate_comparison(results, args.output_dir, args.format, logger)
    
    logger.info("Comparison completed successfully")

if __name__ == "__main__":
    main()