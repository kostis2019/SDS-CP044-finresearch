from tools.chroma_save_tools import save_to_chroma
from tools.chroma_retrieve_tools import retrieve_from_chroma
from tools.chroma_client_tools import get_chroma_client
import pytest
import chromadb.api.shared_system_client as shared


@pytest.fixture(autouse=True)
def reset_chroma_system():
    """
    Reset ChromaDB global system between tests.
    Prevents 'ephemeral with different settings' error.
    """
    shared.SharedSystemClient._identifier_to_system.clear()
    yield
    shared.SharedSystemClient._identifier_to_system.clear()


DUMMY_ANALYST_OUTPUT = {
    "ticker": "AAPL",
    "final_score": 75,
    "rating": "Buy",
    "scores": {
        "valuation": 60,
        "growth": 80,
        "profitability": 85,
        "technical": 70,
    },
}


def test_save_and_retrieve_valid_artifact(tmp_path):
    persist_dir = str(tmp_path / "chroma_test_db")

    get_chroma_client(persist_dir=persist_dir)

    save_to_chroma(
        ticker="AAPL",
        artifact_type="analyst",
        content=DUMMY_ANALYST_OUTPUT,
        metadata={
            "sector": "Technology",
            "source_agent": "AnalystAgent",
            "version": "v1",
        },
        ttl_days=7,
        persist_dir=persist_dir,
    )

    result = retrieve_from_chroma(
        ticker="AAPL",
        artifact_type="analyst",
        persist_dir=persist_dir,
    )

    assert result is not None
    assert result["content"]["rating"] == "Buy"


def test_expired_artifact_not_returned(tmp_path):
    persist_dir = str(tmp_path / "chroma_test_db")

    get_chroma_client(persist_dir=persist_dir)

    save_to_chroma(
        ticker="AAPL",
        artifact_type="analyst",
        content=DUMMY_ANALYST_OUTPUT,
        metadata={
            "sector": "Technology",
            "source_agent": "AnalystAgent",
            "version": "v1",
        },
        ttl_days=0,
        persist_dir=persist_dir,
    )

    result = retrieve_from_chroma(
        ticker="AAPL",
        artifact_type="analyst",
        allow_expired=False,
        persist_dir=persist_dir,
    )

    assert result is None


def test_allow_expired_artifact(tmp_path):
    persist_dir = str(tmp_path / "chroma_test_db")

    get_chroma_client(persist_dir=persist_dir)

    save_to_chroma(
        ticker="AAPL",
        artifact_type="analyst",
        content=DUMMY_ANALYST_OUTPUT,
        metadata={
            "sector": "Technology",
            "source_agent": "AnalystAgent",
            "version": "v1",
        },
        ttl_days=0,
        persist_dir=persist_dir,
    )

    result = retrieve_from_chroma(
        ticker="AAPL",
        artifact_type="analyst",
        allow_expired=True,
        persist_dir=persist_dir,
    )

    assert result is not None
    assert result["content"]["final_score"] == 75
