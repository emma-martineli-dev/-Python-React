from pathlib import Path

from src.config import STORAGE_DIR

SUSPICIOUS_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".js"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def scan(original_name: str, size: int, mime_type: str) -> tuple[str, str, bool]:
    reasons: list[str] = []
    ext = Path(original_name).suffix.lower()

    if ext in SUSPICIOUS_EXTENSIONS:
        reasons.append(f"suspicious extension {ext}")
    if size > MAX_FILE_SIZE:
        reasons.append("file is larger than 10 MB")
    if ext == ".pdf" and mime_type not in {"application/pdf", "application/octet-stream"}:
        reasons.append("pdf extension does not match mime type")

    return (
        "suspicious" if reasons else "clean",
        ", ".join(reasons) if reasons else "no threats found",
        bool(reasons),
    )


def extract_metadata(stored_name: str, original_name: str, size: int, mime_type: str) -> dict:
    stored_path = STORAGE_DIR / stored_name
    metadata: dict = {
        "extension": Path(original_name).suffix.lower(),
        "size_bytes": size,
        "mime_type": mime_type,
    }
    if mime_type.startswith("text/"):
        content = stored_path.read_text(encoding="utf-8", errors="ignore")
        metadata["line_count"] = len(content.splitlines())
        metadata["char_count"] = len(content)
    elif mime_type == "application/pdf":
        metadata["approx_page_count"] = max(stored_path.read_bytes().count(b"/Type /Page"), 1)
    return metadata
