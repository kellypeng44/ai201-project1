"""
Milestone 5 — Step 2: Query interface.

A minimal Gradio web UI for the Unofficial Guide to Stony Brook CSE
Electives RAG pipeline. Type a question, click Ask (or press Enter), and
see the grounded answer plus the documents it was retrieved from.

Usage:
    python app.py
Then open http://localhost:7860
"""

import gradio as gr

from generate import ask

EXAMPLE_QUESTIONS = [
    "What do students say about the workload in CSE 320?",
    "Is it a good idea to take CSE 320 and CSE 316 at the same time?",
    "Which upper-division CSE electives do students say are most useful for getting a job?",
    "What do students say about the difficulty of CSE 306 compared to other electives?",
    "What is the dining hall food like at Stony Brook?",
]


def handle_query(question: str):
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""

    result = ask(question)

    if result["sources"]:
        sources = "\n".join(f"• {s}" for s in result["sources"])
    else:
        sources = "(no sources — question is outside the scope of these documents)"

    return result["answer"], sources


with gr.Blocks(title="Unofficial Guide to SBU CSE Electives") as demo:
    gr.Markdown(
        "# Unofficial Guide to Stony Brook CSE Electives\n"
        "Ask about workload, difficulty, professors, or career relevance for "
        "CSE 303, 306, 312, 316, 320, 337, 373, and 416. Answers are grounded "
        "in student reviews (Reddit, RateMyProfessors, Coursicle) and official "
        "course/faculty pages — if the documents don't cover something, the "
        "system will say so instead of guessing."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. What do students say about the workload in CSE 320?",
    )
    btn = gr.Button("Ask", variant="primary")

    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Examples(examples=EXAMPLE_QUESTIONS, inputs=inp)


if __name__ == "__main__":
    demo.launch()
