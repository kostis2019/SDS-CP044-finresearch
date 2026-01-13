# tools/chroma_client_tools.py
# ChromaDB client with singleton pattern for efficient reuse
# ---------------------------------------------

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import Dict

# Singleton cache for ChromaDB collections
_collection_cache: Dict[str, chromadb.Collection] = {}


def get_chroma_client(persist_dir: str = "chroma_db") -> chromadb.Collection:
    """
    Get or create a ChromaDB collection with singleton pattern.
    
    Uses persistent storage and caches the collection to avoid
    recreating clients on every call.
    
    Parameters
    ----------
    persist_dir : str
        Directory for persistent storage (default: "chroma_db")
    
    Returns
    -------
    chromadb.Collection
        The finresearch_memory collection
    """
    global _collection_cache
    
    # Return cached collection if available
    if persist_dir in _collection_cache:
        return _collection_cache[persist_dir]
    
    # Create embedding function
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # Use PersistentClient for actual disk persistence
    # Note: chromadb.Client() with persist_directory is deprecated
    # and doesn't actually persist in newer versions
    try:
        client = chromadb.PersistentClient(path=persist_dir)
    except Exception:
        # Fallback for older chromadb versions
        client = chromadb.Client(
            Settings(
                is_persistent=True,
                persist_directory=persist_dir,
                anonymized_telemetry=False,
            )
        )
    
    # Get or create the collection
    collection = client.get_or_create_collection(
        name="finresearch_memory",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )
    
    # Cache the collection
    _collection_cache[persist_dir] = collection
    
    return collection


def clear_cache():
    """Clear the collection cache. Useful for testing."""
    global _collection_cache
    _collection_cache = {}
