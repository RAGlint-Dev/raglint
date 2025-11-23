# Metrics API

Built-in metric scorers.

## Faithfulness Scorer

```{eval-rst}
.. autoclass:: raglint.metrics.FaithfulnessScorer
   :members:
   :undoc-members:
   :show-inheritance:
```

## Semantic Similarity Scorer

```{eval-rst}
.. autoclass:: raglint.metrics.SemanticSimilarityScorer
   :members:
   :undoc-members:
   :show-inheritance:
```

## Context Precision Scorer

```{eval-rst}
.. autoclass:: raglint.metrics.ContextPrecisionScorer
   :members:
   :undoc-members:
   :show-inheritance:
```

## Context Recall Scorer

```{eval-rst}
.. autoclass:: raglint.metrics.ContextRecallScorer
   :members:
   :undoc-members:
   :show-inheritance:
```

## Example

```python
from raglint.metrics import (
    FaithfulnessScorer,
    SemanticSimilarityScorer,
    ContextPrecisionScorer,
    ContextRecallScorer
)
from raglint.config import Config

config = Config()

# Faithfulness
faithfulness = FaithfulnessScorer(config)
score = await faithfulness.ascore(
    query="What is Python?",
    response="Python is a programming language.",
    contexts=["Python is a high-level language."]
)

# Semantic similarity
semantic = SemanticSimilarityScorer(config)
score = await semantic.ascore(
    query="What is Python?",
    response="Python is a programming language.",
    contexts=["Python documentation"]
)
```
