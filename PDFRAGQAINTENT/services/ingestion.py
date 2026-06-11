import ollama

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter,
MarkdownTextSplitter

def load_document_pdf(file):
    document = PyPDFLoader(file)
    
    return document.load()

def load_document_txt(file):
    with open(file, 'r') as f:
        content = f.read()
    
    return content

def split_document_chunking(document, strategy):
    if strategy == "recursive":
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
            is_seperator_regex=False,
        )
    elif strategy == "markdown":
        text_splitter = MarkdownTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            length_function=len,
            is_seperator_regex=False,
        )
    
    return text_splitter.split_documents(document)

def embedding_chunks(chunks, embedding_model):
    embeddings = ollama.embed(
        model = embedding_model,
        input = chunk.page_content
        )
    
    return embeddings

