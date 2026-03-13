# K-pop Sentiment Analysis — Project Log

## 13 March 2026

### Practical Phase Begins

* Submitted Interim Progress Report on 8 March 2026
* Discovered Twitter API Basic tier restricts data access to last 7 days only — historical 2024-2025 data not accessible on free tier
* Reddit Data API application rejected — non-compliant with Responsible Builder Policy
* Researched alternative data sources after consulting Gemini and ChatGPT
* Proposed methodology amendment to supervisor via email: replace Twitter with YouTube comments, use Reddit Pushshift archives for historical Reddit data
* Selected six comebacks for data collection:

  * aespa: Whiplash (21 Oct 2024)
  * IVE: Rebel Heart/IVE Empathy (3 Feb 2025)
  * TWICE: Strategy (6 Dec 2024)
  * NCT DREAM: Dreamscape (11 Nov 2024)
  * SEVENTEEN: Spill the Feels/Thunder (14 Oct 2024)
  * Stray Kids: ATE (19 Jul 2024)

* Set up Google Cloud project (kpop-sentiment-research)
* Enabled YouTube Data API v3 and generated API key
* Created .gitignore to protect credentials folder from being pushed to GitHub
* Identified Reddit Pushshift archive files needed on Academic Torrents:

  * July 2024, October 2024, November 2024, December 2024, February 2025

### Decisions Made Today

* Switched from Twitter to YouTube comments as primary sentiment source — more academically defensible, directly tied to comeback videos, free official API
* Used Pushshift archives instead of live Reddit API — avoids need for rejected API approval
* Supervisor approval pending before beginning data collection
