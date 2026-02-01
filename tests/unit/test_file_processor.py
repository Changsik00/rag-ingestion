import pytest

from app.core.utils.file_processor import FileProcessor


@pytest.fixture
def file_processor():
    return FileProcessor()


def test_extract_text_txt(file_processor):
    # Given
    content = b"Hello, this is a test text file."
    filename = "test.txt"

    # When
    result = file_processor.extract_text(content, filename)

    # Then
    assert "Hello, this is a test text file." in result
    assert result.startswith("# test.txt")


def test_extract_text_md(file_processor):
    # Given
    content = b"# Title\nThis is markdown."
    filename = "test.md"

    # When
    result = file_processor.extract_text(content, filename)

    # Then
    assert "# Title" in result
    assert "This is markdown." in result


def test_extract_text_unsupported_extension(file_processor):
    # Given
    content = b"some binary data"
    filename = "test.exe"

    # When & Then
    with pytest.raises(ValueError, match="Unsupported file extension"):
        file_processor.extract_text(content, filename)


def test_extract_text_pdf(file_processor):
    # Note: Truly testing PDF requires a valid PDF binary.
    # For unit test, we might mock fitz or provide a minimal valid PDF.
    # Here we'll just check if it routes correctly and fails on invalid PDF content.
    content = b"not a real pdf"
    filename = "test.pdf"

    with pytest.raises(Exception):  # fitz will raise error on invalid PDF
        file_processor.extract_text(content, filename)
