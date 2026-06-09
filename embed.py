"""
Milestone 4 — Step 1: Embedding.

Loads chunks from documents/chunks.json, embeds each chunk's text with
sentence-transformers' all-MiniLM-L6-v2, and stores the embeddings in a
local persistent ChromaDB collection along with source metadata
(source_name, source_url, chunk_index) for later attribution.

Usage:
    python embed.py
"""

import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path("documents/chunks.json")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "cse_electives_guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def main():
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Drop any existing collection so re-running this script doesn't duplicate chunks.
    existing = {c.name for c in client.list_collections()}
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c["text"] for c in chunks]
    ids = [f"{c['source_name']}_{c['chunk_index']}" for c in chunks]
    metadatas = [
        {
            "source_name": c["source_name"],
            "source_url": c["source_url"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]

    print("Embedding chunks...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True).tolist()

    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    print(f"\nStored {collection.count()} embeddings in collection '{COLLECTION_NAME}' at ./{CHROMA_DIR}/")


if __name__ == "__main__":
    main()
