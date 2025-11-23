# RAGlint Custom Plugin Examples

This directory contains example custom plugins that demonstrate how to extend RAGlint with your own metrics.

## Available Example Plugins

### 1. Answer Completeness (`answer_completeness.py`)
**Purpose**: Evaluates whether answers fully address all parts of multi-part questions

**Use Case**: Customer support, FAQ systems

**Example**:
```
Query: "What's the price and warranty?"
✅ Complete: "Price is $299. Warranty is 2 years."
❌ Incomplete: "Price is $299." (missing warranty info)
```

**Score**: 0.0 (incomplete) to 1.0 (fully complete)

---

### 2. Response Latency Tracker (`latency_tracker.py`)
**Purpose**: Tracks response generation latency and identifies performance bottlenecks

** Use Case**: Production monitoring, optimization

**Metrics**:
- Total latency
- Retrieval vs generation time
- P90/P99 percentiles
- Performance recommendations

**Example Output**:
```
Total: 2500ms
Retrieval: 70% (1750ms) ⚠️
Generation: 30% (750ms) ✅
Recommendation: Optimize vector search or reduce top-k
```

---

## Using Custom Plugins

### Installation

1. **Copy plugin to your project**:
```bash
cp examples/plugins/answer_completeness.py my_project/plugins/
```

2. **Import and use**:
```python
from my_project.plugins.answer_completeness import AnswerCompletenessPlugin

plugin = AnswerCompletenessPlugin()
result = await plugin.calculate_async(
    query="What's the price and warranty?",
    response="Price is $299.",
    contexts=["Product costs $299", "2-year warranty"]
)

print(f"Completeness: {result['score']}")
print(f"Missing: {result['missing_components']}")
```

### Registering Plugins

To use plugins with RAGlint CLI, register them in `pyproject.toml`:

```toml
[project.entry-points."raglint.plugins"]
answer_completeness = "my_project.plugins.answer_completeness:AnswerCompletenessPlugin"
latency_tracker = "my_project.plugins.latency_tracker:ResponseLatencyPlugin"
```

Then use via CLI:
```bash
raglint analyze data.json --smart --plugins answer_completeness,latency_tracker
```

---

## Creating Your Own Plugin

### 1. Subclass `PluginInterface`

```python
from raglint.plugins.interface import PluginInterface

class MyCustomPlugin(PluginInterface):
    name = "my_metric"
    version = "1.0.0"
    description = "My custom evaluation metric"
    
    async def calculate_async(self, query, response, contexts, **kwargs):
        # Your logic here
        score = self._calculate_score(query, response)
        
        return {
            "score": score,
            "reasoning": "Why this score",
        }
```

### 2. Implement `calculate_async`

**Required Parameters**:
- `query` (str): The input query
- `response` (str): The generated response
- `contexts` (list): Retrieved context chunks

**Optional Parameters**:
- `ground_truth` (str): Expected answer (if available)
- `metadata` (dict): Additional data (timestamps, etc.)

**Return Value**:
Must return a dict with at least:
```python
{
    "score": float,  # 0.0 to 1.0 (or any range)
    # Additional fields as needed
}
```

### 3. Test Your Plugin

```python
import asyncio

async def test():
    plugin = MyCustomPlugin()
    result = await plugin.calculate_async(
        query="test query",
        response="test response",
        contexts=["context1", "context2"]
    )
    print(result)

asyncio.run(test())
```

---

## Plugin Ideas

Here are more plugin ideas you could implement:

1. **Citation Accuracy**: Check if responses properly cite sources
2. **Bias Detector**: Detect potential bias in responses
3. **Readability Scorer**: Measure readability (Flesch-Kincaid, etc.)
4. **Multilingual Support**: Evaluate non-English responses
5. **Sentiment Analyzer**: Track sentiment in support conversations
6. **Fact Checker**: Verify facts against knowledge base
7. **Topic Classifier**: Classify query topics
8. **Response Length Validator**: Enforce min/max lengths
9. **Profanity Filter**: Detect inappropriate content
10. **Compliance Checker**: Ensure regulatory compliance

---

## Best Practices

### 1. Keep Plugins Focused
Each plugin should do one thing well. Don't combine multiple metrics in one plugin.

### 2. Handle Errors Gracefully
```python
try:
    score = complex_calculation()
except Exception as e:
    return {"score": 0.0, "error": str(e)}
```

### 3. Provide Reasoning
Always include a "reasoning" field explaining the score:
```python
return {
    "score": 0.7,
    "reasoning": "Answer addresses 2 of 3 query components"
}
```

### 4. Use Async Properly
If making API calls or I/O operations, use `await`:
```python
async def calculate_async(self, ...):
    result = await external_api_call()
    return {"score": result.score}
```

### 5. Document Your Plugin
Include docstrings explaining:
- What the plugin measures
- Score interpretation (0.0 = worst, 1.0 = best)
- Use cases
- Example usage

---

## Contributing Plugins

Want to share your plugin with the community?

1. Fork the RAGlint repository
2. Add your plugin to  `raglint/plugins/builtins/`
3. Add tests to `tests/test_builtin_plugins.py`
4. Submit a pull request

**Community plugins welcome!** 🎉

---

## Resources

- [Plugin Interface Documentation](../../docs/PLUGINS.md)
- [Built-in Plugins](../../raglint/plugins/builtins/)
- [Plugin Tests](../../tests/test_builtin_plugins.py)

---

**Questions?** Open an issue on GitHub or join our Discord community!
