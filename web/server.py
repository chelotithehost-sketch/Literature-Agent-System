# web/server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
from web.exporter import Exporter
from core.state import BookState

app = FastAPI(title="Literature Agent API")

@app.get("/status/{project_id}")
async def get_status(project_id: str):
    state_path = f"data/checkpoints/{project_id}_state.json"
    if not os.path.exists(state_path):
        raise HTTPException(404, "Project not found")
    state = BookState.load(state_path)
    return {
        "project_id": state.project_id,
        "status": state.status.value,
        "current_chapter": state.current_chapter,
        "total_chapters": len(state.chapters),
        "total_words": state.total_words,
        "target_words": state.target_words,
    }

@app.get("/export/{project_id}")
async def export_manuscript(project_id: str, format: str = "markdown"):
    exporter = Exporter()
    output_path = await exporter.export(project_id, format)
    return FileResponse(output_path, media_type="application/octet-stream", filename=os.path.basename(output_path))
