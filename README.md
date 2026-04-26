# K-pop Comeback Sentiment Analysis

**BSc Computer Science (Online) — Final Year Project**
**University of Hertfordshire**
**Student:** Miracle Okoi-Obuli
**Supervisor:** Lili Kirner
**Year:** 2026

---

## Project Overview

This project investigates whether social media sentiment expressed by K-pop fans correlates with the YouTube performance of comeback music videos. Six comebacks from 2024–2025 were selected as case studies, with sentiment data collected from Reddit and YouTube comments and performance metrics collected via the YouTube Data API v3.

**Research Question:** Does social media sentiment toward K-pop comebacks correlate with their YouTube engagement metrics?

---

## Six Comebacks Studied

| Group | Song | Release Date |
|---|---|---|
| aespa | Whiplash | 21 October 2024 |
| ATEEZ | Ice On My Teeth | 15 November 2024 |
| NCT DREAM | When I'm With You | 11 November 2024 |
| Stray Kids | Chk Chk Boom | 19 July 2024 |
| TWICE | Strategy | 6 December 2024 |
| IVE | Rebel Heart | 13 January 2025 |

---

## Repository Structure

```
kpop-sentiment-analysis/
├── 01_raw_data/
│   ├── youtube/          # YouTube comments and metrics
│   └── reddit/           # Reddit raw, cleaned, and English-filtered CSVs
├── 02_processed_data/    # Preprocessed corpora and training sets
├── 03_labeled_data/      # Manually labelled datasets and codebook
├── 04_weka_files/        # ARFF files for WEKA classification
├── 05_models/            # Trained models and classifier results
├── 06_correlation_analysis/  # Pearson/Spearman correlation results
├── 07_tableau/           # Tableau data files and dashboard
├── 08_visualizations/    # Tableau workbook
├── 09_reports/           # Final report, interim report, screenshots
├── 10_scripts/           # All Python scripts
├── anaconda_projects/    # Original Jupyter notebooks
├── methodology_log.md    # Complete methodology documentation
└── project_log.md        # Project diary and decision log
```

---

## Pipeline

1. **Data Collection** — YouTube metrics and comments via YouTube Data API v3; Reddit comments via Pushshift monthly archive dumps (RC_*.zst)
2. **Filtering** — Keyword relevance filter (reddit_filter.py); English-only language filter (language_filter.py)
3. **Preprocessing** — Encoding normalisation, tokenisation, stopword removal, Porter stemming (preprocess.py)
4. **Manual Labelling** — 597 comments labelled positive/negative/neutral using formal codebook
5. **Classification** — Naïve Bayes and SVM trained in WEKA; full corpus predicted using scikit-learn LinearSVC
6. **Correlation Analysis** — Pearson and Spearman coefficients between sentiment scores and YouTube metrics
7. **Visualisation** — Interactive Tableau Public dashboard

---

## Scripts

| Script | Purpose |
|---|---|
| `10_scripts/reddit_collection.py` | Collect Reddit comments from Pushshift archive dumps |
| `10_scripts/reddit_filter.py` | Apply word-boundary-aware keyword filter |
| `10_scripts/language_filter.py` | Filter to English-only content |
| `10_scripts/preprocess.py` | Text cleaning pipeline and ARFF export |
| `10_scripts/sample_for_labelling.py` | Random stratified sampling for manual labelling |
| `10_scripts/collect_youtube_metrics.py` | Collect YouTube engagement metrics |

Original data collection and preprocessing notebooks are in `anaconda_projects/`.

---

## Key Results

- **Best classifier:** SVM (SMO), 65.49% accuracy, weighted F1 0.642
- **Strongest correlation:** Reddit sentiment vs like-to-view ratio, Pearson r = -0.795, p = 0.059
- **No statistically significant correlation** found between YouTube sentiment and any engagement metric
- All results presented in the [Tableau Public dashboard](https://public.tableau.com/views/KPop_Sentiment_Analysis_Dashboard/K-popSentimentDashboard)

---

## Dependencies

```
pip install pandas numpy scikit-learn nltk langdetect scipy zstandard google-api-python-client
```

WEKA 3.8 is required for the classifier training steps documented in `04_weka_files/`.

---

## Data Sources

- **Reddit:** Pushshift monthly comment archives via [Academic Torrents](https://academictorrents.com). Dumps not included in this repository due to file size (~30GB each).
- **YouTube:** YouTube Data API v3. API key required (store in `credentials/api_keys.txt`, excluded from version control).

---

## AI Use Declaration

This project was developed with assistance from Claude (Anthropic, claude.ai) and Perplexity AI. Full details are documented in the Final Project Report (Introduction and Appendix H) and in `project_log.md`.

---

## Tableau Dashboard

Interactive dashboard published at:
https://public.tableau.com/views/KPop_Sentiment_Analysis_Dashboard/K-popSentimentDashboard
