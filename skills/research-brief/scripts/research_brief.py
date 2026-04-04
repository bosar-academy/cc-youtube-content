#!/usr/bin/env python3
"""
YouTube Competitor Research Script
Searches YouTube for top videos on a topic, pulls video details and comments,
and outputs structured JSON for Claude to analyze.

Usage:
    python research_brief.py "topic keyword" [--max-videos 20] [--max-comments 50]

Requires:
    YOUTUBE_API_KEY environment variable
    pip install google-api-python-client
"""

import argparse
import json
import os
import sys
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_youtube_client():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    return build("youtube", "v3", developerKey=api_key)


def search_videos(youtube, query, max_results=20):
    """Search YouTube for videos on a topic, sorted by view count."""
    results = []

    # Search by relevance first
    response = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        order="relevance",
        maxResults=min(max_results, 50),
        relevanceLanguage="en",
    ).execute()

    video_ids = [item["id"]["videoId"] for item in response.get("items", [])]

    # Search by view count as well to catch viral outliers
    response_views = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        order="viewCount",
        maxResults=min(max_results, 50),
        relevanceLanguage="en",
    ).execute()

    for item in response_views.get("items", []):
        vid = item["id"]["videoId"]
        if vid not in video_ids:
            video_ids.append(vid)

    return video_ids[:max_results]


def get_video_details(youtube, video_ids):
    """Get detailed stats for a list of video IDs."""
    videos = []
    # API allows max 50 IDs per request
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(batch),
        ).execute()

        for item in response.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            videos.append({
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "channel_id": snippet.get("channelId", ""),
                "description": snippet.get("description", "")[:500],
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "tags": snippet.get("tags", [])[:10],
                "duration": item.get("contentDetails", {}).get("duration", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
            })

    # Sort by view count descending
    videos.sort(key=lambda x: x["view_count"], reverse=True)
    return videos


def get_video_comments(youtube, video_id, max_comments=50):
    """Get top comments for a video, sorted by relevance."""
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            order="relevance",
            maxResults=min(max_comments, 100),
            textFormat="plainText",
        ).execute()

        comments = []
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "text": comment.get("textDisplay", "")[:500],
                "like_count": comment.get("likeCount", 0),
                "author": comment.get("authorDisplayName", ""),
            })

        return comments
    except HttpError as e:
        if e.resp.status == 403:
            return [{"text": "[Comments disabled]", "like_count": 0, "author": ""}]
        return []


def get_channel_stats(youtube, channel_ids):
    """Get channel-level stats for competitor analysis."""
    if not channel_ids:
        return []

    response = youtube.channels().list(
        part="snippet,statistics",
        id=",".join(channel_ids[:10]),
    ).execute()

    channels = []
    for item in response.get("items", []):
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})
        channels.append({
            "channel_id": item["id"],
            "channel_title": snippet.get("title", ""),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "description": snippet.get("description", "")[:300],
        })

    return channels


def main():
    parser = argparse.ArgumentParser(description="YouTube competitor research")
    parser.add_argument("topic", help="Topic or keyword to research")
    parser.add_argument("--max-videos", type=int, default=20, help="Max videos to analyze")
    parser.add_argument("--max-comments", type=int, default=50, help="Max comments per video")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    youtube = get_youtube_client()

    print(f"Searching YouTube for: {args.topic}", file=sys.stderr)

    # Step 1: Search videos
    video_ids = search_videos(youtube, args.topic, args.max_videos)
    print(f"Found {len(video_ids)} videos", file=sys.stderr)

    # Step 2: Get video details
    videos = get_video_details(youtube, video_ids)
    print(f"Got details for {len(videos)} videos", file=sys.stderr)

    # Step 3: Get comments from top 5 videos
    top_5 = videos[:5]
    for video in top_5:
        print(f"Getting comments for: {video['title'][:60]}...", file=sys.stderr)
        video["comments"] = get_video_comments(
            youtube, video["video_id"], args.max_comments
        )

    # Step 4: Get channel stats for top 3 unique channels
    unique_channels = list(dict.fromkeys(v["channel_id"] for v in videos[:10]))[:3]
    channels = get_channel_stats(youtube, unique_channels)

    # Build output
    output = {
        "query": args.topic,
        "timestamp": datetime.now().isoformat(),
        "videos": videos,
        "top_channels": channels,
        "summary": {
            "total_videos_analyzed": len(videos),
            "total_views": sum(v["view_count"] for v in videos),
            "avg_views": sum(v["view_count"] for v in videos) // max(len(videos), 1),
            "max_views": videos[0]["view_count"] if videos else 0,
            "min_views": videos[-1]["view_count"] if videos else 0,
        },
    }

    # Output
    result = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
