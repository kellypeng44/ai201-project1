"""
Milestone 3 — Step 2: Chunking.

Reads every .txt file in documents/raw/, strips the header written by ingest.py,
and splits the text into chunks using LangChain's RecursiveCharacterTextSplitter
with a token-counting function tied to the same model used for embedding
(all-MiniLM-L6-v2, max 256 tokens). Chunk size: 200 tokens, overlap: 25 tokens.

Output: documents/chunks.json — a list of chunk objects, each with:
  - text:        the chunk content
  - source_name: filename stem (e.g. "reddit_cse320_pass")
  - source_url:  original URL
  - chunk_index: position within the source document

Usage:
    python chunk.py
"""

import json
import random
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

RAW_DIR = Path("documents/raw")
OUT_FILE = Path("documents/chunks.json")

# Use the embedding model's own tokenizer so "200 tokens" means exactly what
# all-MiniLM-L6-v2 will see — no approximation needed.
_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")


def token_length(text: str) -> int:
    return len(_tokenizer.encode(text, add_special_tokens=False))


splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=25,
    length_function=token_length,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def load_metadata() -> dict:
    meta_path = RAW_DIR / "metadata.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {}


def parse_raw_file(path: Path) -> tuple[str, str]:
    """Return (source_url, body_text) by stripping the 3-line header ingest.py writes."""
    content = path.read_text(encoding="utf-8")
    if content.startswith("SOURCE_NAME:"):
        lines = content.split("\n", 3)
        # lines[0] = SOURCE_NAME: ...
        # lines[1] = SOURCE_URL: ...
        # lines[2] = ---
        # lines[3] = body
        url = lines[1].removeprefix("SOURCE_URL:").strip()
        body = lines[3] if len(lines) > 3 else ""
    else:
        url = ""
        body = content
    return url, body.strip()


def main():
    metadata = load_metadata()
    all_chunks = []

    txt_files = sorted(f for f in RAW_DIR.glob("*.txt"))
    if not txt_files:
        print("No files found in documents/raw/. Run ingest.py first.")
        return

    print(f"Found {len(txt_files)} source file(s) in documents/raw/\n")

    for path in txt_files:
        source_name = path.stem
        url, body = parse_raw_file(path)
        if not url and source_name in metadata:
            url = metadata[source_name]["url"]

        if not body:
            print(f"  ⚠ {source_name}: empty after stripping header, skipping")
            continue

        raw_chunks = splitter.split_text(body)
        # Filter out chunks that are too short to be meaningful (< 10 tokens)
        raw_chunks = [c for c in raw_chunks if token_length(c) >= 30]

        for i, text in enumerate(raw_chunks):
            all_chunks.append({
                "text": text,
                "source_name": source_name,
                "source_url": url,
                "chunk_index": i,
            })

        print(f"  {source_name}: {len(raw_chunks)} chunks")

    OUT_FILE.write_text(json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{'='*50}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Saved to: {OUT_FILE}")

    if len(all_chunks) < 50:
        print("⚠ Fewer than 50 chunks — consider adding more sources or reducing chunk size.")
    elif len(all_chunks) > 2000:
        print("⚠ More than 2000 chunks — chunks may be too small for useful retrieval.")

    # Print 5 random sample chunks for inspection
    print("\n--- 5 sample chunks (verify these look clean and self-contained) ---")
    samples = random.sample(all_chunks, min(5, len(all_chunks)))
    for i, chunk in enumerate(samples, 1):
        token_count = token_length(chunk["text"])
        print(f"\n[{i}] source={chunk['source_name']}  chunk_index={chunk['chunk_index']}  tokens={token_count}")
        print(f"    {chunk['text'][:300]}{'...' if len(chunk['text']) > 300 else ''}")


if __name__ == "__main__":
    main()
