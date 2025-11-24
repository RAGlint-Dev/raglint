"""
Testset Generator for creating synthetic evaluation data.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

from tqdm.asyncio import tqdm as atqdm

from raglint.config import Config
from raglint.generation.prompts import GENERATE_QA_PROMPT
from raglint.llm import LLMFactory

logger = logging.getLogger(__name__)

class TestsetGenerator:
    """Generates synthetic testsets from documents."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.llm = LLMFactory.create(self.config.as_dict())

    async def generate_from_file(self, file_path: str, count: int = 10) -> list[dict[str, Any]]:
        """
        Generate testset from a file (PDF or Text).

        Args:
            file_path: Path to the input file.
            count: Number of QA pairs to generate.

        Returns:
            List of RAGLint-compatible test cases.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        text = ""
        if path.suffix.lower() == ".pdf":
            text = self._read_pdf(path)
        else:
            text = path.read_text(encoding="utf-8")

        return await self.generate_from_text(text, count)

    async def generate_from_text(self, text: str, count: int = 10) -> list[dict[str, Any]]:
        """
        Generate testset from raw text.

        Args:
            text: Input text.
            count: Number of QA pairs to generate.

        Returns:
            List of RAGLint-compatible test cases.
        """
        # 1. Chunk the text
        chunks = self._chunk_text(text)
        if not chunks:
            raise ValueError("Input text is empty or could not be chunked.")

        logger.info(f"Generated {len(chunks)} chunks from input text.")

        # 2. Select chunks to generate from
        # Simple strategy: Round-robin or random. For now, just iterate.
        selected_chunks = []
        for i in range(count):
            selected_chunks.append(chunks[i % len(chunks)])

        # 3. Generate QA pairs in parallel
        tasks = [self._generate_single_qa(chunk) for chunk in selected_chunks]
        results = await atqdm.gather(*tasks, desc="Generating Testset", unit="pair")

        # 4. Filter failed generations
        valid_results = [r for r in results if r is not None]
        logger.info(f"Successfully generated {len(valid_results)}/{count} QA pairs.")

        return valid_results

    async def _generate_single_qa(self, chunk: str) -> Optional[dict[str, Any]]:
        """Generate a single QA pair from a chunk."""
        try:
            prompt = GENERATE_QA_PROMPT.format(context=chunk)
            response = await self.llm.agenerate(prompt)

            # Parse JSON output
            # Clean markdown code blocks if present
            cleaned = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)

            return {
                "query": data["question"],
                "response": "", # Empty response for evaluation (model needs to generate this)
                "ground_truth": data["answer"],
                "ground_truth_contexts": [chunk],
                "retrieved_contexts": [] # Empty for evaluation input
            }
        except Exception as e:
            logger.error(f"Failed to generate QA pair: {e}")
            return None

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        """
        Semantic text chunking with sentence boundaries.

        Uses sentence boundaries to create more coherent chunks instead of
        arbitrary word splits. This improves quality of generated test cases.

        Args:
            text: Input text to chunk
            chunk_size: Target size in characters
            overlap: Overlap size in characters for context continuity

        Returns:
            List of text chunks
        """
        import re

        # Split into sentences using robust regex
        sentence_endings = re.compile(r'(?<=[.!?])\s+')
        sentences = sentence_endings.split(text)

        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_len = len(sentence)

            # If adding this sentence exceeds chunk_size, finalize current chunk
            if current_size + sentence_len > chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text) > 50:  # Filter very small chunks
                    chunks.append(chunk_text)

                # Start new chunk with overlap
                # Keep last few sentences for context
                overlap_sentences = []
                overlap_size = 0
                for s in reversed(current_chunk):
                    if overlap_size + len(s) <= overlap:
                        overlap_sentences.insert(0, s)
                        overlap_size += len(s)
                    else:
                        break

                current_chunk = overlap_sentences
                current_size = overlap_size

            current_chunk.append(sentence)
            current_size += sentence_len

        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) > 50:
                chunks.append(chunk_text)

        return chunks

    def _read_pdf(self, path: Path) -> str:
        """Read text from PDF."""
        try:
            import pypdf
        except ImportError:
            raise ImportError(
                "pypdf is required for PDF support. Install it with: pip install pypdf"
            )

        reader = pypdf.PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
