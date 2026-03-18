---
name: cross-niche-outliers
description: Find high-performing YouTube videos from adjacent niches for content ideation. Use when the user asks to find content ideas, research YouTube outliers, discover viral videos, or plan content strategy.
argument-hint: [keywords] [--queries N] [--size N]
disable-model-invocation: true
---

# Cross-Niche Outlier Detection

Find high-performing videos from adjacent business niches to extract transferable content patterns, hooks, and title ideas. Monitors 45+ channels across business, productivity, science, creator economy, and finance niches.

## Inputs

Ask the user for any missing information:

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| queries | No | 1 | Number of search queries to run |
| terms | No | "entrepreneur" | Search terms (space or comma-separated) |
| size | No | 100 | Results per query |
| min_views | No | 10,000 | Minimum view count filter |
| max_days | No | 30 | Maximum video age in days |
| min_score | No | 1.1 | Minimum outlier score (1.1 = 10% above channel avg) |
| limit | No | None | Max outliers to process (for testing) |
| skip_transcripts | No | false | Skip transcript fetching (faster, cheaper) |
| workers | No | 5 | Parallel workers for content processing |
| user_niche | No | "AI agents, automation, LangGraph, CrewAI, agentic workflows" | User's channel niche for title adaptation |

If arguments were provided: `$ARGUMENTS`

## Prerequisites

Verify these environment variables and files exist:

**API Keys** (check `.env` or ask user):
- `YOUTUBE_API_KEY` — YouTube Data API v3 (free, 10,000 units/day)
- `ANTHROPIC_API_KEY` — for Claude summaries and title variants
- `APIFY_API_TOKEN` — optional, for fallback transcript fetching

**Google OAuth** (for Sheets output):
- `config/credentials.json` — OAuth client credentials
- `config/token.json` — auto-generated after first auth

**Python packages**:
```bash
pip install yt-dlp anthropic gspread google-auth-oauthlib youtube-transcript-api apify-client python-dotenv
```

## Process

### Step 1: Video Discovery

Two methods available:

#### Method A: YouTube Data API v3 (RECOMMENDED — FREE)
- Endpoint: `https://www.googleapis.com/youtube/v3/search` + `https://www.googleapis.com/youtube/v3/videos`
- Auth: API key via `?key=` query param
- Free tier: 10,000 quota units/day (1 search = 100 units, 1 video detail = 1 unit)
- ~100 searches/day + unlimited video stat lookups
- Steps: search → get video IDs → batch fetch statistics → calculate outlier scores
- Also uses `https://www.googleapis.com/youtube/v3/channels` for channel averages (1 unit per channel)

#### Method B: yt-dlp Scraping (FALLBACK)
- Direct YouTube scraping via yt-dlp
- Keywords: Search 50 videos per keyword from 17 default keywords
- Channels: Monitor last 15 videos from 45+ monitored channels
- Free but unreliable due to 80%+ failure rate from rate limiting
- Use only if YouTube API quota exhausted

**Default Keywords** (if user doesn't specify):
```python
CROSS_NICHE_KEYWORDS = [
    # Business building
    "how to scale a business",
    "business growth strategies",
    "increase business revenue",
    "gym launch strategy",
    "acquisition.com",

    # Sales & marketing
    "how to sell more",
    "closing sales techniques",
    "marketing funnel strategy",
    "lead generation tips",

    # Wealth building
    "how to make your first million",
    "millionaire business advice",
    "building wealth through business",
    "cash flow strategies",

    # Mindset & systems
    "entrepreneur mindset for success",
    "business systems automation",
    "scaling without burnout",
    "productivity for founders"
]
```

**Extraction**: For each video, get:
- Title, video URL, video ID, view count, duration
- Channel name, channel URL, channel average views (last 10 videos)
- Thumbnail URL (highres), publish date
- Source (keyword or channel name)

**Filters**:
- Duration >= 180 seconds (filter out shorts)
- View count >= min_views (default 1,000)
- Upload date within max_days back
- Deduplicate by video ID

### Step 2: Outlier Score Calculation

For each video:

1. **Calculate base outlier score**: `video_views / channel_average_views`
2. **Apply recency boost** (newer videos get multiplier):
   - < 1 day old: 2.0x multiplier
   - < 3 days old: 1.5x multiplier
   - < 7 days old: 1.2x multiplier
   - >= 7 days old: 1.0x (no boost)
3. **Filter**: Keep only videos with outlier score >= min_score (default 1.1)

### Step 3: Cross-Niche Scoring

Calculate **cross-niche potential score** to prioritize transferable content:

**Hard Exclusions** (return score = 0, skip video):
- Own niche terms: AI, automation, code, ChatGPT, agent, LangGraph, etc.
- Goal: cross-niche only, not competitive intelligence

**Heavy Penalties** (-70%):
- Non-transferable formats: gear reviews, challenges, vlogs, Q&A, shorts, music, gaming, ASMR, relationship content, news/politics

**Soft Penalties**:
- Technical terms (-20% per term, max -80%): API, Python, code, SDK, framework, JavaScript, database, etc.

**Bonuses**:
- Money hooks: +40% (e.g., $, revenue, income, profit, million, salary, wealth)
- Curiosity hooks: +30% (e.g., ?, secret, nobody, shocking, truth about, hidden)
- Transformation hooks: +25% (e.g., before/after, from zero, how I built, journey)
- Contrarian hooks: +25% (e.g., wrong, mistake, myth, why I stopped, unpopular opinion)
- Time hooks: +20% (e.g., faster, save time, productivity, quick, hack)
- Urgency hooks: +15% (e.g., before it's too late, last chance, must watch)
- Numbers/listicles: +10% (e.g., "7 ways", "3 secrets")

**Auto-categorize** each outlier:
- Money, Productivity, Creator, Business, AI/Tech, or General

Sort outliers by cross-niche score (highest transferability first).

### Step 4: Fetch Transcripts (unless `--skip_transcripts`)

2-tier transcript system (parallel processing with N workers):

1. **Try youtube-transcript-api first** (free, fast):
   ```python
   from youtube_transcript_api import YouTubeTranscriptApi
   transcript = YouTubeTranscriptApi.get_transcript(video_id)
   ```
   - 1-second delay between requests
   - Retry once on 429 errors with 5-second delay

2. **Fallback to Apify** if youtube-transcript-api fails:
   - Actor: `karamelo/youtube-transcripts`
   - Pass video URL
   - ~20-30 seconds per video
   - Free tier available

3. **If both fail**: Set transcript to empty string, summary to "No transcript available"

### Step 5: Generate Summaries + Title Variants

For each outlier with transcript, call Claude Sonnet 4.5:

**Summary** (3-4 sentences, 500 max tokens):
```
Analyze this YouTube video for transferable content patterns.

Title: {title}
Transcript (first 8000 chars): {transcript}

Provide BRIEF analysis (3-4 sentences total) covering:
1. Core hook/angle and why it works
2. Key content structure or pattern
3. How to adapt this for AI/automation content

Keep it concise and actionable.
```

**3 Title Variants** adapted to user's niche (400 max tokens):
```
You're a YouTube strategist for a channel about {user_niche}.

Analyze this high-performing title from a different niche and generate 3 adapted variants for my channel.

Original Title: "{original_title}"
Context from original video: {summary}

Generate 3 NEW title variants that:
- Adapt the hook/structure to AI agents and automation
- Use the same emotional trigger and curiosity gap as original
- Are specific to {user_niche}
- Are meaningfully different from each other
- Stay under 100 characters

Return ONLY a JSON array of 3 strings (the variant titles), nothing else.
Example format: ["Variant 1", "Variant 2", "Variant 3"]
```

For videos **without transcripts**, generate title variants from title alone (no summary).

### Step 6: Output to Google Sheet

Create new Google Sheet: "Cross-Niche Outliers v2 - [YYYYMMDD_HHMMSS]"

**19 Columns** (sorted by publish date, most recent first):

| # | Column | Description |
|---|--------|-------------|
| 1 | Cross-Niche Score | Transferability metric (with modifiers) |
| 2 | Outlier Score (w/ Recency) | Video views / channel avg × recency boost |
| 3 | Raw Outlier Score | Without recency boost |
| 4 | Days Old | Days since publish |
| 5 | Category | Money / Productivity / Creator / Business / AI/Tech / General |
| 6 | Title | Original video title |
| 7 | Video Link | YouTube URL |
| 8 | View Count | Total views |
| 9 | Duration (min) | Video length in minutes |
| 10 | Channel Name | Channel name |
| 11 | Channel Avg Views | Channel's average views (last 10 videos) |
| 12 | Thumbnail | `=IMAGE("url")` formula for visual preview |
| 13 | Summary | Claude-generated pattern analysis |
| 14 | Title Variant 1 | First adapted title for user's niche |
| 15 | Title Variant 2 | Second adapted title |
| 16 | Title Variant 3 | Third adapted title |
| 17 | Raw Transcript | Full video transcript for deeper analysis |
| 18 | Publish Date | YYYYMMDD format |
| 19 | Source | "keyword: X" or "channel: Y" |

Use `gspread` with OAuth credentials for Google Sheets API.

## Keyword Strategy

When user doesn't specify custom terms, use these 4 tiers:

### Tier 1: Adjacent Business/Tech
High audience overlap with AI/automation content:
- "AI for business"
- "ChatGPT business use cases"
- "automation tools for entrepreneurs"
- "no-code automation"
- "productivity AI tools"
- "business process automation"

### Tier 2: Broad Business Performance
Universal patterns from successful business creators:
- "scale your business"
- "grow your startup"
- "solopreneur success"
- "founder productivity"
- "business systems that scale"
- "entrepreneur time management"

### Tier 3: Money/Revenue Hooks
Financial triggers that work across niches:
- "increase revenue"
- "passive income systems"
- "profitable business models"
- "10x your income"
- "business growth strategy"

### Tier 4: Personal Brand/Creator Economy
Content creation strategies:
- "YouTube strategy"
- "content creation tips"
- "personal brand building"
- "creator monetization"

## Monitored Channels (45+ Channels)

### Tier S (Must Monitor)
- Alex Hormozi — Business scaling, systems
- My First Million — Business ideas, trends
- Starter Story — Founder interviews, tactics

### Tier A (High Value)
- Colin and Samir — Creator economy insights
- Ali Abdaal — Productivity, systems
- Leila Hormozi — Operations, hiring
- Codie Sanchez — Contrarian investing
- Noah Kagan — Business experiments

### Tier B (Additional Sources)
- Greg Isenberg — Startup ideas, trend-spotting
- Dan Martell — SaaS, Buy Back Your Time
- Patrick Bet-David — Business philosophy
- Thomas Frank — Study/productivity systems
- Matt D'Avella — Minimalism, habits
- Tiago Forte — Second Brain
- Cal Newport — Deep work
- August Bradley — Notion systems

### Academic & Science (Storytelling hooks)
- Veritasium, 3Blue1Brown, Kurzgesagt, ASAP Science, Computerphile, SciShow, TED-Ed

### Business Documentary
- Johnny Harris, Wendover Productions, Polymatter, Economics Explained, ColdFusion, CGP Grey, Half as Interesting

### Creator Economy & YouTube
- Paddy Galloway, Film Booth, Jenny Hoyos

### Finance & Investing
- Graham Stephan, Andrei Jikh, Mark Tilbury, The Plain Bagel, Minority Mindset

### Self-Improvement
- Chris Williamson, Huberman Lab, Hamza

### Writing & Communication
- Simon Sinek, TED, Chris Do

### Philosophy & Thinking
- Pursuit of Wonder, Academy of Ideas, Einzelgänger

## Cross-Niche Scoring Modifiers

Complete modifier table:

| Type | Modifier | Example Terms |
|------|----------|---------------|
| **HARD EXCLUDE** | 0 (skip) | AI, automation, code, ChatGPT, LangGraph, CrewAI, agent, Python, API, SDK, GitHub, Docker, Kubernetes |
| **HEAVY PENALTY** | -70% | Setup, tour, review, unboxing, challenge, prank, react, day in life, Q&A, shorts, podcast, news, crypto, election, gaming, ASMR, dating |
| **Technical Terms** | -20% each (max -80%) | API, Python, code, SDK, framework, JavaScript, database, server, cloud, SaaS |
| **Money Hooks** | +40% | $, revenue, income, profit, money, earn, million, billionaire, wealth, salary, pricing |
| **Curiosity Hooks** | +30% | ?, secret, nobody, shocking, truth about, hidden, insider, exclusive, this changed everything |
| **Transformation Hooks** | +25% | before/after, from zero, how I built, journey, changed my life, breakthrough |
| **Contrarian Hooks** | +25% | wrong, mistake, myth, lie, overrated, unpopular opinion, why I stopped, uncomfortable truth |
| **Time Hooks** | +20% | faster, save time, productivity, quick, in minutes, instantly, hack, shortcut, accelerate |
| **Urgency Hooks** | +15% | before it's too late, last chance, now or never, don't miss, must watch |
| **Listicles (Numbers)** | +10% | "7 ways", "3 secrets", "10 tips" |

## Output Schema

All 19 columns explained:

```python
[
    "Cross-Niche Score",        # 1. Transferability metric (with all modifiers)
    "Outlier Score (w/ Recency)", # 2. Views/avg × recency boost
    "Raw Outlier Score",        # 3. Views/avg (no boost)
    "Days Old",                 # 4. Days since publish
    "Category",                 # 5. Money/Productivity/Creator/Business/AI/Tech/General
    "Title",                    # 6. Original video title
    "Video Link",               # 7. YouTube URL
    "View Count",               # 8. Total views
    "Duration (min)",           # 9. Video length in minutes
    "Channel Name",             # 10. Channel name
    "Channel Avg Views",        # 11. Channel's avg views (last 10 videos)
    "Thumbnail",                # 12. =IMAGE("url") formula
    "Summary",                  # 13. Claude pattern analysis (3-4 sentences)
    "Title Variant 1",          # 14. First adapted title
    "Title Variant 2",          # 15. Second adapted title
    "Title Variant 3",          # 16. Third adapted title
    "Raw Transcript",           # 17. Full transcript text
    "Publish Date",             # 18. YYYYMMDD
    "Source"                    # 19. "keyword: X" or "channel: Y"
]
```

## Cost & Performance

### YouTube Data API v3 (Recommended — FREE)
- **Per Query**: ~100 quota units (search) + ~1 unit per video detail + ~3 units per channel avg
- **Daily Quota**: 10,000 units free (enough for ~80-100 searches/day)
- **Default Run**: 1 search query → ~50 videos → batch stats → ~150 units total
- **Claude Costs**: ~$0.15-0.25 per outlier (summary + 3 title variants)
  - Summary: 500 tokens max
  - Title variants: 400 tokens max
- **Time with transcripts**: ~5-10 minutes for full run
- **Time without transcripts** (`--skip_transcripts`): ~30 seconds
- **Recommended frequency**: Weekly
- **Total cost per run**: $0 (API) + ~$3-5 (Claude for 20 outliers)

### yt-dlp (Fallback)
- **API Cost**: None (free)
- **Claude Costs**: ~$0.15-0.25 per outlier
- **Time**: 15-25 minutes (often fails due to rate limiting)
- **Failure rate**: 80%+ due to YouTube rate limiting
- **Use only if**: YouTube API quota exhausted

**Example Run Costs**:
- 20 outliers with transcripts: $0 (API) + ~$3-5 in Claude
- 20 outliers without transcripts: $0 total

## Error Handling

### YouTube Data API v3 Issues
- **Quota exceeded (403)**: Daily limit hit (10,000 units). Wait until midnight Pacific time or use yt-dlp fallback
- **Invalid API key (400)**: Check `YOUTUBE_API_KEY` in `.env`. Ensure YouTube Data API v3 is enabled in Google Cloud Console
- **No results**: Broaden search terms or increase `max_days`

### yt-dlp Timeouts (Fallback)
- Some keywords timeout (acquisition.com, scaling without burnout)
- Some channels timeout (Pat Flynn, GaryVee, Iman Gadzhi)
- Script continues with remaining keywords/channels
- Expected behavior: still find ~20 outliers

### Transcript Failures
- **youtube-transcript-api fails**: Auto-fallback to Apify
- **Both fail**: Set transcript to empty, summary to "No transcript available"
- **Title variants still generated** from title alone
- **429 errors**: 1-second delay between requests, retry once with 5-second delay

### Google Sheets Auth
- **Token expired**: Prompt user to re-authenticate via OAuth flow
- **credentials.json missing**: Ask user to provide OAuth client credentials
- **Permission denied**: Ensure scopes include spreadsheets + drive

### No Outliers Found
- Suggest lowering `--min_score` (try 1.05 for 5% above average)
- Suggest increasing `--max_days` (try 60, 90, or 180)
- Check that user isn't using `--keywords_only` (use full mode with channels)

## Output

Present the user with:

1. **Google Sheet URL** (clickable link)
2. **Summary stats**:
   - Total outliers found
   - Date range covered (oldest to newest)
   - Top 3 by cross-niche score (title + score)
   - Breakdown by category (Money: X, Productivity: Y, etc.)
3. **Next steps**:
   - Review recent outliers sorted by publish date
   - Filter by cross-niche score for most transferable content
   - Use title variants as starting points for video ideas
   - Study thumbnails for visual hook patterns

**Example output**:
```
✅ Done! Created sheet with 23 cross-niche outliers
   Each outlier has 3 title variants adapted for AI agents, automation, LangGraph, CrewAI, agentic workflows
   📊 Sheet URL: https://docs.google.com/spreadsheets/d/abc123...

Summary:
- 23 outliers from Dec 1-24, 2025
- Top 3 by cross-niche score:
  1. "How I Made $1M in 90 Days (No Code Required)" - 4.2
  2. "The Productivity System That Changed Everything" - 3.8
  3. "7 Business Mistakes Costing You 6 Figures" - 3.5
- Categories: Money (8), Business (7), Productivity (5), Creator (3)

Next steps:
- Review recent videos (sorted by publish date)
- Pick outliers with high cross-niche scores (>2.5)
- Use title variants as inspiration for your next videos
```

## Python Code Template

### Main Execution Script (yt-dlp version)

```python
#!/usr/bin/env python3
"""
Cross-niche outlier detection for content ideation.
Finds high-performing videos from adjacent niches.
"""

import os
import sys
import json
import time
import datetime
import subprocess
import argparse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from anthropic import Anthropic
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

# Configuration
USER_CHANNEL_NICHE = "AI agents, automation, LangGraph, CrewAI, agentic workflows"
MAX_VIDEOS_PER_KEYWORD = 50
MAX_VIDEOS_PER_CHANNEL = 15
DAYS_BACK = 90
MIN_OUTLIER_SCORE = 1.1
MIN_VIDEO_DURATION_SECONDS = 180
MIN_VIEW_COUNT = 1000

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Keywords and channels
CROSS_NICHE_KEYWORDS = [
    "how to scale a business", "business growth strategies",
    "increase business revenue", "how to sell more",
    "marketing funnel strategy", "how to make your first million",
    "entrepreneur mindset for success", "scaling without burnout"
]

MONITORED_CHANNELS = {
    "UCMrnHNmYzP3LgvKzyq0ILgw": "Alex Hormozi",
    "UCwgz-59Z39I8-ZrrHjy6nKw": "My First Million",
    "UCoOae5nYA7VqaXzerajD0lg": "Ali Abdaal",
    # ... add all 45+ channels
}

# Scoring modifiers
OWN_NICHE_TERMS = ["ai", "automation", "chatgpt", "agent", "code"]
EXCLUDE_FORMATS = ["setup", "review", "challenge", "q&a", "shorts"]
TECHNICAL_TERMS = ["API", "Python", "code", "SDK"]
MONEY_HOOKS = ["$", "revenue", "income", "profit", "million"]
CURIOSITY_HOOKS = ["?", "secret", "nobody", "shocking"]
TIME_HOOKS = ["faster", "save time", "productivity", "hack"]

def calculate_cross_niche_score(title, base_score):
    """Calculate cross-niche potential score."""
    title_lower = title.lower()
    score = base_score

    # Hard exclude own niche
    if any(term in title_lower for term in OWN_NICHE_TERMS):
        return 0

    # Heavy penalty for non-transferable formats
    if any(fmt in title_lower for fmt in EXCLUDE_FORMATS):
        score *= 0.3

    # Soft penalty for technical terms
    tech_count = sum(1 for term in TECHNICAL_TERMS if term.lower() in title_lower)
    score *= max(0.2, 1.0 - (tech_count * 0.2))

    # Bonuses
    if any(hook in title_lower for hook in MONEY_HOOKS):
        score *= 1.4
    if any(hook in title_lower for hook in CURIOSITY_HOOKS):
        score *= 1.3
    if any(hook in title_lower for hook in TIME_HOOKS):
        score *= 1.2
    if re.search(r'\b\d+\b', title):
        score *= 1.1

    return round(score, 2)

def fetch_transcript(video_id):
    """Fetch transcript with 2-tier fallback."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        time.sleep(1)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except:
        # Fallback to Apify
        apify_token = os.getenv("APIFY_API_TOKEN")
        if not apify_token:
            return None
        try:
            from apify_client import ApifyClient
            client = ApifyClient(apify_token)
            run = client.actor("karamelo/youtube-transcripts").call(
                run_input={"urls": [f"https://www.youtube.com/watch?v={video_id}"]},
                timeout_secs=120
            )
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            if items and "captions" in items[0]:
                return " ".join(items[0]["captions"])
        except:
            pass
    return None

def generate_title_variants(original_title, summary=None):
    """Generate 3 title variants adapted for user's niche."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return ["", "", ""]

    client = Anthropic(api_key=api_key)
    context = f"\n\nContext: {summary}" if summary else ""

    prompt = f"""You're a YouTube strategist for a channel about {USER_CHANNEL_NICHE}.

Analyze this high-performing title from a different niche and generate 3 adapted variants.

Original Title: "{original_title}"{context}

Generate 3 NEW title variants that:
- Adapt the hook/structure to AI agents and automation
- Use the same emotional trigger as original
- Are specific to {USER_CHANNEL_NICHE}
- Are meaningfully different from each other
- Stay under 100 characters

Return ONLY a JSON array: ["Variant 1", "Variant 2", "Variant 3"]"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        variants = json.loads(message.content[0].text.strip())
        return variants if len(variants) == 3 else ["", "", ""]
    except:
        return ["", "", ""]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="Max outliers to process")
    parser.add_argument("--days", type=int, default=90, help="Days to look back")
    parser.add_argument("--min_score", type=float, default=1.1, help="Min outlier score")
    parser.add_argument("--skip_transcripts", action="store_true", help="Skip transcripts")
    parser.add_argument("--workers", type=int, default=5, help="Parallel workers")
    args = parser.parse_args()

    print(f"🔍 Cross-Niche Outlier Detection")
    print(f"   Days back: {args.days}")
    print(f"   Min score: {args.min_score}")

    # Step 1: Scrape videos (implement scrape_keyword, scrape_channel)
    # Step 2: Calculate outlier scores
    # Step 3: Cross-niche scoring
    # Step 4: Fetch transcripts in parallel
    # Step 5: Generate summaries + variants
    # Step 6: Create Google Sheet

    print(f"\n✅ Done! Sheet URL: {spreadsheet.url}")

if __name__ == "__main__":
    sys.exit(main())
```

### YouTube Data API v3 Integration (RECOMMENDED — FREE)

```python
import requests
from datetime import datetime, timedelta

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

def search_youtube_videos(api_key, query, max_results=50, max_days=30):
    """Search YouTube videos via Data API v3. Cost: 100 units per search."""
    from_date = (datetime.utcnow() - timedelta(days=max_days)).isoformat() + "Z"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "publishedAfter": from_date,
        "maxResults": min(max_results, 50),  # API max is 50 per page
        "relevanceLanguage": "en",
        "key": api_key
    }

    resp = requests.get(f"{YOUTUBE_API_BASE}/search", params=params)
    resp.raise_for_status()
    return [item["id"]["videoId"] for item in resp.json().get("items", [])]

def get_video_details(api_key, video_ids):
    """Batch fetch video statistics + snippet. Cost: 1 unit per video."""
    videos = []
    # API allows up to 50 IDs per request
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(batch),
            "key": api_key
        }
        resp = requests.get(f"{YOUTUBE_API_BASE}/videos", params=params)
        resp.raise_for_status()

        for item in resp.json().get("items", []):
            snippet = item["snippet"]
            stats = item["statistics"]
            # Parse ISO 8601 duration (PT1H2M3S)
            duration_str = item["contentDetails"]["duration"]
            videos.append({
                "title": snippet["title"],
                "video_id": item["id"],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "view_count": int(stats.get("viewCount", 0)),
                "duration_iso": duration_str,
                "channel_id": snippet["channelId"],
                "channel_name": snippet["channelTitle"],
                "thumbnail_url": snippet["thumbnails"].get("high", {}).get("url", ""),
                "date": snippet["publishedAt"][:10],
                "source": "youtube_api"
            })
    return videos

def get_channel_avg_views(api_key, channel_id):
    """Get channel's recent uploads and calculate average views. Cost: ~3 units."""
    # Get uploads playlist
    params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": api_key
    }
    resp = requests.get(f"{YOUTUBE_API_BASE}/channels", params=params)
    resp.raise_for_status()
    items = resp.json().get("items", [])
    if not items:
        return 0

    uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Get last 10 videos from uploads playlist
    params = {
        "part": "contentDetails",
        "playlistId": uploads_id,
        "maxResults": 10,
        "key": api_key
    }
    resp = requests.get(f"{YOUTUBE_API_BASE}/playlistItems", params=params)
    resp.raise_for_status()

    recent_ids = [item["contentDetails"]["videoId"] for item in resp.json().get("items", [])]
    if not recent_ids:
        return 0

    # Get view counts for those videos
    recent_videos = get_video_details(api_key, recent_ids)
    if not recent_videos:
        return 0

    return sum(v["view_count"] for v in recent_videos) // len(recent_videos)
```

## Implementation Steps

When user requests cross-niche outliers:

1. **Parse arguments**: Extract search terms, filters, flags from `$ARGUMENTS`
2. **Verify prerequisites**: Check API keys, OAuth credentials
3. **Choose method**:
   - If `YOUTUBE_API_KEY` exists: Use YouTube Data API v3 (recommended, free)
   - Else: Use yt-dlp scraping (fallback)
4. **Fetch videos**: Call API or scrape with yt-dlp
5. **Calculate scores**: Outlier score + cross-niche score
6. **Filter**: Keep outlier_score >= min_score, cross_niche_score > 0
7. **Sort**: By cross-niche score descending
8. **Process content** (if not skipped):
   - Fetch transcripts in parallel (N workers)
   - Generate summaries with Claude
   - Generate 3 title variants per outlier
9. **Create Google Sheet**: 19 columns, sorted by publish date
10. **Output**: Sheet URL + summary stats

## Recommended Usage

### Weekly Content Planning
```bash
# Default: 1 query, 100 results, last 30 days, with transcripts
python3 scrape_cross_niche_outliers.py
```

### Fast Test (Skip Transcripts)
```bash
# Get outliers only, no summaries/variants (30 seconds)
python3 scrape_cross_niche_outliers.py --skip_transcripts
```

### Custom Search Terms
```bash
# Multiple custom terms
python3 scrape_cross_niche_outliers.py --terms "business scaling" "solopreneur" "productivity"
```

### Adjust Thresholds
```bash
# More selective: higher score, shorter lookback
python3 scrape_cross_niche_outliers.py --min_score 1.3 --days 30

# More inclusive: lower score, longer lookback
python3 scrape_cross_niche_outliers.py --min_score 1.05 --days 180
```

### Test Mode
```bash
# Process only first 5 outliers (testing)
python3 scrape_cross_niche_outliers.py --limit 5
```
