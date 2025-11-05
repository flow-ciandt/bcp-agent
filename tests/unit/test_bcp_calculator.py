import logging
import pytest

from bcp.bcp_calculator import BCPCalculator
from bcp.logger import setup_logger

class FakePromptHandler:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []
    def process_prompt(self, prompt_file, variables):
        self.calls.append((prompt_file, variables))
        return self._responses.get(prompt_file, {})

@pytest.fixture
def logger():
    return setup_logger(logging.DEBUG)


def test_bcp_happy_path(logger):
    responses = {
        # Step 3: Break Elements
        "step3_flow_bcp_break_elements.jinja2": {
            "Integrations (Boundaries)": [
                {"Boundary": "Payments API", "Size": "M"},
                {"Boundary": "Email Service", "Size": "S"},
                {"Boundary": "Analytics", "Size": "XL"},
            ],
            "User View": "Login page",
            "Acceptance Criteria": [
                "User can request reset",
                "Link expires in 24h"
            ],
            "Test Plan": {"GIVEN": "user requests reset", "WHEN": "link used", "THEN": "password updated"},
            "Business Narrative": "Allow password resets",
            "Requirements and Business Rules": "Password must meet policy"
        },
        # Step 4: External Integrations Complexity -> returns list with Size
        "step4_flow_bcp_boundaries.jinja2": [
            {"Boundary": "Payments API", "Size": "M"},
            {"Boundary": "Email Service", "Size": "S"},
            {"Boundary": "Analytics", "Size": "XL"},
        ],
        # Step 5: UI Elements Complexity -> Static and Dynamic counts
        "step5_flow_bcp_interface_elements.jinja2": {
            "Static": 5,  # ceil(5/5)*3 = 1*3 = 3
            "Dynamic": 6  # ceil(6/5)*5 = 2*5 = 10
        },
        # Step 6: Business Rules Complexity -> list of rules with Score
        "step6_flow_bcp_business_rule.jinja2": [
            {"Rule": "Password policy", "Score": 4},
            {"Rule": "Rate limit", "Score": 2}
        ],
    }
    fake = FakePromptHandler(responses)

    calc = BCPCalculator(logger=logger, provider_name="openai", prompt_handler=fake)
    story = "Password Reset\nAs a user I want to reset my password."
    result = calc.calculate_bcp(story)

    # Total = UI (13) + Business (6) + External (13) = 32
    assert result["total_bcp"] == 32
    assert result["breakdown"]["UI Elements"] == 13
    assert result["breakdown"]["Business Rules"] == 6
    assert result["breakdown"]["External Integrations"] == 13


def test_bcp_raw_response_skips_calculation(logger):
    responses = {
        "step3_flow_bcp_break_elements.jinja2": {},
        # Provide raw_response for a required step
        "step4_flow_bcp_boundaries.jinja2": {"raw_response": "unparsed"},
        "step5_flow_bcp_interface_elements.jinja2": {"Static": 0, "Dynamic": 0},
        "step6_flow_bcp_business_rule.jinja2": [
            {"Rule": "X", "Score": 1}
        ],
    }
    fake = FakePromptHandler(responses)
    calc = BCPCalculator(logger=logger, prompt_handler=fake)
    story = "Test\nBody"
    result = calc.calculate_bcp(story)
    # Boundaries skipped, UI=0, Business=1
    assert result["total_bcp"] == 1
    assert "External Integrations" not in result["breakdown"]
    assert result["breakdown"]["Business Rules"] == 1


def test_bcp_missing_elements_defaults(logger):
    responses = {
        # Break Elements missing content -> later steps get variables["elements"] == ""
        "step3_flow_bcp_break_elements.jinja2": {},
        # With empty elements, code sets default response for boundaries (XS -> 1)
        "step4_flow_bcp_boundaries.jinja2": [
            {"Boundary": 1, "Summary": "There is no external integration detected", "Size": "XS"}
        ],
        # UI default response total 0, Business default response total 0
        "step5_flow_bcp_interface_elements.jinja2": {"step": "Interface", "description": "There is no interface elements detected", "total": 0},
        "step6_flow_bcp_business_rule.jinja2": {"step": "Business", "description": "There is no logical rules detected", "total": 0},
    }
    fake = FakePromptHandler(responses)
    calc = BCPCalculator(logger=logger, prompt_handler=fake)
    story = "A\nB"
    result = calc.calculate_bcp(story)
    assert result["total_bcp"] == 1
    assert result["breakdown"]["External Integrations"] == 1


def test_bcp_required_step_error_halts(logger):
    class ErrorPromptHandler(FakePromptHandler):
        def process_prompt(self, prompt_file, variables):
            if prompt_file == "step4_flow_bcp_boundaries.jinja2":
                raise RuntimeError("LLM error")
            return super().process_prompt(prompt_file, variables)

    responses = {
        "step3_flow_bcp_break_elements.jinja2": {},
        "step5_flow_bcp_interface_elements.jinja2": {"Static": 0, "Dynamic": 0},
        "step6_flow_bcp_business_rule.jinja2": [],
    }
    fake = ErrorPromptHandler(responses)
    calc = BCPCalculator(logger=logger, prompt_handler=fake)
    story = "A\nB"
    result = calc.calculate_bcp(story)
    assert "error" in result
    assert result["steps"]["External Integrations Complexity"]["error"].startswith("LLM error")
