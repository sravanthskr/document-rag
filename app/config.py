import os

class Config:
    project_root = "/content/document-rag"

    data_dir = "/content/drive/MyDrive/rag_platform_data"
    upload_dir = os.path.join(data_dir, "uploads")
    chroma_dir = os.path.join(data_dir, "chroma")
    sqlite_path = os.path.join(data_dir, "registry.db")

    use_drive_model_cache = False
    model_cache_dir = os.path.join(data_dir, "model_cache")

    embedding_model = "BAAI/bge-small-en-v1.5"
    llm_model = "Qwen/Qwen2.5-7B-Instruct"
    reranker_model = "BAAI/bge-reranker-base"

CONFIG = Config()

# Ensure all data folders exist before anything (SQLite, ChromaDB, file
# uploads) tries to write into them - needed on a fresh Drive that's
# never had this app's folder structure created before.
os.makedirs(CONFIG.upload_dir, exist_ok=True)
os.makedirs(CONFIG.chroma_dir, exist_ok=True)
