import os

class Config:
    project_root = "/content/document-rag"

    # Data (uploaded docs, vector DB, SQLite) still persists to Drive -
    # this is small and worth keeping so your documents survive between
    # sessions. Only the large model cache is disabled below.
    data_dir = "/content/drive/MyDrive/rag_platform_data"
    upload_dir = os.path.join(data_dir, "uploads")
    chroma_dir = os.path.join(data_dir, "chroma")
    sqlite_path = os.path.join(data_dir, "registry.db")

    # Models re-download each fresh Colab session instead of being cached
    # to Drive - keeps Drive usage minimal, at the cost of a longer wait
    # (~10 min for the 7B model) on every new session.
    use_drive_model_cache = False
    model_cache_dir = os.path.join(data_dir, "model_cache")

    embedding_model = "BAAI/bge-small-en-v1.5"
    llm_model = "Qwen/Qwen2.5-7B-Instruct"
    reranker_model = "BAAI/bge-reranker-base"

CONFIG = Config()
