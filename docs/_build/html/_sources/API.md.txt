# RAGlint API Reference

## Complete API Documentation

### Core Classes

#### RAGPipelineAnalyzer

Main analyzer for RAG pipeline evaluation.

```python
from raglint import RAGPipelineAnalyzer

analyzer = RAGPipelineAnalyzer(
    use_smart_metrics: bool = False,
    llm: Optional[LLM] = None,
    plugins: Optional[List[PluginInterface]] = None
)
```

**Parameters:**
- `use_smart_metrics` (bool): Enable LLM-powered metrics. Default: False
- `llm` (Optional[LLM]): Custom LLM instance. If None, uses MockLLM or OpenAI
- `plugins` (Optional[List[PluginInterface]]): Custom plugins to use

**Methods:**

##### analyze_async()
```python
async def analyze_async(
    data: List[Dict[str, Any]],
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]
```

Asynchronously analyze RAG pipeline data.

**Parameters:**
- `data`: List of test cases, each with keys:
  - `query` (str): User query
  - `retrieved_contexts` (List[str]): Retrieved context chunks
  - `response` (str): Generated response
  - `ground_truth` (Optional[str]): Expected answer
- `progress_callback` (Optional[Callable]): Callback for progress updates

**Returns:**
Dict with scores and metrics:
```python
{
    "faithfulness_score": float,  # 0.0-1.0
    "metrics": {
        "context_relevance": float,
        "answer_relevance": float,
        "semantic_similarity": float,
        # ... plugin metrics
    },
    "details": List[Dict],  # Per-query results
    "summary": Dict  # Aggregate statistics
}
```

**Example:**
```python
import asyncio
from raglint import RAGPipelineAnalyzer

async def main():
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    
    data = [
        {
            "query": "What is the return policy?",
            "retrieved_contexts": ["30-day money-back guarantee..."],
            "response": "You can return items within 30 days.",
            "ground_truth": "30-day return policy"
        }
    ]
    
    results = await analyzer.analyze_async(data)
    print(f"Faithfulness: {results['faithfulness_score']}")

asyncio.run(main())
```

---

### Plugin System

#### PluginInterface

Base class for creating custom plugins.

```python
from raglint.plugins.interface import PluginInterface
from typing import Dict, Any, List

class MyPlugin(PluginInterface):
    name = "my_plugin"
    version = "1.0.0"
    description = "My custom plugin"
    
    async def calculate_async(
        self,
        query: str,
        response: str,
        contexts: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        # Your logic here
        return {
            "score": 0.85,
            "details": {...}
        }
```

**Required Attributes:**
- `name` (str): Unique plugin identifier
- `version` (str): Semantic version
- `description` (str): Brief description

**Required Methods:**
- `calculate_async()`: Async evaluation method

**Returns:**
Must return dict with at least:
- `score` (float): Metric score (typically 0.0-1.0)
- Optional: Any additional details

---

### Built-in Plugins (15 Total)

#### Core Plugins

##### HallucinationPlugin
Detects hallucinations in generated responses.

```python
from raglint.plugins.builtins import HallucinationPlugin

plugin = HallucinationPlugin(llm=None)
result = await plugin.calculate_async(
    query="What is X?",
    response="X is Y",
    contexts=["X is actually Y"]
)
# Returns: {"score": 0.95, "hallucination_detected": False}
```

##### ChunkCoveragePlugin
Analyzes chunk size and coverage effectiveness.

```python
from raglint.plugins.builtins import ChunkCoveragePlugin

plugin = ChunkCoveragePlugin()
result = await plugin.calculate_async(
    query="...",
    response="...",
    contexts=["chunk1", "chunk2"]
)
# Returns: {"score": 0.85, "coverage_ratio": 0.75}
```

##### QueryDifficultyPlugin
Assesses query complexity.

```python
from raglint.plugins.builtins import QueryDifficultyPlugin

plugin = QueryDifficultyPlugin()
result = await plugin.calculate_async(
    query="What is the meaning of life?",
    response="...",
    contexts=[]
)
# Returns: {"score": 0.8, "difficulty": "hard"}
```

#### Quality & Readability

##### ReadabilityPlugin
Calculates readability scores (Flesch, FK Grade, SMOG).

```python
from raglint.plugins.builtins import ReadabilityPlugin

plugin = ReadabilityPlugin()
result = await plugin.calculate_async(
    query="",
    response="The product is easy to use.",
    contexts=[]
)
# Returns: {
#     "flesch_reading_ease": 85.0,
#     "flesch_kincaid_grade": 4.2,
#     "readability_interpretation": "Easy (6th grade)"
# }
```

##### CompletenessPlugin
Evaluates if responses address all query components.

```python
from raglint.plugins.builtins import CompletenessPlugin

plugin = CompletenessPlugin(llm=None)
result = await plugin.calculate_async(
    query="What's the price, warranty, and shipping?",
    response="Price is $99 with 1-year warranty.",
    contexts=[]
)
# Returns: {
#     "score": 0.67,  # 2/3 components addressed
#     "missing_components": ["shipping"]
# }
```

##### ConcisenessPlugin
Detects verbosity and redundancy.

```python
from raglint.plugins.builtins import ConcisenessPlugin

plugin = ConcisenessPlugin()
result = await plugin.calculate_async(
    query="",
    response="Well, basically, to be honest...",
    contexts=[]
)
# Returns: {
#     "score": 0.4,
#     "filler_words": 3,
#     "verbosity_level": "Verbose"
# }
```

##### ResponseDiversityPlugin
Measures linguistic diversity.

```python
from raglint.plugins.builtins import ResponseDiversityPlugin

plugin = ResponseDiversityPlugin()
result = await plugin.calculate_async(
    query="",
    response="The product is good. It's very good.",
    contexts=[]
)
# Returns: {
#     "score": 0.5,
#     "repetition_detected": True,
#     "lexical_diversity": 0.6
# }
```

#### Security & Compliance

##### PIIDetectorPlugin
Detects personally identifiable information.

```python
from raglint.plugins.builtins import PIIDetectorPlugin

plugin = PIIDetectorPlugin()
result = await plugin.calculate_async(
    query="",
    response="Contact john@example.com or 555-1234",
    contexts=[]
)
# Returns: {
#     "score": 0.6,  # PII found
#     "pii_types": {"email": 1, "phone_us": 1},
#     "risk_level": "low"
# }
```

##### SQLInjectionDetectorPlugin
Identifies SQL injection patterns.

```python
from raglint.plugins.builtins import SQLInjectionDetectorPlugin

plugin = SQLInjectionDetectorPlugin()
result = await plugin.calculate_async(
    query="",
    response="SELECT * FROM users WHERE id=1",
    contexts=[]
)
# Returns: {
#     "score": 0.3,
#     "sql_patterns_found": True,
#     "risk_level": "high"
# }
```

##### BiasDetectorPlugin
Detects bias in responses.

```python
from raglint.plugins.builtins import BiasDetectorPlugin

plugin = BiasDetectorPlugin()
result = await plugin.calculate_async(
    query="",
    response="The chairman will meet with businessmen.",
    contexts=[]
)
# Returns: {
#     "score": 0.7,
#     "bias_level": "Low",
#     "issues_found": ["Gendered term: 'chairman'"]
# }
```

##### CitationAccuracyPlugin
Verifies citation presence and format.

```python
from raglint.plugins.builtins import CitationAccuracyPlugin

plugin = CitationAccuracyPlugin(llm=None)
result = await plugin.calculate_async(
    query="",
    response="According to Section 5.2 [1], the policy is...",
    contexts=[]
)
# Returns: {
#     "score": 0.95,
#     "citation_count": 2,
#     "coverage_percent": 100
# }
```

#### Advanced Analytics

##### MultilingualSupportPlugin
Checks language consistency and encoding.

```python
from raglint.plugins.builtins import MultilingualSupportPlugin

plugin = MultilingualSupportPlugin()
result = await plugin.calculate_async(
    query="天气怎么样？",  # Chinese
    response="今天天气晴朗。",  # Chinese
    contexts=[]
)
# Returns: {
#     "score": 1.0,
#     "is_consistent": True,
#     "query_languages": ["chinese"],
#     "response_languages": ["chinese"]
# }
```

##### HallucinationConfidencePlugin
Multi-signal confidence scoring.

```python
from raglint.plugins.builtins import HallucinationConfidencePlugin

plugin = HallucinationConfidencePlugin()
result = await plugin.calculate_async(
    query="",
    response="According to the manual, the price is $299.",
    contexts=["The manual states price is $299"]
)
# Returns: {
#     "score": 0.9,
#     "confidence_level": "very high",
#     "hallucination_risk": "low"
# }
```

##### ContextCompressionPlugin
Analyzes context efficiency.

```python
from raglint.plugins.builtins import ContextCompressionPlugin

plugin = ContextCompressionPlugin()
result = await plugin.calculate_async(
    query="",
    response="The price is $99.",
    contexts=["Price: $99", "The price is $99", "Cost is $99"]
)
# Returns: {
#     "score": 0.6,
#     "redundancy_ratio": 0.7,
#     "potential_token_savings": 25
# }
```

##### UserIntentPlugin
Classifies query intent and validates alignment.

```python
from raglint.plugins.builtins import UserIntentPlugin

plugin = UserIntentPlugin()
result = await plugin.calculate_async(
    query="How do I reset my password?",
    response="1. Click Forgot Password 2. Enter email",
    contexts=[]
)
# Returns: {
#     "score": 0.95,
#     "detected_intent": "instructional",
#     "alignment_quality": "excellent"
# }
```

---

### Dashboard API

#### Starting the Dashboard

```python
# Command line
raglint dashboard --port 8000 --host localhost

# Or programmatically
from raglint.dashboard import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### API Endpoints

##### POST /api/analyze
Analyze RAG data via API.

**Request:**
```json
{
  "test_data": [
    {
      "query": "What is X?",
      "retrieved_contexts": ["X is Y"],
      "response": "X is Y",
      "ground_truth": "X is Y"
    }
  ],
  "use_smart_metrics": false
}
```

**Response:**
```json
{
  "run_id": "uuid",
  "faithfulness_score": 0.95,
  "metrics": {...},
  "timestamp": "2024-01-01T00:00:00"
}
```

##### GET /api/runs
Get all analysis runs.

**Response:**
```json
[
  {
    "id": "uuid",
    "timestamp": "2024-01-01T00:00:00",
    "faithfulness_score": 0.95
  }
]
```

##### GET /api/runs/{run_id}
Get specific run details.

---

### Configuration

#### Config File (raglint.yml)

```yaml
llm:
  provider: "openai"  # or "anthropic", "mock"
  model: "gpt-4"
  api_key: "${OPENAI_API_KEY}"  # Or set directly

metrics:
  use_smart: false
  plugins:
    - hallucination
    - readability
    - pii_detector

thresholds:
  faithfulness: 0.85
  context_relevance: 0.70
  answer_relevance: 0.75

output:
  format: "html"  # or "json", "both"
  directory: "./reports"
```

#### Loading Config

```python
from raglint.config import load_config

config = load_config("raglint.yml")
analyzer = RAGPipelineAnalyzer(**config.to_analyzer_kwargs())
```

---

### CLI Reference

```bash
# Initialize config
raglint init

# Analyze data
raglint analyze data.json --smart --output results.html

# Start dashboard
raglint dashboard --port 8000

# Run benchmarks
raglint benchmark --compare ragas

# Generate report
raglint report --run-id <uuid> --format pdf
```

---

### Error Handling

```python
from raglint.exceptions import RAGLintError, ValidationError

try:
    results = await analyzer.analyze_async(data)
except ValidationError as e:
    print(f"Invalid data: {e}")
except RAGLintError as e:
    print(f"Analysis error: {e}")
```

---

### Type Hints

All public APIs are fully typed:

```python
from typing import List, Dict, Any, Optional
from raglint import RAGPipelineAnalyzer

analyzer: RAGPipelineAnalyzer = RAGPipelineAnalyzer()
data: List[Dict[str, Any]] = [...]
results: Dict[str, Any] = await analyzer.analyze_async(data)
```

---

## Complete Example

```python
import asyncio
from raglint import RAGPipelineAnalyzer
from raglint.plugins.builtins import (
    ReadabilityPlugin,
    PIIDetectorPlugin,
    BiasDetectorPlugin
)

async def comprehensive_analysis():
    # Create analyzer with custom plugins
    analyzer = RAGPipelineAnalyzer(
        use_smart_metrics=True,
        plugins=[
            ReadabilityPlugin(),
            PIIDetectorPlugin(),
            BiasDetectorPlugin()
        ]
    )
    
    # Prepare test data
    data = [
        {
            "query": "What's the return policy?",
            "retrieved_contexts": [
                "30-day money-back guarantee",
                "Items must be in original condition"
            ],
            "response": "You can return items within 30 days for a full refund.",
            "ground_truth": "30-day return policy with refund"
        }
    ]
    
    # Run analysis
    results = await analyzer.analyze_async(
        data,
        progress_callback=lambda p: print(f"Progress: {p}%")
    )
    
    # Check results
    print(f"Faithfulness: {results['faithfulness_score']}")
    print(f"Readability: {results['metrics']['readability']}")
    print(f"PII Risk: {results['metrics']['pii_detector']}")
    
    # Check thresholds
    if results['faithfulness_score'] < 0.85:
        print("⚠️ Low faithfulness - possible hallucination!")
    
    return results

# Run
results = asyncio.run(comprehensive_analysis())
```

---

**For more examples, see:**
- [Basic Usage](../examples/basic_usage.py)
- [Advanced Usage](../examples/advanced_usage.py)
- [Plugin Development](../examples/plugins/README.md)
- [LangChain Integration](../examples/langchain_integration.py)
