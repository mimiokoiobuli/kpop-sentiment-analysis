# K-pop Sentiment Analysis — Project Methodology Log
**Author**: Miracle Okoi-Obuli  
**Last Updated**: 23 April 2026  
**Purpose**: Complete record of every methodological decision, tool, file, and step taken during the practical phase of the project. For use in Final Report writing and VIVA preparation.

---

## 1. Research Question and Aim

**Aim**: To investigate whether social media sentiment toward K-pop comebacks, as expressed in Reddit fan discussion and YouTube comments, correlates with the comebacks' performance on YouTube.

**Six comebacks studied**:

| Label | Group | Song | Release Date | Video ID |
|---|---|---|---|---|
| aespa_Whiplash | aespa | Whiplash | 2024-10-21 | jWQx2f-CErU |
| ATEEZ_IceOnMyTeeth | ATEEZ | Ice On My Teeth | 2024-11-15 | 5OflOlcHLb8 |
| NCTDREAM_WhenImWithYou | NCT DREAM | When I'm With You | 2024-11-11 | B1qq8IvzSz4 |
| TWICE_Strategy | TWICE | Strategy | 2024-12-06 | Sz_wWzgh-vQ |
| IVE_RebelHeart | IVE | Rebel Heart | 2025-01-13 | g36q0ZLvygQ |
| StrayKids_ChkChkBoom | Stray Kids | Chk Chk Boom | 2024-07-19 | 0P0aQreFs8w |

**Note on IVE**: Rebel Heart was released as a pre-release single on 13 January 2025. The full IVE EMPATHY mini-album (title track: ATTITUDE) was released on 3 February 2025. This project studies the Rebel Heart single specifically, to match the YouTube MV collected. An earlier collection attempt used the February 2025 window by mistake and was corrected.

**Note on Twitter**: The Interim Progress Report proposed using Twitter alongside Reddit. Twitter API access was not granted. On 13 March 2026, the supervisor (Lili Kirner) approved a pivot to YouTube comments and Reddit archive data as the two social media sources.

---

## 2. Data Collection

### 2.1 YouTube Engagement Metrics

**Script**: `anaconda_projects/01_youtube_collector.ipynb` (Jupyter Notebook)  
**Tool**: YouTube Data API v3 via `google-api-python-client`  
**API key location**: `credentials/api_keys.txt`  
**Output**: `07_tableau/youtube_metrics_snapshot.csv`  
**Collected**: 20 March 2026  

**Metrics collected per comeback**:
- `view_count`
- `like_count`
- `comment_count`
- `like_to_view_ratio` (derived: like_count / view_count)

**Results**:

| Comeback | Views | Likes | Comments | Like/View |
|---|---|---|---|---|
| aespa_Whiplash | 272,860,242 | 2,496,666 | 94,955 | 0.00915 |
| IVE_RebelHeart | 64,041,208 | 784,179 | 42,838 | 0.01225 |
| TWICE_Strategy | 146,374,901 | 1,970,932 | 204,572 | 0.01347 |
| NCTDREAM_WhenImWithYou | 15,889,568 | 515,104 | 42,525 | 0.03242 |
| ATEEZ_IceOnMyTeeth | 98,921,178 | 1,062,250 | 68,104 | 0.01074 |
| StrayKids_ChkChkBoom | 198,946,095 | 3,631,709 | 391,720 | 0.01826 |

**Note**: Metrics represent cumulative totals as of the collection date (March 2026), not window-specific counts. This is a limitation acknowledged in the Discussion chapter.

---

### 2.2 YouTube Comments

**Script**: `anaconda_projects/01_youtube_collector.ipynb` (same notebook, Part 2)  
**Tool**: YouTube Data API v3, `commentThreads().list()` endpoint  
**Window**: 14-day window from each comeback's release date  
**Max per comeback**: 500 (API pagination limit applied)  
**Output**: `01_raw_data/youtube/youtube_comments_raw.csv`  

**Schema**: `video_id, comment, likes, published_at, group_comeback`  
**Total rows**: 3,283  

---

### 2.3 Reddit Comments

**Original script**: Lost from local storage before being committed to git. Reconstructed on 21 April 2026 from the existing raw CSV files using reverse-engineering of the schema, subreddit distribution, date windows, and keyword filter behaviour.

**Script**: `10_scripts/reddit_collection.py`  
**Data source**: Pushshift monthly archive dumps (Academic Torrents), `.zst` format  
**Dump files used**:

| Dump | Comebacks covered |
|---|---|
| RC_2024-07.zst | StrayKids_ChkChkBoom |
| RC_2024-10.zst | aespa_Whiplash |
| RC_2024-11.zst | NCTDREAM_WhenImWithYou, ATEEZ_IceOnMyTeeth |
| RC_2024-12.zst | TWICE_Strategy |
| RC_2025-01.zst | IVE_RebelHeart |
| RC_2025-02.zst | Not used (February IVE window was incorrect) |

**Dump files location**: `01_raw_data/reddit/comments/`  
**Submission dumps** (RS_*.zst): Downloaded but not used. Only comment dumps (RC_*.zst) were used.

**Subreddits searched** (9 total):
- General: r/kpop, r/kpopthoughts, r/unpopularkpopopinions
- Group-specific: r/straykids, r/Aespa, r/NCTDream, r/ATEEZ, r/twice, r/IVE

**Window**: 14 days starting on each comeback's official release date (day 0 to day +13 inclusive)

**Keyword filter (initial)**:
- Own-sub comments: kept unconditionally (topical relevance assumed)
- Other-sub comments: kept only if text contains group name OR song title (case-insensitive substring match)

**IVE correction**: Original collection used `datetime(2025, 2, 3)` (album release date). Corrected to `datetime(2025, 1, 13)` (Rebel Heart pre-release single date) and re-collected using RC_2025-01.zst.

**Raw CSV outputs**: `01_raw_data/reddit/` (one file per comeback)

| File | Rows | Date range |
|---|---|---|
| aespa_Whiplash_reddit_raw.csv | 2,860 | 2024-10-21 to 2024-11-03 |
| ATEEZ_IceOnMyTeeth_reddit_raw.csv | 4,102 | 2024-11-15 to 2024-11-28 |
| NCTDREAM_WhenImWithYou_reddit_raw.csv | 534 | 2024-11-11 to 2024-11-24 |
| StrayKids_ChkChkBoom_reddit_raw.csv | 4,654 | 2024-07-19 to 2024-07-31 |
| TWICE_Strategy_reddit_raw.csv | 2,792 | 2024-12-06 to 2024-12-19 |
| IVE_RebelHeart_reddit_raw.csv | 7,450 | 2025-01-13 to 2025-01-26 |

---

## 3. Data Filtering

### 3.1 Reddit Keyword Filter (Post-hoc Refinement)

**Problem identified**: The initial substring filter admitted false positives for group names that collide with common English words:
- "IVE" matches "I've", "give", "alive", "received" → 76% of IVE non-own-sub comments were noise
- "TWICE" matches "twice" (adverb) → 21% noise
- "NCT DREAM When I'm With You" → "when i'm with you" matches common English → 20% noise
- aespa, ATEEZ, Stray Kids: <1.5% false positives (distinctive tokens)

**Solution**: Written `10_scripts/reddit_filter.py` applying word-boundary-aware matching:
- IVE: case-sensitive `\bIVE\b` (not `\bive\b`)
- TWICE: case-sensitive `\bTWICE\b`
- Song titles marked ambiguous ("strategy", "when i'm with you"): require group name OR member name in same comment
- Member names used as supplementary signal for all comebacks

**Filter applied symmetrically to all six comebacks.**

**Results**:

| Comeback | Raw | Cleaned | Dropped | Drop % |
|---|---|---|---|---|
| IVE_RebelHeart | 7,450 | 1,763 | 5,687 | 76.3% |
| TWICE_Strategy | 2,792 | 2,214 | 578 | 20.7% |
| NCTDREAM_WhenImWithYou | 534 | 428 | 106 | 19.9% |
| aespa_Whiplash | 2,860 | 2,826 | 34 | 1.2% |
| ATEEZ_IceOnMyTeeth | 4,102 | 4,044 | 58 | 1.4% |
| StrayKids_ChkChkBoom | 4,654 | 4,642 | 12 | 0.3% |

**Output**: `01_raw_data/reddit/cleaned/` (six `*_reddit_cleaned.csv` files)

---

### 3.2 Language Filter

**Decision**: Interim Progress Report committed to English-language content only (C1). Both Reddit and YouTube corpora contain non-English content.

**Script**: `10_scripts/language_filter.py`

**Method (two-stage)**:
1. Non-Latin script check: comments containing ≥20% Hangul, CJK, Cyrillic, Thai, Arabic, or Hebrew characters are excluded
2. Short comments (<15 words): kept by default (langdetect unreliable on short text)
3. Longer comments (≥15 words): langdetect consulted, English required at ≥80% confidence

**Limitation**: Romanised Korean and some other Latin-script languages pass this filter. A small number of non-English comments remain in the corpus. Acknowledged in Discussion.

**Reddit results**: 0.0%–0.5% drop per comeback (Reddit is overwhelmingly English)  
**YouTube results**: 20.2% overall drop; IVE specifically 60.4% (large Korean/Japanese fanbase)

**Reddit output**: `01_raw_data/reddit/cleaned_en/` (six `*_reddit_en.csv` files)  
**YouTube output**: `01_raw_data/youtube/youtube_comments_en.csv` (2,619 rows)

---

### 3.3 Reddit Corpus Scope Note

Reddit comments were collected during each comeback's 14-day window based on group name/member name keyword matching. This captures general fan discourse about the group during the comeback window, not exclusively discussion of the specific comeback title track. This operationalisation is a known limitation of keyword-based filtering on social media data. It is assumed that group-related fan discourse during a comeback window is primarily driven by the comeback event. Acknowledged in Methodology and Limitations.

---

## 4. Manual Labelling

### 4.1 YouTube Labelling

**Source file**: `anaconda_projects/02_youtube_preprocessing.ipynb` produced `03_labeled_data/youtube_comments_for_labelling.csv`  
**Schema**: `group_comeback, comment, cleaned_comment, sentiment`  
**Total rows**: 1,035 (after deduplication from 1,082)  
**Labelling approach**: Sequential top-50 per comeback (not random sample)  
**Labels assigned**: 300 total (50 per comeback)  
**Label distribution**: positive 152, neutral 138, negative 10  

**Limitation**: Sequential sampling introduces ordering bias. A random stratified sample would have been methodologically stronger. Acknowledged in Discussion.

**Labelling tool**: Microsoft Excel  
**Labeller**: Project author (Miracle Okoi-Obuli)  
**Codebook**: `03_labeled_data/labelling_codebook.md`

---

### 4.2 Reddit Labelling

**Script**: `10_scripts/sample_for_labelling.py`  
**Sampling method**: Random stratified sample (seed=42), 50 per comeback from `cleaned_en` corpus  
**Output template**: `03_labeled_data/reddit_labelling_template.csv`  
**Schema**: `id, subreddit, text, score, created_utc, comeback, label, source`  
**Total rows**: 297 (NCT DREAM had 47 unique comments after deduplication; 3 duplicates removed)  
**Label distribution**: neutral 196, positive 88, negative 13  

**Labelling approach**: Random sample, labelled using same codebook as YouTube  
**Labeller**: Project author  

---

### 4.3 Class Imbalance

Combined training set: 597 instances  
- Neutral: 334 (55.9%)
- Positive: 240 (40.2%)
- Negative: 23 (3.9%)

Class imbalance reflects genuine skew of K-pop fan discourse in public spaces toward positive sentiment. Not a labelling error. Handled in classification via `class_weight='balanced'` (scikit-learn) / cost-sensitive approach. Acknowledged in Discussion.

---

## 5. Preprocessing

**Script**: `10_scripts/preprocess.py`  
**Pipeline** (applied identically to YouTube and Reddit):
1. Encoding normalisation (fixes â€™ and similar UTF-8 mojibake from Pushshift)
2. Lowercase
3. URL removal
4. Emoji and non-ASCII removal
5. Number removal
6. Punctuation removal
7. Tokenisation (whitespace split)
8. Stopword removal (NLTK English stopwords)
9. Porter stemming (NLTK PorterStemmer)
10. Rejoin to cleaned string

**Note**: The `cleaned_comment` column in the original YouTube labelling file used a lighter pipeline (no stopword removal, no stemming). The preprocessing script re-cleaned from raw `comment` text using the full pipeline to match the Interim Report commitment (C2). The lighter `cleaned_comment` column was not used.

**Outputs**:

| File | Rows | Description |
|---|---|---|
| 02_processed_data/youtube_labelled_processed.csv | 300 | Labelled YouTube, cleaned |
| 02_processed_data/reddit_labelled_processed.csv | 297 | Labelled Reddit, cleaned |
| 02_processed_data/combined_labelled_processed.csv | 597 | Combined training set |
| 02_processed_data/youtube_full_processed.csv | 1,035 | Full YouTube corpus |
| 02_processed_data/reddit_full_processed.csv | 15,917 | Full Reddit corpus |
| 04_weka_files/training_data.arff | 597 | WEKA training ARFF |
| 04_weka_files/youtube_full.arff | 1,035 | WEKA YouTube full ARFF |
| 04_weka_files/reddit_full.arff | 15,917 | WEKA Reddit full ARFF |

**Note on ARFF**: Class attribute named `@@class@@` (not `class`) to avoid WEKA reserved-word conflict with FilteredClassifier. Text attribute uses double-quote wrapping.

---

## 6. Classification

### 6.1 WEKA Experiments (Reported in Results)

**Tool**: WEKA Explorer 3.8  
**Training data**: `04_weka_files/training_data.arff` (597 instances)  
**Filter**: StringToWordVector (IDFTransform=True, TFTransform=True, wordsToKeep=1000, outputWordCounts=True, lowerCaseTokens=True, NullStemmer, Null stopwords handler)  
**Evaluation**: 10-fold stratified cross-validation  

**Algorithm 1 — Naïve Bayes (NaiveBayes)**:

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Negative | 0.059 | 0.043 | 0.050 |
| Neutral | 0.719 | 0.452 | 0.555 |
| Positive | 0.497 | 0.767 | 0.603 |
| Weighted avg | 0.604 | 0.563 | 0.555 |

Overall accuracy: **56.28%**  
Kappa: 0.209  
Model saved: `05_models/naive_bayes.model`  
Results saved: `05_models/naive_bayes_results.txt`

**Algorithm 2 — SVM (SMO, polynomial kernel)**:

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Negative | 0.167 | 0.043 | 0.069 |
| Neutral | 0.675 | 0.778 | 0.723 |
| Positive | 0.631 | 0.542 | 0.583 |
| Weighted avg | 0.638 | 0.655 | 0.642 |

Overall accuracy: **65.49%**  
Kappa: 0.310  
Model saved: `05_models/smo_svm.model`  
Results saved: `05_models/svm_results.txt`

**Best model: SVM (SMO)** — higher accuracy, higher weighted F1, better performance across all three classes.

---

### 6.2 Full Corpus Classification (Python scikit-learn)

**Reason for switching from WEKA GUI to Python**: WEKA GUI's "Visualize classifier errors → Save" function produced empty output files. Python scikit-learn LinearSVC was used to replicate and extend the WEKA SVM for full corpus prediction.

**Tableau dashboard published URL**: https://public.tableau.com/views/KPop_Sentiment_Analysis_Dashboard/K-popSentimentDashboard

---

**Script**: `10_scripts/preprocess.py` (classification section)  
**Algorithm**: LinearSVC (C=1.0, max_iter=2000, class_weight='balanced')  
**Feature extraction**: TfidfVectorizer (max_features=1000, sublinear_tf=True, use_idf=True)  
**Cross-validation accuracy**: **68.52%** (±6.83%) — slightly higher than WEKA due to class_weight='balanced'

**Training**: Full 597-instance combined labelled set  
**Prediction applied to**:
- `01_raw_data/youtube/youtube_comments_for_labelling.csv` → 1,035 comments
- `01_raw_data/reddit/cleaned/` (all six cleaned files) → 15,917 comments

**Prediction outputs**:
- `05_models/youtube_predictions.arff`
- `05_models/reddit_predictions.arff`

Note: predictions were saved in ARFF format (not CSV) as a direct export from the WEKA Visualize classifier errors window. The downstream sentiment score aggregation and correlation analysis were computed directly in Python from the classifier predictions, not from these files.

**Sentiment score per comeback** (sentiment_score = (positive - negative) / total):

| Comeback | YT sentiment score | Reddit sentiment score |
|---|---|---|
| aespa_Whiplash | 0.349 | 0.306 |
| IVE_RebelHeart | 0.431 | 0.383 |
| TWICE_Strategy | 0.344 | 0.424 |
| NCTDREAM_WhenImWithYou | 0.419 | 0.154 |
| ATEEZ_IceOnMyTeeth | 0.445 | 0.318 |
| StrayKids_ChkChkBoom | 0.464 | 0.297 |

---

## 7. Correlation Analysis

**Script**: Inline Python (scipy.stats)  
**Metrics correlated**: yt_sentiment_score and rd_sentiment_score vs view_count, like_count, comment_count, like_to_view_ratio  
**Methods**: Pearson r and Spearman ρ, both with p-values  
**Output**: `06_correlation_analysis/correlation_results.csv`

**Full results**:

| Sentiment | Performance | Pearson r | p | Spearman ρ | p |
|---|---|---|---|---|---|
| YT sentiment | view_count | -0.404 | 0.427 | -0.086 | 0.872 |
| YT sentiment | like_count | -0.046 | 0.931 | 0.143 | 0.787 |
| YT sentiment | comment_count | 0.193 | 0.714 | 0.086 | 0.872 |
| YT sentiment | like_to_view_ratio | 0.273 | 0.601 | 0.143 | 0.787 |
| Reddit sentiment | view_count | 0.301 | 0.562 | 0.086 | 0.872 |
| Reddit sentiment | like_count | 0.208 | 0.693 | 0.029 | 0.957 |
| Reddit sentiment | comment_count | 0.186 | 0.724 | 0.200 | 0.704 |
| Reddit sentiment | like_to_view_ratio | **-0.795** | **0.059** | -0.429 | 0.397 |

**Key finding**: Reddit sentiment score vs like-to-view ratio shows the strongest correlation (Pearson r = -0.795, p = 0.059). This is borderline significant at the p < 0.1 level. All other correlations are non-significant.

**Critical limitation**: n = 6 comebacks. With only 6 data points, statistical power is very low. Approximately 15–20 data points would be needed for correlations to reach p < 0.05 reliably. All findings must be interpreted with extreme caution. This is the most important limitation of the study.

---

## 8. Key Methodological Decisions and Rationale

| Decision | What was chosen | Why | Alternative rejected |
|---|---|---|---|
| Twitter vs Reddit | Reddit (Pushshift) | Twitter API access not granted | Twitter API (blocked) |
| API vs archive dumps | Pushshift archive dumps | Reddit API access not granted in time | Reddit API via PRAW |
| Sentiment source | YouTube comments + Reddit comments | Dual-source per C6 objective | Reddit-only, YouTube-only |
| Labelling sample | 50 per comeback per source | Realistic given deadline | 100 per comeback (too slow) |
| Sampling method (YouTube) | Sequential top-50 | Already labelled before random sampling was set up | Random stratified (methodologically stronger) |
| Sampling method (Reddit) | Random stratified (seed=42) | Best practice for representative training set | Sequential |
| Class imbalance handling | class_weight='balanced' in LinearSVC | Prevents classifier from ignoring minority class | SMOTE oversampling |
| Classification tool (training metrics) | WEKA (Naïve Bayes + SMO) | Required by C4/C5 objectives | scikit-learn only |
| Classification tool (prediction) | scikit-learn LinearSVC | WEKA GUI prediction export failed (empty files) | WEKA FilteredClassifier |
| Advanced objectives | All three dropped | Insufficient time given deadline constraints | Pursued (A1, A2, A3) |

---

## 9. File Index

```
kpop-sentiment-analysis/
├── 01_raw_data/
│   ├── youtube/
│   │   ├── youtube_comments_raw.csv         (3,283 rows — all languages)
│   │   └── youtube_comments_en.csv          (2,619 rows — English only)
│   └── reddit/
│       ├── [comeback]_reddit_raw.csv        (6 files — raw from Pushshift)
│       ├── cleaned/
│       │   └── [comeback]_reddit_cleaned.csv (6 files — keyword filtered)
│       └── cleaned_en/
│           └── [comeback]_reddit_en.csv     (6 files — English only)
├── 02_processed_data/
│   ├── youtube_labelled_processed.csv       (300 rows)
│   ├── reddit_labelled_processed.csv        (297 rows)
│   ├── combined_labelled_processed.csv      (597 rows — WEKA training set)
│   ├── youtube_full_processed.csv           (1,035 rows)
│   └── reddit_full_processed.csv           (15,917 rows)
├── 03_labeled_data/
│   ├── labelling_codebook.md
│   ├── youtube_comments_for_labelling.csv   (labelled, 300 rows used)
│   └── reddit_labelling_template.csv        (labelled, 297 rows)
├── 04_weka_files/
│   ├── training_clean.arff                  (597 instances)
│   ├── youtube_full_clean.arff             (1,035 instances)
│   └── reddit_full_clean.arff              (15,917 instances)
├── 05_models/
│   ├── naive_bayes.model
│   ├── naive_bayes_results.txt
│   ├── smo_svm.model
│   ├── svm_results.txt
│   ├── filtered_svm.model
│   ├── youtube_predictions.arff
│   └── reddit_predictions.arff
├── 06_correlation_analysis/
│   ├── correlation_results.csv
│   └── combined_analysis.csv
├── 07_tableau/
│   ├── youtube_metrics_snapshot.csv
│   ├── tableau_master.csv
│   └── tableau_sentiment_long.csv
├── 09_reports/screenshots/
│   ├── weka_01 through weka_14 (WEKA process screenshots)
└── 10_scripts/
    ├── reddit_collection.py
    ├── reddit_filter.py
    ├── language_filter.py
    ├── sample_for_labelling.py
    ├── preprocess.py
    └── collect_youtube_metrics.py
```

---

## 10. Tools and Versions

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.13.9 (Anaconda) | All scripting |
| pandas | latest | Data manipulation |
| scikit-learn | latest | TF-IDF, LinearSVC, cross-validation |
| nltk | latest | Stopwords, PorterStemmer |
| langdetect | 1.0.9 | Language detection |
| scipy | latest | Pearson/Spearman correlation |
| WEKA | 3.8 | Naïve Bayes and SMO classification (training metrics) |
| Tableau Public | latest | Dashboard visualisation |
| Git | latest | Version control |
| Jupyter Notebook | latest | Original collection and preprocessing |
| Zotero | latest | Reference management |

---

## 11. Limitations Summary (for Discussion chapter)

1. **Sample size (n=6)**: Too small for statistically significant correlation. All correlation findings are indicative only.
2. **Class imbalance**: Negative class severely underrepresented (3.9% of training data). Negative F1 scores are poor (0.069 SVM). Reflects genuine skew of fan discourse, not labelling error.
3. **Sequential YouTube sampling**: Top-50 per comeback rather than random sample. May introduce ordering bias if comments are sorted by recency or likes.
4. **Single annotator**: No inter-annotator agreement statistics available. Labelling consistency relies on adherence to codebook.
5. **Reddit corpus scope**: Comments reference the group during the comeback window, not exclusively the comeback itself. General fan discourse is included.
6. **Language filter imperfection**: Romanised Korean and some Latin-script non-English content passes the filter.
7. **Cumulative YouTube metrics**: View/like/comment counts were collected in March 2026, reflecting cumulative totals since release, not window-specific engagement.
8. **Domain mismatch**: Classifier trained on YouTube and Reddit combined. Linguistic conventions differ between platforms.
9. **English-only**: Korean, Japanese, Indonesian, Spanish fan discourse excluded. Significant portion of global K-pop fandom not represented.
10. **Twitter excluded**: Originally proposed, blocked by API access constraints.
