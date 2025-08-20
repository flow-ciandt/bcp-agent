# BCP Calculator - Claude Code Assistant Guide

## Project Overview

The BCP Calculator is a command-line tool that analyzes user stories and calculates Business Complexity Points (BCP) using LangChain with support for multiple LLM providers (OpenAI GPT-4o-2024-05-13 and Anthropic Claude). This application orchestrates a 6-step prompt flow to evaluate story complexity across three dimensions: Business Rules, Interface Elements, and Boundaries.

The tool also provides functionality to compare results between different LLM providers, generating detailed comparison reports and visualizations to help evaluate differences in BCP calculations.

## Architecture

### Core Components
- **main.py**: Entry point wrapper for the CLI application
- **run_comparison.py**: Wrapper script for running provider comparisons
- **src/main.py**: Main CLI implementation with argument parsing
- **src/bcp/bcp_calculator.py**: Core orchestration logic for the 6-step flow
- **src/bcp/prompt_handler.py**: Manages loading and processing prompt templates
- **src/bcp/llm_providers.py**: Provider abstraction for different LLM services
- **src/bcp/logger.py**: Custom logging functionality
- **src/bcp/prompts/**: Directory containing step1-step6 prompt templates
- **tests/compare_providers.py**: Tool for comparing BCP results between different providers
- **tests/data/**: Directory containing sample user stories for testing

### Flow Structure
1. **Step 1**: Story Maturity Complexity (complementary analysis)
2. **Step 2**: Story INVEST Maturity (complementary analysis)
3. **Step 3**: Break Elements (separates story into Business Rules, Interface Elements, Boundaries)
4. **Step 4**: Boundaries Complexity (calculates complexity points)
5. **Step 5**: Interface Elements Complexity (calculates complexity points)
6. **Step 6**: Business Rules Complexity (calculates complexity points)

## Technology Stack
- **Python**: Primary programming language
- **LangChain**: LLM orchestration framework
- **OpenAI GPT-4o-2024-05-13**: Language model for analysis (default provider)
- **Anthropic Claude**: Alternative language model provider
- **Pandas**: Data manipulation and analysis for provider comparisons
- **Matplotlib**: Visualization library for comparison reports
- **Environment Variables**: Configuration management

## Common Tasks

### Running the Application
```bash
python main.py path/to/user_story.md --log-level DEBUG --output-file results.txt
```

### Running Provider Comparisons
Compare BCP calculations between OpenAI and Claude using the provider comparison tool:
```bash
python run_comparison.py --stories-dir tests/data --output-dir tests/results --format excel
```

Available options:
- `--stories-dir`: Directory containing user story files (default: tests/data)
- `--output-dir`: Directory to save results (default: tests/results)
- `--log-level`: Set the logging level (default: INFO)
- `--format`: Output format for comparison (json, csv, or excel) (default: excel)

### Testing
The application includes test data in the `tests/data/` directory with sample user stories.

### Environment Setup
1. Copy `.env.example` to `.env`
2. Add your API keys (OpenAI and/or Anthropic) to the `.env` file
3. Install dependencies: `pip install -r requirements.txt`

## Development Notes

### Key Design Patterns
- Sequential step execution with dependency between steps
- Structured output parsing from LLM responses
- Comprehensive logging for debugging and monitoring
- File-based input/output for user stories and results

### Error Handling
The application should handle:
- Invalid user story formats
- API rate limits and failures
- Missing or malformed prompt templates
- File I/O errors

### Performance Considerations
- Steps 1-2 are complementary analysis (validation)
- Steps 4-6 calculate actual complexity points that get summed
- Step 3 is critical as it breaks down the story for subsequent steps

## Troubleshooting

### Common Issues
- **API Key Issues**: Ensure the appropriate API keys are properly set in `.env`
- **Missing Dependencies**: Run `pip install -r requirements.txt`
- **File Path Errors**: Use absolute paths for user story files
- **Logging**: Use `--log-level DEBUG` for detailed execution info

### Output Validation
The final output should include:
- Results from each of the 6 steps
- Individual complexity points from steps 4-6
- Total BCP (sum of steps 4-6)
- Breakdown by component type

#### Provider Comparison Reports
When using the provider comparison functionality, reports include:
- Raw comparison data for each story processed with each provider
- Pivot tables comparing results between providers
- Difference analysis showing absolute and percentage differences
- Visualizations (when using excel format):
  - Total BCP comparison charts
  - Processing time comparison
  - Component breakdown averages

## Code Conventions
- Follow Python PEP 8 style guidelines
- Use descriptive variable names for step results
- Implement proper error handling for each step
- Maintain comprehensive logging throughout the flow