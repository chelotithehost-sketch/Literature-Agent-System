# agents/orchestrator.py
import asyncio
from typing import Dict, Any
from core.state import BookState, TaskStatus
from agents.planner import Planner
from agents.writer import Writer
from agents.reviewer import Reviewer
from agents.compiler import Compiler
from core.routing import Router
from loguru import logger

class Orchestrator:
    def __init__(self, config: Dict[str, Any], router: Router):
        self.config = config
        self.router = router
        self.planner = Planner(router, config.get("planner", {}))
        self.writer = Writer(router, config.get("writer", {}))
        self.reviewer = Reviewer(router, config.get("reviewer", {}))
        self.compiler = Compiler(router, config.get("compiler", {}))

    async def execute(self, state: BookState) -> BookState:
        """DAG execution based on current state."""
        try:
            if state.status == TaskStatus.PENDING:
                state = await self.planner.run(state)
                state.status = TaskStatus.PLANNING
                state.save(self._checkpoint_path(state))

            if state.status == TaskStatus.PLANNING:
                state = await self.writer.run(state)
                if state.current_chapter >= len(state.chapters)-1:
                    state.status = TaskStatus.REVIEWING
                state.save(self._checkpoint_path(state))

            if state.status == TaskStatus.REVIEWING:
                state = await self.reviewer.run(state)
                state.status = TaskStatus.COMPILING
                state.save(self._checkpoint_path(state))

            if state.status == TaskStatus.COMPILING:
                state = await self.compiler.run(state)
                state.save(self._checkpoint_path(state))

            return state
        except Exception as e:
            logger.exception(f"Execution failed: {e}")
            state.status = TaskStatus.FAILED
            raise

    def _checkpoint_path(self, state: BookState) -> str:
        return f"data/checkpoints/{state.project_id}_state.json"

    async def resume(self, project_id: str) -> BookState:
        path = f"data/checkpoints/{project_id}_state.json"
        state = BookState.load(path)
        logger.info(f"Resumed project {project_id} from status {state.status}")
        return await self.execute(state)
