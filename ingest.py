"""
Milestone 3 — Step 1: Document ingestion.

Fetches each source from the Documents table in planning.md and saves it as a
plain-text file in documents/raw/<source_name>.txt.

Sources marked "manual" (Rate My Professors, Coursicle) require JavaScript to
render and cannot be scraped with requests. For those, copy the text you want
into documents/manual/<source_name>.txt — this script will read from there.

Usage:
    python ingest.py
"""

import json
import time
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

RAW_DIR = Path("documents/raw")
MANUAL_DIR = Path("documents/manual")
RAW_DIR.mkdir(parents=True, exist_ok=True)
MANUAL_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) research-project/1.0"}

# Sources from planning.md Documents table.
# type: "web"    — scraped with requests + BeautifulSoup
#       "reddit" — fetched via Reddit JSON API (no credentials needed)
#       "manual" — JS-rendered; copy text to documents/manual/<name>.txt
SOURCES = [
    {
        "name": "sbu_cs_faculty",
        "url": "https://www.cs.stonybrook.edu/people/faculty",
        "type": "web",
        "description": "SBU CS faculty page — names, titles, research areas",
    },
    {
        "name": "sbu_cs_courses",
        "url": "https://www.cs.stonybrook.edu/students/Undergraduate-Studies/csecourses",
        "type": "web",
        "description": "SBU CS undergraduate course list",
    },
    {
        "name": "sbu_cs_catalog",
        "url": "https://catalog.stonybrook.edu/preview_program.php?catoid=11&poid=1411",
        "type": "web",
        "description": "SBU Computer Science BS degree catalog",
    },
    {
        "name": "rmp_sbu_cs_list",
        "url": "https://www.ratemyprofessors.com/search/professors/971?q=*&did=11",
        "type": "manual",
        "description": "Rate My Professors — SBU CS professor list",
    },
    {
        "name": "rmp_individual_professors",
        "url": "https://www.ratemyprofessors.com/professor/2640556",
        "type": "manual",
        "description": "Rate My Professors — individual CSE professor reviews",
    },
    {
        "name": "coursicle_professors",
        "url": "https://www.coursicle.com/professors/",
        "type": "manual",
        "description": "Coursicle — SBU professor reviews",
    },
    {
        "name": "coursicle_cse303",
        "url": "https://www.coursicle.com/stonybrook/courses/CSE/303/",
        "type": "web",
        "description": "Coursicle — CSE 303 student reviews",
    },
    {
        "name": "coursicle_cse306",
        "url": "https://www.coursicle.com/stonybrook/courses/CSE/306/",
        "type": "web",
        "description": "Coursicle — CSE 306 student reviews",
    },
    {
        "name": "coursicle_cse312",
        "url": "https://www.coursicle.com/stonybrook/courses/CSE/312/",
        "type": "web",
        "description": "Coursicle — CSE 312 student reviews",
    },
    {
        "name": "coursicle_cse316",
        "url": "https://www.coursicle.com/stonybrook/courses/CSE/316/",
        "type": "web",
        "description": "Coursicle — CSE 316 student reviews",
    },
    {
        "name": "coursicle_cse320",
        "url": "https://www.coursicle.com/stonybrook/courses/CSE/320/",
        "type": "web",
        "description": "Coursicle — CSE 320 student reviews",
    },
    {
        "name": "coursicle_cse337",
        "url": "https://www.coursicle.com/stonybrook/courses/CSE/337/",
        "type": "web",
        "description": "Coursicle — CSE 337 student reviews",
    },
    {
        "name": "coursicle_cse373",
        "url": "https://www.coursicle.com/stonybrook/courses/CSE/373/",
        "type": "web",
        "description": "Coursicle — CSE 373 student reviews",
    },
    {
        "name": "coursicle_cse416",
        "url": "https://www.coursicle.com/stonybrook/courses/CSE/416/",
        "type": "web",
        "description": "Coursicle — CSE 416 student reviews",
    },
    {
        "name": "reddit_cse320_pass",
        "url": "https://www.reddit.com/r/SBU/comments/1osu0wo/what_does_it_take_to_pass_cse_320",
        "type": "reddit",
        "description": "r/SBU — what does it take to pass CSE 320",
    },
    {
        "name": "reddit_cse316_questions",
        "url": "https://www.reddit.com/r/SBU/comments/1emwui9/questions_about_cse_316",
        "type": "reddit",
        "description": "r/SBU — questions about CSE 316",
    },
    {
        "name": "reddit_cse320_cse316",
        "url": "https://www.reddit.com/r/SBU/comments/dqgcow/cse320_and_cse_316",
        "type": "reddit",
        "description": "r/SBU — taking CSE 320 and CSE 316 together",
    },
    {
        "name": "reddit_cse_difficulty",
        "url": "https://www.reddit.com/r/SBU/comments/ka92z6/cse_major_difficulty/",
        "type": "reddit",
        "description": "r/SBU — CSE major difficulty discussion",
    },
    {
        "name": "reddit_useful_electives",
        "url": "https://www.reddit.com/r/SBU/comments/mouep1/what_are_the_most_useful_cse_electives",
        "type": "reddit",
        "description": "r/SBU — most useful CSE electives",
    },
]


def scrape_web(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["nav", "header", "footer", "script", "style", "aside", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Collapse runs of blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def scrape_reddit(url: str) -> str:
    """Scrape a Reddit thread via old.reddit.com (static HTML, no JS required)."""
    old_url = url.replace("www.reddit.com", "old.reddit.com").rstrip("/") + "?limit=500"
    resp = requests.get(old_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    lines = []

    # Post title (inside the main link element with class "title")
    title_tag = soup.find("a", class_="title")
    if title_tag:
        lines.append(f"Title: {title_tag.get_text(strip=True)}")

    # Post self-text is the first usertext-body NOT inside a comment div
    for entry in soup.find_all("div", class_="entry"):
        body = entry.find("div", class_="usertext-body")
        if body:
            text = body.get_text(separator="\n", strip=True)
            if text:
                lines.append(f"Post: {text}")
            break

    # Individual comments — each is a <div class="comment"> with a usertext-body inside
    for comment in soup.find_all("div", class_="comment"):
        body = comment.find("div", class_="usertext-body")
        if body:
            text = body.get_text(separator=" ", strip=True)
            if text and text not in ("[deleted]", "[removed]"):
                lines.append(text)

    return "\n\n".join(lines)


def load_manual(source: dict) -> str | None:
    path = MANUAL_DIR / f"{source['name']}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return None


def save_document(source: dict, text: str) -> None:
    out = RAW_DIR / f"{source['name']}.txt"
    header = f"SOURCE_NAME: {source['name']}\nSOURCE_URL: {source['url']}\n---\n"
    out.write_text(header + text, encoding="utf-8")


def main():
    results = []

    for source in SOURCES:
        name = source["name"]
        print(f"\n[{source['type'].upper()}] {name}")

        try:
            if source["type"] == "manual":
                text = load_manual(source)
                if text is None:
                    print(f"  ⚠ Skipped — copy text to documents/manual/{name}.txt")
                    print(f"    URL: {source['url']}")
                    results.append({**source, "status": "skipped"})
                    continue
                print(f"  ✓ Loaded from documents/manual/{name}.txt")

            elif source["type"] == "reddit":
                text = scrape_reddit(source["url"])
                print(f"  ✓ Fetched {len(text.splitlines())} lines")

            else:  # web
                text = scrape_web(source["url"])
                print(f"  ✓ Scraped {len(text.splitlines())} lines")

            if len(text.strip()) < 50:
                print(f"  ⚠ Content looks empty — may be JS-rendered. Save manually to documents/manual/{name}.txt")
                results.append({**source, "status": "empty"})
                continue

            save_document(source, text)
            results.append({**source, "status": "ok", "chars": len(text)})

        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({**source, "status": "error", "error": str(e)})

        time.sleep(1)  # be polite to servers

    # Summary
    ok = [r for r in results if r["status"] == "ok"]
    skipped = [r for r in results if r["status"] in ("skipped", "empty", "error")]
    print(f"\n{'='*50}")
    print(f"Saved: {len(ok)}/{len(SOURCES)} sources")
    if skipped:
        print("\nSources needing manual collection:")
        for r in skipped:
            print(f"  - documents/manual/{r['name']}.txt  ({r['url']})")

    # Save metadata for chunk.py
    meta_path = RAW_DIR / "metadata.json"
    meta = {s["name"]: {"url": s["url"], "description": s["description"]} for s in SOURCES}
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"\nMetadata saved to {meta_path}")


if __name__ == "__main__":
    main()
