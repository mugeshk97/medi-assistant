"""PDF ingestion module using PyMuPDF."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def ingest_pdf(
    file_path: str | Path, chunk_size: int = 4000, chunk_overlap: int = 500
) -> list[Document]:
    """
    Load and chunk a PDF document.

    Args:
        file_path: Path to the PDF file.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks for context continuity.

    Returns:
        A list of LangChain Document objects, each with page content and metadata
        (including source page number).
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    if not file_path.suffix.lower() == ".pdf":
        raise ValueError(f"File is not a PDF: {file_path}")

    # Load PDF — PyMuPDFLoader returns one Document per page with page metadata
    loader = PyMuPDFLoader(str(file_path))
    raw_docs = loader.load()

    if not raw_docs:
        raise ValueError("PDF appears to be empty or could not be parsed.")

    # Split into smaller chunks while preserving page metadata
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(raw_docs)

    logger.info(
        f"Loaded {len(raw_docs)} pages -> {len(chunks)} chunks from '{file_path.name}'"
    )
    return chunks
