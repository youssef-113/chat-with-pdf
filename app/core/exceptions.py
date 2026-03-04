"""

Custom application exceptions — gives clear error messages
instead of generic Python errors bubbling to the UI.
"""


class DocChatBaseError(Exception):
    """Base for all app errors."""


class UnsupportedFileTypeError(DocChatBaseError):
    def __init__(self, ext: str):
        super().__init__(f"File type '.{ext}' is not supported. Use PDF, DOCX, or TXT.")


class TextExtractionError(DocChatBaseError):
    def __init__(self, filename: str, reason: str):
        super().__init__(f"Could not extract text from '{filename}': {reason}")


class VectorStoreError(DocChatBaseError):
    def __init__(self, reason: str):
        super().__init__(f"Vector store error: {reason}")


class LLMError(DocChatBaseError):
    def __init__(self, reason: str):
        super().__init__(f"LLM error: {reason}")


class ConfigurationError(DocChatBaseError):
    pass
