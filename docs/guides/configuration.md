# Configuration

Configure RAGLint for your use case.

## Config Class

RAGLint uses a dataclass-based configuration system:

```python
from raglint.config import Config

config = Config(
    llm_provider="openai",
    llm_model="gpt-4",
    llm_api_key="your-key",
    embedding_model="all-MiniLM-L6-v2",
    max_concurrent_tasks=5,
)
```

## Configuration Options

### LLM Provider

```python
# OpenAI
config = Config(
    llm_provider="openai",
    llm_api_key=os.getenv("OPENAI_API_KEY"),
    llm_model="gpt-3.5-turbo"  # or gpt-4, gpt-4-turbo
)

# Ollama (local)
config = Config(
    llm_provider="ollama",
    llm_model="llama2",
    ollama_base_url="http://localhost:11434"
)

# Mock (testing)
config = Config(llm_provider="mock")
```

### Embedding Model

```python
config = Config(
    embedding_model="all-MiniLM-L6-v2"  # Fast, good for most use cases
    # embedding_model="all-mpnet-base-v2"  # Slower but more accurate
)
```

### Concurrency

```python
config = Config(
    max_concurrent_tasks=10  # Process 10 items in parallel
)
```

### Environment Variables

RAGLint respects these environment variables:

- `OPENAI_API_KEY` - OpenAI API key
- `RAGLINT_DB_PATH` - Database path (default: `./raglint.db`)
- `RAGLINT_SECRET_KEY` - Dashboard secret key

## Using Config

### With Analyzer

```python
from raglint import RAGPipelineAnalyzer
from raglint.config import Config

config = Config(llm_provider="openai", llm_model="gpt-4")
analyzer = RAGPipelineAnalyzer(config=config, use_smart_metrics=True)
```

### Default Config

If no config is provided, RAGLint uses sensible defaults:

```python
analyzer = RAGPipelineAnalyzer()  # Uses default config
```

## See Also

- [API Reference](../api/config.md) - Config class documentation
- [LLM Providers](../api/llm.md) - LLM provider details
