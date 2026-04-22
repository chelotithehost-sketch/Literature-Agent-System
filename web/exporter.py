# web/exporter.py
import subprocess
import os
from loguru import logger

class Exporter:
    async def export(self, project_id: str, fmt: str) -> str:
        md_path = f"data/output/{project_id}.md"
        if not os.path.exists(md_path):
            raise FileNotFoundError("Manuscript not compiled yet")
        if fmt == "markdown":
            return md_path
        elif fmt == "pdf":
            pdf_path = md_path.replace(".md", ".pdf")
            subprocess.run(["pandoc", md_path, "-o", pdf_path, "--pdf-engine=xelatex"], check=True)
            return pdf_path
        elif fmt == "epub":
            epub_path = md_path.replace(".md", ".epub")
            subprocess.run(["pandoc", md_path, "-o", epub_path], check=True)
            return epub_path
        elif fmt == "docx":
            docx_path = md_path.replace(".md", ".docx")
            subprocess.run(["pandoc", md_path, "-o", docx_path], check=True)
            return docx_path
        else:
            raise ValueError("Unsupported format")
