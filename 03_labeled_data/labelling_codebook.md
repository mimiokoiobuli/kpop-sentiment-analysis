# Labelling Codebook

**Project**: K-pop Comeback Sentiment Analysis
**Author**: Miracle Okoi-Obuli
**Date**: April 2026
**Scope**: Manual sentiment labelling of YouTube and Reddit comments for six K-pop comebacks.

\---

## 1\. Purpose

This codebook defines the rules used to assign sentiment labels to comments sampled from YouTube and Reddit during the manual labelling phase of the project. Its purpose is to make the labelling process transparent, consistent, and reproducible. The labelled dataset is used to train the sentiment classifier in WEKA (Naïve Bayes and Support Vector Machine), which is subsequently applied to the full preprocessed corpus.

\---

## 2\. Label Classes

Each comment is assigned exactly one of three labels.

### 2.1 Positive

A comment is labelled **positive** if it expresses approval, enthusiasm, affection, admiration, excitement, or praise directed at the group, its members, the song, the music video, the performance, the concept, the choreography, the visuals, or any aspect of the comeback.

Indicators include:

* Explicit expressions of love, enjoyment, or excitement ("this is amazing", "obsessed with this song", "they ate").
* Complimentary observations about members or performance ("Wonyoung's vocals are incredible").
* Supportive rallying messages ("let's stream this for them", "they deserve a win").
* Enthusiastic emoji use where the accompanying text is positive or neutral (🔥 💖 😍 ❤️ 🥹 👑).
* Fan-coded positivity such as "mother", "slayed", "ate and left no crumbs", "PAK incoming", or group-specific hype phrases.

### 2.2 Negative

A comment is labelled **negative** if it expresses disapproval, disappointment, criticism, dislike, frustration, or hostility directed at the group, its members, the song, the music video, the performance, the concept, the label, or any aspect of the comeback.

Indicators include:

* Explicit statements of disappointment or dislike ("this is boring", "worst title track", "I expected more").
* Criticism of production, concept, choreography, vocals, or visuals.
* Unfavourable comparisons to previous releases or other groups, where the comparison is made as criticism.
* Expressions of frustration with the group's label, management, or promotion strategy when directed at this comeback.
* Sarcasm or backhanded remarks whose clear intent is critical, even when surface wording sounds positive.

### 2.3 Neutral

A comment is labelled **neutral** if it does not express a clear positive or negative sentiment toward the comeback. This includes factual, informational, observational, or ambiguous comments.

Indicators include:

* Factual statements or announcements ("MV drops at 6pm KST", "released on 13 January").
* Questions without evaluative content ("what time is the comeback showcase?", "is this a pre-release?").
* Observations about unrelated topics, streaming strategy, or industry context that do not themselves evaluate the comeback.
* Short comments with no clear evaluative content ("first", "here", "hi").
* Comments whose sentiment cannot be determined with reasonable confidence.

\---

## 3\. Decision Rules for Edge Cases

The following rules apply when a comment is not clearly one label.

**Mixed sentiment.** If a comment contains both positive and negative signals, label based on the dominant sentiment. Count the number and strength of positive vs. negative signals. If the comment is genuinely balanced and neither side clearly dominates, label as neutral.

**Sarcasm.** Label based on perceived intent, not surface wording. A comment such as "wow, so original" used sarcastically to mock a repetitive concept is negative, not positive. Rely on context, punctuation (exaggerated capitalisation, excessive punctuation), and adjacent phrases to identify sarcasm.

**Praise for one member, criticism of another.** If a comment praises one member while criticising another in the same group, and the comment is about this comeback, label based on the dominant sentiment toward the comeback as a whole. If the comment is neutral toward the comeback itself but evaluative only about individual members, lean neutral.

**Comments about streaming or charts.** Rally messages ("stream for them!", "let's get them to number one") are positive. Neutral observations about chart performance ("they're at number 5 on Melon right now") are neutral. Criticism of chart performance or fan behaviour ("flop era", "nobody is streaming") is negative.

**Emoji-only comments.** Label based on the clear valence of the emoji set. 🔥🔥🔥 or 💖 alone is positive. 💀 used ironically is typically negative. 😐 or ❓ alone is neutral. If uncertain, neutral.

**Non-comeback content.** If a sampled comment discusses something unrelated to the comeback (e.g., a tangential reply about another group's scandal), label based on the sentiment of that content if clearly evaluative, or neutral if not. Do not discard; the sample is fixed.

**Short or ambiguous comments.** If a comment is too short or too ambiguous to confidently determine sentiment, label as neutral. Do not default to positive simply because K-pop fan discourse is often positive.

**Multilingual residue.** If a comment passed the English filter but contains a significant non-English portion that changes meaning, label only on the basis of the English portion. If the English portion alone does not carry clear sentiment, label as neutral.

\---

## 4\. Process

1. Open the sample file (`reddit\_labelling\_template.csv` or `youtube\_labelling\_template.csv`) in Excel or an equivalent spreadsheet tool.
2. Label each row by entering `positive`, `negative`, or `neutral` in the `label` column (exact lowercase values, consistent across all 600 rows).
3. Save the labelled file at regular intervals to avoid data loss.
4. Work in focused batches of 50 comments at a time. Labelling judgement deteriorates after roughly 30 minutes of continuous work; short breaks preserve consistency.
5. When a decision is genuinely difficult, pause, re-read the codebook, and make a best judgement. Do not skip rows.

\---

## 5\. Quality and Limitations

This labelling was conducted by a single annotator (the project author), which is a known limitation of small-scale undergraduate projects. Inter-annotator agreement statistics such as Cohen's kappa cannot therefore be reported. To reduce within-annotator drift, all labels were assigned within a single week following this codebook, and the codebook was not revised after labelling commenced.

The three-class scheme (positive, negative, neutral) was chosen to align with WEKA's supported classification tasks and with the Interim Progress Report commitment. Finer-grained schemes (e.g. five-point Likert or emotion-specific categories) were rejected as impractical for the project scale and timeline.

Sentiment labelling of fan-generated content is inherently subjective and fandom-literate judgement is required to interpret slang, sarcasm, and in-group references correctly. The author is familiar with K-pop fan culture, which supports accurate interpretation of such content but also introduces a known fan-perspective bias that is acknowledged in the Discussion chapter of the Final Report.

