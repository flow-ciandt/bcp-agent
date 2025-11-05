import logging
import pytest

from bcp.llm_providers import get_provider, OpenAIProvider, ClaudeProvider, FlowProvider, FlowBedrockProvider
from bcp.logger import setup_logger

@pytest.fixture
def logger():
    return setup_logger(logging.DEBUG)


def test_get_provider_basic(logger):
    p = get_provider("openai", logger)
    assert isinstance(p, OpenAIProvider)
    p = get_provider("claude", logger)
    assert isinstance(p, ClaudeProvider)


def test_get_provider_flow_mapping(logger, monkeypatch):
    # Avoid constructing real Flow providers by intercepting constructors
    constructed = {"flow": False, "bedrock": False}

    class DummyFlow(FlowProvider):
        def __init__(self, *a, **kw):
            constructed["flow"] = True
            # Do not call super to avoid token fetch
    class DummyBedrock(FlowBedrockProvider):
        def __init__(self, *a, **kw):
            constructed["bedrock"] = True
            # Do not call super to avoid token fetch

    monkeypatch.setattr("bcp.llm_providers.FlowProvider", DummyFlow)
    monkeypatch.setattr("bcp.llm_providers.FlowBedrockProvider", DummyBedrock)

    p = get_provider("flow-openai", logger)
    assert constructed["flow"] is True
    p = get_provider("flow-bedrock", logger)
    assert constructed["bedrock"] is True
