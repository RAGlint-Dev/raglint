# Troubleshooting Guide

Common issues and solutions when using RAGLint.

## Installation Issues

### ImportError: No module named 'raglint'

**Problem**: Package not installed or wrong Python environment.

**Solution**:
```bash
# Check if installed
pip list | grep raglint

# Install if missing
pip install raglint

# Or install from source
pip install -e .

# Verify installation
python -c "import raglint; print(raglint.__version__)"
```

### ModuleNotFoundError: sentence_transformers

**Problem**: Missing optional dependencies.

**Solution**:
```bash
# Install all dependencies
pip install -e ".[dev]"

# Or install missing package
pip install sentence-transformers
```

## Runtime Issues

### "Error: Invalid JSON in input file"

**Problem**: Malformed JSON file.

**Solution**:
```bash
# Validate JSON
python -m json.tool data.json

# Check file encoding
file data.json  # Should be UTF-8 text

# Fix common issues:
# - Remove trailing commas
# - Ensure double quotes (not single)
# - Check for special characters
```

### "OpenAI API Error: 401 Unauthorized"

**Problem**: Invalid or missing API key.

**Solution**:
```bash
# Check API key in config
cat raglint.yml

# Or set environment variable
export OPENAI_API_KEY="sk-..."

# Verify key is valid at https://platform.openai.com/api-keys
```

### "Mock mode warning" when using --smart

**Problem**: LLM provider not configured.

**Solution**:
```yaml
# Create raglint.yml
provider: openai
openai_api_key: "sk-..."
model_name: gpt-4
```

Or:
```bash
raglint analyze data.json --smart --api-key sk-...
```

### Slow analysis with smart metrics

**Problem**: Sequential processing.

**Solution**:
```python
# RAGLint auto-uses async for 5+ items
# But you can force it:
import asyncio
results = asyncio.run(analyzer.analyze_async(data, show_progress=True))

# Or increase dataset size to trigger async
```

## Data Format Issues

### "Error: Input data must be a list"

**Problem**: Wrong data structure.

**Solution**:
```json
// ❌ Wrong
{
  "query": "What is RAG?"
}

// ✅ Correct
[
  {
    "query": "What is RAG?",
    "retrieved_contexts": ["..."],
    "ground_truth_contexts": ["..."],
    "response": "..."
  }
]
```

### Missing required fields

**Problem**: Data missing required fields.

**Required fields**:
- `query` (string)
- `retrieved_contexts` (list of strings)
- `response` (string) - for smart metrics
- `ground_truth_contexts` (list of strings) - for retrieval metrics

**Solution**:
```python
# Validate your data
data = [
    {
        "query": "Your query",
        "retrieved_contexts": ["Context 1", "Context 2"],
        "ground_truth_contexts": ["Truth 1"],  # Optional
        "response": "AI response"  # Optional
    }
]
```

### Empty contexts or responses

**Problem**: Empty lists or strings.

**Expected**:
- `retrieved_contexts`: Should have at least 1 context
- `ground_truth_contexts`: Can be empty (skips retrieval metrics)
- `response`: Can be empty (skips faithfulness)

**Solution**:
```python
# Handle missing data gracefully
if not data_item.get("response"):
    # RAGLint will skip faithfulness scoring
    pass
```

## Configuration Issues

### "Config file not found"

**Problem**: No `raglint.yml` in current directory.

**Solution**:
```bash
# Create basic config
cat > raglint.yml << EOF
provider: mock
metrics:
  chunking: true
  retrieval: true
  semantic: true
  faithfulness: true
EOF

# Or specify custom path
raglint analyze data.json --config /path/to/config.yml
```

### Custom prompts not working

**Problem**: Prompt template syntax error.

**Solution**:
```yaml
# Correct template syntax
prompts:
  faithfulness: |
    Query: {query}
    Context: {context}
    Response: {response}
    
    Evaluate faithfulness...

# Available variables:
# - {query}
# - {context}
# - {response}
```

## Performance Issues

### High memory usage

**Problem**: Processing very large datasets.

**Solution**:
```python
# Process in batches
batch_size = 100
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    results = analyzer.analyze(batch)
    # Save results
```

### Timeout errors with LLM

**Problem**: LLM taking too long.

**Solution**:
```python
# Switch to faster model
config = {"provider": "openai", "model_name": "gpt-3.5-turbo"}  # Faster than gpt-4

# Or use Ollama locally
config = {"provider": "ollama", "model_name": "llama3"}

# Or increase timeout (future feature)
```

## Testing Issues

### Tests fail due to missing dependencies

**Problem**: Dev dependencies not installed.

**Solution**:
```bash
pip install -e ".[dev]"
```

### Coverage too low

**Problem**: Not all code paths tested.

**Solution**:
```bash
# See coverage report
pytest --cov=raglint --cov-report=html
open htmlcov/index.html

# Focus on untested modules
pytest --cov=raglint --cov-report=term-missing
```

### Async tests fail

**Problem**: Missing pytest-asyncio.

**Solution**:
```bash
pip install pytest-asyncio

# Verify
pytest tests/test_async.py -v
```

## CLI Issues

### Command not found: raglint

**Problem**: Script not in PATH.

**Solution**:
```bash
# Reinstall package
pip install -e .

# Or run directly
python -m raglint.cli analyze data.json

# Check installation
which raglint
```

### Exit code always 0

**Problem**: Using old version without proper error handling.

**Solution**:
```bash
# Update to latest version
pip install --upgrade raglint

# Verify error codes work
raglint analyze nonexistent.json
echo $?  # Should be 1
```

## Common Error Messages

### "Error during analysis: ..."

**Cause**: Generic error, check logs.

**Solution**:
```bash
# Run with verbose logging
raglint analyze data.json --verbose --log-file debug.log

# Check log file
cat debug.log
```

### "Coverage failure: total of X is less than fail-under=Y"

**Cause**: Test coverage below threshold.

**Solution**:
```bash
# Lower threshold temporarily
pytest --cov-fail-under=70

# Or add more tests
```

## Getting Help

### Still stuck?

1. **Check documentation**:
   - [API.md](API.md) - Complete API reference
   - [CONTRIBUTING.md](../CONTRIBUTING.md) - Development guide
   - [README.md](../README.md) - Usage examples

2. **Search existing issues**:
   - https://github.com/yourusername/raglint/issues

3. **Create an issue**:
   - Include error message
   - Provide minimal code example
   - Share your configuration
   - Specify Python version and OS

4. **Enable debug logging**:
   ```bash
   raglint analyze data.json --verbose --log-file debug.log
   ```
   
   Include `debug.log` in your issue.

## Tips for Success

✅ **Do**:
- Use virtual environments
- Keep dependencies updated
- Validate JSON before processing
- Start with mock mode for testing
- Read error messages carefully
- Check logs with --verbose

❌ **Don't**:
- Mix Python versions
- Ignore warnings
- Skip dependency installation
- Use global pip install
- Hardcode API keys in code
