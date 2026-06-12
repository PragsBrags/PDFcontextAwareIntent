from pathlib import Path
from typing import List
import ollama

from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownTextSplitter


def load_document(file_path: str) -> list:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        return PyPDFLoader(str(file_path)).load()

    if suffix == ".txt":
        return TextLoader(str(file_path), encoding="utf-8").load()

    raise ValueError("Only .pdf and .txt files are supported")


def split_document_chunking(documents: list, strategy: str) -> list:
    if strategy == "recursive":
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
    elif strategy == "markdown":
        text_splitter = MarkdownTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")

    return text_splitter.split_documents(documents)


def embedding_chunks(chunks: List[str], embedding_model: str) -> List[List[float]]:
    """Return embeddings for a list of text chunks using Ollama.

    The Ollama embed API may return a dict with an 'embeddings' key or an
    object attribute; handle both shapes.
    """
    response = ollama.embed(model=embedding_model, input=chunks)

    if isinstance(response, dict) and "embeddings" in response:
        return response["embeddings"]

    # fallback: try attribute-style
    embeddings = getattr(response, "embeddings", None)
    if embeddings is not None:
        return embeddings

    # last resort: return response directly (may already be a list)
    return response

