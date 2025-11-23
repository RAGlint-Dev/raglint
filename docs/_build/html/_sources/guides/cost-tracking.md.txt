# Cost & Latency Tracking

RAGLint automatically tracks LLM costs and latency during evaluation.

## Features

- **Automatic Cost Tracking** - Tracks token usage and calculates costs
- **Latency Metrics** - P50, P95, P99 latencies for all operations  
- **Cost Estimation** - Predict costs for larger evaluations
- **By-Operation Breakdown** - See costs per metric type

## Usage

### Automatic Tracking

Tracking happens automatically when you run an analysis:

```python
from raglint import RAGPipelineAnalyzer
from raglint.tracking import get_tracker

# Run analysis
analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(test_data)

# Get performance stats
tracker = get_tracker()
stats = tracker.get_summary()

print(f"Total cost: ${stats['cost']['total_cost_usd']:.4f}")
print(f"Avg latency: {stats['latency']['avg_latency_ms']:.2f}ms")
```

### Cost Summary

```python
cost = stats["cost"]

# Cost overview
print(f"Total cost: ${cost['total_cost_usd']:.4f}")
print(f"Input tokens: {cost['total_input_tokens']:,}")
print(f"Output tokens: {cost['total_output_tokens']:,}")
print(f"LLM calls: {cost['num_llm_calls']}")

# Cost by operation
for operation, cost_value in cost['costs_by_operation'].items():
    print(f"{operation}: ${cost_value:.4f}")
```

### Latency Summary

```python
latency = stats["latency"]

# Latency overview
print(f"Total time: {latency['total_time_seconds']:.2f}s")
print(f"Avg latency: {latency['avg_latency_ms']:.2f}ms")
print(f"P95 latency: {latency['p95_latency_ms']:.2f}ms")
print(f"P99 latency: {latency['p99_latency_ms']:.2f}ms")

# Per-operation latency
for op, op_stats in stats['operations'].items():
    print(f"{op}: avg={op_stats['avg_latency_ms']:.2f}ms")
```

### Cost Estimation

Estimate costs for larger runs:

```python
# Estimate cost for 1000 queries
estimate = tracker.estimate_cost(1000, model="gpt-3.5-turbo")

print(f"Est. cost: ${estimate['estimated_cost_usd']:.2f}")
print(f"Cost/query: ${estimate['avg_cost_per_query']:.4f}")
```

## Pricing

RAGLint tracks costs for these models:

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| gpt-4 | $0.03 | $0.06 |
| gpt-4-turbo | $0.01 | $0.03 |
| gpt-3.5-turbo | $0.0005 | $0.0015 |
| gpt-4o | $0.005 | $0.015 |
| claude-3-opus | $0.015 | $0.075 |
| claude-3-sonnet | $0.003 | $0.015 |
| claude-3-haiku | $0.00025 | $0.00125 |
| ollama (local) | $0.00 | $0.00 |

*Prices as of 2024. Check with providers for current rates.*

## Operations Tracked

RAGLint tracks performance by operation type:

- **text_generation** - General LLM calls
- **json_generation** - Structured JSON responses
- **faithfulness** - Faithfulness scoring
- **semantic_similarity** - Semantic metrics
- **context_precision** - Context relevance
- **context_recall** - Context coverage

## Reset Tracker

Reset the tracker between runs:

```python
from raglint.tracking import reset_tracker

# Reset for clean stats
reset_tracker()

# Run new analysis
results = analyzer.analyze(new_data)
```

## Example Output

```
============================================================
COST TRACKING
============================================================

💰 Total Cost: $0.0142
   Input tokens: 2,450
   Output tokens: 850
   Total tokens: 3,300
   Avg cost/call: $0.0014
   LLM calls: 10

   Costs by operation:
     - text_generation: $0.0098
     - json_generation: $0.0044

============================================================
LATENCY TRACKING
============================================================

⏱️  Total time: 12.45s
   Operations: 10
   Avg latency: 1245.00ms
   Min latency: 890.00ms
   Max latency: 2100.00ms
   P50 latency: 1200.00ms
   P95 latency: 1950.00ms
   P99 latency: 2100.00ms

   Latency by operation:
     - text_generation:
         avg: 1150.00ms
         p95: 1800.00ms
         calls: 7
     - json_generation:
         avg: 1450.00ms
         p95: 2000.00ms
         calls: 3

============================================================
COST ESTIMATION
============================================================

📊 100 queries with gpt-3.5-turbo:
   Estimated cost: $0.14
   Cost per query: $0.0014
   Estimated tokens: 33,000

📊 1,000 queries with gpt-3.5-turbo:
   Estimated cost: $1.42
   Cost per query: $0.0014
   Estimated tokens: 330,000

📊 100 queries with gpt-4:
   Estimated cost: $11.47
   Cost per query: $0.1147
   Estimated tokens: 33,000
```

## CLI Integration

View costs after a run:

```bash
# Run analysis
raglint analyze --file data.json --smart --output results.json

# View cost summary in results.json under "performance"
cat results.json | jq '.performance'
```

## Dashboard Integration

The RAGLint dashboard displays:

- Total cost per run
- Cost trends over time
- Latency distributions
- Cost breakdown by metric

**Coming soon!** (Currently tracked but not yet displayed in dashboard)

## Best Practices

### 1. Monitor Costs in Production

```python
tracker = get_tracker()
stats = tracker.get_summary()

if stats['cost']['total_cost_usd'] > BUDGET_LIMIT:
    alert("RAG evaluation cost exceeded budget!")
```

### 2. Compare Model Costs

```python
# Test with different models
estimates = {
    "gpt-3.5-turbo": tracker.estimate_cost(1000, "gpt-3.5-turbo"),
    "gpt-4": tracker.estimate_cost(1000, "gpt-4"),
    "gpt-4-turbo": tracker.estimate_cost(1000, "gpt-4-turbo"),
}

# Choose most cost-effective
for model, est in estimates.items():
    print(f"{model}: ${est['estimated_cost_usd']:.2f}")
```

### 3. Optimize for Latency

```python
# Identify slow operations
for op, stats in tracker.get_summary()['operations'].items():
    if stats['p95_latency_ms'] > 2000:  # > 2s
        print(f"⚠️  {op} is slow: {stats['p95_latency_ms']:.0f}ms")
```

### 4. Budget Planning

```python
# Weekly evaluation budget
weekly_queries = 5000
cost_estimate = tracker.estimate_cost(weekly_queries, "gpt-3.5-turbo")

monthly_cost = cost_estimate['estimated_cost_usd'] * 4
annual_cost = monthly_cost * 12

print(f"Monthly: ${monthly_cost:.2f}")
print(f"Annual: ${annual_cost:.2f}")
```

## Limitations

- Only tracks OpenAI models currently
- Ollama tracking shows $0 (local models)
- Costs are estimates based on published pricing
- Actual costs may vary slightly due to caching/batching

## See Also

- [examples/cost_tracking.py](file://../../examples/cost_tracking.py) - Complete example
- [LLM Provider Documentation](LLM.md) - Configure LLM providers
- [Dashboard Guide](DASHBOARD.md) - View metrics in web UI
