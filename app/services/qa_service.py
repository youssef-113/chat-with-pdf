"""

QAService is the single entry-point used by the UI layer.
It orchestrates FileHandler → TextProcessor → VectorStoreManager → LLMChain.

The UI only needs to call:
    service = QAService()
    answer  = service.answer(question, uploaded_file)
"""

from app.db.vector_store import VectorStoreManager
from app.core.llm import LLMChain
from app.utils.file_handler import FileHandler
from app.utils.text_processor import TextProcessor
from app.utils.logger import logger


class QAService:
    """
    Stateful per-session service.
    Re-builds the index whenever a new file is uploaded.
    """

    def __init__(self) -> None:
        self._vector_store = VectorStoreManager()
        self._llm_chain = LLMChain()
        self._text_processor = TextProcessor()
        self._last_file_name: str | None = None

    # ── Public API ────────────────────────────────────────────────────────

    def answer(self, question: str, uploaded_file) -> str:
        """
        Full pipeline:
          1. Extract text from file (only re-processes if file changed)
          2. Chunk text
          3. Build vector store
          4. Similarity search
          5. Ask LLM and return answer
        """
        self._maybe_index_file(uploaded_file)
        docs = self._vector_store.search(question)
        return self._llm_chain.ask(question, docs)

    # ── Private helpers ───────────────────────────────────────────────────

    def _maybe_index_file(self, uploaded_file) -> None:
        """Re-index only when a new/different file is uploaded."""
        if uploaded_file.name == self._last_file_name:
            logger.debug("Same file detected — skipping re-indexing.")
            return

        logger.info(f"New file '{uploaded_file.name}' — starting indexing pipeline…")

        # Step 1: Extract
        text = FileHandler(uploaded_file).extract()

        # Step 2: Chunk
        chunks = self._text_processor.split(text)

        # Step 3: Index
        self._vector_store.build(chunks)

        self._last_file_name = uploaded_file.name
        logger.info("Indexing complete.")
