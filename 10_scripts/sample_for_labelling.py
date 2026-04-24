"""
sample_for_labelling.py
-----------------------
Draws a stratified random sample of 50 comments per comeback from both
Reddit and YouTube English-filtered corpora, producing two labelling
workbooks. Adds an empty 'label' column for the user to fill with
positive, negative, or neutral.

Rationale
    Random stratified sampling is reproducible (fixed seed) and avoids
    self-selection bias that would occur if the labeller chose which
    comments to label. This is the standard practice for building a
    labelled training set from a larger corpus.

Output
    03_labeled_data/reddit_labelling_template.csv
    03_labeled_data/youtube_labelling_template.csv
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path


RANDOM_SEED        = 42
SAMPLE_PER_COMEBACK = 50

REDDIT_DIR = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\reddit\cleaned_en")
YT_FILE    = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\youtube\youtube_comments_en.csv")
OUT_DIR    = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\03_labeled_data")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def sample_reddit() -> pd.DataFrame:
    frames = []
    for path in sorted(REDDIT_DIR.glob("*_en.csv")):
        df = pd.read_csv(path)
        if len(df) < SAMPLE_PER_COMEBACK:
            print(f"  WARN: {path.name} has only {len(df)} rows, taking all")
            sampled = df.copy()
        else:
            sampled = df.sample(n=SAMPLE_PER_COMEBACK, random_state=RANDOM_SEED)
        frames.append(sampled)
    result = pd.concat(frames, ignore_index=True)
    result["label"] = ""   # empty column for manual labelling
    result["source"] = "reddit"
    return result


def sample_youtube() -> pd.DataFrame:
    df = pd.read_csv(YT_FILE)
    frames = []
    for cb, sub in df.groupby("group_comeback"):
        if len(sub) < SAMPLE_PER_COMEBACK:
            print(f"  WARN: {cb} has only {len(sub)} rows, taking all")
            sampled = sub.copy()
        else:
            sampled = sub.sample(n=SAMPLE_PER_COMEBACK, random_state=RANDOM_SEED)
        frames.append(sampled)
    result = pd.concat(frames, ignore_index=True)
    result["label"] = ""
    result["source"] = "youtube"
    return result


def main() -> None:
    print("Sampling Reddit ...")
    rd = sample_reddit()
    rd_out = OUT_DIR / "reddit_labelling_template.csv"
    rd.to_csv(rd_out, index=False)
    print(f"  -> {rd_out}  ({len(rd)} rows)")

    print("Sampling YouTube ...")
    yt = sample_youtube()
    yt_out = OUT_DIR / "youtube_labelling_template.csv"
    yt.to_csv(yt_out, index=False)
    print(f"  -> {yt_out}  ({len(yt)} rows)")


if __name__ == "__main__":
    main()
