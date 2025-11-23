"""
Tests for Testset Generator.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, mock_open
from raglint.generation import TestsetGenerator
from raglint.config import Config

class TestTestsetGenerator:
    """Test TestsetGenerator."""
    
    @pytest.fixture
    def mock_llm(self):
        with patch("raglint.generation.generator.LLMFactory") as MockFactory:
            mock_llm = Mock()
            mock_llm.agenerate = AsyncMock(return_value='{"question": "Q", "answer": "A"}')
            MockFactory.create.return_value = mock_llm
            yield mock_llm

    @pytest.mark.asyncio
    async def test_generate_from_text(self, mock_llm):
        """Test generation from text."""
        generator = TestsetGenerator()
        text = "This is a sample text for testing generation. " * 100
        
        results = await generator.generate_from_text(text, count=2)
        
        assert len(results) == 2
        assert results[0]["query"] == "Q"
        assert results[0]["ground_truth"] == "A"
        assert len(results[0]["ground_truth_contexts"]) == 1
        assert mock_llm.agenerate.call_count == 2

    @pytest.mark.asyncio
    async def test_generate_from_file_text(self, mock_llm):
        """Test generation from text file."""
        generator = TestsetGenerator()
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value="Sample text " * 100), \
             patch("pathlib.Path.suffix", ".txt"): # Mock property
             
             # Note: mocking property on Path is tricky, simpler to mock _read_pdf or just trust read_text logic
             # Let's mock the internal methods to simplify test
             pass
             
        # Alternative: Create a real temp file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Sample text " * 100)
            path = f.name
            
        try:
            results = await generator.generate_from_file(path, count=1)
            assert len(results) == 1
        finally:
            os.remove(path)

    def test_chunk_text(self):
        """Test chunking logic."""
        generator = TestsetGenerator()
        text = "word " * 2000
        chunks = generator._chunk_text(text, chunk_size=100, overlap=0)
        # 2000 words / 100 words per chunk = 20 chunks
        # But it's char based? No, implementation was word based split but char length check?
        # Let's check implementation:
        # words = text.split()
        # chunk = " ".join(words[i:i + chunk_size])
        # So chunk_size is in WORDS.
        
        assert len(chunks) == 20
