"""
Milestone 3 — Step 1b: Professor review ingestion.

Two data sources, both fully automatic:
  1. Rate My Professors (GraphQL API)
     - Discovers which SBU professors have reviews for the 8 target courses
     - Fetches all matching review text
  2. Coursicle (JSON reviews API)
     - Fetches reviews for every professor in professors.py using a shared
       app-level UUID (COURSICLE_UUID below)

Usage:
    python ingest_professors.py              # discover + collect all
    python ingest_professors.py --discover   # only print which professors have target-course reviews

Output: one file per professor in documents/raw/
  - rmp_<slug>.txt     — RMP reviews for target courses
  - coursicle_<slug>.txt — Coursicle reviews
"""

import argparse
import base64
import html
import json
import re
import time
from pathlib import Path

import requests

from professors import PROFESSORS, TARGET_COURSES

RAW_DIR = Path("documents/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

RMP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) research-project/1.0",
    "Authorization": "Basic dGVzdDp0ZXN0",
    "Content-Type": "application/json",
}
COURSICLE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) research-project/1.0",
}

SBU_SCHOOL_ID = "U2Nob29sLTk3MQ=="  # base64("School-971")

# Shared app-level UUID — works for any professor's getReviews.php request,
# not tied to a specific professor.
COURSICLE_UUID = "01871cf9-156b-4f12-b5a8-3ba393ae0e06"


def normalize_course(raw: str) -> str:
    return re.sub(r"\s+", "", raw.strip().upper())


def rmp_search_professor(name: str) -> str | None:
    """Return the RMP base64 teacher ID for the first result matching `name`."""
    first, *rest = name.split()
    last = rest[-1] if rest else ""
    query = """
    query($text: String!, $schoolID: ID!) {
      newSearch {
        teachers(query: {text: $text, schoolID: $schoolID}, first: 5) {
          edges { node { id firstName lastName department } }
        }
      }
    }
    """
    r = requests.post(
        "https://www.ratemyprofessors.com/graphql",
        headers=RMP_HEADERS,
        json={"query": query, "variables": {"text": name, "schoolID": SBU_SCHOOL_ID}},
        timeout=15,
    )
    r.raise_for_status()
    edges = r.json()["data"]["newSearch"]["teachers"]["edges"]
    for edge in edges:
        node = edge["node"]
        if node["lastName"].lower() == last.lower():
            return node["id"]
    return edges[0]["node"]["id"] if edges else None


def rmp_fetch_reviews(rmp_id: str, professor_name: str) -> list[dict]:
    """Fetch all RMP reviews for a professor, returning those for target courses."""
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on Teacher {
          firstName lastName avgRating avgDifficulty numRatings
          ratings(first: 100) {
            edges {
              node {
                class comment qualityRating difficultyRating date
              }
            }
          }
        }
      }
    }
    """
    r = requests.post(
        "https://www.ratemyprofessors.com/graphql",
        headers=RMP_HEADERS,
        json={"query": query, "variables": {"id": rmp_id}},
        timeout=15,
    )
    r.raise_for_status()
    teacher = r.json()["data"]["node"]
    if not teacher:
        return []

    results = []
    for edge in teacher.get("ratings", {}).get("edges", []):
        node = edge["node"]
        course = normalize_course(node.get("class") or "")
        if course in TARGET_COURSES:
            results.append({
                "course": course,
                "quality": node.get("qualityRating"),
                "difficulty": node.get("difficultyRating"),
                "date": node.get("date"),
                "comment": html.unescape((node.get("comment") or "").strip()),
            })
    return results


def rmp_discover_all_professors() -> list[dict]:
    """Return all SBU professors from RMP (up to 200 results)."""
    query = """
    query($schoolID: ID!) {
      newSearch {
        teachers(query: {text: "", schoolID: $schoolID}, first: 200) {
          edges { node { id firstName lastName avgRating avgDifficulty numRatings department } }
        }
      }
    }
    """
    r = requests.post(
        "https://www.ratemyprofessors.com/graphql",
        headers=RMP_HEADERS,
        json={"query": query, "variables": {"schoolID": SBU_SCHOOL_ID}},
        timeout=20,
    )
    r.raise_for_status()
    edges = r.json()["data"]["newSearch"]["teachers"]["edges"]
    return [e["node"] for e in edges]


def coursicle_fetch_reviews(professor_name: str) -> list[dict]:
    """Fetch Coursicle reviews for a professor, returning those for target courses."""
    r = requests.get(
        "https://www.coursicle.com/shared/reviews/getReviews.php",
        params={"school": "stonybrook", "professor": professor_name, "uuid": COURSICLE_UUID},
        headers=COURSICLE_HEADERS,
        timeout=15,
    )
    r.raise_for_status()
    reviews = r.json()
    return [
        rev for rev in reviews
        if rev.get("course") and normalize_course(rev["course"]) in TARGET_COURSES
    ]


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def rmp_profile_url(rmp_id: str) -> str:
    """Build a working RMP profile URL from a base64 'Teacher-<numeric id>' rmp_id.

    RMP profile pages are keyed by the numeric id only
    (https://www.ratemyprofessors.com/professor/<numeric id>) — the raw
    base64 string returns a 404.
    """
    decoded = base64.b64decode(rmp_id).decode()  # "Teacher-926577"
    numeric_id = decoded.removeprefix("Teacher-")
    return f"https://www.ratemyprofessors.com/professor/{numeric_id}"


def save_rmp(professor_name: str, rmp_id: str, reviews: list[dict]) -> Path:
    lines = [f"Professor: {professor_name}", f"Source: Rate My Professors", ""]
    for rev in reviews:
        lines.append(f"Course: {rev['course']} | Quality: {rev['quality']}/5 | Difficulty: {rev['difficulty']}/5 | Date: {rev['date']}")
        if rev["comment"]:
            lines.append(rev["comment"])
        lines.append("")
    text = "\n".join(lines)
    path = RAW_DIR / f"rmp_{slug(professor_name)}.txt"
    header = f"SOURCE_NAME: rmp_{slug(professor_name)}\nSOURCE_URL: {rmp_profile_url(rmp_id)}\n---\n"
    path.write_text(header + text, encoding="utf-8")
    return path


def save_coursicle(professor_name: str, reviews: list[dict]) -> Path:
    lines = [f"Professor: {professor_name}", f"Source: Coursicle", ""]
    for rev in reviews:
        course = rev.get("course", "")
        year = rev.get("userYear", "")
        major = rev.get("userMajor", "")
        body = (rev.get("body") or "").strip()
        lines.append(f"Course: {course} | Year: {year} | Major: {major}")
        if body:
            lines.append(body)
        lines.append("")
    text = "\n".join(lines)
    path = RAW_DIR / f"coursicle_{slug(professor_name)}.txt"
    # Coursicle has no stable per-professor review URL reachable from outside
    # the app, so link to the general professor search page instead.
    header = f"SOURCE_NAME: coursicle_{slug(professor_name)}\nSOURCE_URL: https://www.coursicle.com/professors/\n---\n"
    path.write_text(header + text, encoding="utf-8")
    return path


def discover_mode():
    """Print all SBU professors on RMP who have reviews for target courses."""
    print("Fetching all professors from RMP at SBU...")
    all_profs = rmp_discover_all_professors()
    print(f"Found {len(all_profs)} professors total. Checking for target-course reviews...\n")

    relevant = []
    for prof in all_profs:
        time.sleep(0.5)
        try:
            reviews = rmp_fetch_reviews(prof["id"], prof["firstName"] + " " + prof["lastName"])
            if reviews:
                courses_found = sorted({r["course"] for r in reviews})
                relevant.append({**prof, "courses": courses_found, "review_count": len(reviews)})
                print(f"  ✓ {prof['firstName']} {prof['lastName']} — {courses_found} ({len(reviews)} reviews)")
        except Exception as e:
            pass

    print(f"\n{'='*60}")
    print(f"Professors with target-course reviews: {len(relevant)}")
    print("\nAdd these to professors.py:")
    for p in relevant:
        print(f'    {{"name": "{p["firstName"]} {p["lastName"]}", "rmp_id": None}},')


def collect_mode():
    """Collect reviews for all professors in professors.py."""
    for prof in PROFESSORS:
        name = prof["name"]
        print(f"\n{'='*50}")
        print(f"Professor: {name}")

        # RMP
        rmp_id = prof.get("rmp_id")
        if not rmp_id:
            print("  Searching RMP for ID...")
            try:
                rmp_id = rmp_search_professor(name)
                if rmp_id:
                    print(f"  Found RMP ID: {rmp_id}")
                    prof["rmp_id"] = rmp_id
                else:
                    print("  Not found on RMP")
            except Exception as e:
                print(f"  RMP search error: {e}")

        if rmp_id:
            try:
                reviews = rmp_fetch_reviews(rmp_id, name)
                if reviews:
                    path = save_rmp(name, rmp_id, reviews)
                    print(f"  RMP: {len(reviews)} target-course reviews → {path}")
                else:
                    print(f"  RMP: no reviews for target courses")
            except Exception as e:
                print(f"  RMP fetch error: {e}")

        time.sleep(1)

        # Coursicle
        try:
            reviews = coursicle_fetch_reviews(name)
            if reviews:
                path = save_coursicle(name, reviews)
                print(f"  Coursicle: {len(reviews)} target-course reviews → {path}")
            else:
                print(f"  Coursicle: no reviews for target courses (all are for other courses)")
        except Exception as e:
            print(f"  Coursicle error: {e}")

        time.sleep(1)

    # Update professors.py with discovered RMP IDs
    _update_professors_file()


def _update_professors_file():
    """Write discovered RMP IDs back to professors.py so they're cached."""
    content = Path("professors.py").read_text(encoding="utf-8")
    for prof in PROFESSORS:
        if prof.get("rmp_id") and '"rmp_id": None' in content:
            content = content.replace(
                f'"name": "{prof["name"]}", "rmp_id": None',
                f'"name": "{prof["name"]}", "rmp_id": "{prof["rmp_id"]}"',
                1,
            )
    Path("professors.py").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--discover", action="store_true",
                        help="Scan all SBU RMP professors to find who teaches target courses")
    args = parser.parse_args()

    if args.discover:
        discover_mode()
    else:
        collect_mode()
