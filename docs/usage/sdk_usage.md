# SDK Usage Guide for BCP Calculator

This guide explains how to use the BCP Calculator as a Python SDK.

## Prerequisites

Before using the SDK, make sure you have:

1. Installed the BCP Calculator package:
   ```bash
   # From the bcp-agent directory
   pip install -e .
   ```
   or
   ```bash
   pip install bcp-calculator
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your API keys for the providers you want to use (OpenAI and/or Anthropic).

## Basic Usage

### Initialize the Client

```python
from src.sdk import BCPClient

# Initialize with default settings (OpenAI provider)
client = BCPClient()

# Or initialize with specific settings
client = BCPClient(
    log_level="INFO",  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    provider="claude"  # LLM provider to use (openai or claude)
)
```

### Calculate BCP for a String

```python
# User story content as a string
story_content = """
# User Story: View Account Balance

As a bank customer, I want to view my account balance, so that I can keep track of my finances.

## Acceptance Criteria:
1. Customer can log in and see their account dashboard
2. Dashboard displays current balance for all accounts
3. Balance is updated in real-time when transactions occur
4. Customer can click on an account to view detailed transaction history
"""

# Calculate BCP
results = client.calculate(story_content)

# Access the results
print(f"Total BCP: {results['total_bcp']}")
print("Breakdown:")
for component, points in results["breakdown"].items():
    print(f"  {component}: {points}")
```

### Calculate BCP for a File

```python
# Calculate BCP for a file
file_results = client.calculate_file("path/to/user_story.md")

# Access the results
print(f"Total BCP: {file_results['total_bcp']}")
```

## Advanced Usage

### Batch Processing

```python
# Process multiple stories in a directory
batch_results = client.batch_calculate(
    stories_dir="path/to/stories",
    output_path="path/to/results.json",  # Optional: save results to file
    file_pattern="*.md"  # Optional: glob pattern for matching files
)

# Process each result
for filename, result in batch_results.items():
    print(f"\nFile: {filename}")
    print(f"Total BCP: {result['total_bcp']}")
```

### Provider Comparison

```python
# Compare results between providers
comparison = client.compare_providers(
    story_content,
    providers=["openai", "claude"]  # Optional: specify providers to compare
)

# Print the comparison
print("\nProvider Comparison:")
for provider, result in comparison.items():
    print(f"{provider}: {result['total_bcp']} BCP")
```

## Complete Example

```python
from src.sdk import BCPClient

# Initialize the client
client = BCPClient(provider="openai")

# User story
story = """
# User Story: View Account Balance

As a bank customer, I want to view my account balance, so that I can keep track of my finances.

## Acceptance Criteria:
1. Customer can log in and see their account dashboard
2. Dashboard displays current balance for all accounts
3. Balance is updated in real-time when transactions occur
4. Customer can click on an account to view detailed transaction history
"""

# Calculate BCP
results = client.calculate(story)

# Print results
print("=== CALCULATION RESULTS ===")
print(f"Total BCP: {results['total_bcp']}")
print("Breakdown:")
for component, points in results["breakdown"].items():
    print(f"  {component}: {points}")

# Compare providers
print("\n=== PROVIDER COMPARISON ===")
comparison = client.compare_providers(story)
for provider, result in comparison.items():
    print(f"{provider}: {result['total_bcp']} BCP")

# Batch processing example
try:
    print("\n=== BATCH PROCESSING ===")
    batch_results = client.batch_calculate("tests/data", "batch_results.json")
    print(f"Processed {len(batch_results)} files")
except Exception as e:
    print(f"Batch processing failed: {str(e)}")
```

## SDK Reference

### BCPClient Class

#### Constructor

```python
BCPClient(log_level="INFO", provider="openai")
```

- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `provider`: LLM provider to use (openai or claude)

#### Methods

##### calculate

```python
calculate(story_content: str) -> Dict[str, Any]
```

Calculate BCP for a user story string.

- `story_content`: The user story content
- Returns: A dictionary containing the BCP calculation results

##### calculate_file

```python
calculate_file(file_path: Union[str, Path]) -> Dict[str, Any]
```

Calculate BCP for a user story file.

- `file_path`: Path to the user story file
- Returns: A dictionary containing the BCP calculation results
- Raises: `FileNotFoundError` if the file does not exist

##### batch_calculate

```python
batch_calculate(stories_dir: Union[str, Path], output_path: Optional[Union[str, Path]] = None, file_pattern: str = "*.md") -> Dict[str, Dict[str, Any]]
```

Calculate BCP for multiple user story files in a directory.

- `stories_dir`: Directory containing user story files
- `output_path`: Optional path to save the batch results
- `file_pattern`: Glob pattern for matching story files (default: *.md)
- Returns: A dictionary mapping file names to their BCP calculation results
- Raises: `NotADirectoryError` if the directory does not exist

##### compare_providers

```python
compare_providers(story_content: str, providers: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]
```

Compare BCP calculations between different providers.

- `story_content`: The user story content
- `providers`: List of providers to compare (defaults to ["openai", "claude"])
- Returns: A dictionary mapping providers to their BCP calculation results

## Troubleshooting

### Common Issues

1. **Package Installation Issues**:
   - Ensure you are using Python 3.10 or higher
   - Verify all dependencies are installed correctly

2. **API Key Issues**:
   - Ensure the appropriate API keys are properly set in `.env`
   - Check that you have access to the LLM provider you're trying to use

3. **File Path Issues**:
   - Use absolute paths if experiencing issues with relative paths
   - Ensure files and directories exist and have the correct permissions