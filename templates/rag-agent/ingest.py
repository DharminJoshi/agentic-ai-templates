"""
ingest.py — RAG Agent Document Ingestion
──────────────────────────────────────────
Handles loading, chunking, and embedding documents
into a ChromaDB vector store.

Supported formats: PDF, TXT, Markdown, DOCX
"""

import os
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def load_document(file_path: str) -> str:
    """
    Load a document from disk and return its text content.

    Supports: .txt, .md, .pdf, .docx
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix in (".txt", ".md"):
        return path.read_text(encoding="utf-8")

    elif suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            raise ImportError("Install pypdf: pip install pypdf")

    elif suffix == ".docx":
        try:
            from docx import Document
            doc = Document(str(path))
            return "\n".join(para.text for para in doc.paragraphs)
        except ImportError:
            raise ImportError("Install python-docx: pip install python-docx")

    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def chunk_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> list[str]:
    """
    Split text into overlapping chunks for better retrieval.

    Args:
        text: Full document text.
        chunk_size: Target characters per chunk.
        chunk_overlap: Characters to overlap between chunks.

    Returns:
        List of text chunks.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to split at a sentence/paragraph boundary
        if end < len(text):
            # Look for a good break point
            for delimiter in ["\n\n", "\n", ". ", " "]:
                split_point = text.rfind(delimiter, start, end)
                if split_point > start:
                    end = split_point + len(delimiter)
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap

    return chunks


def ingest_documents(
    file_paths: list[str],
    collection_name: str = "documents",
    persist_dir: str = "./data/chroma",
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> chromadb.Collection:
    """
    Load, chunk, embed, and store documents in ChromaDB.

    Args:
        file_paths: List of document file paths to ingest.
        collection_name: ChromaDB collection name.
        persist_dir: Directory to persist the vector store.
        chunk_size: Characters per chunk.
        chunk_overlap: Overlap between chunks.

    Returns:
        The populated ChromaDB collection.
    """
    # Initialize ChromaDB
    client = chromadb.PersistentClient(path=persist_dir)

    # Use OpenAI embeddings
    embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
    )

    # Get or create collection
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    console.print(f"[bold]📚 Ingesting {len(file_paths)} document(s)...[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for file_path in file_paths:
            task = progress.add_task(f"Processing {Path(file_path).name}...", total=None)

            try:
                # Load document
                text = load_document(file_path)
                console.log(f"[cyan]Loaded:[/cyan] {file_path} ({len(text):,} chars)")

                # Chunk it
                chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                console.log(f"[cyan]Chunks:[/cyan] {len(chunks)} @ {chunk_size} chars each")

                # Build IDs and metadata
                doc_name = Path(file_path).stem
                ids = [f"{doc_name}_chunk_{i}" for i in range(len(chunks))]
                metadatas = [
                    {"source": file_path, "doc_name": doc_name, "chunk_index": i}
                    for i in range(len(chunks))
                ]

                # Upsert into ChromaDB (handles duplicates gracefully)
                collection.upsert(
                    ids=ids,
                    documents=chunks,
                    metadatas=metadatas,
                )

                progress.update(task, description=f"✅ {Path(file_path).name}")
                console.log(f"[green]✓ Ingested:[/green] {len(chunks)} chunks from {Path(file_path).name}")

            except Exception as e:
                console.log(f"[red]Error ingesting {file_path}:[/red] {e}")
                progress.update(task, description=f"❌ {Path(file_path).name}")

    total = collection.count()
    console.print(f"\n[bold green]✅ Collection '{collection_name}' now has {total} chunks.[/bold green]")

    return collection
