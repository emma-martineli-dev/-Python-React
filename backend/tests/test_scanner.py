import pytest
from src.services.scanner import scan, SUSPICIOUS_EXTENSIONS, MAX_FILE_SIZE


def test_clean_file():
    status, details, attention = scan("report.pdf", 1024, "application/pdf")
    assert status == "clean"
    assert attention is False
    assert details == "no threats found"


@pytest.mark.parametrize("ext", SUSPICIOUS_EXTENSIONS)
def test_suspicious_extension(ext):
    status, details, attention = scan(f"file{ext}", 1024, "application/octet-stream")
    assert status == "suspicious"
    assert attention is True
    assert ext in details


def test_file_too_large():
    status, details, attention = scan("big.txt", MAX_FILE_SIZE + 1, "text/plain")
    assert status == "suspicious"
    assert attention is True
    assert "larger than 10 MB" in details


def test_pdf_mime_mismatch():
    status, details, attention = scan("doc.pdf", 1024, "text/html")
    assert status == "suspicious"
    assert attention is True
    assert "mime type" in details


def test_pdf_correct_mime():
    status, details, attention = scan("doc.pdf", 1024, "application/pdf")
    assert status == "clean"
    assert attention is False


def test_multiple_reasons():
    status, details, attention = scan("evil.exe", MAX_FILE_SIZE + 1, "application/octet-stream")
    assert status == "suspicious"
    assert attention is True
    assert ".exe" in details
    assert "larger than 10 MB" in details
