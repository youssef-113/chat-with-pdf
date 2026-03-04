"""

Splits raw text into chunks suitable for embedding.
Keeps chunking logic isolated so it can be swapped easily.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
from app.core.logger import logger


class TextProcessor:
    """
    Converts a long string of text into a list of overlapping chunks.

    Usage:
        processor = TextProcessor()
        chunks = processor.split(raw_text)
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.chunking.chunk_size,
            chunk_overlap=chunk_overlap or settings.chunking.chunk_overlap,
        )

    def split(self, text: str) -> list[str]:
        if not text or not text.strip():
            raise ValueError("Cannot split empty text.")
        chunks = self._splitter.split_text(text)
        logger.info(f"Text split into {len(chunks)} chunks.")
        return chunks
