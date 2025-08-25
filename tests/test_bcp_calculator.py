#!/usr/bin/env python3
"""
Test script for the BCP Calculator

This script tests the BCP Calculator with a sample user story.
"""



import os
import logging
import json
import argparse
import csv
from dotenv import load_dotenv
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from bcp import BCPCalculator, setup_logger


def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test the BCP Calculator with sample user stories.")
    parser.add_argument(
        "--executions",
        type=int,
        default=1,
        help="Number of times to execute BCP calculation for each story (default: 1)"
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Setup logging
    logger = setup_logger(logging.DEBUG)
    logger.info("Starting BCP Calculator test")

    # Check if test data directory exists
    test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.isdir(test_data_dir):
        logger.error(f"Test data directory not found: {test_data_dir}")
        return

    # Get list of test stories
    test_stories = [f for f in os.listdir(test_data_dir) if f.endswith(".md")]
    if not test_stories:
        logger.error(f"No test stories found in {test_data_dir}")
        return

    # Initialize BCP calculator
    calculator = BCPCalculator(logger)

    # Prepare to collect results for CSV
    csv_rows = []
    csv_header = ["story"]
    for i in range(args.executions):
        csv_header += [f"business_exec_{i+1}", f"interface_exec_{i+1}", f"integration_exec_{i+1}", f"total_bcp_exec_{i+1}"]
        csv_header += [f"business_rules_{i+1}", f"interface_elements_{i+1}", f"boundaries_{i+1}"]
    
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_path, exist_ok=True)

    for story_file in test_stories:
        story_path = os.path.join(test_data_dir, story_file)
        logger.info(f"Testing with story: {story_file}")

        total_bcp_list = []

        try:
            # Read story content
            with open(story_path, 'r', encoding='utf-8') as file:
                story_content = file.read()

            results_list = []
            
            for i in range(args.executions):
                logger.info(f"Execution {i+1}/{args.executions} for {story_file}")
                # Calculate BCP
                results = calculator.calculate_bcp(story_content)
                results_list.append(results)

                logger.info(f"Total BCP: {results['total_bcp']}")
                logger.info(f"Breakdown: {results['breakdown']}")

                # total_bcp_list.append(results.get('total_bcp', ''))
                total_bcp_list.append(results.get('breakdown', {}).get('Business Rules', ''))
                total_bcp_list.append(results.get('breakdown', {}).get('UI Elements', ''))
                total_bcp_list.append(results.get('breakdown', {}).get('External Integrations', ''))
                total_bcp_list.append(results.get('total_bcp', ''))
                total_bcp_list.append(results.get('steps', {}).get('Business Rules Complexity', ''))
                total_bcp_list.append(results.get('steps', {}).get('UI Elements Complexity', ''))
                total_bcp_list.append(results.get('steps', {}).get('External Integrations Complexity', ''))

            # Save results
            output_file = os.path.join(
                output_path,
                f"{os.path.splitext(story_file)[0]}_results.json"
            )
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump(results_list, file, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_file}")

        except Exception as e:
            logger.error(f"Error processing {story_file}: {str(e)}")
            # Fill with empty values if error
            while len(total_bcp_list) < args.executions:
                total_bcp_list.append('')
        
        # Add row for this story
        csv_rows.append([story_file] + total_bcp_list)

    # Write CSV file
    csv_output_path = os.path.join(output_path, f"bcp_results_summary-{datetime.now().strftime('_%Y%m%d_%H%M%S')}.csv")
    with open(csv_output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_header)
        writer.writerows(csv_rows)
    logger.info(f"CSV summary written to {csv_output_path}")

if __name__ == "__main__":
    main()