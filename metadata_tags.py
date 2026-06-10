"""
Shared course/professor tagging used by embed.py (to tag stored chunks)
and retrieve.py (to detect filter terms in a query).

A single chunk can mention more than one course or professor (e.g. a
"CSE320 and CSE316" Reddit thread, or an RMP chunk that bundles reviews
for multiple courses) — extract_courses / extract_professors return a
list, and embed.py stores one boolean field per match so a chunk can
match several filters at once.
"""

import re

# The 8 in-scope electives (see planning.md). Course numbers outside this
# set are not tagged, since they're outside the project's domain.
TARGET_COURSES = {"303", "306", "312", "316", "320", "337", "373", "416"}

# Surname (or short form) used to spot a professor mention inside review text.
PROFESSOR_ALIASES = {
    "Eugene Stark": ["stark"],
    "Ahmad Esmaili": ["esmaili"],
    "Praveen Tripathi": ["tripathi"],
    "Anita Wasilewska": ["wasilewska"],
    "Jennifer Carter": ["carter"],
    "Dominik Kempa": ["kempa"],
    "Ali Raza": ["raza"],
    "Himanshu Gupta": ["gupta"],
    "Richard Mckenna": ["mckenna"],
}

# Per-professor and per-course source files where every chunk is "about"
# that professor/course, even if the chunk text itself doesn't repeat the
# name/number (e.g. a one-line "No Comments" review on Stark's RMP page).
SOURCE_PROFESSOR_MAP = {
    "rmp_eugene_stark": "Eugene Stark",
    "coursicle_eugene_stark": "Eugene Stark",
    "rmp_anita_wasilewska": "Anita Wasilewska",
    "coursicle_anita_wasilewska": "Anita Wasilewska",
    "rmp_richard_mckenna": "Richard Mckenna",
    "coursicle_richard_mckenna": "Richard Mckenna",
    "rmp_himanshu_gupta": "Himanshu Gupta",
    "coursicle_himanshu_gupta": "Himanshu Gupta",
    "rmp_ali_raza": "Ali Raza",
    "coursicle_ali_raza": "Ali Raza",
    "rmp_dominik_kempa": "Dominik Kempa",
    "coursicle_dominik_kempa": "Dominik Kempa",
    "rmp_jennifer_carter": "Jennifer Carter",
}

SOURCE_COURSE_MAP = {
    "coursicle_cse303": ["303"],
    "coursicle_cse306": ["306"],
    "coursicle_cse312": ["312"],
    "coursicle_cse316": ["316"],
    "coursicle_cse320": ["320"],
    "coursicle_cse337": ["337"],
    "coursicle_cse373": ["373"],
    "coursicle_cse416": ["416"],
}

_COURSE_RE = re.compile(r"CSE\s*-?\s*(\d{3})", re.IGNORECASE)


def extract_courses(text: str, source_name: str | None = None) -> list[str]:
    """Return every in-scope course number (e.g. "320") mentioned in `text`,
    plus any course implied by `source_name` (e.g. coursicle_cse320 -> 320)."""
    found = {c for c in _COURSE_RE.findall(text) if c in TARGET_COURSES}
    if source_name:
        found.update(SOURCE_COURSE_MAP.get(source_name, []))
    return sorted(found)


def extract_professors(text: str, source_name: str | None = None) -> list[str]:
    """Return every professor whose surname appears in `text`, plus the
    professor implied by `source_name` (e.g. rmp_eugene_stark -> Eugene Stark)."""
    text_lower = text.lower()
    found = {
        name
        for name, aliases in PROFESSOR_ALIASES.items()
        if any(re.search(rf"\b{re.escape(alias)}\b", text_lower) for alias in aliases)
    }
    if source_name and source_name in SOURCE_PROFESSOR_MAP:
        found.add(SOURCE_PROFESSOR_MAP[source_name])
    return sorted(found)


def professor_slug(name: str) -> str:
    return name.lower().replace(" ", "_")
