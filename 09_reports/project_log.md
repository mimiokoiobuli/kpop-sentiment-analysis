# K-pop Sentiment Analysis — Project Log

---

## 8 March 2026

Submitted the Interim Progress Report on Canvas before the 23:30 deadline.
Sections completed: all 10. Word count within limits.
Will begin practical phase after some rest.

---

## 13 March 2026

### Data Source Crisis

Tried to move forward with data collection today but hit a wall immediately.
Discovered that the Twitter API Basic tier only allows access to tweets from 
the last 7 days. My project needs 2024-2025 historical data. This is a big 
problem since Twitter was my primary data source.

Reddit API application (submitted earlier) also came back rejected today.
Reason given: non-compliant with Responsible Builder Policy / lacks detail.
So both original data sources are blocked.

Spent time researching alternatives. Consulted multiple AI tools for advice.
Best recommendation: replace Twitter with YouTube comments (free, official API,
directly tied to the comeback videos) and use Reddit Pushshift archive dumps 
for historical Reddit data (widely used in academic research).

Emailed supervisor Lili to explain the problem and propose the methodology 
amendment. Waiting for her response before officially changing anything.

### Setting Up YouTube Data API

Created a Google Cloud project called kpop-sentiment-research.
Enabled YouTube Data API v3 and generated an API key.
Stored key in credentials/api_keys.txt (excluded from GitHub via .gitignore).

### Selecting Comebacks

Finalised the six comebacks for data collection:
- aespa: Whiplash — 21 October 2024
- IVE: Rebel Heart (IVE Empathy EP) — 3 February 2025  
- TWICE: Strategy — 6 December 2024
- NCT DREAM: When I'm With You (Dreamscape) — 11 November 2024
- SEVENTEEN: Thunder (Spill the Feels) — 14 October 2024
- Stray Kids: Chk Chk Boom (ATE) — 19 July 2024

These six were chosen based on album sales and spread across different months
to minimise the number of Reddit archive files needed.

### Data Collected Today

Wrote and ran two Python scripts in Jupyter Notebook:

Script 1 — YouTube Engagement Metrics Collector
Collected current view count, like count, and comment count for all 6 MVs.
Saved to: 07_tableau/youtube_metrics_snapshot.csv

Notable findings:
- aespa Whiplash: 271M views, 94K comments
- Stray Kids Chk Chk Boom: 198M views, 391K comments (highest comments)
- TWICE Strategy: 145M views, 204K comments
- NCT DREAM When I'm With You: only 15M views (noticeably lower than others)

Note: Could not collect 24hr/72hr/1 week snapshots since these are historical
comebacks. Using current totals as YouTube performance measure instead. 
Will justify this decision in the methodology chapter.

Script 2 — YouTube Comments Collector
Collected 500 comments per video = 3,000 comments total.
Saved to: 01_raw_data/youtube/youtube_comments_raw.csv

Important finding: many comments are in Korean, not English. Will need to 
filter for English-only comments during the preprocessing stage. This was 
expected given K-pop fanbases are international, but good to confirm early.

Personal note: TWICE Strategy featured Megan Thee Stallion and Stray Kids 
Chk Chk Boom was made for the Deadpool and Wolverine soundtrack. Both likely 
inflated engagement beyond what a typical comeback would generate. Worth 
mentioning in limitations.

### Pending

- Supervisor response to methodology amendment email
- Reddit Pushshift archive download (5 monthly files needed)
- YouTube comments preprocessing (filter English, clean text)

## 13 March 2026 (Evening)

### Security Incident - API Key Exposed on GitHub

Received an automated alert from GitGuardian shortly after pushing to GitHub.
A Google API key had been exposed in the repository.

What happened:
Jupyter automatically saves checkpoint files (.ipynb_checkpoints) as you work.
An earlier draft of the YouTube data collector notebook had the API key 
hardcoded directly in the code before I switched to reading it from the 
credentials file. This checkpoint file was committed to GitHub before the 
.ipynb_checkpoints folder was added to .gitignore.

Steps taken to fix it:
1. Revoked the compromised API key immediately on Google Cloud Console
2. Created a new restricted API key (restricted to YouTube Data API v3 only)
3. Updated credentials/api_keys.txt with the new key
4. Used git filter-branch to remove the checkpoint file from entire Git history
5. Force pushed cleaned history to GitHub
6. Cleaned up local repository with git gc

Lesson learned:
Never hardcode API keys directly in notebook cells even temporarily.
Always read from a credentials file from the very first line of code.
The .ipynb_checkpoints folder must be in .gitignore before any notebook work begins.