"""
language_filter.py
------------------
Filters the cleaned Reddit CSVs (and YouTube CSVs) down to English-only
comments for downstream preprocessing, manual labelling, and classification.

Rationale
    The Interim Progress Report (March 2026) committed the methodology to
    English-language content only. K-pop fan comments across both platforms
    regularly contain Korean (in Hangul and in romanised form), Indonesian,
    Spanish, Thai, Turkish, and other languages. Including these in the
    corpus would produce garbage features for an English-trained classifier.

    The `langdetect` library is the standard Python tool for this task but
    is known to be unreliable on short text (it reports high confidence on
    obviously-wrong guesses like "Wow." -> Polish, "Rebel Heart slaps"
    -> Dutch). Because fan comments are overwhelmingly short, a naive
    langdetect filter would discard a substantial amount of genuine English
    content.

Filter logic
    1. Non-Latin script check: if a comment contains substantial Hangul,
       CJK, Cyrillic, Thai, Arabic, or Hebrew characters, it is flagged
       as non-English and excluded.
    2. Very short comments (under 15 words) are kept by default. The
       small amount of non-English noise this admits is preferable to
       the high rate of false-negative English exclusions langdetect
       produces on short text.
    3. For comments of 15 words or more, langdetect is consulted. Only
       comments detected as English with confidence >= 0.80 are kept.

    This favours recall (keeping genuine English) over precision
    (excluding every non-English comment), which is the right trade-off
    for a small training corpus.

Input
    Cleaned CSVs from 01_raw_data/reddit/cleaned/
    YouTube raw CSVs from their existing location (adjust YT_INPUT_DIR)

Output
    English-only CSVs in 01_raw_data/reddit/cleaned_en/
    A summary table reporting rows kept vs. dropped per file.
"""

from __future__ import annotations

import re
import pandas as pd
from pathlib import Path
from langdetect import detect_langs, DetectorFactory, LangDetectException


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Deterministic langdetect behaviour across runs
DetectorFactory.seed = 0

REDDIT_INPUT_DIR  = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\reddit\cleaned")
REDDIT_OUTPUT_DIR = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\reddit\cleaned_en")
REDDIT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# YouTube data is stored as a single combined CSV rather than per-comeback
# files. If YT_INPUT_FILE is set to None, YouTube filtering is skipped.
YT_INPUT_FILE  = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\youtube\youtube_comments_raw.csv")
YT_OUTPUT_FILE = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\youtube\youtube_comments_en.csv")
YT_TEXT_COL    = "comment"
YT_GROUP_COL   = "group_comeback"

LONG_TEXT_WORDS_THRESHOLD = 15
LANGDETECT_CONFIDENCE     = 0.80

# Unicode ranges for non-Latin scripts common in K-pop fan comments
NON_LATIN_RANGES = [
    (0xAC00, 0xD7AF),   # Hangul syllables
    (0x1100, 0x11FF),   # Hangul Jamo
    (0x3130, 0x318F),   # Hangul compat
    (0x3040, 0x309F),   # Hiragana
    (0x30A0, 0x30FF),   # Katakana
    (0x4E00, 0x9FFF),   # CJK unified ideographs
    (0x0400, 0x04FF),   # Cyrillic
    (0x0E00, 0x0E7F),   # Thai
    (0x0600, 0x06FF),   # Arabic
    (0x0590, 0x05FF),   # Hebrew
]


# ---------------------------------------------------------------------------
# Filtering logic
# ---------------------------------------------------------------------------

def non_latin_char_ratio(text: str) -> float:
    """Return the fraction of characters that fall in non-Latin scripts."""
    if not text:
        return 0.0
    non_latin = 0
    total = 0
    for ch in text:
        cp = ord(ch)
        if ch.isspace() or not ch.isalpha():
            continue
        total += 1
        for lo, hi in NON_LATIN_RANGES:
            if lo <= cp <= hi:
                non_latin += 1
                break
    if total == 0:
        return 0.0
    return non_latin / total


def is_english(text: str) -> bool:
    """Decide whether a comment should be kept as English content."""
    if not isinstance(text, str) or not text.strip():
        return False

    # Rule 1: heavy non-Latin script -> drop
    if non_latin_char_ratio(text) >= 0.20:
        return False

    # Rule 2: short text -> keep (langdetect unreliable)
    word_count = len(text.split())
    if word_count < LONG_TEXT_WORDS_THRESHOLD:
        return True

    # Rule 3: longer text -> consult langdetect with confidence threshold
    try:
        langs = detect_langs(text)
        top = langs[0]
        return top.lang == "en" and top.prob >= LANGDETECT_CONFIDENCE
    except LangDetectException:
        # langdetect gave up (e.g. pure emoji/symbol content). Default to
        # keeping, since the non-Latin check already ran.
        return True


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------

def filter_csv(in_path: Path, out_path: Path, text_col: str = "text") -> dict:
    df = pd.read_csv(in_path)
    total = len(df)
    if text_col not in df.columns:
        raise ValueError(f"{in_path.name}: no '{text_col}' column")

    mask = df[text_col].apply(is_english)
    kept = df[mask].copy()
    kept.to_csv(out_path, index=False)

    return {
        "file":    in_path.name,
        "total":   total,
        "kept":    int(mask.sum()),
        "dropped": total - int(mask.sum()),
        "drop_pct": round(100 * (total - int(mask.sum())) / total, 1)
                    if total else 0.0,
        "output":  out_path.name,
    }


def filter_youtube_single_file() -> list:
    """
    Filter the combined YouTube CSV and report per-comeback drop rates.
    Returns a list of summary dicts (one per comeback + one total row).
    """
    df = pd.read_csv(YT_INPUT_FILE)
    if YT_TEXT_COL not in df.columns:
        raise ValueError(f"{YT_INPUT_FILE.name}: no '{YT_TEXT_COL}' column")

    print(f"Filtering YouTube: {YT_INPUT_FILE.name} ...")
    mask = df[YT_TEXT_COL].apply(is_english)
    kept = df[mask].copy()

    YT_OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    kept.to_csv(YT_OUTPUT_FILE, index=False)

    rows = []
    for cb, sub in df.groupby(YT_GROUP_COL):
        sub_mask = sub[YT_TEXT_COL].apply(is_english)
        total = len(sub)
        k = int(sub_mask.sum())
        rows.append({
            "file":     f"youtube:{cb}",
            "total":    total,
            "kept":     k,
            "dropped":  total - k,
            "drop_pct": round(100 * (total - k) / total, 1) if total else 0.0,
            "output":   YT_OUTPUT_FILE.name,
        })
    # Combined row
    rows.append({
        "file":     "youtube:TOTAL",
        "total":    len(df),
        "kept":     int(mask.sum()),
        "dropped":  len(df) - int(mask.sum()),
        "drop_pct": round(100 * (len(df) - int(mask.sum())) / len(df), 1) if len(df) else 0.0,
        "output":   YT_OUTPUT_FILE.name,
    })
    return rows


def main() -> None:
    summary = []

    # Reddit cleaned CSVs
    for in_path in sorted(REDDIT_INPUT_DIR.glob("*_cleaned.csv")):
        out_path = REDDIT_OUTPUT_DIR / in_path.name.replace("_cleaned.csv", "_en.csv")
        print(f"Filtering Reddit: {in_path.name} ...")
        summary.append(filter_csv(in_path, out_path, text_col="text"))

    # YouTube combined CSV
    if YT_INPUT_FILE is not None and YT_INPUT_FILE.exists():
        summary.extend(filter_youtube_single_file())
    else:
        print(f"YouTube file not found at {YT_INPUT_FILE}; skipping YouTube.")

    summary_df = pd.DataFrame(summary)
    print("\n=== LANGUAGE FILTER SUMMARY ===")
    print(summary_df.to_string(index=False))

    summary_path = REDDIT_OUTPUT_DIR / "_language_filter_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"\nSummary written to {summary_path}")


if __name__ == "__main__":
    main()
