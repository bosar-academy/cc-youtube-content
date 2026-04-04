#!/usr/bin/env python3
"""
YouTube Analytics Data Fetcher
Pulls channel and video analytics data, outputs structured JSON for dashboard generation.

Usage:
    # Fetch own channel analytics
    python youtube_analytics.py channel --days 30 --output analytics.json

    # Fetch competitor channel data
    python youtube_analytics.py competitor --channel-id UCxxxxxx --output competitor.json

    # Fetch video-level stats for own channel
    python youtube_analytics.py videos --max-videos 50 --output videos.json

Requires:
    YOUTUBE_API_KEY environment variable
    pip install google-api-python-client
    For Analytics API: google-auth-oauthlib (OAuth flow)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_youtube_client():
    """Get YouTube Data API v3 client."""
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    return build("youtube", "v3", developerKey=api_key)


def get_own_channel_id(youtube):
    """Get the authenticated user's channel ID.
    Note: This requires OAuth, not just API key. Falls back to env var."""
    channel_id = os.environ.get("YOUTUBE_CHANNEL_ID")
    if channel_id:
        return channel_id
    print("ERROR: Set YOUTUBE_CHANNEL_ID environment variable (e.g., UCxxxxxxxx).",
          file=sys.stderr)
    print("Find yours at: https://www.youtube.com/account_advanced", file=sys.stderr)
    sys.exit(1)


def fetch_channel_stats(youtube, channel_id):
    """Fetch channel-level statistics."""
    response = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=channel_id,
    ).execute()

    if not response.get("items"):
        print(f"ERROR: Channel {channel_id} not found.", file=sys.stderr)
        sys.exit(1)

    item = response["items"][0]
    stats = item.get("statistics", {})
    snippet = item.get("snippet", {})

    return {
        "channel_id": channel_id,
        "title": snippet.get("title", ""),
        "description": snippet.get("description", "")[:300],
        "subscriber_count": int(stats.get("subscriberCount", 0)),
        "total_views": int(stats.get("viewCount", 0)),
        "total_videos": int(stats.get("videoCount", 0)),
        "created_at": snippet.get("publishedAt", ""),
        "uploads_playlist": item.get("contentDetails", {}).get(
            "relatedPlaylists", {}).get("uploads", ""),
    }


def fetch_channel_videos(youtube, channel_id, max_videos=50):
    """Fetch recent videos from a channel with full stats."""
    # First get uploads playlist
    channel = fetch_channel_stats(youtube, channel_id)
    uploads_id = channel.get("uploads_playlist", "")

    if not uploads_id:
        print("ERROR: Could not find uploads playlist.", file=sys.stderr)
        return []

    # Get video IDs from uploads playlist
    video_ids = []
    next_page = None

    while len(video_ids) < max_videos:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_id,
            maxResults=min(50, max_videos - len(video_ids)),
            pageToken=next_page,
        ).execute()

        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page = response.get("nextPageToken")
        if not next_page:
            break

    # Get full video details
    videos = []
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
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "duration": item.get("contentDetails", {}).get("duration", ""),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "tags": snippet.get("tags", [])[:10],
            })

    # Sort by publish date (newest first)
    videos.sort(key=lambda x: x["published_at"], reverse=True)
    return videos


def fetch_competitor_data(youtube, channel_id):
    """Fetch public data for a competitor channel."""
    channel = fetch_channel_stats(youtube, channel_id)
    videos = fetch_channel_videos(youtube, channel_id, max_videos=30)

    # Calculate derived metrics
    if videos:
        avg_views = sum(v["view_count"] for v in videos) // len(videos)
        avg_likes = sum(v["like_count"] for v in videos) // len(videos)
        max_views = max(v["view_count"] for v in videos)
        min_views = min(v["view_count"] for v in videos)

        # Upload frequency (days between videos)
        dates = sorted([v["published_at"] for v in videos])
        if len(dates) > 1:
            first = datetime.fromisoformat(dates[0].replace("Z", "+00:00"))
            last = datetime.fromisoformat(dates[-1].replace("Z", "+00:00"))
            days_span = max((last - first).days, 1)
            upload_frequency = round(days_span / len(dates), 1)
        else:
            upload_frequency = None

        # Engagement ratio
        engagement_ratio = round(avg_likes / max(avg_views, 1) * 100, 2)
    else:
        avg_views = avg_likes = max_views = min_views = 0
        upload_frequency = None
        engagement_ratio = 0

    return {
        "channel": channel,
        "videos": videos,
        "metrics": {
            "avg_views": avg_views,
            "avg_likes": avg_likes,
            "max_views": max_views,
            "min_views": min_views,
            "upload_frequency_days": upload_frequency,
            "engagement_ratio_pct": engagement_ratio,
        },
    }


def analyze_posting_times(videos):
    """Analyze what days/hours videos were posted."""
    hour_counts = {}
    day_counts = {}

    for video in videos:
        try:
            dt = datetime.fromisoformat(video["published_at"].replace("Z", "+00:00"))
            hour = dt.hour
            day = dt.strftime("%A")

            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            day_counts[day] = day_counts.get(day, 0) + 1
        except (ValueError, KeyError):
            continue

    # Find best hour and day
    best_hour = max(hour_counts, key=hour_counts.get) if hour_counts else None
    best_day = max(day_counts, key=day_counts.get) if day_counts else None

    return {
        "hour_distribution": dict(sorted(hour_counts.items())),
        "day_distribution": day_counts,
        "best_hour_utc": best_hour,
        "best_day": best_day,
    }


def main():
    parser = argparse.ArgumentParser(description="YouTube analytics data fetcher")
    subparsers = parser.add_subparsers(dest="command")

    # Channel command
    ch = subparsers.add_parser("channel", help="Fetch own channel data")
    ch.add_argument("--days", type=int, default=30, help="Number of days to analyze")
    ch.add_argument("--max-videos", type=int, default=50, help="Max videos to fetch")
    ch.add_argument("--output", required=True, help="Output JSON path")

    # Competitor command
    comp = subparsers.add_parser("competitor", help="Fetch competitor data")
    comp.add_argument("--channel-id", required=True, help="Competitor channel ID")
    comp.add_argument("--output", required=True, help="Output JSON path")

    # Videos command
    vids = subparsers.add_parser("videos", help="Fetch video-level data")
    vids.add_argument("--max-videos", type=int, default=50, help="Max videos")
    vids.add_argument("--output", required=True, help="Output JSON path")

    args = parser.parse_args()
    youtube = get_youtube_client()

    if args.command == "channel":
        channel_id = get_own_channel_id(youtube)
        print(f"Fetching channel data for: {channel_id}", file=sys.stderr)

        channel = fetch_channel_stats(youtube, channel_id)
        videos = fetch_channel_videos(youtube, channel_id, args.max_videos)

        # Filter to date range
        cutoff = datetime.now() - timedelta(days=args.days)
        recent_videos = [
            v for v in videos
            if datetime.fromisoformat(v["published_at"].replace("Z", "+00:00")).replace(tzinfo=None) > cutoff
        ]

        posting_times = analyze_posting_times(videos)

        output = {
            "timestamp": datetime.now().isoformat(),
            "date_range_days": args.days,
            "channel": channel,
            "all_videos": videos,
            "recent_videos": recent_videos,
            "posting_analysis": posting_times,
            "summary": {
                "total_videos_in_range": len(recent_videos),
                "total_views_in_range": sum(v["view_count"] for v in recent_videos),
                "avg_views_per_video": (sum(v["view_count"] for v in recent_videos) // max(len(recent_videos), 1)),
                "best_video": max(recent_videos, key=lambda v: v["view_count"])["title"] if recent_videos else None,
                "worst_video": min(recent_videos, key=lambda v: v["view_count"])["title"] if recent_videos else None,
            },
        }

    elif args.command == "competitor":
        print(f"Fetching competitor data for: {args.channel_id}", file=sys.stderr)
        output = fetch_competitor_data(youtube, args.channel_id)

    elif args.command == "videos":
        channel_id = get_own_channel_id(youtube)
        videos = fetch_channel_videos(youtube, channel_id, args.max_videos)
        output = {
            "timestamp": datetime.now().isoformat(),
            "videos": videos,
            "count": len(videos),
        }

    else:
        parser.print_help()
        return

    # Save output
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Saved to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
