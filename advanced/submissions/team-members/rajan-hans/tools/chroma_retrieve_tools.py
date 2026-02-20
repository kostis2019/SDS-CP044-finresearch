# tools/chroma_retrieve_tools.py

from datetime import datetime, timezone
import json

from tools.chroma_client_tools import get_chroma_client


def retrieve_from_chroma(
    *,
    ticker: str,
    artifact_type: str,
    allow_expired: bool = False,
    persist_dir: str = "chroma_db",
):
    """
    Retrieve the latest JSON document for a ticker.

    Returns the parsed content dictionary directly (unwrapped).
    This fixes the compatibility issue with app_service_new.py.
    """
    collection = get_chroma_client(persist_dir=persist_dir)

    results = collection.get(
        where={
            "$and": [
                {"ticker": ticker},
                {"artifact_type": artifact_type},
            ]
        }
    )

    if not results or not results.get("documents"):
        return None

    now = datetime.now(timezone.utc)

    candidates = []
    for doc, meta in zip(results["documents"], results["metadatas"]):
        # Parse dates safely
        try:
            expires_at = datetime.fromisoformat(meta["expires_at"])
            created_at = datetime.fromisoformat(meta["created_at"])
        except (KeyError, ValueError):
            # If metadata is malformed, skip this record
            continue

        # Safety: ensure timezone-aware (should already be true)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        # Check expiration
        if allow_expired or expires_at >= now:
            candidates.append((created_at, doc, meta))

    if not candidates:
        return None

    # Return the most recent valid artifact
    # Sort by created_at (index 0) descending
    candidates.sort(key=lambda x: x[0], reverse=True)

    # Unpack the best candidate
    _, doc, meta = candidates[0]

    # --- THE FIX IS HERE ---
    # Previous version returned: {"content": json.loads(doc), "metadata": meta}
    # New version returns: json.loads(doc) directly.
    # We also inject the metadata into the result just in case, but keep the structure flat.

    try:
        content_dict = json.loads(doc)

        # Optional: verify it's a dict before returning
        if isinstance(content_dict, dict):
            # Inject metadata fields into the top level if they don't exist
            # This is useful for debugging but maintains the flat structure the App expects
            if "_meta_created_at" not in content_dict:
                content_dict["_meta_created_at"] = meta.get("created_at")

            return content_dict

        return content_dict

    except json.JSONDecodeError:
        print(f"Error decoding JSON content for {ticker}")
        return None
