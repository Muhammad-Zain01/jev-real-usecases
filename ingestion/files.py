"""Convert uploaded resume files into text before sending them to Jev."""

from pathlib import Path


def extract_text(file_path: str | Path) -> str:
    """Extract text from a TXT, PDF, or DOCX file."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    if suffix == ".docx":
        from docx import Document

        document = Document(str(path))
        return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()

    raise ValueError("Unsupported file type. Use .txt, .pdf, or .docx.")
