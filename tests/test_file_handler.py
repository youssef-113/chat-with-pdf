

import io
import pytest
from unittest.mock import MagicMock
from app.utils.file_handler import FileHandler
from app.core.exceptions import UnsupportedFileTypeError


def _mock_file(name: str, content: bytes) -> MagicMock:
    f = MagicMock()
    f.name = name
    f.read.return_value = content
    return f


def test_txt_extraction():
    content = "Hello, this is a test document."
    mock = _mock_file("sample.txt", content.encode("utf-8"))
    text = FileHandler(mock).extract()
    assert "Hello" in text


def test_unsupported_extension():
    mock = _mock_file("sample.csv", b"a,b,c")
    with pytest.raises(UnsupportedFileTypeError):
        FileHandler(mock).extract()
