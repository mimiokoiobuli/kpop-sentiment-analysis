# K-pop Sentiment Analysis — Project Log

**Student**: Miracle Okoi-Obuli  
**Module**: BSc Computer Science Project  
**Supervisor**: Lili Kirner

\---

## 8 March 2026

Submitted the Interim Progress Report on Canvas before the 23:30 deadline. All ten sections completed and word count within limits. Feeling relieved. Going to rest before starting the practical phase.

\---

## 13 March 2026

Tried to move forward with data collection today but hit a wall immediately. The Twitter API Basic tier only allows access to tweets from the last 7 days — my project needs 2024–2025 historical data, so that's completely unusable. On top of that, my Reddit API application came back rejected today for non-compliance with the Responsible Builder Policy. Both original data sources are now blocked on the same day.

Spent several hours researching alternatives. The best path forward seems to be: replace Twitter with YouTube comments (free, official API, directly tied to the comeback videos already in the study) and use the Pushshift Reddit archive dumps for historical Reddit data. Pushshift is widely used in academic research so it should be academically defensible.

Emailed Lili to explain the problem and propose the change. Waiting for her response before officially amending anything.

While waiting, set up the YouTube Data API. Created a Google Cloud project called kpop-sentiment-research, enabled YouTube Data API v3, and generated an API key. Stored the key in credentials/api\_keys.txt, which is excluded from GitHub via .gitignore.

Also finalised the six comebacks for data collection:

* aespa: Whiplash — 21 October 2024
* IVE: Rebel Heart — 3 February 2025 (IVE Empathy EP)
* TWICE: Strategy — 6 December 2024
* NCT DREAM: When I'm With You — 11 November 2024
* SEVENTEEN: Thunder — 14 October 2024
* Stray Kids: Chk Chk Boom — 19 July 2024

Chose these based on commercial profile and spread across different months to minimise the number of Reddit archive files needed.

Wrote and ran two scripts in Jupyter Notebook today:

**Script 1 — YouTube Engagement Metrics Collector**  
Collected current view count, like count, and comment count for all six MVs. Saved to 07\_tableau/youtube\_metrics\_snapshot.csv. Notable findings: aespa Whiplash at 271M views, Stray Kids Chk Chk Boom with the highest comment count at 391K, NCT DREAM When I'm With You noticeably lower at only 15M views. Could not collect window-specific snapshots since these are historical comebacks, so using current totals as the performance measure. Will justify this in the methodology chapter.

**Script 2 — YouTube Comments Collector**  
Collected 500 comments per video, 3,000 total. Saved to 01\_raw\_data/youtube/youtube\_comments\_raw.csv. Many comments are in Korean and other languages, as expected for K-pop fanbases. Will filter for English-only during preprocessing.

\---

## 13 March 2026 (Evening)

Security incident. Received an automated alert from GitGuardian shortly after pushing to GitHub — a Google API key had been exposed in the repository.

What happened: Jupyter automatically saves checkpoint files as you work. An earlier draft of the YouTube collector notebook had the API key hardcoded in the code before I switched to reading from a credentials file. That checkpoint file got committed before .ipynb\_checkpoints was added to .gitignore.

Steps taken: revoked the compromised key immediately on Google Cloud Console, created a new restricted key (YouTube Data API v3 only), updated credentials/api\_keys.txt, used git filter-branch to remove the checkpoint file from the entire git history, force pushed the cleaned history, and ran git gc locally.

Lesson: never hardcode API keys in notebook cells even temporarily, and .ipynb\_checkpoints must be in .gitignore before any notebook work begins.

\---

## 16 March 2026

Ran the YouTube comments preprocessing notebook. Results: 3,000 raw comments down to 1,036 after English language filtering (34.5%), then 1,026 after text cleaning. Preprocessing pipeline: langdetect language filter, lowercasing, URL/mention/hashtag removal, special character and number removal, tokenisation, stopword removal, Porter stemming. Saved processed file to 02\_processed\_data/ and labelling template to 03\_labeled\_data/.

Also started downloading the monthly Reddit Pushshift archive dumps via qBittorrent. Five files needed covering July 2024, October 2024, November 2024, December 2024, and February 2025. Reddit filter script written and ready to run once downloads complete.

\---

## 19 March 2026

Identified a methodological problem with the YouTube comments. The original script retrieved comments sorted by relevance, which meant most returned comments were from 2026 rather than the actual comeback window. For example, the aespa Whiplash comments went back no further than February 2026, even though the comeback was October 2024.

Fixed the collector to sort by date and filter strictly to the 14-day window around each release date. Will re-run collection to replace the raw comments CSV.

All five Pushshift monthly archive files now downloaded and ready.

\---

## 20 March 2026

Two major methodology updates today, both logged carefully.

**SEVENTEEN replaced with ATEEZ**  
Discovered that SEVENTEEN Thunder was released in May 2025, not October 2024 as I had assumed. The date window was completely wrong and no comments were collected. Replaced with ATEEZ Ice On My Teeth (Golden Hour Part 2), released 15 November 2024. The November 2024 Pushshift dump is already downloaded so no additional files needed.

Updated final comeback list:

* aespa: Whiplash — 21 October 2024
* IVE: Rebel Heart — 13 January 2025 (corrected from February — see note below)
* TWICE: Strategy — 6 December 2024
* NCT DREAM: When I'm With You — 11 November 2024
* ATEEZ: Ice On My Teeth — 15 November 2024
* Stray Kids: Chk Chk Boom — 19 July 2024

**Scripts rebuilt from scratch**  
The original notebooks had accumulated conflicting cells from iterative fixes. Deleted and rebuilt all three notebooks cleanly: 01\_youtube\_collector.ipynb, 02\_youtube\_preprocessing.ipynb, 03\_reddit\_filter.ipynb. Re-collected YouTube metrics and comments with the corrected methodology. Running overnight.

Writing this at 3:36am.

\---

## 21 April 2026

Returned to the project after a gap and picked up all remaining practical work. Long session.

**Reddit collection script reconstruction**  
The original Reddit collection script had been lost from local storage and was never committed to git. Reconstructed it by reverse-engineering the methodology from the existing raw CSV files — examining the schema, subreddit distribution, date windows, and keyword filter behaviour. The script uses the Pushshift RC\_\*.zst monthly archive dumps, searches nine subreddits (r/kpop, r/kpopthoughts, r/unpopularkpopopinions, plus all six group-specific subs), and applies a 14-day window from each comeback's release date.

**IVE release date correction**  
Identified that the IVE data had been collected around the wrong event. The February 2025 window captured discussion of the full IVE EMPATHY mini-album, but the YouTube metrics are for the Rebel Heart MV which was released as a pre-release single on 13 January 2025. Re-collected IVE from the RC\_2025-01.zst dump with the corrected window. New IVE file: 7,450 rows covering 13–26 January 2025.

**Keyword filter refinement**  
Audited the original substring keyword filter and found substantial false positives: IVE matched "I've", "alive", "give" etc. (76% noise in non-own-sub comments), TWICE matched the adverb "twice" (21% noise), NCT DREAM's song title "When I'm With You" matched the common English phrase (20% noise). Wrote reddit\_filter.py applying word-boundary-aware matching with case-sensitive tokens for IVE and TWICE. Filter applied symmetrically to all six comebacks. Results: IVE 76.3% drop, TWICE 20.7%, NCT DREAM 19.9%, aespa 1.2%, ATEEZ 1.4%, Stray Kids 0.3%. The near-zero drops for distinctive group names confirmed the refinement was targeting noise rather than genuine content.

**Language filter**  
Wrote language\_filter.py to enforce the English-only methodology committed to in the Interim Report. Two-stage approach: non-Latin script detection (Hangul, CJK, Cyrillic, Thai, Arabic, Hebrew) followed by langdetect for longer comments. Reddit drops: 0.0–0.5% per comeback (Reddit is overwhelmingly English). YouTube drops: 20.2% overall, with IVE at 60.4% due to its large Korean and Japanese fanbase.

**Methodology decisions**  
Locked final research objectives (8 core, advanced objectives dropped due to deadline constraints). Decided to use dual-source sentiment analysis (YouTube comments + Reddit comments). Set Wednesday 23 April as a checkpoint to assess whether to drop back to YouTube-only if behind schedule.

\---

## 22 April 2026

**Manual labelling**  
Completed YouTube comment labelling: 300 comments labelled (50 per comeback, sequential top-50 from the labelling file). Label distribution: positive 152, neutral 138, negative 10. Class imbalance noted — the very low negative count reflects genuine skew of K-pop fan discourse on official MV pages rather than a labelling error.

Completed Reddit comment labelling: 297 comments labelled (random stratified sample, seed=42, 50 per comeback; NCT DREAM had 47 after deduplication removed 3 duplicates). Label distribution: neutral 196, positive 88, negative 13.

Wrote labelling codebook (03\_labeled\_data/labelling\_codebook.md) documenting decision rules for positive, negative, and neutral labels including edge cases: sarcasm, mixed sentiment, fandom-coded language, administrative comments, and comments unrelated to the specific comeback.

Combined training set: 597 instances. Class distribution: neutral 55.9%, positive 40.2%, negative 3.9%.

\---

## 23 April 2026

Long technical day. Preprocessing, classification, correlation, and dashboard all completed.

**Preprocessing**  
Wrote preprocess.py applying a consistent pipeline to both YouTube and Reddit data: encoding normalisation (fixes UTF-8 mojibake from Pushshift dumps), lowercase, URL removal, non-ASCII removal, digit removal, punctuation removal, tokenisation, NLTK stopword removal, Porter stemming. Note: the existing cleaned\_comment column in the YouTube labelling file used a lighter pipeline without stopwords or stemming. Re-cleaned from raw text to match the Interim Report methodology commitment. Outputs: five processed CSVs in 02\_processed\_data/ and three ARFF files in 04\_weka\_files/. ARFF class attribute named @@class@@ rather than class to avoid a WEKA reserved-word conflict discovered during testing.

**WEKA classification**  
Trained two classifiers using 10-fold stratified cross-validation on the 597-instance combined training set:

Naïve Bayes: 56.28% accuracy, weighted F1 0.555. Negative class F1: 0.050 (very poor).
SVM (SMO): 65.49% accuracy, weighted F1 0.642. Negative class F1: 0.069 (still poor but better).

SVM selected as the best model. Both models saved to 05\_models/. Full results text saved for the appendix.

The WEKA GUI FilteredClassifier produced empty prediction files when attempting to export via Visualize classifier errors. Switched to scikit-learn LinearSVC (C=1.0, class\_weight='balanced') for full corpus prediction. Cross-validated accuracy: 68.52% (±6.83%), consistent with WEKA result. Predictions applied to full YouTube corpus (1,035 comments) and full Reddit corpus (15,917 comments).

**Correlation analysis**  
Computed Pearson and Spearman correlations between per-comeback sentiment scores (YouTube and Reddit) and YouTube engagement metrics (view count, like count, comment count, like-to-view ratio). Most correlations are weak and non-significant, which is expected given n=6. The strongest finding: Reddit sentiment score vs like-to-view ratio, Pearson r = -0.795, p = 0.059 (borderline significant at p < 0.1). This negative correlation — higher Reddit positivity associated with lower like-to-view efficiency — is counterintuitive and will be discussed in the report. Full results saved to 06\_correlation\_analysis/correlation\_results.csv.

**Tableau dashboard**  
Built five-chart interactive dashboard in Tableau Public:

1. YouTube Engagement Metrics by Comeback (bar chart, sorted by view count)
2. YouTube Sentiment Distribution by Comeback (stacked bar, red/grey/green)
3. Reddit Sentiment Distribution by Comeback (stacked bar, red/grey/green)
4. YouTube Sentiment Score vs View Count (scatter, coloured by group type)
5. Reddit Sentiment Score vs Like-to-View Ratio (scatter, r = -0.795 in title)

Published to Tableau Public. URL: https://public.tableau.com/views/KPop\_Sentiment\_Analysis\_Dashboard/K-popSentimentDashboard

\---

## 24 April 2026

Wrote up and updated project documentation: methodology log, project log, labelling codebook. All scripts committed to git. Report writing begins today. Deadline: 26 April 2026.

Outstanding:

* Email to Lili Kirner confirming ethics position and requesting pre-submission check
* Final Report (8,000 words, all chapters)
* Risk register update for appendix
* Appendices compilation

\---

## AI Usage Note

Claude (Anthropic, accessed via claude.ai) was used extensively throughout the practical phase of this project, primarily from 21–24 April 2026. Usage included:

* **Debugging and troubleshooting**: diagnosing issues in Python scripts, identifying the WEKA ARFF class attribute conflict, resolving the WEKA FilteredClassifier empty output issue, diagnosing UTF-8 encoding problems in Pushshift data.
* **Script development**: the Reddit keyword filter (reddit\_filter.py), the language filter (language\_filter.py), the preprocessing pipeline (preprocess.py), the sampling script (sample\_for\_labelling.py), and the YouTube metrics collector (collect\_youtube\_metrics.py) were all developed with Claude's assistance. All scripts were reviewed, tested, and approved by the project author before use.
* **Methodological review**: Claude identified that the IVE comeback window had been collected around the wrong release date, that the initial keyword filter produced significant false positives for IVE and TWICE, and raised the domain mismatch concern for classifier training across two platforms.
* **Labelling guidance**: Claude provided labelling decisions for edge cases during the Reddit manual labelling process, cross-referencing the labelling codebook.
* **Report structure and documentation**: Claude assisted with structuring the Final Report chapters, drafting SMART objectives, and writing the methodology log and project log entries. All final report text will be authored by the project author.
* **Tableau guidance**: step-by-step guidance for building the five-chart dashboard.

All AI interactions are reflected in the project log. The project author takes full responsibility for all methodological decisions, data, and written work. Use of AI tools is declared in the Introduction chapter of the Final Report in accordance with the University of Hertfordshire AI policy.

