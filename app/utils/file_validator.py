import os
from pathlib import Path
from typing import Tuple

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md'}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB


def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """Validates if filename has an accepted document extension."""
    if not filename:
        return False, "Filename cannot be empty"

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"

    return True, ext


def get_file_size(file_path: str) -> int:
    """Returns size of file in bytes, or 0 if file does not exist."""
    p = Path(file_path)
    return p.stat().st_size if p.exists() else 0
