# agents/thinker.py
from agents.base import BaseAgent
from core.state import BookState, ChapterState
from loguru import logger

class Thinker(BaseAgent):
    async def run(self, state: BookState, **kwargs) -> BookState:
        chapter_idx = kwargs.get("chapter_idx", state.current_chapter)
        chapter = state.chapters[chapter_idx]
        max_loops = self.config.get("max_refinement_loops", 5)
        threshold = self.config.get("convergence_threshold", 0.85)

        # Initial draft if empty
        if not chapter.draft:
            chapter = await self._initial_draft(state, chapter)

        # Refinement loop (Recurrent-Depth reasoning)
        for loop in range(max_loops):
            logger.info(f"Refining chapter {chapter_idx} loop {loop+1}/{max_loops}")
            refined = await self._refine_chapter(state, chapter)
            # Evaluate coherence / quality (ACT halting)
            score = await self._evaluate_quality(state, refined)
            if score > threshold or (score > chapter.quality_score and loop > 0):
                chapter.draft = refined
                chapter.quality_score = score
                chapter.refinement_loops = loop + 1
                if score > threshold:
                    chapter.converged = True
                    logger.info(f"Chapter {chapter_idx} converged at loop {loop+1} with score {score:.2f}")
                    break
            else:
                logger.info(f"No improvement, stopping refinement")
                break
            chapter.draft = refined
            chapter.quality_score = score
            chapter.refinement_loops = loop + 1

        chapter.word_count = len(chapter.draft.split())
        state.chapters[chapter_idx] = chapter
        return state

    async def _initial_draft(self, state: BookState, chapter: ChapterState) -> ChapterState:
        prompt = f"""Write the first draft of chapter titled "{chapter.title}" for a {state.genre} novel "{state.title}". 
        Outline: {chapter.outline}
        Write approximately {chapter.metadata.get('word_target', 3000)} words. Be descriptive and engaging."""
        messages = [{"role": "user", "content": prompt}]
        draft = await self._call_llm("drafting", messages, priority="quality", max_tokens=4096)
        chapter.draft = draft
        return chapter

    async def _refine_chapter(self, state: BookState, chapter: ChapterState) -> str:
        prompt = f"""Refine the following chapter draft to improve coherence, prose quality, and narrative flow.
        Original draft:
        {chapter.draft}
        Provide the refined version (only the chapter text, no extra commentary)."""
        messages = [{"role": "user", "content": prompt}]
        return await self._call_llm("review", messages, priority="quality", temperature=0.6)

    async def _evaluate_quality(self, state: BookState, text: str) -> float:
        # Simple heuristic: use another LLM call to score, or rule-based.
        # For resource constraints, use a lightweight model.
        prompt = f"""Rate the following chapter text on a scale of 0 to 1 for coherence, narrative flow, and literary quality. Output only a number.
        Text: {text[:2000]}..."""
        messages = [{"role": "user", "content": prompt}]
        response = await self._call_llm("light", messages, priority="speed", temperature=0.0, max_tokens=10)
        try:
            return float(response.strip())
        except:
            return 0.7
