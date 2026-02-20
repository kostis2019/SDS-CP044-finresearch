# inspect_db.py
import json
from tools.chroma_client_tools import get_chroma_client


def inspect_chroma():
    print("--- 🔍 Inspecting ChromaDB Content ---")

    try:
        # The function returns the collection directly
        collection = get_chroma_client()

        # Fetch all data
        data = collection.get()

        ids = data["ids"]
        metadatas = data["metadatas"]
        documents = data["documents"]

        count = len(ids)
        print(f"✅ Found {count} records in database.\n")

        if count == 0:
            print("Database is empty.")
            return

        # Print the most recent 3 records
        for i in range(count):
            print(f"📄 Record ID: {ids[i]}")
            print(f"   📂 Metadata: {metadatas[i]}")

            # Show a snippet of the stored document content
            content_preview = (
                documents[i][:200] + "..." if len(documents[i]) > 200 else documents[i]
            )
            print(f"   💾 Document Content (First 200 chars): {content_preview}")

            # Try to parse the document to see if 'final_score' is inside
            try:
                doc_json = json.loads(documents[i])
                score = doc_json.get("final_score")
                print(f"   ✅ Parsed 'final_score' from Document: {score}")
            except:
                print(f"   ❌ Could not parse Document as JSON")

            print("-" * 50)

    except Exception as e:
        print(f"❌ Error inspecting DB: {e}")


if __name__ == "__main__":
    inspect_chroma()
