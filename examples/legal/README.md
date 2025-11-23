# Legal Document Analysis - RAGlint Example

## Overview

Evaluating a RAG system for legal contract Q&A. This is a high-stakes use case where accuracy is critical - incorrect answers could have legal implications.

## Use Case

**Scenario**: Law firm using RAG to help associates quickly find information in employment contracts  
**Critical Requirement**: **100% accuracy** - No hallucinations allowed  
**Challenge**: Legal language is complex and precise; small errors matter

## Dataset

`contract_qa.json` contains 5 employment contract questions:
- Termination grounds and procedures
- Intellectual property rights
- Non-compete clauses
- Contract modification rules
- Overtime/compensation policies

## Running the Analysis

```bash
cd examples/legal
export OPENAI_API_KEY="your-key-here"
raglint analyze contract_qa.json --smart --output-dir=results/
```

## Critical Metrics for Legal

### 1. Faithfulness (CRITICAL)
**Target**: **> 0.95** (Higher than other use cases!)

In legal contexts, even small hallucinations are dangerous:
- Stating wrong clause numbers
- Inventing terms that don't exist
- Misrepresenting durations (12 months vs 18 months)

**Zero tolerance for hallucinations.**

### 2. Citation Accuracy (Custom Metric)
**Target**: > 0.98

Every answer should cite the exact section:
- ✅ "Section 8.2: Termination for cause includes..."
- ❌ "The contract says you can be terminated for misconduct"

**Recommendation**: Add custom citation plugin.

### 3. Precision over Recall
**Better to say**: "I don't have that information, let me connect you with an attorney"  
**Than to say**: Incorrect or incomplete legal information

## Common Issues

### Issue 1: Paraphrasing Changes Meaning

**Problem**: Legal language is precise; paraphrasing can change legal meaning

**Example**:
```
Contract: "Employee agrees not to solicit... for eighteen (18) months"
❌ Bad Answer: "You can't contact clients for about a year and a half"
✅ Good Answer: "Non-solicitation period is eighteen (18) months as stated in Section 7.2"
```

**Fix**: Use direct quotes when possible, cite exact sections

### Issue 2: Missing Conditions or Exceptions

**Problem**: Legal clauses often have exceptions; missing them is dangerous

**Example**:
```
Query: "Can the company fire me?"
Contract: "...may terminate for cause...or without cause with 60 days notice..."

❌ Incomplete: "Yes, the company can terminate you"
✅ Complete: "Yes, either for cause (immediate) or without cause with 60 days written notice (Section 8.2-8.3)"
```

**Fix**: Use completeness plugin to verify all conditions are mentioned

### Issue 3: Not Disclaiming Legal Advice

**Problem**: RAG system answers should not constitute legal advice

**Fix**: Always append disclaimer:
```
"This is general information from the contract. For legal advice specific to your situation, consult an attorney."
```

## Optimization for Legal Use Cases

### 1. Larger Chunks
Legal clauses often span multiple paragraphs. Use larger chunks (1024-2048 tokens) to capture full context.

```python
# Don't chunk mid-section
chunks = chunk_by_section(contract, section_headers=['Section', 'Article'])
```

### 2. Exact Matching + Semantic Search
Combine BM25 (exact word matching) with vector search:
```python
# Hybrid search
bm25_results = bm25_search(query, chunks)
vector_results = vector_search(query, chunks)
combined = combine_results(bm25_results, vector_results, weights=[0.6, 0.4])
```

### 3. Citation Extraction
Extract section numbers automatically:
```python
import re

def extract_citations(text):
    # Match "Section X.Y" pattern
    sections = re.findall(r'Section \d+\.\d+', text)
    return sections

# Add to response
response += f"\n\nReferences: {', '.join(extract_citations(response))}"
```

### 4. Confidence Thresholds
Only answer if highly confident:
```python
if faithfulness_score < 0.95 or semantic_similarity < 0.90:
    return "I recommend consulting the full contract or an attorney for this specific question."
```

## Production Safeguards

```python
from raglint import RAGPipelineAnalyzer

async def legal_qa_with_safeguards(query, contract_contexts):
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    
    # Generate answer
    response = generate_answer(query, contract_contexts)
    
    # Evaluate
    result = await analyzer._process_item_async(query, response, contract_contexts)
    
    # Strict thresholds
    if result['faithfulness_score'] < 0.95:
        log_warning(f"Low faithfulness: {result['faithfulness_score']}")
        return {
            "answer": "For accurate information on this topic, please refer to the full contract or consult with legal counsel.",
            "confidence": "low",
            "reason": "Potential accuracy concerns"
        }
    
    # Add disclaimer
    response += "\n\n⚠️ This is informational only, not legal advice. Consult an attorney for specific guidance."
    
    return {
        "answer": response,
        "confidence": "high",
        "citations": extract_citations(response),
        "faithfulness": result['faithfulness_score']
    }
```

## Testing Strategy

### Adversarial Testing
Test with intentionally tricky questions:
- Asking about clauses that don't exist
- Queries that could match multiple sections
- Questions with embedded assumptions

**Example Adversarial Queries**:
```
"Can I be fired for any reason?" (Test: Should mention "for cause" vs "without cause")
"What's the non-compete area?" (Test: Should cite exact radius, not approximate)
"Do I own my side project?" (Test: Should explain exception conditions)
```

### Red Team Review
Have lawyers review a sample of RAG responses to catch:
- Subtle misinterpretations
- Missing conditions
- Incorrect legal terminology

## Recommended Thresholds

```yaml
legal_config:
  faithfulness_threshold: 0.95  # Stricter than normal
  require_citations: true
  max_answer_length: 200  # Force conciseness
  include_disclaimer: true
  
  # Escalate to human for:
  escalation_triggers:
    - faithfulness < 0.95
    - no_matching_context: true
    - ambiguous_query: true
```

## Example Analysis Results

```bash
$ raglint analyze contract_qa.json --smart

Analyzing legal Q&A...
✅ Faithfulness: 0.97 (Excellent - meets legal threshold)
✅ Context Relevance: 0.92 (Good section matching)
✅ Citation Coverage: 0.89 (Could improve - add section numbers)
⚠️  Answer Length: avg 52 words (consider more concise)

Recommendations:
1. ✅ Safe for production use (faithfulness > 0.95)
2. → Add automatic citation extraction
3. → Consider adding legal disclaimer to all responses
```

## Resources for Legal RAG

- **Chunking**: Preserve section structure
- **Retrieval**: Hybrid BM25 + vector search
- **Generation**: Low temperature (0.0-0.1)
- **Validation**: Custom citation \u0026 completeness plugins
- **Monitoring**: Track faithfulness daily, alert if < 0.95

## Risk Mitigation

1. **Never replace lawyers**: RAG is for research, not legal advice
2. **Human in the loop**: Flag low-confidence answers for review
3. **Audit trail**: Log all queries and responses
4. **Version control**: Track contract versions and updates
5. **Regular validation**: Monthly review of RAG answer quality

---

## Next Steps

1. Run analysis on your contracts
2. Implement citation plugin
3. Set up monitoring with alerts
4. Conduct red team review
5. Add legal disclaimers

**Expected Analysis Time**: 3-5 minutes with OpenAI API

⚠️ **IMPORTANT**: This example is for demonstration only. Always consult qualified legal counsel for actual legal matters.
