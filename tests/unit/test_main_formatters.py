from bcp.logger import setup_logger
from src.main import format_results_json, format_results_text


def test_format_results_json_structure():
    results = {
        "story_name": "Story",
        "total_bcp": 5,
        "breakdown": {"Business Rules": 2, "UI Elements": 3},
        "steps": {
            "Story Maturity Complexity": {"assessment": "ok", "score": 4, "classification": "Mature"},
            "Story INVEST Maturity": {"assessment": "ok", "score": 3, "classification": "Partial"},
            "Business Rules Complexity": {"total": 2},
        }
    }
    out = format_results_json(results)
    assert "\"total_bcp\": 5" in out
    assert "\"components\": {" in out
    assert "\"score\": {" in out


def test_format_results_text_contains_sections():
    results = {
        "steps": {
            "A": {"x": 1},
            "B": "raw",
        },
        "total_bcp": 7,
        "breakdown": {"X": 3, "Y": 4},
    }
    out = format_results_text(results)
    assert "=== FINAL BUSINESS COMPLEXITY POINTS ===" in out
    assert "Total BCP: 7" in out
    assert "=== BCP BREAKDOWN ===" in out
