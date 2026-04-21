"""
reddit_filter.py
----------------
Post-hoc keyword filter applied to the six raw Reddit CSVs produced by
reddit_collection.py. Replaces the initial case-insensitive substring
match with a stricter, word-boundary-aware ruleset that eliminates
false positives caused by group names colliding with common English
words (notably IVE vs. the contraction "I've", and TWICE vs. the
adverb "twice").

Rationale
    The original collection script used `group_name in text.lower()`.
    This worked well for distinctive tokens (aespa, ATEEZ, stray kids,
    nct dream) but introduced substantial noise for IVE and TWICE.
    Audit of the raw IVE data showed that comments pulled from non-IVE
    subreddits matched "ive" as a substring of common words (I've,
    received, alive, give) in the large majority of cases.

    This filter is applied symmetrically to all six comebacks so the
    refinement does not bias one group relative to the others.

Filter rules (applied only to comments outside the comeback's own sub)
    A comment is kept if any one of:
        1. The song title phrase matches (case-insensitive). If the
           title is itself a common English word or phrase (Strategy,
           When I'm With You), the comment must also contain the
           group name token or a recognised member name.
        2. The group name pattern matches. For all-caps stylized
           names (IVE, TWICE), matching is case-sensitive to
           distinguish "IVE" from "I've" / "ive".
        3. A member name (word-boundary, case-insensitive) appears.

Own-sub comments are always kept. Topical relevance is implicit when
a user posts in the group's own subreddit.

Input
    Six raw CSVs in 01_raw_data/reddit/

Output
    Six cleaned CSVs in 01_raw_data/reddit/cleaned/
    Plus a _filter_summary.csv table of rows kept vs. dropped.
"""

from __future__ import annotations

import re
import pandas as pd
from pathlib import Path


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INPUT_DIR  = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\reddit")
OUTPUT_DIR = INPUT_DIR / "cleaned"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Per-comeback filter specification.
#   own_sub:        subreddit name (case-insensitive comparison)
#   song_pattern:   regex for the song title
#   song_ambiguous: True if the song title is a common English word/phrase
#                   and therefore requires additional context to match
#   group_pattern:  regex for the group name
#   group_case:     True = case-sensitive match (for all-caps stylizations)
#   members:        list of member names (word-boundary, case-insensitive)
FILTERS = {
    "IVE_RebelHeart": {
        "file":           "IVE_RebelHeart_reddit_raw.csv",
        "own_sub":        "ive",
        "song_pattern":   r"rebel\s+heart",
        "song_ambiguous": False,
        "group_pattern":  r"\bIVE\b",
        "group_case":     True,
        "members":        ["yujin", "gaeul", "rei", "wonyoung", "liz", "leeseo"],
    },
    "TWICE_Strategy": {
        "file":           "TWICE_Strategy_reddit_raw.csv",
        "own_sub":        "twice",
        "song_pattern":   r"\bstrategy\b",
        "song_ambiguous": True,
        "group_pattern":  r"\bTWICE\b",
        "group_case":     True,
        "members":        ["nayeon", "jeongyeon", "momo", "sana", "jihyo",
                           "mina", "dahyun", "chaeyoung", "tzuyu"],
    },
    "aespa_Whiplash": {
        "file":           "aespa_Whiplash_reddit_raw.csv",
        "own_sub":        "aespa",
        "song_pattern":   r"\bwhiplash\b",
        "song_ambiguous": False,
        "group_pattern":  r"\baespa\b",
        "group_case":     False,
        "members":        ["karina", "giselle", "winter", "ningning"],
    },
    "StrayKids_ChkChkBoom": {
        "file":           "StrayKids_ChkChkBoom_reddit_raw.csv",
        "own_sub":        "straykids",
        "song_pattern":   r"chk\s*chk\s*boom",
        "song_ambiguous": False,
        "group_pattern":  r"\bstray\s*kids\b|\bSKZ\b",
        "group_case":     False,
        "members":        ["bang chan", "bangchan", "lee know", "leeknow",
                           "changbin", "hyunjin", "felix", "seungmin",
                           "han jisung"],
    },
    "NCTDREAM_WhenImWithYou": {
        "file":           "NCTDREAM_WhenImWithYou_reddit_raw.csv",
        "own_sub":        "nctdream",
        "song_pattern":   r"when\s+i'?m\s+with\s+you",
        "song_ambiguous": True,
        "group_pattern":  r"\bnct\s*dream\b",
        "group_case":     False,
        "members":        ["renjun", "jeno", "haechan", "jaemin",
                           "chenle", "jisung"],
    },
    "ATEEZ_IceOnMyTeeth": {
        "file":           "ATEEZ_IceOnMyTeeth_reddit_raw.csv",
        "own_sub":        "ateez",
        "song_pattern":   r"ice\s+on\s+my\s+teeth",
        "song_ambiguous": False,
        "group_pattern":  r"\bateez\b",
        "group_case":     False,
        "members":        ["hongjoong", "seonghwa", "yunho", "yeosang",
                           "wooyoung", "jongho", "mingi"],
    },
}


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def match_group(text: str, spec: dict) -> bool:
    flags = 0 if spec["group_case"] else re.IGNORECASE
    return bool(re.search(spec["group_pattern"], text, flags))


def match_song(text: str, spec: dict) -> bool:
    return bool(re.search(spec["song_pattern"], text, re.IGNORECASE))


def match_member(text: str, spec: dict) -> bool:
    for m in spec["members"]:
        if re.search(rf"\b{re.escape(m)}\b", text, re.IGNORECASE):
            return True
    return False


def is_true_mention(text: str, spec: dict) -> bool:
    if not isinstance(text, str) or not text:
        return False

    if match_song(text, spec):
        if spec["song_ambiguous"]:
            if match_group(text, spec) or match_member(text, spec):
                return True
        else:
            return True

    if match_group(text, spec):
        return True

    if match_member(text, spec):
        return True

    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def filter_file(label: str, spec: dict) -> dict:
    path = INPUT_DIR / spec["file"]
    df = pd.read_csv(path)
    total = len(df)

    own_mask = df["subreddit"].str.lower() == spec["own_sub"].lower()
    other_df = df[~own_mask].copy()
    kept_other = other_df["text"].apply(lambda t: is_true_mention(t, spec))

    cleaned = pd.concat([df[own_mask], other_df[kept_other]], ignore_index=True)

    out_path = OUTPUT_DIR / spec["file"].replace("_raw.csv", "_cleaned.csv")
    cleaned.to_csv(out_path, index=False)

    return {
        "comeback":     label,
        "total_raw":    total,
        "own_sub_kept": int(own_mask.sum()),
        "other_raw":    int((~own_mask).sum()),
        "other_kept":   int(kept_other.sum()),
        "total_clean":  len(cleaned),
        "dropped":      total - len(cleaned),
        "drop_pct":     round(100 * (total - len(cleaned)) / total, 1),
        "output":       out_path.name,
    }


def main() -> None:
    summary = [filter_file(label, spec) for label, spec in FILTERS.items()]
    summary_df = pd.DataFrame(summary)

    print("\n=== FILTER SUMMARY ===")
    print(summary_df.to_string(index=False))

    summary_path = OUTPUT_DIR / "_filter_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"\nSummary written to {summary_path}")


if __name__ == "__main__":
    main()
