"""
preprocess.py
-------------
Preprocesses the labelled YouTube and Reddit corpora and the full
English-filtered corpora for WEKA sentiment classification.

Steps applied to every comment:
    1. Encoding normalisation (fixes â€™ and similar UTF-8 mojibake
       common in Pushshift Reddit dumps)
    2. Lowercase
    3. URL removal
    4. Emoji and non-ASCII removal
    5. Number removal (digits stripped)
    6. Punctuation removal
    7. Tokenisation (whitespace split after cleaning)
    8. Stopword removal (NLTK English stopwords)
    9. Stemming (Porter stemmer, matching standard NLP pipeline)
    10. Rejoin to cleaned string

This pipeline matches the existing cleaned_comment column in
youtube_comments_for_labelling.csv, with the addition of encoding
normalisation and explicit stopword/stemming steps for consistency
with the Interim Report's stated methodology (C2).

Outputs
-------
02_processed_data/
    youtube_labelled_processed.csv   - 300 labelled YouTube rows
    reddit_labelled_processed.csv    - 297 labelled Reddit rows
    combined_labelled_processed.csv  - merged for WEKA training
    youtube_full_processed.csv       - full YouTube corpus (2619 rows)
    reddit_full_processed.csv        - full Reddit corpus (~15k rows)

04_weka_files/
    training_data.arff               - combined labelled set for WEKA
    youtube_full.arff                - full YouTube corpus for WEKA
    reddit_full.arff                 - full Reddit corpus for WEKA
"""

from __future__ import annotations

import re
import pandas as pd
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download required NLTK data if not already present
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE = Path(r"C:\Users\lenovo\kpop-sentiment-analysis")

YOUTUBE_LABELLED = BASE / "03_labeled_data" / "youtube_comments_for_labelling.csv"
REDDIT_LABELLED  = BASE / "03_labeled_data" / "reddit_labelling_template.csv"
YOUTUBE_FULL     = BASE / "01_raw_data" / "youtube" / "youtube_comments_en.csv"
REDDIT_EN_DIR    = BASE / "01_raw_data" / "reddit" / "cleaned_en"

OUT_PROCESSED    = BASE / "02_processed_data"
OUT_WEKA         = BASE / "04_weka_files"
OUT_PROCESSED.mkdir(parents=True, exist_ok=True)
OUT_WEKA.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Cleaning pipeline
# ---------------------------------------------------------------------------

STOP_WORDS = set(stopwords.words('english'))
STEMMER    = PorterStemmer()

# Encoding fix map for common UTF-8 mojibake sequences from Pushshift
ENCODING_FIXES = {
    'â€™': "'",
    'â€œ': '"',
    'â€':  '"',
    'â€"': '-',
    'â€"': '-',
    'Â':   '',
    'â€¦': '...',
}


def fix_encoding(text: str) -> str:
    """Fix common UTF-8 mojibake sequences from Pushshift dumps."""
    for bad, good in ENCODING_FIXES.items():
        text = text.replace(bad, good)
    return text


def clean(text: str) -> str:
    """Apply the full cleaning pipeline to a single comment."""
    if not isinstance(text, str) or not text.strip():
        return ''

    # Step 1: encoding fix
    text = fix_encoding(text)

    # Step 2: lowercase
    text = text.lower()

    # Step 3: remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)

    # Step 4: remove non-ASCII (emoji, Hangul residue, etc.)
    text = text.encode('ascii', errors='ignore').decode('ascii')

    # Step 5: remove digits
    text = re.sub(r'\d+', '', text)

    # Step 6: remove punctuation (keep spaces)
    text = re.sub(r'[^\w\s]', '', text)

    # Step 7: tokenise
    tokens = text.split()

    # Step 8: stopword removal
    tokens = [t for t in tokens if t not in STOP_WORDS]

    # Step 9: stemming
    tokens = [STEMMER.stem(t) for t in tokens]

    # Step 10: rejoin
    return ' '.join(tokens)


# ---------------------------------------------------------------------------
# ARFF export
# ---------------------------------------------------------------------------

def to_arff(df: pd.DataFrame,
            text_col: str,
            label_col: str,
            relation_name: str,
            path: Path,
            label_values: list[str] | None = None) -> None:
    """
    Write a simple bag-of-words ARFF file suitable for WEKA StringToWordVector.

    The text column is written as a STRING attribute so that WEKA's
    StringToWordVector filter can convert it to TF-IDF features before
    classification. This is the standard approach for text classification
    in WEKA when you don't want to pre-compute the vocabulary yourself.
    """
    if label_values is None:
        label_values = sorted(df[label_col].dropna().unique().tolist())

    lines = [
        f"@relation {relation_name}",
        "",
        "@attribute text STRING",
        f"@attribute class {{{','.join(label_values)}}}",
        "",
        "@data",
    ]

    for _, row in df.iterrows():
        text  = str(row[text_col]).replace("'", "\\'").replace('"', '\\"')
        label = str(row[label_col])
        # ARFF string values are wrapped in single quotes
        lines.append(f"'{text}',{label}")

    path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"  -> ARFF: {path}  ({len(df)} instances)")


# ---------------------------------------------------------------------------
# Processing functions
# ---------------------------------------------------------------------------

def process_youtube_labelled() -> pd.DataFrame:
    """Load, filter to labelled rows, apply cleaning, return DataFrame.

    Note: the existing 'cleaned_comment' column in the source file used a
    lighter pipeline (no stopword removal, no stemming). This function
    re-cleans from the raw 'comment' column using the full pipeline defined
    above, which matches the methodology stated in the Interim Progress
    Report (C2: tokenisation, stopword removal, stemming via NLTK).
    The 'cleaned_comment' column is intentionally ignored.
    """
    df = pd.read_csv(YOUTUBE_LABELLED)
    # Keep only labelled rows
    df = df[df['sentiment'].notna()].copy()
    df = df.rename(columns={'sentiment': 'label', 'comment': 'raw_text',
                             'group_comeback': 'comeback'})
    # Re-clean from raw text (not cleaned_comment)
    df['cleaned_text'] = df['raw_text'].apply(clean)
    df['source'] = 'youtube'
    return df[['comeback', 'raw_text', 'cleaned_text', 'label', 'source']]


def process_reddit_labelled() -> pd.DataFrame:
    """Load labelled Reddit rows, apply cleaning, return DataFrame."""
    df = pd.read_csv(REDDIT_LABELLED)
    df = df[df['label'].notna()].copy()
    df = df.rename(columns={'text': 'raw_text'})
    df['cleaned_text'] = df['raw_text'].apply(clean)
    df['source'] = 'reddit'
    return df[['comeback', 'raw_text', 'cleaned_text', 'label', 'source']]


def process_youtube_full() -> pd.DataFrame:
    """Load the full English-filtered YouTube corpus and clean it."""
    df = pd.read_csv(YOUTUBE_FULL)
    df = df.rename(columns={'comment': 'raw_text',
                             'group_comeback': 'comeback'})
    df['cleaned_text'] = df['raw_text'].apply(clean)
    df['label'] = '?'   # unknown — to be predicted by classifier
    df['source'] = 'youtube'
    return df[['comeback', 'raw_text', 'cleaned_text', 'label', 'source']]


def process_reddit_full() -> pd.DataFrame:
    """Load all six English-filtered Reddit CSVs and clean them."""
    frames = []
    for path in sorted(REDDIT_EN_DIR.glob("*_en.csv")):
        sub = pd.read_csv(path)
        sub = sub.rename(columns={'text': 'raw_text'})
        frames.append(sub)
    df = pd.concat(frames, ignore_index=True)
    df['cleaned_text'] = df['raw_text'].apply(clean)
    df['label'] = '?'
    df['source'] = 'reddit'
    return df[['comeback', 'raw_text', 'cleaned_text', 'label', 'source']]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    label_values = ['negative', 'neutral', 'positive']

    print("Processing YouTube labelled ...")
    yt_lab = process_youtube_labelled()
    yt_lab.to_csv(OUT_PROCESSED / "youtube_labelled_processed.csv", index=False)
    print(f"  {len(yt_lab)} rows  |  {yt_lab['label'].value_counts().to_dict()}")

    print("Processing Reddit labelled ...")
    rd_lab = process_reddit_labelled()
    rd_lab.to_csv(OUT_PROCESSED / "reddit_labelled_processed.csv", index=False)
    print(f"  {len(rd_lab)} rows  |  {rd_lab['label'].value_counts().to_dict()}")

    print("Combining labelled sets ...")
    combined = pd.concat([yt_lab, rd_lab], ignore_index=True)
    combined.to_csv(OUT_PROCESSED / "combined_labelled_processed.csv", index=False)
    print(f"  {len(combined)} rows  |  {combined['label'].value_counts().to_dict()}")

    print("Processing full YouTube corpus ...")
    yt_full = process_youtube_full()
    yt_full.to_csv(OUT_PROCESSED / "youtube_full_processed.csv", index=False)
    print(f"  {len(yt_full)} rows")

    print("Processing full Reddit corpus ...")
    rd_full = process_reddit_full()
    rd_full.to_csv(OUT_PROCESSED / "reddit_full_processed.csv", index=False)
    print(f"  {len(rd_full)} rows")

    print("\nExporting ARFF files ...")
    to_arff(combined, 'cleaned_text', 'label',
            'kpop_sentiment_training', OUT_WEKA / 'training_data.arff',
            label_values)
    to_arff(yt_full, 'cleaned_text', 'label',
            'youtube_full', OUT_WEKA / 'youtube_full.arff',
            label_values)
    to_arff(rd_full, 'cleaned_text', 'label',
            'reddit_full', OUT_WEKA / 'reddit_full.arff',
            label_values)

    print("\nDone. Summary:")
    print(f"  Training instances : {len(combined)}")
    print(f"  YouTube to predict : {len(yt_full)}")
    print(f"  Reddit to predict  : {len(rd_full)}")
    print(f"  ARFF files in      : {OUT_WEKA}")


if __name__ == "__main__":
    main()
