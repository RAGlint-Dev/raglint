# Customer Support Chatbot - RAGlint Example

## Overview

Evaluating a customer support RAG chatbot that answers common questions about account management, orders, payments, and technical issues.

## Use Case

**Scenario**: SaaS company support chatbot  
**Goal**: Reduce support tickets by providing accurate self-service answers  
**Challenge**: Handle diverse, informal queries while maintaining accuracy

## Dataset

`support_qa.json` contains 5 common support scenarios:
- Account/password issues
- Order tracking
- Subscription management
- Payment security
- Technical troubleshooting

## Running the Analysis

```bash
cd examples/support
raglint analyze support_qa.json --smart --output-dir=results/
```

## Key Metrics for Support

### 1. Answer Relevance (Most Critical)
**Target**: > 0.90

Support queries are often vague ("where's my order?"). The bot must understand intent and provide relevant answers.

**Warning Signs**:
- Bot gives subscription info when asked about orders
- Provides technical details when user wants simple steps

### 2. Faithfulness (Critical)
**Target**: > 0.85

Never make up policies! If unsure, say "Let me connect you with an agent."

**Warning Signs**:
- Mentions refund policies that don't exist
- States shipping times that aren't official
- Invents features or capabilities

### 3. Completeness (Custom Metric)
**Target**: Answer includes all necessary steps

Support answers should be actionable. Missing a step = frustrated customer.

## Common Issues

### Issue 1: Over-Technical Answers

**Bad**:
```
User: "App won't open"
Bot: "Please check your application's process scheduler and verify the daemon is running. Inspect system logs at /var/log/app.log for segmentation faults..."
```

**Good**:
```
Bot: "Try these steps:
1. Close and reopen the app
2. Restart your phone
3. Update the app from the app store
Still not working? Contact support at support@company.com"
```

**Fix**: Use simpler language, provide step-by-step instructions

### Issue 2: Missing Escalation Path

**Bad**:
```
User: "I was charged twice!"
Bot: "Check your bank statement"
```

**Good**:
```
Bot: "I'm sorry to hear that! Please contact our billing team immediately at billing@company.com or call 1-800-123-4567. They'll investigate and process a refund if needed."
```

**Fix**: Always provide escalation for billing/urgent issues

### Issue 3: Tone Mismatch

**Bad**:
```
User: "I'm really frustrated, this is the third time!"
Bot: "To reset your password, click..."
```

**Good**:
```
Bot: "I understand your frustration, and I apologize for the repeated issues. Let me help you fix this right away. To reset your password:..."
```

**Fix**: Add empathy detection, adjust tone for frustrated customers

## Optimization Workflow

### 1. Measure Current State
```bash
raglint analyze support_qa.json --smart --track-cost
```

### 2. Identify Problem Categories
- Which query types have low scores?
- Are password resets failing? Technical issues? Billing?

### 3. Targeted Improvements
- **Low Answer Relevance**: Improve query classification
- **Low Faithfulness**: Add fact-checking layer
- **Long Response Time**: Optimize retrieval

### 4. A/B Test
```python
# Compare two prompt strategies
results_v1 = analyze("support_qa.json", prompt="v1")
results_v2 = analyze("support_qa.json", prompt="v2")

if results_v2['answer_relevance'] > results_v1['answer_relevance']:
    print("V2 wins! Deploy to production")
```

## Production Monitoring

```python
from raglint import RAGPipelineAnalyzer

async def monitor_support_quality(conversation):
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    
    result = await analyzer._process_item_async(
        conversation['query'],
        conversation['response'],
        conversation['contexts']
    )
    
    # Alert if quality drops
    if result['faithfulness_score'] < 0.80:
        send_alert("Possible hallucination in support response", conversation)
    
    if result['answer_relevance'] < 0.85:
        escalate_to_human(conversation)
```

## Tips for Support Bots

1. **Keep Answers Short**
   - Aim for 2-4 sentences
   - Use bullet points for steps
   - Link to detailed docs

2. **Always Provide Next Steps**
   - "Didn't solve it? Email support@..."
   - "Need more help? Call..."

3. **Test Edge Cases**
   - Angry customers
   - Multi-issue queries ("password AND refund")
   - Vague questions ("it doesn't work")

4. **Track Customer Satisfaction**
   - Add thumbs up/down after each response
   - Correlate satisfaction with RAGlint metrics

## Example Analysis Results

```
Faithfulness: 0.92 ✅ (Excellent - answers are grounded)
Context Relevance: 0.88 ✅ (Good - retrieval works well)
Answer Relevance: 0.85 👍 (Good - mostly on-topic)

Recommendations:
- Improve answer relevance for technical queries
- Add empathy detection for frustrated customers
- Consider shorter answers (current avg: 47 words, target: 30)
```

## Next Steps

1. Run analysis on your support tickets
2. Identify your top 3 issue categories
3. Create custom test cases for each
4. Monitor in production with alerts

---

**Expected Analysis Time**: 2-3 minutes with OpenAI API
