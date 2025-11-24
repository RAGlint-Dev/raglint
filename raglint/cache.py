"""Simple LRU cache for LLM responses to avoid duplicate API calls."""
import hashlib
from typing import Any, Optional


class LLMCache:
    """Thread-safe LLM response cache."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: dict[str, Any] = {}

    def _make_key(self, prompt: str, model: str = "default") -> str:
        """Generate cache key from prompt and model."""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, model: str = "default") -> Optional[str]:
        """Get cached response if available."""
        key = self._make_key(prompt, model)
        return self._cache.get(key)

    def set(self, prompt: str, response: str, model: str = "default") -> None:
        """Cache a response."""
        if len(self._cache) >= self.max_size:
            # Simple FIFO eviction
            first_key = next(iter(self._cache))
            del self._cache[first_key]

        key = self._make_key(prompt, model)
        self._cache[key] = response

    def clear(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()

    def size(self) -> int:
        """Return current cache size."""
        return len(self._cache)


# Global cache instance
_global_cache = LLMCache(max_size=1000)


def get_cache() -> LLMCache:
    """Get the global LLM cache instance."""
    return _global_cache
