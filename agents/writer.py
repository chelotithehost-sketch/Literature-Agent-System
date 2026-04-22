# agents/writer.py
from agents.base import BaseAgent
from agents.thinker import Thinker
from core.state import BookState
from loguru import logger

class Writer(BaseAgent):
    def __init__(self, router, config):
        super().__init__(router, config)
        self.thinker = Thinker(router, config)

    async def run(self, state: BookState, **kwargs) -> BookState:
        start_idx = kwargs.get("start_chapter", state.current_chapter)
        end_idx = kwargs.get("end_chapter", len(state.chapters))
        for idx in range(start_idx, end_idx):
            logger.info(f"Writing chapter {idx+1}/{len(state.chapters)}")
            state.current_chapter = idx
            state = await self.thinker.run(state, chapter_idx=idx)
            # Save checkpoint after each chapter
            state.save(f"data/checkpoints/{state.project_id}_ch{idx}.json")
            state.total_words += state.chapters[idx].word_count
            if state.total_words >= state.target_words:
                logger.info(f"Target word count reached: {state.total_words}")
                break
        state.status = state.status.WRITING if state.current_chapter < len(state.chapters)-1 else state.status.REVIEWING
        return state
