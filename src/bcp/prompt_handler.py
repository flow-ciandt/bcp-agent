"""
Prompt Handler for BCP Calculator

This module handles loading and processing prompts for the BCP Calculator.
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional

from jinja2 import Template
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

from .llm_providers import LLMProvider, get_provider

class PromptHandler:
    """
    Handler for loading and processing prompts.
    """
    
    def __init__(self, logger: logging.Logger, provider_name: str = "openai"):
        """
        Initialize the prompt handler.
        
        Args:
            logger: The logger instance
            provider_name: The name of the LLM provider to use ('openai' or 'claude')
        """
        self.logger = logger
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # The prompts directory should be at the same level as the current file
        self.prompts_dir = os.path.join(current_dir, "prompts")
        self.provider = get_provider(provider_name, logger)
    
    def load_prompt(self, prompt_file: str) -> str:
        """
        Load a prompt template from file.
        
        Args:
            prompt_file: The filename of the prompt template
            
        Returns:
            The prompt template content
        """
        prompt_path = os.path.join(self.prompts_dir, prompt_file)
        self.logger.debug(f"Loading prompt from {prompt_path}")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Error loading prompt {prompt_file}: {str(e)}")
            raise
    
    def render_prompt(self, prompt_template: str, variables: Dict[str, Any]) -> str:
        """
        Render a prompt template with variables.
        
        Args:
            prompt_template: The prompt template content
            variables: The variables to render in the template
            
        Returns:
            The rendered prompt
        """
        self.logger.debug(f"Rendering prompt with variables: {list(variables.keys())}")
        
        try:
            template = Template(prompt_template)
            return template.render(**variables)
        except Exception as e:
            self.logger.error(f"Error rendering prompt: {str(e)}")
            raise
    
    def process_prompt(self, prompt_file: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a prompt with the LLM.
        
        Args:
            prompt_file: The filename of the prompt template
            variables: The variables to render in the template
            
        Returns:
            The parsed response from the LLM
        """
        self.logger.info(f"Processing prompt: {prompt_file}")
        
        # Load and render prompt
        prompt_template = self.load_prompt(prompt_file)
        rendered_prompt = self.render_prompt(prompt_template, variables)
        
        # Use the provider to invoke the LLM
        response = self.provider.invoke(rendered_prompt)
        
        # Parse response
        try:
            # First, try to extract JSON from markdown code blocks
            json_content = self._extract_json_from_response(response)
            if json_content:
                return json.loads(json_content)
            
            # Fallback: Check if response is direct JSON
            if response.strip().startswith('{') and response.strip().endswith('}'):
                return json.loads(response)
            else:
                return {"raw_response": response}
        except json.JSONDecodeError:
            self.logger.warning("Response is not valid JSON, returning raw text")
            return {"raw_response": response}
    
    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """
        Extract JSON content from markdown code blocks or other formats.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            The extracted JSON string or None if no JSON found
        """
        # Try to find JSON in markdown code blocks
        json_pattern = r'```json\s*\n(.*?)\n```'
        match = re.search(json_pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Try to find JSON without markdown blocks
        json_pattern = r'```\s*\n(\{.*?\})\s*\n```'
        match = re.search(json_pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Try to find standalone JSON
        json_pattern = r'(\{[^}]*"total"[^}]*\})'
        match = re.search(json_pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None