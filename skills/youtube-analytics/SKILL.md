---
name: youtube-analytics
description: Generate an interactive analytics dashboard for YouTube channel performance with views, CTR signals, watch time, posting analysis, and competitor research. Use when the user asks for analytics, channel stats, video performance, or competitor analysis.
argument-hint: [--days 30] [--competitor channel-id]
disable-model-invocation: true
---

# YouTube Analytics Dashboard

Pull channel and video analytics, analyze posting patterns, compare with competitors, and generate a self-contained interactive HTML dashboard. Just double-click to open — no server needed.

## Inputs

Ask the user for any missing information:

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| Days | No | 30 | Date range to analyze (7, 30, 60, 90) |
| Max videos | No | 50 | Number of recent videos to include |
| Competitor IDs | No | — | Comma-separated YouTube channel IDs for comparison |

## Prerequisites

- `YOUTUBE_API_KEY` environment variable must be set
- `YOUTUBE_CHANNEL_ID` environment variable must be set (find at youtube.com/account_advanced)
- Python dependencies: `pip install google-api-python-client`
- Script location: `~/Projects/content/scripts/_tools/youtube_analytics.py`

Check prerequisites:

```bash
python3 -c "import googleapiclient" 2>/dev/null || pip install google-api-python-client
test -n "$YOUTUBE_API_KEY" || echo "ERROR: Set YOUTUBE_API_KEY"
test -n "$YOUTUBE_CHANNEL_ID" || echo "ERROR: Set YOUTUBE_CHANNEL_ID (find at youtube.com/account_advanced)"
```

## Process

### Step 1: Fetch channel data

```bash
python3 ~/Projects/content/scripts/_tools/youtube_analytics.py channel \
  --days [DAYS] \
  --max-videos [MAX] \
  --output /tmp/channel-analytics.json
```

### Step 2: Fetch competitor data (if requested)

For each competitor channel ID:

```bash
python3 ~/Projects/content/scripts/_tools/youtube_analytics.py competitor \
  --channel-id [COMPETITOR_ID] \
  --output /tmp/competitor-[name].json
```

### Step 3: Read and analyze the data

Read all JSON output files. Analyze:

**Channel Health:**
- Subscriber count and growth trend
- Total views in date range
- Average views per video (is it growing or declining?)
- Like-to-view ratio (engagement quality)

**Video Performance:**
- Rank all videos by views — which are overperforming vs channel average?
- Identify patterns in high-performing video titles/topics
- Identify patterns in low-performing videos

**Posting Patterns:**
- Best day of week (from historical data)
- Best hour (UTC) for uploads
- Upload frequency trend

**Competitor Comparison (if data available):**
- Subscriber count comparison
- Average views per video comparison
- Engagement ratio comparison
- Upload frequency comparison
- What topics are competitors covering that you're not?

### Step 4: Generate the HTML dashboard

Create a self-contained HTML file with:
- Chart.js for interactive charts (loaded via CDN)
- Tailwind CSS for styling (loaded via CDN)
- All data embedded as JavaScript variables
- Responsive design (works on mobile)

Save to:
```
~/Projects/content/assets/dashboards/[YYYY-MM-DD]-dashboard.html
```

### Step 5: Open the dashboard

```bash
open ~/Projects/content/assets/dashboards/[YYYY-MM-DD]-dashboard.html
```

## Dashboard Template

The generated HTML must include these sections:

### Section 1: Channel Overview (cards)
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Subscribers  │  │ Views (30d)  │  │ Avg Views/   │  │   Videos     │
│    31,200     │  │   45,000     │  │   Video: 900 │  │  Published:8 │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

### Section 2: Views Trend (line chart)
- X-axis: video publish dates
- Y-axis: view count
- Line color: #8B5CF6 (purple)
- Show channel average as dashed horizontal line
- Highlight overperformers in green, underperformers in red

### Section 3: Video Performance (horizontal bar chart)
- Each bar = one video
- Color-coded: green (above avg), red (below avg), purple (avg)
- Sorted by views descending
- Show video title on Y-axis (truncated to 40 chars)

### Section 4: Best Posting Times (heatmap grid)
- X-axis: hours (0-23 UTC)
- Y-axis: days (Mon-Sun)
- Cell color intensity = number of videos posted at that time
- Highlight the best time slot

### Section 5: Top & Bottom Videos (table)
```
| Rank | Title | Views | Likes | Comments | Published |
|------|-------|-------|-------|----------|-----------|
```
- Top 5 best performing
- Bottom 5 worst performing
- Color-coded rows

### Section 6: Competitor Comparison (if data available)
- Side-by-side bar chart: your channel vs competitors
- Metrics: subscribers, avg views, engagement ratio, upload frequency
- Table with detailed comparison

## HTML Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bo Sar YouTube Analytics — [date]</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; background: #0F172A; color: #F8FAFC; }
        .card { background: #1E293B; border-radius: 12px; padding: 24px; }
        .metric-value { font-size: 2.5rem; font-weight: 700; }
        .metric-label { font-size: 0.875rem; color: #94A3B8; }
        .positive { color: #10B981; }
        .negative { color: #EF4444; }
    </style>
</head>
<body class="p-8">
    <!-- Dashboard title -->
    <!-- Overview cards -->
    <!-- Charts (each in a canvas element) -->
    <!-- Tables -->
    <script>
        // DATA (embedded by Claude)
        const channelData = { ... };
        const videosData = [ ... ];
        const competitorData = [ ... ];

        // Chart.js initialization for each section
    </script>
</body>
</html>
```

**Design rules for dashboard:**
- Dark theme (#0F172A background, #1E293B cards)
- Purple (#8B5CF6) as primary accent
- Green (#10B981) for positive metrics
- Red (#EF4444) for negative metrics
- White text (#F8FAFC) on dark backgrounds
- 12px border radius on all cards
- Inter font family

## API Quota Notes

Each analytics run uses approximately:
- 1 channel.list = 3 units
- 1 playlistItems.list (50 videos) = 3 units
- 1 videos.list (50 videos) = 3 units
- Per competitor: ~9 units
- **Total: ~10-40 units** per dashboard (free tier = 10,000/day)

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `YOUTUBE_API_KEY not set` | Missing env var | `export YOUTUBE_API_KEY=your-key` |
| `YOUTUBE_CHANNEL_ID not set` | Missing env var | `export YOUTUBE_CHANNEL_ID=UCxxxxxx` (find at youtube.com/account_advanced) |
| `Channel not found` | Wrong channel ID | Double-check the channel ID |
| `HttpError 403` quota | Daily quota exceeded | Wait until midnight Pacific |
| Chart not rendering | CDN blocked | Open in a different browser, check internet connection |
