"""
Milestone 4 — Step 2: Retrieval.

Embeds a query string with the same model used in embed.py
(all-MiniLM-L6-v2) and returns the top-k most similar chunks from the
ChromaDB collection, along with their source metadata and distance scores.

Usage:
    python retrieve.py
"""

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "cse_electives_guide"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

_model = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Return the top-k chunks most relevant to `query`.

    Each result is a dict with keys: text, source_name, source_url,
    chunk_index, distance (cosine distance — lower is more similar).
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query], convert_to_numpy=True).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)

    return [
        {
            "text": text,
            "source_name": meta["source_name"],
            "source_url": meta["source_url"],
            "chunk_index": meta["chunk_index"],
            "distance": dist,
        }
        for text, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]


# Evaluation questions from planning.md, used here to sanity-check retrieval.
TEST_QUERIES = [
    "What do students say about the workload in CSE 320?",
    "Is it a good idea to take CSE 320 and CSE 316 at the same time?",
    "Which upper-division CSE electives do students say are the most useful for getting a job?",
    "What do students say about the difficulty of CSE 306 compared to other electives?",
    "What do students say about whether CSE 316 is practical or project-based?",
    # "How is professor Eugene Stark?",
    # "What do you do in CSE 320?"
]


def main():
    for query in TEST_QUERIES:
        print(f"\n{'=' * 70}")
        print(f"Query: {query}")
        print(f"{'=' * 70}")
        for i, r in enumerate(retrieve(query, k=5), 1):
            print(f"\n[{i}] source={r['source_name']}  chunk_index={r['chunk_index']}  distance={r['distance']:.4f}")
            print(f"    {r['text'][:300]}{'...' if len(r['text']) > 300 else ''}")


if __name__ == "__main__":
    main()
