import re
import zipfile
from html import unescape
from pathlib import Path
from xml.etree import ElementTree as ET

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

from app.core.config import settings


OFFICE_XML_EXTENSIONS = {".docx", ".pptx", ".xlsx"}
PLAIN_TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".xml",
    ".html",
    ".htm",
    ".css",
    ".js",
    ".ts",
    ".py",
    ".java",
    ".c",
    ".cpp",
    ".cs",
    ".php",
    ".rb",
    ".go",
    ".rs",
    ".sql",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".conf",
    ".log",
    ".rtf",
}


def ensure_upload_dir() -> Path:
    """Creates the upload folder if it does not exist."""
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


async def save_upload_file(upload_file: UploadFile) -> Path:
    """Stores an uploaded file on disk."""
    ensure_upload_dir()
    filename = Path(upload_file.filename or "").name
    if not filename:
        raise HTTPException(status_code=400, detail="Please choose a valid file.")

    content = await upload_file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File is too large. Maximum size is {settings.max_upload_size_mb} MB.",
        )

    file_path = Path(settings.upload_dir) / filename
    file_path.write_bytes(content)
    return file_path


def read_text_file(file_path: Path) -> str:
    """Attempts to read a file as plain text using common encodings."""
    encodings = ("utf-8", "utf-16", "latin-1")
    for encoding in encodings:
        try:
            return file_path.read_text(encoding=encoding, errors="ignore").strip()
        except Exception:
            continue
    return ""


def normalize_office_text(chunks: list[str]) -> str:
    cleaned = [unescape(re.sub(r"\s+", " ", chunk)).strip() for chunk in chunks]
    return "\n".join(chunk for chunk in cleaned if chunk).strip()


def extract_docx_text(file_path: Path) -> str:
    chunks: list[str] = []
    with zipfile.ZipFile(file_path) as archive:
        with archive.open("word/document.xml") as document:
            tree = ET.parse(document)
            chunks = [node.text or "" for node in tree.iter() if node.text]
    return normalize_office_text(chunks)


def extract_pptx_text(file_path: Path) -> str:
    chunks: list[str] = []
    with zipfile.ZipFile(file_path) as archive:
        slide_files = sorted(
            [name for name in archive.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")]
        )
        for slide_name in slide_files:
            with archive.open(slide_name) as slide:
                tree = ET.parse(slide)
                chunks.extend(node.text or "" for node in tree.iter() if node.text)
    return normalize_office_text(chunks)


def extract_xlsx_text(file_path: Path) -> str:
    chunks: list[str] = []
    with zipfile.ZipFile(file_path) as archive:
        shared_strings = {}
        if "xl/sharedStrings.xml" in archive.namelist():
            with archive.open("xl/sharedStrings.xml") as shared:
                tree = ET.parse(shared)
                index = 0
                for item in tree.iter():
                    if item.text and item.text.strip():
                        shared_strings[str(index)] = item.text.strip()
                        index += 1

        sheet_files = sorted(
            [name for name in archive.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")]
        )
        for sheet_name in sheet_files:
            with archive.open(sheet_name) as sheet:
                tree = ET.parse(sheet)
                for cell in tree.iter():
                    if cell.tag.endswith("v") and cell.text:
                        chunks.append(shared_strings.get(cell.text.strip(), cell.text.strip()))
    return normalize_office_text(chunks)


def extract_text_fallback(file_path: Path) -> str:
    raw_bytes = file_path.read_bytes()
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text = raw_bytes.decode(encoding, errors="ignore").strip()
        except Exception:
            continue
        printable = sum(char.isprintable() or char.isspace() for char in text)
        if text and printable / max(len(text), 1) > 0.8:
            return text
    return ""


def extract_text_from_file(file_path: Path) -> str:
    """Extracts readable text from common document and text-based file formats."""
    extension = file_path.suffix.lower()

    if extension in PLAIN_TEXT_EXTENSIONS:
        return read_text_file(file_path)

    if extension == ".pdf":
        reader = PdfReader(str(file_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()

    if extension == ".docx":
        return extract_docx_text(file_path)

    if extension == ".pptx":
        return extract_pptx_text(file_path)

    if extension == ".xlsx":
        return extract_xlsx_text(file_path)

    fallback_text = extract_text_fallback(file_path)
    if fallback_text:
        return fallback_text

    raise HTTPException(
        status_code=400,
        detail="This file could not be read as text. Try a text-based file, PDF, DOCX, PPTX, or XLSX.",
    )
