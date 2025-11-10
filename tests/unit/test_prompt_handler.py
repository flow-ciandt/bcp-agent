import logging
import json
import pytest

from bcp.prompt_handler import PromptHandler
from bcp.logger import setup_logger

class FakeProvider:
    def __init__(self, response_text):
        self.response_text = response_text
    def invoke(self, prompt: str) -> str:
        return self.response_text

@pytest.fixture
def logger():
    return setup_logger(logging.DEBUG)


def test_render_prompt(logger):
    handler = PromptHandler(logger, provider_name="openai")
    template = "Hello {{ name }}"
    rendered = handler.render_prompt(template, {"name": "World"})
    assert rendered == "Hello World"


def test_process_prompt_codeblock_json(logger, monkeypatch):
    # Fake provider returns JSON inside a code block
    response = """```json\n{\n  \"total\": 5\n}\n```"""
    handler = PromptHandler(logger, provider_name="openai")
    handler.provider = FakeProvider(response)

    # Create a simple prompt file in-memory by intercepting load_prompt
    monkeypatch.setattr(handler, "load_prompt", lambda f: "Total? {{ x }}")
    out = handler.process_prompt("any", {"x": 1})
    assert out == {"total": 5}


def test_process_prompt_plain_json(logger, monkeypatch):
    response = "{\n  \"total\": 7\n}"
    handler = PromptHandler(logger, provider_name="openai")
    handler.provider = FakeProvider(response)
    monkeypatch.setattr(handler, "load_prompt", lambda f: "X")
    out = handler.process_prompt("any", {})
    assert out == {"total": 7}


def test_process_prompt_raw_text(logger, monkeypatch):
    response = "No JSON here"
    handler = PromptHandler(logger, provider_name="openai")
    handler.provider = FakeProvider(response)
    monkeypatch.setattr(handler, "load_prompt", lambda f: "X")
    out = handler.process_prompt("any", {})
    assert out == {"raw_response": "No JSON here"}


def test_extract_json_variants(logger):
    handler = PromptHandler(logger, provider_name="openai")
    s1 = """```json\n{\"total\":1}\n```"""
    assert handler._extract_json_from_response(s1) == '{"total":1}'
    s2 = """```\n{\"total\":2}\n```"""
    assert handler._extract_json_from_response(s2) == '{"total":2}'
    s3 = "prefix {\"total\":3} suffix"
    assert handler._extract_json_from_response(s3) == '{"total":3}'
    s4 = "no json"
    assert handler._extract_json_from_response(s4) is None
