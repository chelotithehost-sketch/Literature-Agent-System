# agents/compiler.py
from agents.base import BaseAgent
from core.state import BookState
from loguru import logger

class Compiler(BaseAgent):
    async def run(self, state: BookState, **kwargs) -> BookState:
        logger.info("Compiling final manuscript")
        manuscript = self._assemble_manuscript(state)
        output_path = f"data/output/{state.project_id}.md"
        with open(output_path, "w") as f:
            f.write(manuscript)
        state.status = state.status.COMPLETED
        return state

    def _assemble_manuscript(self, state: BookState) -> str:
        parts = [f"# {state.title}\n\n"]
        for ch in state.chapters:
            parts.append(f"## Chapter {ch.index+1}: {ch.title}\n\n")
            parts.append(ch.draft + "\n\n")
        return "".join(parts)
