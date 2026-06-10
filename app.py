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
from gradio.themes.utils.sizes import Size

from generate import ask

# 1.5x the default text_md / spacing_md scales, so fonts, textboxes, and
# buttons all render at 150% of their normal size (not just browser zoom).
TEXT_150 = Size(name="text_150", xxs="14px", xs="15px", sm="18px", md="21px", lg="24px", xl="33px", xxl="39px")
SPACING_150 = Size(name="spacing_150", xxs="2px", xs="3px", sm="6px", md="9px", lg="12px", xl="15px", xxl="24px")

EXAMPLE_QUESTIONS = [
    "What do students say about the workload in CSE 320?",
    "Is it a good idea to take CSE 320 and CSE 316 together?",
    "Which CSE electives do students say are most useful for getting a job?",
    "What do students say about the difficulty of CSE 306?",
    "What is the dining hall food like at Stony Brook?",
]


def handle_query(question: str):
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""

    result = ask(question)

    if result["sources"]:
        sources = "\n".join(f"- [{s['name']}]({s['url']})" for s in result["sources"])
    else:
        sources = "_(no sources — question is outside the scope of these documents)_"

    return result["answer"], sources


TITLE_CSS = "#title { margin-top: 24px; }"

# The example "buttons" (and the text node inside them) default to
# nowrap + ellipsis/hidden overflow, which clips long questions. Override
# both the button and its inner content so the full text wraps and shows.
EXAMPLES_CSS = EXAMPLES_CSS ="""
/* Let the example item itself size to its content */
#examples .gallery-item {
    width: auto !important;
    max-width: none !important;
    flex: 0 0 auto !important;
}

/* Let the examples area wrap items naturally */
#examples .gallery {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 10px !important;
    align-items: flex-start !important;
}

/* Make the button size to text instead of the grid column */
#examples button {
    width: max-content !important;
    max-width: 900px !important;
    height: auto !important;
    padding: 12px 16px !important;
    text-align: left !important;
}

/* Remove ellipsis from inner text elements */
#examples button,
#examples button *,
#examples .gallery-item *,
#examples [data-testid="block-label"] {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    line-height: 1.3 !important;
}
"""

with gr.Blocks(title="Unofficial Guide to SBU CSE Electives") as demo:
    gr.Markdown(
        "# Unofficial Guide to Stony Brook CSE Electives\n"
        "Ask about workload, difficulty, professors, or career relevance for "
        "CSE 303, 306, 312, 316, 320, 337, 373, and 416. Answers are grounded "
        "in student reviews (Reddit, RateMyProfessors, Coursicle) and official "
        "course/faculty pages — if the documents don't cover your question , the "
        "system will not provide an answer.",
        elem_id="title",
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. What do students say about the workload in CSE 320?",
    )
    btn = gr.Button("Ask", variant="primary")

    answer = gr.Textbox(label="Answer", lines=8)
    gr.Markdown("**Related Sources**")
    sources = gr.Markdown()

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Examples(examples=EXAMPLE_QUESTIONS, inputs=inp, elem_id="examples")


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Base(text_size=TEXT_150, spacing_size=SPACING_150), css=TITLE_CSS + EXAMPLES_CSS)
