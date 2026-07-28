# Document Intelligence Platform

A free, open-source RAG (Retrieval-Augmented Generation) system that answers questions from your own documents — with citations, hallucination guardrails, and hybrid search — built entirely on Google Colab's free tier.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sravanthskr/document-rag/blob/main/Document_Intelligence_Platform.ipynb)

---

## What it is

Most "chat with PDF" projects handle one document and stop there. This is closer to what real companies build: a platform that ingests multiple document types, indexes them for fast semantic + keyword search, scopes questions to specific documents, and grounds every answer in retrieved evidence — with a deterministic guard against hallucinated answers, not just a prompt asking the model nicely.

## Screenshots

**Chat — grounded answers with citations, scoped to selected documents**
<img width="1912" height="902" alt="Chat interface with citations" src="https://github.com/user-attachments/assets/f31b4943-ee54-4b9c-9253-d1fc0b0cca2a" />

**Hallucination guard — correctly refuses an off-topic question**
<img width="1917" height="907" alt="Off-topic question correctly refused" src="https://github.com/user-attachments/assets/69f51f9c-a516-4c60-a716-8790b6ef1779" />

**Live backend activity log during model loading and retrieval**
<img width="1917" height="906" alt="Live backend activity log" src="https://github.com/user-attachments/assets/31c74176-048a-4bfd-96fb-9e6362577dfc" />

**Document upload and knowledge base management**
<img width="1917" height="906" alt="Document upload and knowledge base" src="https://github.com/user-attachments/assets/9029363e-d7e9-45e1-b063-6acfac3adcb1" />


## Features

- **Multi-format ingestion** — PDF, TXT, Markdown, DOCX, with automatic OCR fallback for scanned pages
- **Hybrid retrieval** — combines semantic search (embeddings) with keyword search (BM25) via Reciprocal Rank Fusion, then reranks with a cross-encoder
- **Grounded generation** — answers are built strictly from retrieved context, with page-level citations
- **Deterministic hallucination guard** — a relevance threshold blocks generation entirely when no retrieved content is actually relevant, instead of trusting the LLM to say "I don't know"
- **Document scoping** — search across all documents or restrict to a specific selection
- **Live backend activity log** — see model loading and retrieval steps happening in real time
- **Fully free** — runs on Google Colab's free T4 GPU tier, no paid APIs

## Architecture

Two independent pipelines share the same storage layer.

```
                          INGESTION PIPELINE
  ┌────────┐   ┌───────────┐   ┌───────┐   ┌───────┐   ┌────────┐   ┌─────────────┐
  │ Upload │ → │  Parse    │ → │ Clean │ → │ Chunk │ → │ Embed  │ → │   Store     │
  │  file  │   │ (+ OCR if │   │  text │   │ into  │   │ chunks │   │ ChromaDB +  │
  │        │   │  scanned) │   │       │   │pieces │   │        │   │   SQLite    │
  └────────┘   └───────────┘   └───────┘   └───────┘   └────────┘   └─────────────┘
```

```
                            QUERY PIPELINE
  ┌──────────┐   ┌────────────────┐   ┌────────┐   ┌───────────┐   ┌──────────┐   ┌───────┐
  │ Question │ → │ Hybrid Retrieve │ → │ Rerank │ → │ Relevance │ → │ Generate │ → │  Cite │
  │          │   │ (semantic + BM25│   │(cross- │   │  Check    │   │  Answer  │   │sources│
  │          │   │  + fusion)      │   │encoder)│   │ (guard)   │   │          │   │       │
  └──────────┘   └────────────────┘   └────────┘   └───────────┘   └──────────┘   └───────┘
```

**What each stage actually does:**

| Stage | Purpose |
|---|---|
| Parse (+OCR) | Extract text from any supported format; scanned pages fall back to OCR automatically |
| Chunk | Split text into small, page-tracked pieces for accurate citations |
| Embed | Convert text into vectors that capture meaning, not just keywords |
| Hybrid Retrieve | Search by meaning (embeddings) *and* exact wording (BM25) — catches cases either method alone would miss |
| Rerank | A more precise model re-scores the top candidates for true relevance |
| Relevance Check | If nothing retrieved is actually relevant, stop here — refuse instead of guessing |
| Generate | The LLM answers using *only* the retrieved chunks |
| Cite | Every answer is returned with the source document and page number |

**Storage**
- **ChromaDB** — chunk embeddings + metadata (vector search)
- **SQLite** — document registry: filenames, status, hashes for duplicate detection

**Serving**
- **FastAPI** backend exposes the pipeline as REST endpoints
- **Custom HTML/CSS/JS** frontend calls the API directly — no framework

## Tech stack

| Component | Tool |
|---|---|
| PDF parsing | PyMuPDF |
| OCR | Tesseract |
| Embeddings | BAAI/bge-small-en-v1.5 |
| Keyword search | BM25 (rank_bm25) |
| Reranking | BAAI/bge-reranker-base (cross-encoder) |
| LLM | Qwen2.5-7B-Instruct (4-bit quantized) |
| Vector DB | ChromaDB |
| Backend | FastAPI |
| Frontend | Vanilla HTML/CSS/JS |

## Getting started

1. Click **Open in Colab** above (or open `Document_Intelligence_Platform.ipynb` directly in this repo).
2. Run the cells top to bottom. First run downloads the models (~10 min for the 7B LLM).
3. You'll need a free [ngrok](https://dashboard.ngrok.com/signup) account and authtoken to get a public URL — the notebook prompts for it.
4. Open the printed URL, upload a document, start asking questions.

Google Drive is mounted for persistent storage (your uploaded documents and vector database survive across sessions). Models are not cached to Drive by default and re-download each fresh session — see `app/config.py` (`use_drive_model_cache`) to change this.

## Known limitations

- The 7B model occasionally gets specific numeric details slightly wrong on dense, list-heavy pages (e.g. off-by-one on a set of scores) — retrieval is accurate, generation isn't perfect
- No conversation memory — each question is answered independently, which keeps grounding reliable but means follow-up questions need full context restated
- No multi-user auth — designed as a single-user tool, not a multi-tenant product
- Citations for TXT/MD/DOCX show "page 1" only, since those formats have no fixed page boundaries (PDF citations are page-accurate)
- Free Colab sessions are ephemeral — the backend needs to be relaunched each time the runtime disconnects

## Possible improvements

- Swap in a larger LLM for better instruction-following on edge cases
- Add conversation memory with careful context-window management
- Support more formats (CSV, XLSX, HTML)
- Deploy outside Colab for persistent uptime
