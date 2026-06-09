"""
Professor configuration for the 8 target CSE courses.

rmp_id is auto-discovered by ingest_professors.py — leave as None and the
script will fill it in by searching RMP, then cache it back here.

Coursicle reviews are fetched for every professor below using a shared
app-level UUID (see COURSICLE_UUID in ingest_professors.py) — no per-professor
UUID needed.

Only professors who teach at least one of the 8 target courses need entries here.
Run `python ingest_professors.py --discover` to find more candidates.
"""

TARGET_COURSES = {
    "CSE303", "CSE306", "CSE312", "CSE316",
    "CSE320", "CSE337", "CSE373", "CSE416",
}

# Add/remove professors as you discover them.
# rmp_id: base64 RMP teacher ID (auto-filled by ingest_professors.py)
PROFESSORS = [
    {"name": "Eugene Stark", "rmp_id": "VGVhY2hlci05MjY1Nzc="},
    {"name": "Ahmad Esmaili", "rmp_id": "VGVhY2hlci04NjAyMA=="},
    {"name": "Praveen Tripathi", "rmp_id": "VGVhY2hlci0yMjcwMjQ0"},
    {"name": "Anita Wasilewska", "rmp_id": "VGVhY2hlci0zMzgzMDc="},
    {"name": "Jennifer Carter", "rmp_id": "VGVhY2hlci0xMjE1NTY3"},
    {"name": "Dominik Kempa", "rmp_id": "VGVhY2hlci0yOTcxNDA4"},
    {"name": "Ali Raza", "rmp_id": "VGVhY2hlci0yNjcwNjkz"},
    {"name": "Himanshu Gupta", "rmp_id": "VGVhY2hlci01MzQ0Nzg="},
    {"name": "Richard Mckenna", "rmp_id": "VGVhY2hlci0yNjY4OTM="},
    # Add more professors below as you identify who teaches the 8 target courses.
    # Pattern:
    # {"name": "First Last", "rmp_id": None},
]
