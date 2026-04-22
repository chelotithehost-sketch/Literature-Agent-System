# agents/reviewer.py
from agents.base import BaseAgent
from core.state import BookState
from loguru import logger

class Reviewer(BaseAgent):
    async def run(self, state: BookState, **kwargs) -> BookState:
        logger.info("Reviewing full manuscript for continuity")
        # For memory efficiency, process in sliding window
        window_size = 3
        for i in range(0, len(state.chapters), window_size):
            window = state.chapters[i:i+window_size]
            if len(window) < 2:
                continue
            continuity_report = await self._check_continuity(state, window)
            # Apply fixes if needed (simplified)
            if continuity_report.get("issues"):
                logger.warning(f"Continuity issues in chapters {i}-{i+window_size-1}")
                # Could invoke a fixer agent
        state.status = state.status.COMPILING
        return state

    async def _check_continuity(self, state: BookState, chapters) -> dict:
        summaries = "\n".join([f"Chapter {c.index}: {c.title} - {c.outline}" for c in chapters])
        prompt = f"""Review the following chapter summaries for narrative continuity and consistency issues in a {state.genre} novel.
        {summaries}
        Output JSON with "issues" (list of problems) and "suggestions" (list of fixes)."""
        messages = [{"role": "user", "content": prompt}]
        response = await self._call_llm("review", messages, priority="quality", temperature=0.3)
        import json
        try:
            return json.loads(response)
        except:
            return {"issues": []}
