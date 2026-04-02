"""
Vector Store for Memory

This module handles storing and retrieving conversation memories using vectors.
It uses Chroma (a vector database) and SentenceTransformers to turn text into
numbers (vectors) so we can find similar past messages.
"""

import os

# Support multiple LangChain versions: langchain (v0.2+), langchain_community, langchain_classic
try:
    from langchain.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        from langchain_classic.vectorstores import Chroma
        from langchain_classic.embeddings import HuggingFaceEmbeddings

# Set up the AI model that turns text into vectors (numbers)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Where to store the vector database files
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./chroma_db")

# Create the vector store (this is like a smart memory box)
vector_store = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)

def add_memory(session_id: str, text: str, metadata: dict = None):
    """Add a piece of text to the memory for a specific session."""
    if metadata is None:
        metadata = {}
    metadata["session_id"] = session_id  # Tag it with the session
    vector_store.add_texts([text], metadatas=[metadata])  # Store it

def retrieve_memory(session_id: str, query: str, k: int = 3):
    """Find similar past memories for a session based on a question."""
    # Search for memories that match the query, only for this session
    results = vector_store.similarity_search(query, k=k, filter={"session_id": session_id})
    # Return just the text of the memories
    return [doc.page_content for doc in results]

def clear_session_memory(session_id: str):
    """Clear all memories for a session (placeholder for now)."""
    # Note: Chroma doesn't easily delete by filter, so this is not implemented yet
    pass