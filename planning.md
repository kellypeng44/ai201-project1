# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Unofficial Guide to Popular Upper-Division CSE Electives at Stony Brook University

### Scope
Covers 8 commonly discussed CSE upper-division electies: CSE 303, CSE 306, CSE 312, CSE 316, CSE 320, CSE 337, CSE 373, and CSE 416. Focusing on student experiences with workload, difficulty, grading, professor teaching style and career usefulness. It also will include professor's information like research area or academic background to help students to understand professor's background better.

### why is it useful
Unlike required courses, upper-division CSE electives give students more freedom, which also makes course selection harder. This guide helps students compare official course information with unofficial student reviews from sources like Reddit, Rate My Professors, and Coursicle before making enrollment decisions.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | SBU CS faculty page | Official list of CS faculty, titles, research/teaching areas | https://www.cs.stonybrook.edu/people/faculty |
| 2 | SBU CS undergraduate course list | Official CSE course numbers and titles | https://www.cs.stonybrook.edu/students/Undergraduate-Studies/csecourses |
| 3 | SBU Computer Science BS catalog | Degree requirements and course structure | https://catalog.stonybrook.edu/preview_program.php?catoid=11&poid=1411 |
| 4 | Rate My Professors CS professors | list of professor ratings across SBU CS major | https://www.ratemyprofessors.com/search/professors/971?q=*&did=11 |
| 5 | Rate My Professors — individual CSE professors | Ratings, difficulty, would-take-again, review text per class | https://www.ratemyprofessors.com/professor/2640556 |
| 6 | Professor Reviews on Coursicle | student reviews | https://www.coursicle.com/professors/ |
| 7 | Coursicle SBU CSE course pages | Student reviews and course descriptions for individual CSE courses | https://www.coursicle.com/stonybrook/courses/CSE/337/ |
| 8 | r/SBU "What does it take to pass CSE 320" | CSE 320 related information | https://www.reddit.com/r/SBU/comments/1osu0wo/what_does_it_take_to_pass_cse_320 |
| 9 | r/SBU "Questions about CSE 316" | CSE 316 related information | https://www.reddit.com/r/SBU/comments/1emwui9/questions_about_cse_316 |
| 10 | r/SBU “CSE320 and CSE 316” | Student advice about whether taking CSE 320 and CSE 316 together is manageable | https://www.reddit.com/r/SBU/comments/dqgcow/cse320_and_cse_316 |
| 11 | r/SBU “CSE Major Difficulty” | Broad student discussion about which upper-division CSE courses are difficult, including CSE 306, CSE 320, CSE 312, and CSE 373 | https://www.reddit.com/r/SBU/comments/ka92z6/cse_major_difficulty/ |
| 12 | r/SBU “What are the most useful CSE electives” | Student discussion about career usefulness and practical value of different CSE electives | https://www.reddit.com/r/SBU/comments/mouep1/what_are_the_most_useful_cse_electives |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
