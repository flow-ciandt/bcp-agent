"""
LLM Providers for BCP Calculator

This module provides a unified interface for different LLM providers.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union

from langchain.schema import StrOutputParser
from langchain.schema.language_model import BaseLanguageModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


class LLMProvider(ABC):
    """Base abstract class for LLM providers."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize the LLM provider.
        
        Args:
            logger: The logger instance
        """
        self.logger = logger
    
    @abstractmethod
    def get_model(self) -> BaseLanguageModel:
        """
        Get the LLM model for this provider.
        
        Returns:
            The LLM model
        """
        pass
    
    def invoke(self, prompt: str) -> str:
        """
        Invoke the LLM with a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM response as a string
        """
        self.logger.debug("Sending prompt to LLM")
        chain = self.get_model() | StrOutputParser()
        response = chain.invoke(prompt)
        self.logger.debug("Received response from LLM")
        return response


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, logger: logging.Logger, model_name: str = "gpt-4o-2024-05-13", temperature: float = 0):
        """
        Initialize the OpenAI provider.
        
        Args:
            logger: The logger instance
            model_name: The name of the OpenAI model to use
            temperature: The temperature parameter for the model
        """
        super().__init__(logger)
        self.model_name = model_name
        self.temperature = temperature
        self.logger.info(f"Initialized OpenAI provider with model {model_name}")
    
    def get_model(self) -> BaseLanguageModel:
        """
        Get the OpenAI model.
        
        Returns:
            The OpenAI model
        """
        return ChatOpenAI(model=self.model_name, temperature=self.temperature)


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, logger: logging.Logger, model_name: str = "claude-3-sonnet-20240229-v1:0", temperature: float = 0):
        """
        Initialize the Claude provider.
        
        Args:
            logger: The logger instance
            model_name: The name of the Claude model to use
            temperature: The temperature parameter for the model
        """
        super().__init__(logger)
        self.model_name = model_name
        self.temperature = temperature
        self.logger.info(f"Initialized Claude provider with model {model_name}")
    
    def get_model(self) -> BaseLanguageModel:
        """
        Get the Claude model.
        
        Returns:
            The Claude model
        """
        return ChatAnthropic(model=self.model_name, temperature=self.temperature)


def get_provider(provider_name: str, logger: logging.Logger) -> LLMProvider:
    """
    Get the LLM provider based on the provider name.
    
    Args:
        provider_name: The name of the provider ('openai' or 'claude')
        logger: The logger instance
        
    Returns:
        The LLM provider
        
    Raises:
        ValueError: If the provider name is not supported
    """
    provider_name = provider_name.lower()
    
    if provider_name == "openai":
        model_name = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-2024-05-13")
        return OpenAIProvider(logger, model_name=model_name)
    elif provider_name == "claude":
        model_name = os.environ.get("ANTHROPIC_MODEL_NAME", "claude-3-sonnet-20240229-v1:0")
        return ClaudeProvider(logger, model_name=model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")