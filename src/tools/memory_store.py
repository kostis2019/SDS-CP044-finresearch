#import os
from pathlib import Path
import sys
import chromadb
from chromadb.utils import embedding_functions

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_config

# 1. SETUP: Define where the memory lives
# "persistent" means it saves to your hard drive, so agents remember things 
# even if you restart the script.
DATA_PATH = "./internal_memory_db"

class FinancialMemory:
    def __init__(self, collection_name="financial_research"):
        """
        Initialize the Vector Database.
        """
        print(f"🧠 Initializing Memory: {collection_name}")
        
        # Connect to ChromaDB (it creates the folder if it doesn't exist)
        self.client = chromadb.PersistentClient(path=DATA_PATH)
        
        # Use OpenAI's embedding model (standard for this project)
        # Ensure OPENAI_API_KEY is set in your .env file
        config = get_config()
        openai_api_key = config["openai_api_key"]

        self.openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key, ##os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small" # Cheaper and faster
        )

        # Create or Get the collection (like a 'table' in SQL)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.openai_ef
        )

    def save_context(self, text: str, metadata: dict):
        """
        The Researcher uses this to 'Save' a finding.
        Args:
            text: The actual content (e.g., news snippet).
            metadata: Extra info (e.g., {'source': 'Bloomberg', 'ticker': 'AAPL'})
        """
        # We need a unique ID for every entry. We can generate one based on the count.
        # In a real app, use UUIDs. Here, simplistic counting works for demos.
        doc_id = f"doc_{self.collection.count() + 1}"
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        print(f"💾 Saved to memory: {text[:30]}...")

    def query_memory(self, query: str, n_results=3):
        """
        The Analyst/Reporter uses this to 'Recall' info.
        Args:
            query: The question (e.g., "What are the risks for Tesla?")
            n_results: How many relevant snippets to return.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Chroma returns a complex object; let's simplify it for the Agent
        # It returns lists of lists, so we flatten it.
        found_texts = results['documents'][0]
        return "\n\n".join(found_texts)

# Simple test to run if you execute this file directly
if __name__ == "__main__":
    mem = FinancialMemory()
    mem.save_context("Tesla Q3 revenue grew by 20% year over year.", {"ticker": "TSLA"})
    print("Querying:", mem.query_memory("How did Tesla do financially?"))