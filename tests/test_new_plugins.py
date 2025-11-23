"""
Comprehensive tests for all 12 new plugins.
"""
import pytest
from raglint.plugins.builtins import (
    CitationAccuracyPlugin,
    ReadabilityPlugin,
    CompletenessPlugin,
    ConcisenessPlugin,
    BiasDetectorPlugin,
    MultilingualSupportPlugin,
    PIIDetectorPlugin,
    SQLInjectionDetectorPlugin,
    HallucinationConfidencePlugin,
    ContextCompressionPlugin,
    ResponseDiversityPlugin,
    UserIntentPlugin,
)


@pytest.mark.asyncio
async def test_citation_accuracy_plugin():
    """Test citation accuracy detection."""
    plugin = CitationAccuracyPlugin()
    
    # Test with citations
    result = await plugin.calculate_async(
        query="What is the policy?",
        response="According to Section 5.2 [1], the policy states...",
        contexts=["Section 5.2: Policy details"]
    )
    
    assert "score" in result
    assert 0 <= result["score"] <= 1
    assert result["citation_count"] > 0
    
    # Test without citations
    result_no_cite = await plugin.calculate_async(
        query="What is the policy?",
        response="The policy is very simple.",
        contexts=["Policy details"]
    )
    
    assert result_no_cite["citation_count"] == 0
    assert result_no_cite["score"] < result["score"]


@pytest.mark.asyncio
async def test_readability_plugin():
    """Test readability scoring."""
    plugin = ReadabilityPlugin()
    
    # Test simple text
    result = await plugin.calculate_async(
        query="",
        response="The cat sat on the mat. It was warm.",
        contexts=[]
    )
    
    assert "flesch_reading_ease" in result
    assert "flesch_kincaid_grade" in result
    assert result["flesch_reading_ease"] > 50  # Should be easy to read
    
    # Test complex text
    result_complex = await plugin.calculate_async(
        query="",
        response="The implementation of sophisticated algorithmic methodologies necessitates comprehensive understanding.",
        contexts=[]
    )
    
    assert result_complex["flesch_kincaid_grade"] > result["flesch_kincaid_grade"]


@pytest.mark.asyncio
async def test_completeness_plugin():
    """Test answer completeness for multi-part queries."""
    plugin = CompletenessPlugin()
    
    # Test complete answer
    result = await plugin.calculate_async(
        query="What's the price and warranty?",
        response="The price is $299 and it comes with a 2-year warranty.",
        contexts=[]
    )
    
    assert "score" in result
    assert result["score"] > 0.7  # Should be mostly complete
    
    # Test incomplete answer
    result_incomplete = await plugin.calculate_async(
        query="What's the price, warranty, and shipping?",
        response="The price is $299.",
        contexts=[]
    )
    
    assert result_incomplete["score"] < result["score"]


@pytest.mark.asyncio
async def test_conciseness_plugin():
    """Test response conciseness detection."""
    plugin = ConcisenessPlugin()
    
    # Test concise response
    result = await plugin.calculate_async(
        query="",
        response="30-day return policy. Full refund.",
        contexts=[]
    )
    
    assert "score" in result
    assert result["score"] > 0.7
    assert result["verbosity_level"] in ["Concise", "Moderate"]
    
    # Test verbose response
    result_verbose = await plugin.calculate_async(
        query="",
        response="Well, basically, to be honest, I think that we have what you could call a very comprehensive policy.",
        contexts=[]
    )
    
    assert result_verbose["filler_words"] > 0
    assert result_verbose["score"] < result["score"]


@pytest.mark.asyncio
async def test_bias_detector_plugin():
    """Test bias detection."""
    plugin = BiasDetectorPlugin()
    
    # Test neutral text
    result = await plugin.calculate_async(
        query="",
        response="The chairperson will meet with business leaders.",
        contexts=[]
    )
    
    assert "score" in result
    assert result["bias_level"] in ["Minimal/None", "Low"]
    
    # Test biased text
    result_biased = await plugin.calculate_async(
        query="",
        response="The chairman will meet with the businessmen.",
        contexts=[]
    )
    
    assert len(result_biased["issues_found"]) > 0


@pytest.mark.asyncio
async def test_multilingual_plugin():
    """Test multilingual support detection."""
    plugin = MultilingualSupportPlugin()
    
    # Test consistent language
    result = await plugin.calculate_async(
        query="What is the weather?",
        response="The weather is sunny today.",
        contexts=[]
    )
    
    assert "score" in result
    assert result["is_consistent"] is True
    
    # Test language detection
    assert "latin" in result["response_languages"]


@pytest.mark.asyncio
async def test_pii_detector_plugin():
    """Test PII detection."""
    plugin = PIIDetectorPlugin()
    
    # Test clean text
    result = await plugin.calculate_async(
        query="",
        response="Please contact our support team for assistance.",
        contexts=[]
    )
    
    assert result["pii_found"] is False
    assert result["score"] == 1.0
    
    # Test with PII
    result_pii = await plugin.calculate_async(
        query="",
        response="Contact john.doe@example.com or call 555-123-4567.",
        contexts=[]
    )
    
    assert result_pii["pii_found"] is True
    assert result_pii["pii_count"] > 0
    assert "email" in result_pii["pii_types"]


@pytest.mark.asyncio
async def test_sql_injection_detector_plugin():
    """Test SQL injection pattern detection."""
    plugin = SQLInjectionDetectorPlugin()
    
    # Test clean text
    result = await plugin.calculate_async(
        query="",
        response="The product costs $49.99.",
        contexts=[]
    )
    
    assert result["sql_patterns_found"] is False
    assert result["score"] == 1.0
    
    # Test with SQL patterns
    result_sql = await plugin.calculate_async(
        query="",
        response="SELECT * FROM users WHERE id=1",
        contexts=[]
    )
    
    assert result_sql["sql_patterns_found"] is True
    assert result_sql["pattern_count"] > 0


@pytest.mark.asyncio
async def test_hallucination_confidence_plugin():
    """Test hallucination confidence scoring."""
    plugin = HallucinationConfidencePlugin()
    
    # Test high confidence (good context overlap)
    result = await plugin.calculate_async(
        query="What is the price?",
        response="The price is $299 as stated in the manual.",
        contexts=["The manual states the price is $299"]
    )
    
    assert "score" in result
    assert result["confidence_level"] in ["high", "very high"]
    assert result["hallucination_risk"] == "low"
    
    # Test low confidence
    result_low = await plugin.calculate_async(
        query="What is the price?",
        response="Maybe it's expensive, I'm not sure.",
        contexts=["Price information"]
    )
    
    assert result_low["score"] < result["score"]


@pytest.mark.asyncio
async def test_context_compression_plugin():
    """Test context compression analysis."""
    plugin = ContextCompressionPlugin()
    
    # Test with redundant contexts
    result = await plugin.calculate_async(
        query="",
        response="The price is $99.",
        contexts=[
            "Price: $99",
            "The price is $99",
            "Cost is $99"
        ]
    )
    
    assert "redundancy_ratio" in result
    assert result["redundancy_ratio"] > 0.3  # Should detect redundancy
    assert result["potential_token_savings"] > 0


@pytest.mark.asyncio
async def test_response_diversity_plugin():
    """Test response diversity measurement."""
    plugin = ResponseDiversityPlugin()
    
    # Test diverse response
    result = await plugin.calculate_async(
        query="",
        response="This laptop features excellent performance. The display quality amazes users. Storage capacity meets professional needs.",
        contexts=[]
    )
    
    assert "lexical_diversity" in result
    assert result["diversity_level"] in ["medium", "high"]
    
    # Test repetitive response
    result_rep = await plugin.calculate_async(
        query="",
        response="Good product. Very good. Really good. Extremely good.",
        contexts=[]
    )
    
    assert result_rep["repetition_detected"] is True


@pytest.mark.asyncio
async def test_user_intent_plugin():
    """Test user intent classification."""
    plugin = UserIntentPlugin()
    
    # Test instructional intent
    result = await plugin.calculate_async(
        query="How do I reset my password?",
        response="1. Click Forgot Password 2. Enter your email 3. Check inbox",
        contexts=[]
    )
    
    assert result["detected_intent"] == "instructional"
    assert result["score"] > 0.7
    
    # Test factual intent
    result_factual = await plugin.calculate_async(
        query="What is the capital of France?",
        response="Paris is the capital of France.",
        contexts=[]
    )
    
    assert result_factual["detected_intent"] == "factual"


# Integration test: Multiple plugins together
@pytest.mark.asyncio
async def test_multiple_plugins_integration():
    """Test using multiple plugins together."""
    plugins = [
        ReadabilityPlugin(),
        PIIDetectorPlugin(),
        BiasDetectorPlugin(),
    ]
    
    test_response = "The chairperson announced the new policy. Contact support@company.com for details."
    
    results = []
    for plugin in plugins:
        result = await plugin.calculate_async(
            query="What's the new policy?",
            response=test_response,
            contexts=[]
        )
        results.append(result)
    
    assert len(results) == 3
    assert all("score" in r for r in results)
    
    # Check PII was detected
    pii_result = results[1]
    assert pii_result["pii_found"] is True
