import os
from typing import Optional


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz) with clean formatting.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        import fitz  # PyMuPDF
        document = fitz.open(file_path)
        pages_text = []

        for page in document:
            text = page.get_text()
            if text and text.strip():
                pages_text.append(text)

        document.close()
        return "\n\n".join(pages_text).strip()

    except ImportError:
        # Fallback if fitz is not installed in the current environment
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            return "\n\n".join([page.extract_text() or "" for page in reader.pages]).strip()
        except Exception:
            # Fallback raw extraction for ascii content
            with open(file_path, "rb") as f:
                content = f.read().decode("latin1", errors="ignore")
                import re
                words = re.findall(r"\((.*?)\)Tj", content)
                if words:
                    return " ".join(words)
                return "Unable to parse PDF: please install PyMuPDF (fitz)."
