# agents/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.state import BookState
from core.routing import Router
import asyncio

class BaseAgent(ABC):
    def __init__(self, router: Router, config: Dict[str, Any]):
        self.router = router
        self.config = config
        self.name = self.__class__.__name__

    @abstractmethod
    async def run(self, state: BookState, **kwargs) -> BookState:
        """Execute agent task and return updated state."""
        pass

    async def _call_llm(self, task_type: str, messages: list, priority: str = "quality", **kwargs) -> str:
        provider = self.router.select_provider(task_type, priority)
        return await provider.complete(messages, **kwargs)
