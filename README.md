# The Unofficial Guide — Project 1

**Demo Video:** [https://youtu.be/hLxRNSkt6qQ](https://youtu.be/hLxRNSkt6qQ)

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Unofficial Guide to Popular Upper-Division CSE Electives at Stony Brook University.

### Scope
Covers 8 commonly discussed CSE upper-division electives: CSE 303, CSE 306, CSE 312, CSE 316, CSE 320, CSE 337, CSE 373, and CSE 416. Focusing on student experiences with workload, difficulty, grading, professor teaching style and career usefulness. It also will include professor's information like research area or academic background to help students to understand professor's background better.

### Why is it useful
Unlike required courses, upper-division CSE electives give students more freedom, which also makes course selection harder. This guide helps students compare official course information with unofficial student reviews from sources like Reddit, Rate My Professors, and Coursicle before making enrollment decisions.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | SBU CS Faculty Page | Official faculty directory | https://www.cs.stonybrook.edu/people/faculty (`documents/raw/sbu_cs_faculty.txt`) |
| 2 | SBU CS Undergraduate Course List | Official course list | https://www.cs.stonybrook.edu/students/Undergraduate-Studies/csecourses (`documents/raw/sbu_cs_courses.txt`) |
| 3 | SBU Computer Science BS Degree Catalog | Official degree requirements | https://catalog.stonybrook.edu/preview_program.php?catoid=11&poid=1411 (`documents/raw/sbu_cs_catalog.txt`) |
| 4 | RateMyProfessors reviews — 7 SBU CSE professors (Eugene Stark, Anita Wasilewska, Richard Mckenna, Himanshu Gupta, Dominik Kempa, Jennifer Carter, Ali Raza) | Professor reviews (RMP GraphQL API) | `documents/raw/rmp_<professor>.txt`, e.g. https://www.ratemyprofessors.com/professor/926577 |
| 5 | Coursicle professor reviews — 6 SBU CSE professors (Eugene Stark, Anita Wasilewska, Richard Mckenna, Himanshu Gupta, Dominik Kempa, Ali Raza) | Professor reviews (Coursicle reviews API) | `documents/raw/coursicle_<professor>.txt`, https://www.coursicle.com/professors/ |
| 6 | Coursicle course pages — CSE 303, 306, 312, 316, 320, 337, 373, 416 | Course descriptions + student reviews | `documents/raw/coursicle_cse<NNN>.txt`, e.g. https://www.coursicle.com/stonybrook/courses/CSE/320/ |
| 7 | r/SBU — "What does it take to pass CSE 320" | Reddit thread | https://www.reddit.com/r/SBU/comments/1osu0wo/what_does_it_take_to_pass_cse_320 |
| 8 | r/SBU — "Questions about CSE 316" | Reddit thread | https://www.reddit.com/r/SBU/comments/1emwui9/questions_about_cse_316 |
| 9 | r/SBU — "CSE320 and CSE 316" | Reddit thread | https://www.reddit.com/r/SBU/comments/dqgcow/cse320_and_cse_316 |
| 10 | r/SBU — "CSE Major Difficulty" | Reddit thread | https://www.reddit.com/r/SBU/comments/ka92z6/cse_major_difficulty/ |
| 11 | r/SBU — "What are the most useful CSE electives" | Reddit thread | https://www.reddit.com/r/SBU/comments/mouep1/what_are_the_most_useful_cse_electives |

Rows 4–6 represent 21 individual files (7 RMP professor pages + 6 Coursicle professor pages + 8
Coursicle course pages); together with rows 1–3 and 7–11, the corpus is 29 raw documents covering
official program info, professor-level reviews, course-level reviews, and student discussion
threads.

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 200 tokens, measured with the `all-MiniLM-L6-v2` tokenizer itself (via
`AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")`), using LangChain's
`RecursiveCharacterTextSplitter` with `separators=["\n\n", "\n", ". ", " ", ""]`.

**Overlap:** 25 tokens.

**Why these choices fit your documents:** The corpus is dominated by short-form content — Reddit comments (~50–300 words each) and RMP/Coursicle reviews (~50–150 words each). Each comment or review is typically one student's complete opinion on a course, so 200 tokens is large enough to capture a full thought without merging multiple students' opinions into a single chunk. The 25-token overlap prevents a student's reasoning from being split at a chunk boundary. Another reason to capped the chunk size at 200 is because `all-MiniLM-L6-v2` has a maximum input limit of 256 tokens. Official pages (faculty bios, course descriptions) will produce multiple chunks in order, which is fine since retrieval can pull the most relevant one.

**Preprocessing:** Each raw file written by `ingest.py` / `ingest_professors.py` starts with a
3-line header (`SOURCE_NAME: ...`, `SOURCE_URL: ...`, `---`) before the body text. `chunk.py`
strips this header (using the URL from it, or falling back to `documents/raw/metadata.json`),
splits only the body, and then drops any resulting chunk shorter than 30 tokens — this removes
near-empty fragments (e.g., a lone "Thanks!" reply) that would otherwise add noise to the vector
store without contributing real information.

**Final chunk count:** 222 chunks across 28 source documents (after the &lt;30-token filter). One
raw file, `coursicle_dominik_kempa.txt`, produced zero chunks — its reviews were short enough that
every resulting split fell below the 30-token minimum and was dropped.

## Sample Chunks

### Sample Chunk 1
**Source:** r/SBU — "CSE320 and CSE 316"
**Chunk text:**
> Title: CSE320 and CSE 316
>
> Post: Hi, I'm planning to take CSE320 and CSE316 for the next semester. I do know that 320 is quite time consuming course.
> So, I'm wondering taking both classes is doable in one semester.
> Or would you recommend me to take 320 and cse310 together?
> Thank you for your reply.
>
> 320 + 316 is a mistake. Don't even consider it
>
> They're being offered at the same time, you can't do it.
>
> I'm taking both this semester and my only advice is do it if you feel comfortable with the material being taught and you are someone who starts assignments early. Both classes have rlly long hws and you will end up spending multiple days on them. I made sure to take 3 very easy classes with them with minimal work and so far it hasn't been that bad.

### Sample Chunk 2
**Source:** RateMyProfessors — Eugene Stark
**Chunk text:**
> Professor: Eugene Stark
> Source: Rate My Professors
>
> Course: CSE306 | Quality: 5/5 | Difficulty: 4/5 | Date: 2025-12-16 05:22:36 +0000 UTC
> HWs can be difficult but if you're interested in the topic, it is definitely worth taking. Learned the most from this professor when I was at SBU.
>
> Course: CSE320 | Quality: 3/5 | Difficulty: 4/5 | Date: 2025-07-05 21:35:42 +0000 UTC
> The class itself isn't too hard. Just start the homeworks early. The exam are easy to get average on without studying, your main focus should be doing above average on homeworks

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, run locally. 384-dimensional
embeddings, stored in a persistent ChromaDB collection (`cse_electives_guide`) using cosine
similarity.

**Production tradeoff reflection:** `all-MiniLM-L6-v2` is fast and lightweight, which makes it practical for this project, but in a real deployment maybe I would consider OpenAI's `text-embedding-3-large`. The main tradeoffs are: (1) accuracy — `text-embedding-3-large` produces richer semantic representations that better capture student opinions (using slangs or not as formal/common describing words) (2) context length — `text-embedding-3-large` supports more tokens, useful if later want to embed longer contents without chunking them (3) cost — calling an external API per chunk adds network latency and per-token cost at scale, whereas `all-MiniLM-L6-v2` runs locally for free

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The system prompt (`generate.py`, `SYSTEM_PROMPT`)
gives the model a numbered set of rules, including:

> 1. Answer using ONLY information found in the CONTEXT below. Do not use any outside knowledge,
> training data, or assumptions about Stony Brook, CSE courses, or professors — even if you
> believe you know the answer.
>
> 3. If the CONTEXT does not contain enough information to answer the QUESTION, respond with
> EXACTLY this sentence and nothing else: "I don't have enough information on that."
>
> 4. Never fill gaps with general knowledge, speculation, or "typically" / "usually" style
> reasoning that isn't grounded in the CONTEXT.

Structurally, `_build_context()` formats every retrieved chunk as a numbered block tagged with
its human-readable source, e.g. `[1] (source: RateMyProfessors — Eugene Stark)\n<chunk text>`, and
this is the *only* domain content placed in the user message — there is no separate "background
knowledge" the model can fall back on. The model is run at `temperature=0.0` for reproducibility.
`ask()` checks the model's output against the exact refusal string (`NO_INFO_RESPONSE`,
case-insensitively) to decide whether the question was actually answerable from the retrieved
chunks; this same check is what the UI uses to decide whether to show a source list at all.

Two additional rules (added after testing) keep the *wording* natural without weakening
grounding: rule 5 forbids the model from referring to "the CONTEXT" / "the documents" /
"the provided excerpts" as meta-language (early outputs literally said "According to the
CONTEXT..."), and rule 7 instructs the model to phrase claims drawn from student reviews as
reported opinions ("Some students say...") rather than as settled facts, since the source
material is opinion, not fact.

**How source attribution is surfaced in the response:** Source attribution is **not** left to the
model. `ask()` always returns a `sources` list built programmatically: it iterates over the chunks
actually returned by `retrieve()`, deduplicates by `source_name`, and maps each to a
`{"name": <readable label>, "url": <source_url>}` pair via `display_name()` (which reads
human-written descriptions from `documents/raw/metadata.json`, with fallbacks for per-professor
RMP/Coursicle pages). If the model's answer matches the exact refusal sentence, `sources` is
empty. `app.py` renders this list under "Related Sources" as clickable Markdown links
(`[name](url)`), independent of whatever inline `(source: ...)` tags the model included in the
answer text itself — so attribution is guaranteed correct even if the model's inline citations
were ever malformed or omitted.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about the workload in CSE 320? | Students describe CSE 320 as one of the most demanding courses — heavy C programming, low-level memory management projects, steep learning curve, requires significantly more time than other electives. | Says students (via RMP/Coursicle reviews of Eugene Stark) describe CSE 320's workload as challenging — tests "seem unfair" but actually test class material plus self-study, professor expects initiative, and his courses are "tough" but manageable if not paired with another project-heavy class. | Relevant | Accurate |
| 2 | Is it a good idea to take CSE 320 and CSE 316 at the same time? | Students generally advise against it — both courses are project-heavy and time-consuming, hard to manage together. | Reports both sides from the dedicated Reddit thread: some say "320 + 316 is a mistake, don't even consider it"; others say it's "totally doable" if comfortable with the material and starting assignments early; one suggests pairing 320 with a lighter class like CSE 310 instead. | Relevant | Accurate |
| 3 | Which upper-division CSE electives do students say are the most useful for getting a job? | Based on the collected r/SBU thread, students mention CSE 356, CSE 331, CSE 332, and CSE 306 as useful for jobs or practical software development experience. The thread also includes one opinion warning against CSE 337 for job relevance, so the expected answer should reflect mixed student opinions rather than assume CSE 337 is useful. | "Some students say CSE 356 is useful for getting a job (source: r/SBU — most useful CSE electives)." Nothing else. | Partially relevant | Partially accurate |
| 4 | What do students say about the difficulty of CSE 306 compared to other electives? | CSE 306 (Operating Systems) is one of the hardest electives — complex systems programming, difficult projects, high time commitment. | Reports mixed Coursicle/RMP reviews of Eugene Stark's CSE 306: "difficult homework, but worth it if you're interested in the topic"; one student felt they "didn't learn much" and the homework was "hard and long, with too much focus on NACHOS"; difficulty rated 4/5 on RMP. | Relevant | Accurate |
| 5 | What do students say about whether CSE 316 is practical or project-based? | Students describe CSE 316 as practical/project-oriented — emphasis on software development, web/app development, implementation work; some discuss whether prior tech-stack experience helps. | Reports that CSE 316 "will be a breeze" for students with experience in the class's tech stack (React, Node, MongoDB), and that knowing the material plus not procrastinating is enough — then adds "there is no direct comment on whether CSE 316 is practical or project-based in the given context." | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "Which upper-division CSE electives do students say are the most useful for getting a job?"

**What the system returned:** "Only CSE 356 is mentioned as useful for jobs (source: r/SBU — most useful CSE electives)." — technically true, but it ignores the most informative part of the very thread it cites.

**Root cause (tied to a specific pipeline stage):** This is a **chunking + retrieval** failure. The single Reddit post that directly answers this question (`reddit_useful_electives`) is one long reply with no paragraph breaks. `chunk.py`'s `RecursiveCharacterTextSplitter` (200 tokens, 25
overlap) split it into 4 chunks:

- **chunk 0**: the original poster's question ("what are the most useful... cse electives that can
  translate to actual jobs... I know 356 is really good but it's not being taught next semester")
- **chunk 1**: the actual answer — "CSE 331 is useful... CSE 332 is good if you want to go into
  data visualization... CSE 306 is really good... for general software dev experience"
- **chunk 2**: continuation of chunk 1 — "Avoid CSE 333, 334, 337, and 371 if you are looking for
  classes that teach stuff relevant to actual jobs."
- **chunk 3**: unrelated tangent about CSE 305/databases.

I confirmed through `retrieve(query, k=10)` that **chunk 0 ranks #1** (cosine distance 0.2163) but
**chunks 1 and 2 don't appear in the top 10 at all**. Chunk 0's text closely echoes the question's
own phrasing ("most useful... electives... translate to actual jobs"), so the embedding model
ranks it as highly similar to the query — even though it contains almost none of the actual answer.
Chunks 1 and 2 contain the real recommendations (and an explicit "avoid CSE 337 for job-relevance,"
which directly contradicts the planning document's expected answer) but are phrased as a list of
course numbers and opinions, with weaker lexical/semantic overlap with the question itself. Because
retrieval treats each chunk independently and only chunk 0 made the top-5, the model never saw the
chunks containing the actual recommendations — it correctly refused to invent anything beyond
chunk 0, which is why the answer is narrowly true but badly incomplete.

**What you would change to fix it:** The most direct fix is **chunk-neighbor stitching**: when a
chunk from `source_name=X, chunk_index=i` is retrieved, also pull in `chunk_index=i+1` (and
possibly `i-1`) from the same source before building the context, since adjacent chunks from a
single long reply are very likely to be part of the same answer. A second option is to increase
the chunk size for Reddit sources specifically (e.g., 400–500 tokens) so a single commenter's
multi-sentence answer is less likely to be split across a boundary at all — at the cost of mixing
more topics into one chunk for very long comments. A third, cheaper option is simply increasing
`top_k` from 5 to ~8, though that didn't help here since chunks 1/2 weren't even in the top 10.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Pinning down the chunking parameters in
`planning.md` *before* writing any code — 200 tokens / 25-token overlap, justified by
`all-MiniLM-L6-v2`'s 256-token limit and the typical length of a Reddit comment or RMP review —
meant `chunk.py` had a single, unambiguous, reproducible target instead of needing to be tuned by
trial and error after the fact. Similarly, the Architecture diagram's five fixed stages
(Ingestion → Chunking → Embedding → Retrieval → Generation) made it straightforward to scope each
milestone to one or two files with a clear input/output contract (e.g., `chunk.py` reads
`documents/raw/*.txt` and writes `documents/chunks.json`; `retrieve.py` takes a query string and
returns a list of chunk dicts), which made it easy to test each stage in isolation and to hand
focused, well-scoped requests to Claude per milestone.

**One way your implementation diverged from the spec, and why:** `planning.md`'s Document Sources
table had only generic placeholder rows for professor reviews — an RMP search-results page, one
example RMP professor, the generic Coursicle professors page, and one example Coursicle course
page (CSE 337). None of those URLs actually contain scrapeable per-professor review text — RMP and
Coursicle only expose reviews via per-professor API calls keyed by an internal ID, and there was no
list of which SBU professors teach the 8 target electives. So I built `ingest_professors.py`
(backed by a candidate list in `professors.py`) to look up each professor's RMP ID, pull RMP and
Coursicle reviews filtered to the 8 target courses, and generate a Coursicle page per course
instead of just CSE 337. This turned 3 placeholder rows into 13 per-professor files plus 8
per-course files — over half of the final 29-document corpus.

A smaller divergence: the Evaluation Plan's pre-written "expected answer" for Q3 assumed CSE
416/337 would be cited as job-useful, but the actual Reddit thread instead recommends CSE
356/331/332/306 and explicitly says to *avoid* CSE 337. I judged responses against the real source
documents (what grounding requires) rather than the pre-written expectation, treating this as the
corpus differing from what was planned, not the pipeline being broken.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* `planning.md` (Architecture, Retrieval Approach, and Evaluation Plan
  sections) plus `retrieve.py`'s output format, and asked Claude to implement `generate.py`
  (grounded generation via Groq's `llama-3.3-70b-versatile`) and `app.py`.
- *What it produced:* A `SYSTEM_PROMPT` enforcing context-only answers and an exact refusal
  sentence, an `ask()` function returning the answer plus a deduplicated source list built from
  the raw `source_name`/`source_url` of retrieved chunks, and a basic Gradio app showing a
  "Retrieved from" list of those raw names.
- *What I changed or overrode:* The raw names/URLs weren't presentable (citations literally said
  `(source: reddit_cse320_cse316)`, and per-professor RMP/Coursicle URLs were base64 IDs or 404s).
  I had Claude add `display_name()` to map source names to readable labels via
  `documents/raw/metadata.json`, decode RMP's base64 `Teacher-<id>` into working profile URLs, and
  point Coursicle links at the general professors page. I also caught the model literally saying
  "According to the CONTEXT..." and adding "no other electives are mentioned" disclaimers, so I
  added system-prompt rules banning that meta-language and requiring student-review claims to be
  phrased as reported opinions ("Some students say...").

**Instance 2**

- *What I gave the AI:* Two Gradio UI requests: scale the whole interface up by ~150% (larger
  fonts, textboxes, buttons), and fix the example-question buttons, which were showing truncated
  text cut off mid-word.
- *What it produced:* For scaling, Claude's first attempt used CSS `zoom: 1.5` on the app
  container. For truncation, it first added CSS rules (`white-space: normal`, `overflow: visible`,
  `text-overflow: clip`) assuming the cutoff was an overflow/ellipsis issue, then — when that
  didn't fix it — used a headless-Chrome DOM dump to inspect the rendered HTML.
- *What I changed or overrode:* I rejected `zoom` ("scale the components and font, don't zoom the
  whole page") and had Claude redo it with Gradio's theme `Size` objects — `TEXT_150`/`SPACING_150`
  passed as `text_size=`/`spacing_size=` to `gr.themes.Base()` — so components render larger
  natively. The DOM dump revealed the example text is hard-truncated to 60 characters plus `"..."`
  by Gradio's compiled `Examples` component in JavaScript *before* any CSS applies, so CSS can't
  fully fix it. I kept refining `EXAMPLES_CSS` myself rather than adopting Claude's suggestion to
  replace `gr.Examples` with plain buttons.

## How to Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# add GROQ_API_KEY to .env

python ingest.py
python ingest_professors.py
python chunk.py
python embed.py

python app.py
# then open: http://localhost:7860
```