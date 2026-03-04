"""
vector_store.py
───────────────
Manages FAISS vector store: building from chunks and querying.
Embeddings are cached so the model is only loaded once per session.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document as LCDocument
from app.config.config import settings
from app.core.exceptions import VectorStoreError
from app.utils.logger import logger


class VectorStoreManager:
    """
    Encapsulates FAISS index creation and similarity search.

    Usage:
        vsm = VectorStoreManager()
        vsm.build(chunks)
        docs = vsm.search("your question")
    """

    _embeddings: HuggingFaceEmbeddings | None = None  # class-level cache

    def __init__(self) -> None:
        self._store: FAISS | None = None
        self._embeddings = self._get_embeddings()

    # ── Public API ────────────────────────────────────────────────────────

    def build(self, text_chunks: list[str]) -> None:
        """Build a fresh in-memory FAISS index from text chunks."""
        if not text_chunks:
            raise VectorStoreError("Cannot build vector store from empty chunk list.")
        try:
            logger.info(f"Building FAISS index with {len(text_chunks)} chunks...")
            self._store = FAISS.from_texts(texts=text_chunks, embedding=self._embeddings)
            logger.info("FAISS index built successfully.")
        except Exception as exc:
            raise VectorStoreError(str(exc)) from exc

    def search(self, query: str, k: int = 4) -> list[LCDocument]:
        """Return top-k most similar documents for a query."""
        if self._store is None:
            raise VectorStoreError("Vector store has not been built yet. Call build() first.")
        try:
            results = self._store.similarity_search(query, k=k)
            logger.debug(f"Similarity search for '{query[:60]}…' returned {len(results)} docs.")
            return results
        except Exception as exc:
            raise VectorStoreError(str(exc)) from exc

    def save(self, path: str | None = None) -> None:
        """Persist index to disk (optional)."""
        if self._store is None:
            raise VectorStoreError("Nothing to save — build() has not been called.")
        target = path or settings.vector_store.index_path
        os.makedirs(target, exist_ok=True)
        self._store.save_local(target)
        logger.info(f"FAISS index saved to '{target}'.")

    def load(self, path: str | None = None) -> None:
        """Load a previously saved index from disk."""
        target = path or settings.vector_store.index_path
        if not os.path.exists(target):
            raise VectorStoreError(f"No saved index found at '{target}'.")
        self._store = FAISS.load_local(
            target, self._embeddings, allow_dangerous_deserialization=True
        )
        logger.info(f"FAISS index loaded from '{target}'.")

    # ── Private helpers ───────────────────────────────────────────────────

    @classmethod
    def _get_embeddings(cls) -> HuggingFaceEmbeddings:
        """Singleton-style: load the embedding model once."""
        if cls._embeddings is None:
            logger.info(f"Loading embedding model '{settings.embedding.model_name}'…")
            cls._embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding.model_name
            )
            logger.info("Embedding model loaded.")
        return cls._embeddings
