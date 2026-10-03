import pytest
from app.utils.text_cleaner import clean_text, normalize_term, extract_keywords_from_text
from app.utils.file_validator import validate_file_extension


def test_clean_text():
    dirty = "Line 1   \r\n\r\n\r\n   Line 2\t\twith spaces"
    cleaned = clean_text(dirty)
    assert "Line 1" in cleaned
    assert "Line 2" in cleaned
    assert "\r" not in cleaned


def test_normalize_term():
    assert normalize_term("• Python") == "python"
    assert normalize_term("- FastAPI  ") == "fastapi"
    assert normalize_term("* Docker") == "docker"


def test_extract_keywords():
    text = "We need Python, FastAPI, Docker, and PostgreSQL experience. Python is critical."
    keywords = extract_keywords_from_text(text)
    assert "python" in keywords
    assert keywords["python"] == 2
    assert "fastapi" in keywords


def test_validate_file_extension():
    assert validate_file_extension("resume.pdf")[0] is True
    assert validate_file_extension("resume.docx")[0] is True
    assert validate_file_extension("resume.txt")[0] is True
    assert validate_file_extension("image.png")[0] is False
