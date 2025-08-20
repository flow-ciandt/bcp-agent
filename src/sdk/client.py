"""
BCP Calculator SDK Client.

This module provides a Python client for the BCP Calculator.
"""

from typing import Dict, Any, Optional, Union, List
import os
import logging
from pathlib import Path
import json
from dotenv import load_dotenv

from bcp import BCPCalculator, setup_logger


class BCPClient:
    """Python SDK for the BCP Calculator."""
    
    def __init__(self, 
                log_level: str = "INFO",
                provider: str = "openai"):
        """
        Initialize the BCP client.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            provider: LLM provider to use (openai or claude)
        """
        # Load environment variables if not already loaded
        load_dotenv()
        
        self.log_level = getattr(logging, log_level.upper())
        self.provider = provider
        self.logger = setup_logger(self.log_level)
        self.calculator = BCPCalculator(self.logger, provider_name=self.provider)
        
    def calculate(self, story_content: str) -> Dict[str, Any]:
        """
        Calculate BCP for a user story.
        
        Args:
            story_content: The user story content
            
        Returns:
            A dictionary containing the BCP calculation results
        """
        return self.calculator.calculate_bcp(story_content)
        
    def calculate_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Calculate BCP for a user story file.
        
        Args:
            file_path: Path to the user story file
            
        Returns:
            A dictionary containing the BCP calculation results
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Story file not found: {file_path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            story_content = f.read()
            
        return self.calculate(story_content)
        
    def batch_calculate(self, stories_dir: Union[str, Path], 
                        output_path: Optional[Union[str, Path]] = None,
                        file_pattern: str = "*.md") -> Dict[str, Dict[str, Any]]:
        """
        Calculate BCP for multiple user story files in a directory.
        
        Args:
            stories_dir: Directory containing user story files
            output_path: Optional path to save the batch results
            file_pattern: Glob pattern for matching story files (default: *.md)
            
        Returns:
            A dictionary mapping file names to their BCP calculation results
        """
        dir_path = Path(stories_dir)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {stories_dir}")
            
        results = {}
        for file_path in dir_path.glob(file_pattern):
            self.logger.info(f"Processing {file_path.name}")
            try:
                results[file_path.name] = self.calculate_file(file_path)
            except Exception as e:
                self.logger.error(f"Error processing {file_path.name}: {str(e)}")
                results[file_path.name] = {"error": str(e)}
                
        # Save results if output path is provided
        if output_path:
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
                
        return results
        
    def compare_providers(self, 
                          story_content: str,
                          providers: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Compare BCP calculations between different providers.
        
        Args:
            story_content: The user story content
            providers: List of providers to compare (defaults to ["openai", "claude"])
            
        Returns:
            A dictionary mapping providers to their BCP calculation results
        """
        if providers is None:
            providers = ["openai", "claude"]
            
        results = {}
        original_provider = self.provider
        
        for provider in providers:
            self.logger.info(f"Using provider: {provider}")
            self.provider = provider
            self.calculator = BCPCalculator(self.logger, provider_name=provider)
            try:
                results[provider] = self.calculate(story_content)
            except Exception as e:
                self.logger.error(f"Error with provider {provider}: {str(e)}")
                results[provider] = {"error": str(e)}
                
        # Restore original provider
        self.provider = original_provider
        self.calculator = BCPCalculator(self.logger, provider_name=original_provider)
        
        return results