
import pytest
from app.utils.text_processor import TextProcessor


def test_split_returns_chunks():
    processor = TextProcessor(chunk_size=100, chunk_overlap=20)
    long_text = "word " * 300
    chunks = processor.split(long_text)
    assert len(chunks) > 1


def test_split_empty_raises():
    processor = TextProcessor()
    with pytest.raises(ValueError):
        processor.split("   ")
