# core/memory.py
import gc
import weakref
from collections import OrderedDict
from typing import Any, Optional
import psutil
import torch  # if Ollama local

class MemoryPool:
    """
    Strict memory management for 2GB constraint.
    Uses LRU cache for large objects, forces garbage collection,
    monitors memory usage and triggers fallback to cloud if threshold exceeded.
    """
    def __init__(self, max_memory_mb: int = 1800, threshold_mb: int = 1500):
        self.max_memory_mb = max_memory_mb
        self.threshold_mb = threshold_mb
        self._cache = OrderedDict()
        self._current_size = 0

    def _get_size(self, obj: Any) -> int:
        """Estimate object size in bytes."""
        if hasattr(obj, "nbytes"):
            return obj.nbytes
        # fallback approximation
        import sys
        return sys.getsizeof(obj)

    def put(self, key: str, obj: Any):
        size = self._get_size(obj)
        if size > self.max_memory_mb * 1024 * 1024:
            raise MemoryError("Object too large for pool")
        self._evict_if_needed(size)
        self._cache[key] = obj
        self._current_size += size

    def get(self, key: str) -> Optional[Any]:
        obj = self._cache.get(key)
        if obj is not None:
            self._cache.move_to_end(key)
        return obj

    def _evict_if_needed(self, incoming_size: int):
        while self._current_size + incoming_size > self.max_memory_mb * 1024 * 1024:
            if not self._cache:
                break
            key, obj = self._cache.popitem(last=False)
            self._current_size -= self._get_size(obj)
            del obj
        gc.collect()

    def check_memory_pressure(self) -> bool:
        """Return True if memory usage exceeds threshold."""
        mem = psutil.virtual_memory()
        used_mb = mem.used / (1024 * 1024)
        return used_mb > self.threshold_mb

    def clear(self):
        self._cache.clear()
        self._current_size = 0
        gc.collect()

# Global memory pool instance
memory_pool = MemoryPool()
