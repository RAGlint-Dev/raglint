# RAGLint Plugin System

RAGLint features a powerful plugin system that allows you to extend its functionality with custom LLM providers, evaluation metrics, and more.

## Using Plugins

### Built-in Plugins
RAGLint comes with several built-in plugins for advanced metrics:
- `chunk_coverage`: Measures how much of the retrieved context is relevant.
- `query_difficulty`: Estimates the complexity of the user query.
- `hallucination_score`: Detects potential hallucinations in the answer.

These are enabled automatically when you run `raglint analyze`.

### Listing Plugins
To see all available plugins (both built-in and installed):

```bash
raglint plugins list
```

## Creating Custom Plugins

You can create your own plugins by implementing the interfaces defined in `raglint.plugins.interface`.

### 1. Create a Plugin File
Create a Python file (e.g., `my_plugins.py`) and define your plugin class.

#### Example: Custom Metric
```python
from raglint.plugins.interface import MetricPlugin

class PolitenessMetric(MetricPlugin):
    @property
    def name(self) -> str:
        return "politeness"

    @property
    def description(self) -> str:
        return "Checks if the response is polite."

    @property
    def metric_type(self) -> str:
        return "generation"

    def score(self, **kwargs) -> float:
        response = kwargs.get("response", "").lower()
        if "please" in response or "thank you" in response:
            return 1.0
        return 0.0
```

#### Example: Custom LLM
```python
from raglint.plugins.interface import LLMPlugin

class MyLLM(LLMPlugin):
    @property
    def name(self) -> str:
        return "my_llm"
        
    def generate(self, prompt: str) -> str:
        return "Custom response"
        
    async def agenerate(self, prompt: str) -> str:
        return "Custom async response"
```

### 2. Loading Plugins

#### Option A: Local Directory
Place your plugin file in a `plugins/` directory in your project root. RAGLint loads from here by default.
You can also specify a custom directory:
```bash
raglint plugins list --plugins-dir ./my-custom-plugins
```

#### Option B: Python Package (Entry Points)
If you are packaging your plugin as a library, use `entry_points` in your `pyproject.toml`:

```toml
[project.entry-points."raglint.plugins"]
my_metric = "my_package.metrics:PolitenessMetric"
```

## Integration

- **Metrics**: Custom metric plugins are automatically executed during `raglint analyze`.
- **LLMs**: To use a custom LLM plugin, set the `provider` field in your config to the plugin's name:
  ```yaml
  llm:
    provider: my_llm
  ```
