"""
Milestone 5 — Step 1: Generation.

Takes a user query, retrieves the top-k relevant chunks via retrieve.py,
builds a grounded prompt, and calls Groq's llama-3.3-70b-versatile to
produce an answer that is restricted to the retrieved context.

Source attribution is NOT left to the model: ask() always returns the
deduplicated list of source_names that were actually retrieved, so the
UI can display "Retrieved from" regardless of what the LLM writes.

Usage:
    python generate.py
"""

import os

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

# Exact refusal sentence the model must use when the context is insufficient.
# Checked against the model's output (case-insensitively) so the UI can hide
# the source list when nothing actually grounded the answer.
NO_INFO_RESPONSE = "I don't have enough information on that."

SYSTEM_PROMPT = f"""You are a course-and-professor advisor for the "Unofficial Guide to \
Stony Brook CSE Electives," built from student reviews (Reddit, Rate My \
Professors, Coursicle) and official course/faculty pages.

You will be given a CONTEXT section made of numbered excerpts, each tagged \
with the document it came from, followed by a QUESTION.

Follow these rules exactly:
1. Answer using ONLY information found in the CONTEXT below. Do not use any \
outside knowledge, training data, or assumptions about Stony Brook, CSE \
courses, or professors — even if you believe you know the answer.
2. When you state a fact, name the source it came from inline, e.g. \
"(source: rmp_eugene_stark)", using the exact source tags shown in CONTEXT.
3. If the CONTEXT does not contain enough information to answer the \
QUESTION, respond with EXACTLY this sentence and nothing else: \
"{NO_INFO_RESPONSE}"
4. Never fill gaps with general knowledge, speculation, or "typically" / \
"usually" style reasoning that isn't grounded in the CONTEXT."""


_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY not set. Copy .env.example to .env and add your key."
            )
        _client = Groq(api_key=api_key)
    return _client


def _build_context(chunks: list[dict]) -> str:
    blocks = []
    for i, c in enumerate(chunks, 1):
        blocks.append(f"[{i}] (source: {c['source_name']})\n{c['text']}")
    return "\n\n".join(blocks)


def _is_no_info(answer: str) -> bool:
    return NO_INFO_RESPONSE.lower().rstrip(".") in answer.lower()


def ask(query: str, k: int = 5) -> dict:
    """Run the full retrieve -> generate pipeline for `query`.

    Returns a dict with:
      - answer:  the model's grounded response (str)
      - sources: deduplicated source_names of the retrieved chunks, in
                  retrieval order. Empty if the model declined to answer
                  (i.e. the context wasn't relevant enough).
      - chunks:  the raw retrieved chunks, for debugging/inspection
    """
    chunks = retrieve(query, k=k)
    context = _build_context(chunks)

    user_message = (
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {query}\n\n"
        "Answer the QUESTION using only the CONTEXT above, following the rules "
        "in the system prompt."
    )

    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
    )
    answer = response.choices[0].message.content.strip()

    if _is_no_info(answer):
        sources = []
    else:
        seen = set()
        sources = []
        for c in chunks:
            if c["source_name"] not in seen:
                seen.add(c["source_name"])
                sources.append(c["source_name"])

    return {"answer": answer, "sources": sources, "chunks": chunks}


def main():
    from retrieve import TEST_QUERIES

    test_questions = TEST_QUERIES + [
        "What is the dining hall food like at Stony Brook?",
    ]

    for q in test_questions:
        print(f"\n{'=' * 70}")
        print(f"Q: {q}")
        print(f"{'=' * 70}")
        result = ask(q)
        print(f"\nA: {result['answer']}")
        print(f"\nSources: {', '.join(result['sources']) or '(none)'}")


if __name__ == "__main__":
    main()
