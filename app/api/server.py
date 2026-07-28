import sys
import os

# Compute the project root relative to this file's own location, instead
# of hardcoding a path - works no matter what folder the repo is cloned
# into (fixes the /content/RAG vs /content/document-rag mismatch found
# when testing the clean final notebook).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from app.config import CONFIG
if CONFIG.use_drive_model_cache:
    os.makedirs(CONFIG.model_cache_dir, exist_ok=True)
    os.environ["HF_HOME"] = CONFIG.model_cache_dir

import io
from collections import deque

log_buffer = deque(maxlen=300)

class TeeOutput:
    def __init__(self, original):
        self.original = original
    def write(self, text):
        self.original.write(text)
        if text.strip():
            log_buffer.append(text.strip())
    def flush(self):
        self.original.flush()

sys.stdout = TeeOutput(sys.stdout)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional

from app.pipeline.ingest_pipeline import ingest_document
from app.pipeline.query_pipeline import answer_question
from app.pipeline.delete_pipeline import delete_document
from app.storage.db import init_db, list_documents

init_db()

app = FastAPI(title="Document Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/documents")
def get_documents():
    docs = list_documents()
    return {"documents": docs}


@app.get("/api/logs")
def get_logs():
    return {"logs": list(log_buffer)}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    supported = (".pdf", ".txt", ".md", ".docx")
    if not file.filename.lower().endswith(supported):
        return {"status": "error", "message": f"Unsupported file type. Supported: {', '.join(supported)}"}
    file_bytes = await file.read()
    result = ingest_document(file_bytes, file.filename)
    return result


@app.post("/api/ask")
def ask(question: str = Form(...), document_ids: Optional[str] = Form(None)):
    doc_id_list = document_ids.split(",") if document_ids else None
    result = answer_question(question, document_ids=doc_id_list)
    return result


@app.delete("/api/documents/{doc_id}")
def delete(doc_id: str):
    result = delete_document(doc_id)
    return result


app.mount("/", StaticFiles(directory=os.path.join(PROJECT_ROOT, "app", "frontend"), html=True), name="frontend")
