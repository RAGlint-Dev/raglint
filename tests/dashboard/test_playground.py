import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from raglint.dashboard.app import app
from raglint.dashboard import models
from raglint.dashboard.database import SessionLocal

from raglint.dashboard.app import get_current_user_from_cookie

@pytest.mark.asyncio
async def test_playground_generate(test_db):
    # Mock User
    mock_user = models.User(id="test_id", email="test@example.com")
    
    # Override dependency
    app.dependency_overrides[get_current_user_from_cookie] = lambda: mock_user
    
    try:
        with TestClient(app) as client:
            # 2. Mock LLM
            with patch("raglint.llm.LLMFactory.create") as mock_create:
                mock_llm = MagicMock()
                mock_llm.agenerate = AsyncMock(return_value="Generated Response")
                mock_create.return_value = mock_llm

                # 3. Call Generate Endpoint
                response = client.post(
                    "/playground/generate",
                    data={
                        "system_prompt": "Sys",
                        "user_prompt_template": "User {query}",
                        "query": "Test",
                        "context": "Ctx"
                    }
                )
                
                assert response.status_code == 200
                assert "Generated Response" in response.text
                assert "partials/playground_result_shell.html" in response.text or "Real-time Scores" in response.text
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_playground_analyze_metric(test_db):
    # Mock User
    mock_user = models.User(id="test_id", email="test@example.com")
    
    # Override dependency
    app.dependency_overrides[get_current_user_from_cookie] = lambda: mock_user
    
    try:
        with TestClient(app) as client:
            # 2. Mock Analyzer
            with patch("raglint.core.RAGPipelineAnalyzer") as MockAnalyzer:
                mock_instance = MockAnalyzer.return_value
                
                # Mock Faithfulness
                mock_instance.faithfulness_scorer = MagicMock()
                mock_instance.faithfulness_scorer.ascore = AsyncMock(return_value=(0.9, "Reasoning"))
                
                # 3. Call Metric Endpoint
                response = client.post(
                    "/playground/analyze/metric/faithfulness",
                    data={
                        "query": "Test",
                        "contexts": "Ctx",
                        "response": "Resp"
                    }
                )
                
                assert response.status_code == 200
                assert "0.9" in response.text
                assert "Reasoning" in response.text
    finally:
        app.dependency_overrides.clear()
