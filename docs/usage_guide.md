# BCP Agent Usage Guide

The Business Complexity Points (BCP) Agent is a command-line tool that helps calculate the complexity of user stories using advanced language models. This guide provides detailed instructions on how to use the tool effectively.

## Installation

1. Clone the repository:
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

4. Edit the `.env` file to add your API keys:
   ```
   # OpenAI API Key (required if using OpenAI provider)
   OPENAI_API_KEY=your_openai_api_key_here

   # Anthropic API Key (required if using Claude provider)
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Basic Usage

Run the BCP Agent with a user story file:

```bash
python main.py path/to/user_story.md
```

This will process the user story using the default settings (OpenAI provider, JSON output format).

## Command-Line Arguments

The BCP Agent supports several command-line arguments to customize its behavior:

| Argument | Description | Default |
|----------|-------------|---------|
| `story_file` | Path to the user story markdown file (required) | - |
| `--log-level` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| `--output-file` | Path to save the results (if not specified, prints to stdout) | None |
| `--format` | Output format (text or json) | json |
| `--provider` | LLM provider to use (openai or claude) | openai |

## Examples

### Process a Story with Default Settings

```bash
python main.py tests/data/story1.md
```

### Using Different Providers

With OpenAI:
```bash
python main.py tests/data/story1.md --provider openai
```

With Claude:
```bash
python main.py tests/data/story1.md --provider claude
```

### Saving Results

Save as JSON:
```bash
python main.py tests/data/story1.md --output-file results.json
```

Save as text:
```bash
python main.py tests/data/story1.md --format text --output-file results.txt
```

### Detailed Debugging

For verbose output:
```bash
python main.py tests/data/story1.md --log-level DEBUG
```

## Understanding the Output

The BCP Agent provides a comprehensive output that includes:

1. **Total BCP**: The sum of complexity points from all components.
2. **Component Breakdown**: Individual complexity points for:
   - Business Rules
   - UI Elements
   - External Integrations (Boundaries)
3. **Step Results**: Detailed information from each step in the analysis process.

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

### Understanding Step Results

1. **Story Maturity Complexity**: Assesses how well-defined the story is.
2. **Story INVEST Maturity**: Evaluates the story against INVEST principles.
3. **Break Elements**: Separates the story into Business Rules, Interface Elements, and Boundaries.
4. **External Integrations Complexity**: Calculates complexity points for integration boundaries.
5. **UI Elements Complexity**: Calculates complexity points for interface elements.
6. **Business Rules Complexity**: Calculates complexity points for business logic.

## User Story Format

For optimal results, user stories should include:

1. A clear title
2. User story in the format: "As a [role], I want [feature], so that [benefit]"
3. Acceptance criteria
4. Any additional context or technical notes

Example:
```markdown
# Add Payment Method

As a customer, I want to add a new payment method to my account so that I can use it for future purchases.

## Acceptance Criteria
- User can access the "Add Payment Method" form from account settings
- User can enter credit card details (number, expiry, CVV)
- System validates card details in real-time
- User receives confirmation when card is successfully added
- New payment method appears in the list of saved payment methods

## Technical Notes
- Integration with payment processor API required
- Need to encrypt and securely store payment information
```

## Troubleshooting

### Common Issues

- **API Key Errors**: Ensure your API keys are correctly set in the `.env` file.
- **Missing Dependencies**: Make sure you've installed all dependencies with `pip install -r requirements.txt`.
- **File Path Errors**: Use the correct path to your user story files.

### Debugging

Use the `--log-level DEBUG` flag to get detailed information about the execution process:

```bash
python main.py tests/data/story1.md --log-level DEBUG
```

## Advanced Usage

### Comparing Different Providers

You can compare results between OpenAI and Claude:

```bash
python tests/compare_providers.py tests/data/story1.md
```

### Testing Custom Prompts

If you've modified the prompt templates, you can test them:

```bash
python tests/test_providers.py --provider openai --prompt-file step1_flow_story_maturity_complexity.jinja2
```