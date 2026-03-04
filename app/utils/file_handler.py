"""

Responsible only for reading uploaded files and returning
their raw text content. Supports PDF, DOCX, TXT.
"""

import io
import pdfplumber
from docx import Document
from app.core.exceptions import UnsupportedFileTypeError, TextExtractionError
from app.utils.logger import logger

SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}


def _get_extension(filename: str) -> str:
    """Return lowercase extension without the dot."""
    _, ext = filename.rsplit(".", 1) if "." in filename else ("", "")
    return ext.lower()


class FileHandler:
    """
    Extracts plain text from uploaded Streamlit file objects.

    Usage:
        handler = FileHandler(uploaded_file)
        text = handler.extract()
    """

    def __init__(self, uploaded_file) -> None:
        self._file = uploaded_file
        self._ext = _get_extension(uploaded_file.name)

    def extract(self) -> str:
        """
        Dispatch to the correct extractor and return the full text.
        Raises UnsupportedFileTypeError or TextExtractionError on failure.
        """
        if self._ext not in SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(self._ext)

        logger.info(f"Extracting text from '{self._file.name}' (type={self._ext})")

        try:
            if self._ext == "pdf":
                return self._extract_pdf()
            elif self._ext == "docx":
                return self._extract_docx()
            elif self._ext == "txt":
                return self._extract_txt()
        except (UnsupportedFileTypeError, TextExtractionError):
            raise
        except Exception as exc:
            raise TextExtractionError(self._file.name, str(exc)) from exc

    # ── Private extractors ────────────────────────────────────────────────

    def _extract_pdf(self) -> str:
        raw = self._file.read()
        pages_text = []
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
        if not pages_text:
            raise TextExtractionError(self._file.name, "No readable text found in PDF.")
        return "\n".join(pages_text)

    def _extract_docx(self) -> str:
        raw = self._file.read()
        doc = Document(io.BytesIO(raw))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        if not paragraphs:
            raise TextExtractionError(self._file.name, "DOCX file appears to be empty.")
        return "\n".join(paragraphs)

    def _extract_txt(self) -> str:
        raw = self._file.read()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")
