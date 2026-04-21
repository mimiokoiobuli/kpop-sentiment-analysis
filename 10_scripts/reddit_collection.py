"""
reddit_collection.py
--------------------
Collects Reddit comments from Pushshift monthly archive dumps for six K-pop
comebacks during their release windows.

Background
    The original methodology (documented in the Interim Progress Report,
    March 2026) planned to use the Reddit API via PRAW. After the Reddit
    API access request was not approved in time, the project pivoted to
    the publicly available Pushshift monthly archive dumps, distributed
    as .zst-compressed newline-delimited JSON via Academic Torrents.

    This script replaces the earlier collection script (lost from local
    storage before it was committed to git). It reproduces the same
    methodology that was used to generate the raw CSVs already saved
    under data/raw/reddit/ and is included in the code appendix as the
    canonical reference for the Reddit collection step.

Methodology
    For each of the six target comebacks, Reddit comments are pulled
    from nine K-pop-related subreddits within a 14-day window starting
    on the release date (day 0 through day +13 inclusive).

    Filtering rules per comment:
        1. Subreddit must be in the target list.
        2. created_utc must fall within the comeback's 14-day window.
        3. body must not be empty, '[deleted]', or '[removed]'.
        4. If the comment is posted in the comeback group's *own*
           subreddit (e.g., r/Aespa for the Whiplash comeback), it is
           kept without a keyword filter. Activity in a group's home
           subreddit during its release window is assumed to be
           dominated by that comeback.
        5. Otherwise, the comment body must contain either the group
           name or the song title (case-insensitive substring match).

    Duplicate comment IDs across dump files are removed.

Output
    One CSV per comeback, written to data/raw/reddit/, with columns:
        id, subreddit, text, score, created_utc, comeback

Input
    Pushshift monthly comment dumps named 'RC_YYYY-MM.zst' placed in
    the directory referenced by DUMP_DIR below.

Usage
    python reddit_collection.py

Dependencies
    pip install zstandard
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timedelta
from pathlib import Path

import zstandard as zstd


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Comebacks under study. Release dates confirmed against each group's
# official release; keyword terms are lowercase substrings matched against
# the comment body.

COMEBACKS = [
    {
        "label":        "StrayKids_ChkChkBoom",
        "group":        "stray kids",
        "song":         "chk chk boom",
        "release_date": datetime(2024, 7, 19),
        "own_sub":      "straykids",
    },
    {
        "label":        "aespa_Whiplash",
        "group":        "aespa",
        "song":         "whiplash",
        "release_date": datetime(2024, 10, 21),
        "own_sub":      "Aespa",
    },
    {
        "label":        "NCTDREAM_WhenImWithYou",
        "group":        "nct dream",
        "song":         "when i'm with you",
        "release_date": datetime(2024, 11, 11),
        "own_sub":      "NCTDream",
    },
    {
        "label":        "ATEEZ_IceOnMyTeeth",
        "group":        "ateez",
        "song":         "ice on my teeth",
        "release_date": datetime(2024, 11, 15),
        "own_sub":      "ATEEZ",
    },
    {
        "label":        "TWICE_Strategy",
        "group":        "twice",
        "song":         "strategy",
        "release_date": datetime(2024, 12, 6),
        "own_sub":      "twice",
    },
    {
        "label":        "IVE_RebelHeart",
        "group":        "ive",
        "song":         "rebel heart",
        "release_date": datetime(2025, 1, 13),
        "own_sub":      "IVE",
    },
]

# 14-day window: [release_date, release_date + WINDOW_DAYS)
WINDOW_DAYS = 14

# Subreddits searched for every comeback. Comparisons are case-insensitive.
SUBREDDITS = {
    "kpop", "kpopthoughts", "unpopularkpopopinions",
    "straykids", "aespa", "NCTDream", "ATEEZ", "twice", "IVE",
}
SUBREDDITS_LC = {s.lower() for s in SUBREDDITS}

# Paths. Absolute Windows paths so the script runs from any working directory.
# The r"" prefix makes these raw strings so backslashes are treated literally.
DUMP_DIR   = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\reddit\comments")
OUTPUT_DIR = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\reddit")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# CSV schema (order matters: matches existing raw files).
OUTPUT_FIELDS = ["id", "subreddit", "text", "score", "created_utc", "comeback"]


# ---------------------------------------------------------------------------
# Pushshift .zst streaming
# ---------------------------------------------------------------------------

def read_zst_ndjson(path: Path):
    """
    Yield one JSON object per line from a zstd-compressed ndjson dump.
    The large max_window_size is required because Pushshift dumps are
    compressed with long-range mode.
    """
    dctx = zstd.ZstdDecompressor(max_window_size=2 ** 31)
    with open(path, "rb") as f:
        with dctx.stream_reader(f) as reader:
            text_stream = io.TextIOWrapper(reader, encoding="utf-8")
            for line in text_stream:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    # Skip the occasional malformed line rather than
                    # aborting the whole dump.
                    continue


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def keep_comment(obj: dict, comeback: dict) -> bool:
    """Apply subreddit, date-window, body, and keyword filters."""
    sub = obj.get("subreddit", "") or ""
    if sub.lower() not in SUBREDDITS_LC:
        return False

    # Date window
    try:
        ts = int(obj.get("created_utc", 0))
    except (ValueError, TypeError):
        return False
    comment_date = datetime.utcfromtimestamp(ts)
    start = comeback["release_date"]
    end   = start + timedelta(days=WINDOW_DAYS)
    if not (start <= comment_date < end):
        return False

    # Body validity
    body = obj.get("body") or ""
    body_l = body.strip().lower()
    if not body_l or body_l in ("[deleted]", "[removed]"):
        return False

    # In the group's own subreddit, keep every valid comment in-window.
    if sub.lower() == comeback["own_sub"].lower():
        return True

    # Elsewhere, require a keyword match.
    return comeback["group"] in body_l or comeback["song"] in body_l


# ---------------------------------------------------------------------------
# Collection loop
# ---------------------------------------------------------------------------

def months_covering(start: datetime, end: datetime):
    """Yield (year, month) pairs covering the date range inclusively."""
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        if m == 12:
            y, m = y + 1, 1
        else:
            m += 1


def collect_for_comeback(comeback: dict) -> list[dict]:
    """Return the filtered, de-duplicated comments for one comeback."""
    start = comeback["release_date"]
    end   = start + timedelta(days=WINDOW_DAYS)
    rows  = []
    seen  = set()

    for year, month in months_covering(start, end):
        dump = DUMP_DIR / f"RC_{year}-{month:02d}.zst"
        if not dump.exists():
            print(f"  [warn] Missing dump for {year}-{month:02d}: {dump}")
            continue

        print(f"  Reading {dump.name} ...")
        for obj in read_zst_ndjson(dump):
            if not keep_comment(obj, comeback):
                continue
            cid = obj.get("id")
            if not cid or cid in seen:
                continue
            seen.add(cid)
            rows.append({
                "id":          cid,
                "subreddit":   obj.get("subreddit", ""),
                "text":        obj.get("body", ""),
                "score":       obj.get("score", 0),
                "created_utc": obj.get("created_utc", 0),
                "comeback":    comeback["label"],
            })

    return rows


def main() -> None:
    for cb in COMEBACKS:
        print(f"\n>>> Collecting {cb['label']} ...")
        rows = collect_for_comeback(cb)
        out_path = OUTPUT_DIR / f"{cb['label']}_reddit_raw.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"  Saved {len(rows)} comments -> {out_path}")


if __name__ == "__main__":
    main()
