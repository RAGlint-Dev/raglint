# Custom Plugins

Create custom metrics for RAGLint.

## Plugin Interface

All plugins must inherit from `PluginInterface`:

```python
from raglint.plugins.interface import PluginInterface

class MyPlugin(PluginInterface):
    def __init__(self, config):
        super().__init__(config)
        self.name = "my_metric"
        self.description = "My custom metric"
    
    async def ascore(self, query: str, response: str, contexts: list[str]) -> float:
        # Your scoring logic here
        return 0.85
    
    def score(self, query: str, response: str, contexts: list[str]) -> float:
        # Sync version (optional)
        import asyncio
        return asyncio.run(self.ascore(query, response, contexts))
```

## Built-in Plugins

RAGLint includes these built-in plugins:

### Hallucination Detector

Detects hallucinations using LLM-based fact checking:

```python
from raglint.plugins.builtins.hallucination import HallucinationDetectorPlugin

plugin = HallucinationDetectorPlugin(config)
score = await plugin.ascore(query, response, contexts)
# Returns 0-1 (lower = more hallucination)
```

### Query Difficulty

Measures query complexity:

```python
from raglint.plugins.builtins.query_difficulty import QueryDifficultyPlugin

plugin = QueryDifficultyPlugin(config)
score = await plugin.ascore(query, response, contexts)
# Returns 0-1 (higher = more difficult)
```

### Chunk Coverage

Measures how much of the context is used:

```python
from raglint.plugins.builtins.chunk_coverage import ChunkCoveragePlugin

plugin = ChunkCoveragePlugin(config)
score = await plugin.ascore(query, response, contexts)
# Returns 0-1 (ratio of chunks used)
```

## Loading Plugins

### Automatic Discovery

Place plugins in `~/.raglint/plugins/`:

```bash
~/.raglint/plugins/
  my_plugin.py
  another_plugin.py
```

RAGLint will auto-load them on startup.

### Manual Loading

```python
from raglint.plugins.loader import PluginLoader

loader = PluginLoader(config)
plugins = loader.load_all_plugins()

for plugin in plugins:
    score = await plugin.ascore(query, response, contexts)
```

## Example: Sentiment Plugin

```python
from raglint.plugins.interface import PluginInterface
from textblob import TextBlob

class SentimentPlugin(PluginInterface):
    def __init__(self, config):
        super().__init__(config)
        self.name = "sentiment"
        self.description = "Sentiment analysis of response"
    
    async def ascore(self, query: str, response: str, contexts: list[str]) -> float:
        blob = TextBlob(response)
        sentiment = blob.sentiment.polarity  # -1 to 1
        return (sentiment + 1) / 2  # Normalize to 0-1
```

## See Also

- [API Reference](../api/plugins.md) - Plugin API documentation
- [Built-in Plugins](../api/plugins.md#built-in-plugins) - All built-in plugins
