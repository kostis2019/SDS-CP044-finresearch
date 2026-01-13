# tools/chroma_save_tools.py

import json
from datetime import datetime, timedelta, timezone

from tools.chroma_client_tools import get_chroma_client


def save_to_chroma(
    *,
    ticker: str,
    artifact_type: str,
    content: dict,
    metadata: dict,
    ttl_days: int,
    persist_dir: str = "chroma_db",
) -> None:
    """
    Save a research artifact to ChromaDB with TTL metadata.
    Uses UPSERT to ensure the latest run overwrites previous daily entries.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol (e.g. 'AAPL')
    artifact_type : str
        Type of artifact ('analyst', 'researcher', 'report', etc.)
    content : dict
        Serializable content to store (will be JSON-encoded)
    metadata : dict
        Additional metadata (sector, source_agent, version, etc.)
    ttl_days : int
        Time-to-live in days
    persist_dir : str
        ChromaDB persistence directory
    """

    collection = get_chroma_client(persist_dir=persist_dir)

    # Use timezone-aware UTC timestamps
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=ttl_days)

    # Deterministic document ID (one per day per artifact type)
    doc_id = f"{ticker}:{artifact_type}:{now.date().isoformat()}"

    full_metadata = {
        **metadata,
        "ticker": ticker,
        "artifact_type": artifact_type,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    # UPDATED: Use upsert instead of add to handle re-runs on the same day
    collection.upsert(
        documents=[json.dumps(content, default=str)],
        metadatas=[full_metadata],
        ids=[doc_id],
    )
