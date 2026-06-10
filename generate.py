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

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

# Exact refusal sentence the model must use when the context is insufficient.
# Checked against the model's output (case-insensitively) so the UI can hide
# the source list when nothing actually grounded the answer.
NO_INFO_RESPONSE = "I don't have enough information on that."

# documents/raw/metadata.json carries human-written descriptions for most
# top-level sources (catalog pages, course-specific Coursicle/Reddit threads).
_METADATA_FILE = Path("documents/raw/metadata.json")
_DESCRIPTIONS = (
    {k: v["description"] for k, v in json.loads(_METADATA_FILE.read_text(encoding="utf-8")).items()}
    if _METADATA_FILE.exists()
    else {}
)

def display_name(source_name: str) -> str:
    """Human-readable label for a source_name, used for citations and the UI.

    Falls back to a generated label for the per-professor RMP/Coursicle
    pages, which aren't listed in metadata.json.
    """
    if source_name in _DESCRIPTIONS:
        return _DESCRIPTIONS[source_name]

    if source_name.startswith("rmp_"):
        person = source_name.removeprefix("rmp_").replace("_", " ").title()
        return f"RateMyProfessors — {person}"

    if source_name.startswith("coursicle_"):
        person = source_name.removeprefix("coursicle_").replace("_", " ").title()
        return f"Coursicle — {person}"

    return source_name

SYSTEM_PROMPT = f"""You are a course-and-professor advisor for the "Unofficial Guide to \
Stony Brook CSE Electives," built from student reviews (Reddit, Rate My \
Professors, Coursicle) and official course/faculty pages.

You will be given a CONTEXT section made of numbered excerpts, each tagged \
with the document it came from, followed by a QUESTION.

Follow these rules exactly:
1. Answer using ONLY information found in the CONTEXT below. Do not use any \
outside knowledge, training data, or assumptions about Stony Brook, CSE \
courses, or professors — even if you believe you know the answer.
2. When you state a fact, name the source it came from inline using the \
exact "(source: ...)" tag shown above that excerpt in CONTEXT, e.g. \
"(source: RateMyProfessors — Eugene Stark)".
3. If the CONTEXT does not contain enough information to answer the \
QUESTION, respond with EXACTLY this sentence and nothing else: \
"{NO_INFO_RESPONSE}"
4. Never fill gaps with general knowledge, speculation, or "typically" / \
"usually" style reasoning that isn't grounded in the CONTEXT.
5. Write as if you're directly answering the user — never refer to "the \
CONTEXT", "the context", "the documents", "the provided excerpts", "the \
provided information", or similar meta-language describing this prompt's \
structure. State the information directly and let the inline source tags \
carry the attribution.
6. Answer with only what is actually said. Do not add disclaimers, caveats, \
or wrap-up sentences about what else isn't covered (e.g. do not write \
anything like "no other electives are mentioned" or "this is the only \
information available"). If that's all there is, just stop after stating it.
7. Most excerpts are student opinions (Reddit, RateMyProfessors, Coursicle), \
not established facts — phrase these as reported opinions, e.g. "Some \
students say CSE 356 is useful for getting a job (source: ...)" rather than \
"CSE 356 is useful for getting a job." Information from official course or \
faculty pages can be stated directly."""


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
        blocks.append(f"[{i}] (source: {display_name(c['source_name'])})\n{c['text']}")
    return "\n\n".join(blocks)


def _is_no_info(answer: str) -> bool:
    return NO_INFO_RESPONSE.lower().rstrip(".") in answer.lower()


def ask(query: str, k: int = 5) -> dict:
    """Run the full retrieve -> generate pipeline for `query`.

    Returns a dict with:
      - answer:  the model's grounded response (str)
      - sources: deduplicated {"name": <readable label>, "url": <source_url>}
                  dicts for the retrieved chunks, in retrieval order. Empty
                  if the model declined to answer (i.e. the context wasn't
                  relevant enough).
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
                sources.append({"name": display_name(c["source_name"]), "url": c["source_url"]})

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
        if result["sources"]:
            print("\nSources:")
            for s in result["sources"]:
                print(f"  - {s['name']} ({s['url']})")
        else:
            print("\nSources: (none)")


if __name__ == "__main__":
    main()
