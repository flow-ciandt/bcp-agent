"""
LLM Providers for BCP Calculator

This module provides a unified interface for different LLM providers.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List, Iterator

from langchain.schema import StrOutputParser
from langchain.schema.language_model import BaseLanguageModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.pydantic_v1 import Field, root_validator
from langchain_core.runnables import RunnableLambda
import requests


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


class FlowChatModel(BaseChatModel):
    """Custom implementation for Flow's Chat Completions API."""

    # Define required fields for this chat model
    base_url: str
    flow_tenant: Optional[str]
    flow_agent: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
    api_key: Optional[str]

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True
        extra = "forbid"

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that the environment is properly set up."""
        # Set default values if not provided
        values["model_name"] = values.get("model_name") or "gpt-4o-mini"
        values["temperature"] = values.get("temperature") or 0.0
        values["max_tokens"] = values.get("max_tokens") or 4096
        values["base_url"] = values.get("base_url") or "https://flow.ciandt.com/ai-orchestration-api/v1/openai"

        return values

    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "flow"

    def _convert_messages_to_flow_format(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """Convert LangChain messages to Flow API format."""
        flow_messages = []
        for message in messages:
            if message.type == "human":
                flow_messages.append({"role": "user", "content": message.content})
            elif message.type == "ai":
                flow_messages.append({"role": "assistant", "content": message.content})
            elif message.type == "system":
                flow_messages.append({"role": "system", "content": message.content})
            else:
                flow_messages.append({"role": "user", "content": str(message.content)})
        return flow_messages

    def _generate(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate completion from Flow API."""
        flow_messages = self._convert_messages_to_flow_format(messages)

        headers = {
            "Content-Type": "application/json",
            "accept": "application/json"
        }

        # Get primitive values from Field objects
        flow_tenant = self.flow_tenant
        flow_agent = self.flow_agent
        api_key = self.api_key
        base_url = self.base_url
        max_tokens = self.max_tokens
        temperature = self.temperature
        model_name = self.model_name

        # Add Flow-specific headers if available
        if flow_tenant:
            headers["FlowTenant"] = flow_tenant
        if flow_agent:
            headers["FlowAgent"] = flow_agent

        # Add API key if available
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        url = f"{base_url}/ai-orchestration-api/v1/openai/chat/completions"

        payload = {
            "stream": False,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "allowedModels": [model_name],
            "messages": flow_messages
        }

        # Add stop sequences if provided
        if stop:
            payload["stop"] = stop

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract the assistant's message from the response
            if "choices" in data and len(data["choices"]) > 0:
                message_content = data["choices"][0]["message"]["content"]

                # Create a ChatGeneration object
                chat_generation = ChatGeneration(message=AIMessage(content=message_content))

                # Return a ChatResult
                return ChatResult(generations=[chat_generation])
            else:
                raise ValueError("No message content found in response")
        except Exception as e:
            raise RuntimeError(f"Error calling Flow API: {str(e)}")

    def _stream(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any
    ) -> Iterator[Dict[str, Any]]:
        """Stream completion from Flow API (not implemented)."""
        raise NotImplementedError("Streaming not implemented for FlowChatModel")


class FlowProvider(LLMProvider):
    """Flow provider implementation."""

    def __init__(self,
                 logger: logging.Logger,
                 model_name: str = "gpt-4o-mini",
                 temperature: float = 0,
                 max_tokens: int = 4096):
        """
        Initialize the Flow provider.

        Args:
            logger: The logger instance
            model_name: The name of the Flow model to use
            temperature: The temperature parameter for the model
            max_tokens: Maximum tokens to generate
        """
        super().__init__(logger)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = os.environ.get("FLOW_BASE_URL")
        self.flow_tenant = os.environ.get("FLOW_TENANT", "flowteam")
        self.flow_agent = os.environ.get("FLOW_AGENT", "bcp-opensource")
        self.api_key = self._get_flow_token()
        self.logger.info(f"Initialized Flow provider with model {model_name}")

    def _get_flow_token(self) -> str:
        """
        Retrieve a new Flow token.

        Returns:
            The Flow API token
        """
        headers = {
            "accept": "/",
            "Content-Type": "application/json",
            "FlowTenant": "flowteam",
        }

        payload = {
            "clientId": os.environ.get("FLOW_CLIENT_ID"),
            "clientSecret": os.environ.get("FLOW_CLIENT_SECRET"),
            "appToAccess": "llm-api"
        }

        url = f"{self.base_url}/auth-engine-api/v1/api-key/token"

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        except Exception as e:
            raise RuntimeError(f"Error calling Flow API: {str(e)}")

        return data.get("access_token")

    def get_model(self) -> BaseLanguageModel:
        """
        Get the Flow model.

        Returns:
            The Flow model
        """
        return FlowChatModel(
            base_url=self.base_url,
            model_name=self.model_name,
            flow_tenant=self.flow_tenant,
            flow_agent=self.flow_agent,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key
        )


class FlowBedrockChatModel(BaseChatModel):
    """Custom implementation for Flow's Bedrock API."""

    # Define required fields for this chat model
    base_url: str
    flow_tenant: Optional[str]
    flow_agent: Optional[str]
    model_name: str
    temperature: float
    max_tokens: int
    api_key: Optional[str]
    top_p: float
    top_k: int
    anthropic_version: str
    stop_sequences: List[str]

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True
        extra = "forbid"

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that the environment is properly set up."""
        # Set default values if not provided
        values["model_name"] = values.get("model_name") or "anthropic.claude-3-5-haiku"
        values["temperature"] = values.get("temperature") or 1.0
        values["max_tokens"] = values.get("max_tokens") or 1000
        values["base_url"] = values.get("base_url") or "https://flow.ciandt.com"
        values["top_p"] = values.get("top_p") or 0.999
        values["top_k"] = values.get("top_k") or 250
        values["anthropic_version"] = values.get("anthropic_version") or "bedrock-2023-05-31"
        values["stop_sequences"] = values.get("stop_sequences") or []

        return values

    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "flow_bedrock"

    def _convert_messages_to_bedrock_format(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """Convert LangChain messages to Bedrock API format."""
        bedrock_messages = []

        for message in messages:
            message_dict = {
                "role": "user" if message.type == "human" else "assistant" if message.type == "ai" else "system",
                "content": []
            }

            # Format the content as a text entry
            message_dict["content"].append({
                "type": "text",
                "text": message.content
            })

            bedrock_messages.append(message_dict)

        return bedrock_messages

    def _generate(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any
    ) -> ChatResult:
        """Generate completion from Flow's Bedrock API."""
        bedrock_messages = self._convert_messages_to_bedrock_format(messages)

        headers = {
            "Content-Type": "application/json",
            "accept": "*/*"
        }

        # Get primitive values from Field objects
        flow_tenant = self.flow_tenant
        flow_agent = self.flow_agent
        api_key = self.api_key
        base_url = self.base_url
        max_tokens = self.max_tokens
        temperature = self.temperature
        model_name = self.model_name
        top_p = self.top_p
        top_k = self.top_k
        anthropic_version = self.anthropic_version
        stop_sequences = self.stop_sequences

        # Add Flow-specific headers if available
        if flow_tenant:
            headers["FlowTenant"] = flow_tenant
        if flow_agent:
            headers["FlowAgent"] = flow_agent

        # Add API key if available
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Add stop sequences from method parameters if provided
        if stop:
            stop_sequences = stop

        url = f"{base_url}/ai-orchestration-api/v1/bedrock/invoke"

        payload = {
            "messages": bedrock_messages,
            "anthropic_version": anthropic_version,
            "max_tokens": max_tokens,
            "top_k": top_k,
            "stop_sequences": stop_sequences,
            "temperature": temperature,
            "top_p": top_p,
            "model": model_name
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract the assistant's message from the response
            if "content" in data and len(data["content"]) > 0:
                # Get the text content from the response
                text_contents = []
                for content_part in data["content"]:
                    if content_part["type"] == "text":
                        text_contents.append(content_part["text"])

                message_content = "\n".join(text_contents)

                # Create a ChatGeneration object
                chat_generation = ChatGeneration(message=AIMessage(content=message_content))

                # Return a ChatResult
                return ChatResult(generations=[chat_generation])
            else:
                raise ValueError("No message content found in response")
        except Exception as e:
            raise RuntimeError(f"Error calling Flow Bedrock API: {str(e)}")

    def _stream(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any
    ) -> Iterator[ChatResult]:
        """Stream completion from Flow API (not implemented)."""
        raise NotImplementedError("Streaming not implemented for FlowBedrockChatModel")


class FlowBedrockProvider(LLMProvider):
    """Flow Bedrock provider implementation."""

    def __init__(self,
                 logger: logging.Logger,
                 model_name: str = "anthropic.claude-3-5-haiku",
                 temperature: float = 1.0,
                 max_tokens: int = 1000):
        """
        Initialize the Flow Bedrock provider.

        Args:
            logger: The logger instance
            model_name: The name of the Bedrock model to use
            temperature: The temperature parameter for the model
            max_tokens: Maximum tokens to generate
        """
        super().__init__(logger)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = os.environ.get("FLOW_BASE_URL")
        self.flow_tenant = os.environ.get("FLOW_TENANT", "flowteam")
        self.flow_agent = os.environ.get("FLOW_AGENT", "bcp-opensource")
        self.api_key = self._get_flow_token()
        self.top_p = float(os.environ.get("FLOW_BEDROCK_TOP_P", "0.999"))
        self.top_k = int(os.environ.get("FLOW_BEDROCK_TOP_K", "250"))
        self.anthropic_version = os.environ.get("FLOW_BEDROCK_ANTHROPIC_VERSION", "bedrock-2023-05-31")
        self.stop_sequences = []
        self.logger.info(f"Initialized Flow Bedrock provider with model {model_name}")

    def _get_flow_token(self) -> str:
        """
        Retrieve a new Flow token.

        Returns:
            The Flow API token
        """
        headers = {
            "accept": "/",
            "Content-Type": "application/json",
            "FlowTenant": "flowteam",
        }

        payload = {
            "clientId": os.environ.get("FLOW_CLIENT_ID"),
            "clientSecret": os.environ.get("FLOW_CLIENT_SECRET"),
            "appToAccess": "llm-api"
        }

        url = f"{self.base_url}/auth-engine-api/v1/api-key/token"

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        except Exception as e:
            raise RuntimeError(f"Error calling Flow API: {str(e)}")

        return data.get("access_token")

    def get_model(self) -> BaseLanguageModel:
        """
        Get the Flow Bedrock model.

        Returns:
            The Flow Bedrock model
        """
        return FlowBedrockChatModel(
            base_url=self.base_url,
            model_name=self.model_name,
            flow_tenant=self.flow_tenant,
            flow_agent=self.flow_agent,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key,
            top_p=self.top_p,
            top_k=self.top_k,
            anthropic_version=self.anthropic_version,
            stop_sequences=self.stop_sequences
        )


def get_provider(provider_name: str, logger: logging.Logger) -> LLMProvider:
    """
    Get the LLM provider based on the provider name.

    Args:
        provider_name: The name of the provider ('openai', 'claude', 'flow', or 'flow-bedrock')
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
    elif provider_name == "flow-openai":
        model_name = os.environ.get("FLOW_MODEL_NAME", "gpt-4o-mini")
        max_tokens = int(os.environ.get("FLOW_MAX_TOKENS", "4096"))
        return FlowProvider(logger, model_name=model_name, max_tokens=max_tokens)
    elif provider_name == "flow-bedrock":
        model_name = os.environ.get("FLOW_BEDROCK_MODEL_NAME", "anthropic.claude-3-5-haiku")
        max_tokens = int(os.environ.get("FLOW_BEDROCK_MAX_TOKENS", "1000"))
        temperature = float(os.environ.get("FLOW_BEDROCK_TEMPERATURE", "1.0"))
        return FlowBedrockProvider(logger, model_name=model_name, max_tokens=max_tokens, temperature=temperature)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")
