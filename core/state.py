# core/state.py
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    WRITING = "writing"
    REVIEWING = "reviewing"
    COMPILING = "compiling"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ChapterState:
    """State for a single chapter/scene with iterative refinement."""
    index: int
    title: str
    outline: str
    draft: str = ""
    refinement_loops: int = 0
    quality_score: float = 0.0
    converged: bool = False
    word_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BookState:
    """Global state for the entire book project."""
    project_id: str
    title: str
    genre: str
    tone: str
    structure: Dict[str, Any]  # e.g., chapters, scenes
    chapters: List[ChapterState] = field(default_factory=list)
    current_chapter: int = 0
    status: TaskStatus = TaskStatus.PENDING
    total_words: int = 0
    target_words: int = 200000
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    checkpoints: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "BookState":
        # Convert chapters back to ChapterState objects
        if "chapters" in data:
            data["chapters"] = [ChapterState(**ch) for ch in data["chapters"]]
        data["status"] = TaskStatus(data["status"])
        return cls(**data)

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "BookState":
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)
