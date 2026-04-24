"""
collect_youtube_metrics.py
--------------------------
Collects video-level engagement metrics for the six comeback MVs
using the YouTube Data API v3.

Saves to: 01_raw_data/youtube/youtube_metrics.csv
"""

import requests
import pandas as pd
from pathlib import Path

# Your YouTube Data API v3 key
# Replace with your actual key from credentials folder
API_KEY = "YOUR_YOUTUBE_API_KEY_HERE"

# Video IDs identified from the comments corpus
VIDEOS = {
    "aespa_Whiplash":           "jWQx2f-CErU",
    "ATEEZ_IceOnMyTeeth":       "5OflOlcHLb8",
    "NCTDREAM_WhenImWithYou":   "B1qq8IvzSz4",
    "StrayKids_ChkChkBoom":     "0P0aQreFs8w",
    "TWICE_Strategy":           "Sz_wWzgh-vQ",
    "IVE_RebelHeart":           "g36q0ZLvygQ",
}

OUTPUT = Path(r"C:\Users\lenovo\kpop-sentiment-analysis\01_raw_data\youtube\youtube_metrics.csv")


def get_video_metrics(video_id: str, api_key: str) -> dict:
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics,snippet",
        "id": video_id,
        "key": api_key,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if not data.get("items"):
        print(f"  WARNING: No data returned for {video_id}")
        return {}

    item = data["items"][0]
    stats = item["statistics"]

    return {
        "video_id":      video_id,
        "view_count":    int(stats.get("viewCount", 0)),
        "like_count":    int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
        "title":         item["snippet"]["title"],
        "published_at":  item["snippet"]["publishedAt"],
    }


def main():
    rows = []
    for comeback, video_id in VIDEOS.items():
        print(f"Fetching metrics for {comeback} ({video_id}) ...")
        metrics = get_video_metrics(video_id, API_KEY)
        if metrics:
            metrics["comeback"] = comeback
            # Compute like-to-view ratio
            if metrics["view_count"] > 0:
                metrics["like_to_view_ratio"] = metrics["like_count"] / metrics["view_count"]
            else:
                metrics["like_to_view_ratio"] = 0.0
            rows.append(metrics)
            print(f"  Views: {metrics['view_count']:,}  Likes: {metrics['like_count']:,}  Comments: {metrics['comment_count']:,}")

    df = pd.DataFrame(rows)
    cols = ["comeback", "video_id", "title", "published_at",
            "view_count", "like_count", "comment_count", "like_to_view_ratio"]
    df = df[cols]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"\nSaved to {OUTPUT}")
    print(df[["comeback", "view_count", "like_count", "comment_count", "like_to_view_ratio"]].to_string(index=False))


if __name__ == "__main__":
    main()
