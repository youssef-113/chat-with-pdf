<div align="center">

# 📚 Chat with PDF

**A production-grade RAG application that lets you have intelligent conversations with your PDF documents.**

Upload a PDF, Word document, or plain text file — then ask anything about it.  

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-1C3C3C?style=flat-square)](https://langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=flat-square)](https://console.groq.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)


</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Supported File Types](#supported-file-types)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Option A — Conda (recommended for local dev)](#option-a--conda-recommended-for-local-dev)
  - [Option B — Docker (recommended for production)](#option-b--docker-recommended-for-production)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Chat with Docs is a **Retrieval-Augmented Generation (RAG)** system built for production use.  
It extracts text from your documents, indexes it into a FAISS vector store, and answers your questions using a Groq-hosted LLaMA 3.3 model — all through a clean, dark-themed Streamlit interface.

The codebase is organized into well-separated layers (extraction → chunking → indexing → LLM) so every component can be tested, swapped, or scaled independently.

---

## Features

- **Multi-format support** — PDF, DOCX, and TXT files
- **Intelligent chunking** — overlapping text windows preserve context across chunk boundaries
- **Fast similarity search** — FAISS in-memory index, rebuilt only when a new file is uploaded
- **Groq LLM** — LLaMA 3.3 70B for high-quality, fast answers
- **Persistent chat history** — full conversation thread within a session
- **Production-ready** — structured logging, custom exceptions, typed config, Docker support
- **Tested** — unit tests for all core utilities

---

## Architecture

```
User uploads file
       │
       ▼
 ┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
 │ FileHandler │────▶│  TextProcessor   │────▶│ VectorStoreMgr   │
 │  (extract)  │     │  (chunk/split)   │     │  (FAISS index)   │
 └─────────────┘     └──────────────────┘     └────────┬─────────┘
                                                        │  similarity_search()
                                               ┌────────▼─────────┐
                                               │    LLMChain      │
                                               │  (Groq + prompt) │
                                               └────────┬─────────┘
                                                        │
                                               ┌────────▼─────────┐
                                               │    QAService     │  ◀── UI calls only this
                                               │  (orchestrator)  │
                                               └──────────────────┘
```

The UI layer (`streamlit_app.py`) only ever calls `QAService.answer()` — it is completely decoupled from the underlying pipeline.

---

## Supported File Types

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based PDFs; scanned PDFs require OCR preprocessing |
| Word Document | `.docx` | Extracts paragraph text; tables and headers included |
| Plain Text | `.txt` | UTF-8 and Latin-1 encodings |

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Groq API Key** | Free at [console.groq.com](https://console.groq.com) |
| **Conda** *(Option A)* | [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/) |
| **Docker + Docker Compose** *(Option B)* | Docker Desktop or Docker Engine ≥ 24 |

---

## Installation

### Option A — Conda (recommended for local dev)

Conda creates a fully isolated Python environment and handles system-level dependencies cleanly.

**1. Clone the repository**

```bash
git clone https://github.com/your-username/chat-with-docs.git
cd chat-with-docs
```

**2. Create the Conda environment**

```bash
conda create -n chat-docs python=3.11 -y
```

**3. Activate the environment**

```bash
conda activate chat-docs
```

> You should see `(chat-docs)` appear at the start of your terminal prompt.

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Configure your environment variables**

```bash
cp .env.example .env
```

Open `.env` in your editor and set your Groq API key:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**6. Run the app**

```bash
streamlit run app/ui/streamlit_app.py
```

The app will open automatically at **http://localhost:8501**

---

**To deactivate the environment when done:**

```bash
conda deactivate
```

**To remove the environment entirely:**

```bash
conda remove -n chat-docs --all -y
```

---

### Option B — Docker (recommended for production)

Docker packages the entire application — Python, dependencies, and config — into a portable container. No local Python setup required.

**1. Clone the repository**

```bash
git clone https://github.com/your-username/chat-with-docs.git
cd chat-with-docs
```

**2. Configure your environment variables**

```bash
cp .env.example .env
```

Open `.env` and set your Groq API key:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**3. Build and start the container**

```bash
docker compose up --build
```

> The first build downloads the base image and installs all packages — this takes 2–5 minutes.  
> Subsequent starts use the cached image and launch in seconds.

**4. Open the app**

Navigate to **http://localhost:8501** in your browser.

---

**Run in the background (detached mode):**

```bash
docker compose up --build -d
```

**View live logs:**

```bash
docker compose logs -f
```

**Stop the container:**

```bash
docker compose down
```

**Rebuild after code changes:**

```bash
docker compose up --build
```

---

## Configuration

All settings live in `.env`. Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Required | Description |
|---|---|---|---|
| `GROQ_API_KEY` | — | ✅ Yes | Your Groq API key from [console.groq.com](https://console.groq.com) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | No | Groq model name |
| `LLM_TEMPERATURE` | `0.3` | No | Response creativity (0 = precise, 1 = creative) |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | No | HuggingFace embedding model |
| `CHUNK_SIZE` | `1000` | No | Characters per text chunk |
| `CHUNK_OVERLAP` | `200` | No | Overlap between consecutive chunks |
| `FAISS_INDEX_PATH` | `./data/faiss_index` | No | Where to persist the vector index |
| `LOG_LEVEL` | `INFO` | No | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

> ⚠️ Never commit your `.env` file. It is already listed in `.gitignore`.

---

## Running the App

### Conda

```bash
conda activate chat-docs
streamlit run app/ui/streamlit_app.py
```

### Docker

```bash
docker compose up
```

Both methods serve the app at **http://localhost:8501**.

---

## Project Structure

```
chat-with-docs/
│
├── app/
│   ├── core/
│   │   ├── config.py          # Typed settings loaded from .env
│   │   ├── exceptions.py      # Custom application exceptions
│   │   ├── logger.py          # Structured logging via loguru
│   │   ├── vector_store.py    # FAISS index: build, search, save, load
│   │   ├── llm_chain.py       # Groq LLM + LangChain QA chain
│   │   └── qa_service.py      # Main orchestrator — UI entry point
│   │
│   ├── utils/
│   │   ├── file_handler.py    # PDF / DOCX / TXT text extraction
│   │   └── text_processor.py  # Recursive text chunking
│   │
│   └── ui/
│       └── streamlit_app.py   # Streamlit frontend
│
├── tests/
│   ├── test_file_handler.py
│   └── test_text_processor.py
│
├── data/                      # FAISS index (auto-created, gitignored)
├── logs/                      # Log files (auto-created, gitignored)
│
├── .env.example               # Environment variable template
├── .env                       # Your local config (gitignored)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Service orchestration
└── README.md
```

---

## Running Tests

```bash
# Conda
conda activate chat-docs
pytest tests/ -v

# Docker
docker compose run --rm chat-with-docs pytest tests/ -v
```

---


## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push to your fork: `git push origin feature/my-feature`
5. Open a Pull Request

Please make sure all existing tests pass and add tests for any new behaviour.

---

## License

This project is licensed under the **Youssef bassiony** 

---

