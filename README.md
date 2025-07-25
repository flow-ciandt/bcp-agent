# BCP Calculator

A command-line tool for calculating Business Complexity Points (BCP) of user stories using LangChain with support for multiple LLM providers (OpenAI GPT-4o-2024-05-13 and Anthropic Claude).

## Overview

The BCP Calculator analyzes user stories and calculates their Business Complexity Points based on:
- Business Rules Complexity
- Interface Elements Complexity
- Boundaries Complexity

The application orchestrates a flow through 6 predefined prompt steps:
1. Story Maturity Complexity (complementary analysis)
2. Story INVEST Maturity (complementary analysis)
3. Break Elements (separates the story into Business Rules, Interface Elements, and Boundaries)
4. Boundaries Complexity (calculates complexity points for Boundaries)
5. Interface Elements Complexity (calculates complexity points for Interface Elements)
6. Business Rules Complexity (calculates complexity points for Business Rules)

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd bcp-agent
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```
   cp .env.example .env
   ```
   
   Then edit the `.env` file to add your API keys for the providers you want to use (OpenAI and/or Anthropic).

## Usage

Run the BCP Calculator with a user story file:

```
python main.py path/to/user_story.md
```

### Options

- `--log-level`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO.
- `--output-file`: Path to save the output results. If not provided, results are printed to stdout.
- `--provider`: LLM provider to use (openai or claude). Default is openai.
- `--format`: Output format (text or json). Default is json.

### Examples

#### Basic Usage

Process a user story with the default provider (OpenAI):

```bash
python main.py tests/data/story1.md
```

#### Using Different Providers

Process with OpenAI (explicitly):

```bash
python main.py tests/data/story1.md --provider openai
```

Process with Claude:

```bash
python main.py tests/data/story1.md --provider claude
```

#### Saving Results

Save the results to a JSON file:

```bash
python main.py tests/data/story1.md --output-file results.json
```

Save results in text format:

```bash
python main.py tests/data/story1.md --format text --output-file results.txt
```

#### Detailed Logging

Run with detailed debug logs:

```bash
python main.py tests/data/story1.md --log-level DEBUG
```

#### Complete Example

Process a story with Claude, save as text with detailed logs:

```bash
python main.py tests/data/story1.md --provider claude --format text --output-file claude_results.txt --log-level DEBUG
```

## Output

The output includes:
- Results from each step in the process
- Final Business Complexity Points (BCP)
- Breakdown of points by component (Business Rules, Interface Elements, Boundaries)

### Sample JSON Output

```json
{
  "story_name": "User Story: Add Payment Method",
  "total_bcp": 13,
  "components": {
    "Business Rules": 5,
    "UI Elements": 3,
    "External Integrations": 5
  },
  "steps": {
    "Story Maturity Complexity": {
      "assessment": "The story is well-defined with clear acceptance criteria",
      "score": 4,
      "classification": "Mature"
    },
    "Story INVEST Maturity": {
      "assessment": "Independent, testable, but somewhat large in scope",
      "score": 3,
      "classification": "Partially Mature"
    },
    "Business Rules Complexity": {
      "total": 5
    },
    "UI Elements Complexity": {
      "total": 3
    },
    "External Integrations Complexity": {
      "total": 5
    }
  }
}
```

## Project Structure

### Core Application Files
- `main.py`: Entry point wrapper for the CLI application
- `src/main.py`: Main CLI implementation
- `src/bcp/`: Core package containing all BCP calculator functionality
  - `__init__.py`: Package exports
  - `bcp_calculator.py`: Core logic for orchestrating the flow
  - `prompt_handler.py`: Handle loading and processing prompts
  - `llm_providers.py`: Provider abstraction for different LLM services
  - `logger.py`: Custom logging functionality
  - `prompts/`: Directory containing the prompt templates

### Testing and Utilities
- `tests/test_bcp_calculator.py`: Unit tests for the calculator
- `tests/test_providers.py`: Test script for LLM providers
- `tests/compare_providers.py`: Script to compare results between providers

### Documentation
- `docs/`: Directory containing usage guides and documentation

### Documentation
- `README.md`: Project documentation
- `LICENSE`: License information

## License

[MIT License](LICENSE)