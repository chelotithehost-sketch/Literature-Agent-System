# agents/planner.py
from agents.base import BaseAgent
from core.state import BookState, ChapterState
import json
from loguru import logger

class Planner(BaseAgent):
    async def run(self, state: BookState, **kwargs) -> BookState:
        logger.info(f"Planning book: {state.title}")
        # Generate high-level structure
        structure = await self._generate_structure(state)
        state.structure = structure
        # Create chapter states
        chapters = []
        for i, chap_outline in enumerate(structure["chapters"]):
            chapters.append(ChapterState(
                index=i,
                title=chap_outline["title"],
                outline=chap_outline["summary"],
            ))
        state.chapters = chapters
        state.status = state.status.PLANNING
        return state

    async def _generate_structure(self, state: BookState) -> dict:
        prompt = f"""You are a literary planner. Create a detailed chapter-by-chapter outline for a {state.genre} novel titled "{state.title}" with tone: {state.tone}. 
        The novel should be at least {state.target_words} words. Provide output as JSON with keys: "chapters" (list of {{"title": str, "summary": str, "word_target": int}}), "arc_description": str."""
        messages = [{"role": "user", "content": prompt}]
        response = await self._call_llm("planning", messages, priority="quality", temperature=0.5)
        # Parse JSON (with error handling)
        try:
            data = json.loads(response)
        except:
            # fallback
            data = {"chapters": [{"title": f"Chapter {i+1}", "summary": "TBD", "word_target": state.target_words//20} for i in range(20)]}
        return data
