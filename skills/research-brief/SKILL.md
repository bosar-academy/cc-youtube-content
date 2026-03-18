---
name: research-brief
description: Research YouTube competitors and find content gaps for a video topic. Use when the user asks to research a topic, find content gaps, analyze competitors, or prepare for a video.
argument-hint: [topic-or-keyword]
disable-model-invocation: true
---

# YouTube Competitor Research & Gap Analysis

Search YouTube for top videos on a topic, analyze what's working, find what's missing, and produce a structured research brief. This brief feeds into `/write-script` for data-driven script writing.

## Inputs

Ask the user for any missing information:

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| Topic | Yes | — | Topic or keyword to research (e.g., "Claude Code for business") |
| Max videos | No | 20 | Number of videos to analyze |
| Video slug | No | auto from topic | Kebab-case folder name for outputs |

## Prerequisites

- `YOUTUBE_API_KEY` environment variable must be set
- Python dependencies: `pip install google-api-python-client`
- Script location: `~/Projects/content/scripts/_tools/research_brief.py`

Check prerequisites before running:

```bash
python3 -c "import googleapiclient" 2>/dev/null || pip install google-api-python-client
test -n "$YOUTUBE_API_KEY" || echo "ERROR: Set YOUTUBE_API_KEY environment variable"
```

## Process

### Step 1: Create output directory

```bash
mkdir -p ~/Projects/content/scripts/[video-slug]/
```

### Step 2: Run the research script

```bash
python3 ~/Projects/content/scripts/_tools/research_brief.py "[topic]" \
  --max-videos 20 \
  --max-comments 50 \
  --output ~/Projects/content/scripts/[video-slug]/raw-research.json
```

This script:
- Searches YouTube by relevance AND view count (catches viral outliers)
- Gets full video details (views, likes, duration, tags, thumbnails, description)
- Pulls top 50 comments from the top 5 videos (sorted by relevance)
- Gets channel stats for top 3 unique creators
- Outputs structured JSON

### Step 3: Read the raw JSON and analyze

Read the output JSON file. Then analyze across these dimensions:

**Title & Hook Analysis:**
- What title patterns appear in the top 10 by views?
- Which titles use numbers, questions, bold claims, or "how to"?
- What emotional triggers are present (fear, curiosity, opportunity, urgency)?

**Thumbnail Patterns:**
- Note thumbnail URLs from the data — describe common patterns
- Look for: faces, text overlay amount, color schemes, before/after layouts

**Content Structure:**
- From descriptions and tags: what topics are covered?
- What video lengths perform best?
- What tags are most common?

**Comment Analysis (top 5 videos):**
- What questions do viewers ask? (= content gaps)
- What frustrations do they express? (= pain points to address)
- What do they praise? (= what to replicate)
- What do they request? (= future video ideas)

**Competitor Channel Analysis:**
- Channel sizes (subscriber counts)
- Upload frequency
- Average views vs subscriber count (engagement ratio)

**Gap Analysis:**
- What angles are NOT covered by any top video?
- What's outdated or no longer accurate?
- What's poorly explained that {{CHANNEL_NAME}} could do better?
- Where can the AI-First Framework angle provide unique value?

### Step 4: Generate the research brief

Write a structured markdown brief and save to:
```
~/Projects/content/scripts/[video-slug]/research-brief.md
```

## Output Format

```markdown
# Research Brief: [Topic]

**Generated**: [date]
**Query**: [topic keyword]
**Videos analyzed**: [count]

---

## Top 10 Competitors

| # | Title | Channel | Views | Likes | Duration | Published |
|---|-------|---------|-------|-------|----------|-----------|
| 1 | ... | ... | ... | ... | ... | ... |

## What's Working

### Title Patterns
- [Pattern 1]: "[example title]" — [X] views
- [Pattern 2]: "[example title]" — [X] views

### Hook Signals
- [What the top videos seem to promise in their titles/descriptions]

### Thumbnail Patterns
- [Common elements across top thumbnails]

### Content Structure
- Average length of top 10: [X] minutes
- Most common format: [tutorial / listicle / case study / opinion]
- Common sections: [list]

### Top Tags
- [tag1], [tag2], [tag3], ...

## Viewer Pain Points (from comments)

### Top Questions (opportunities to answer)
1. "[Question from comments]" — [X] likes on comment
2. ...

### Frustrations
1. "[Frustration]"
2. ...

### Praise (what to replicate)
1. "[What viewers loved]"
2. ...

### Requests (future video ideas)
1. "[What viewers asked for]"
2. ...

## Content Gaps

### Missing Angles
- [Angle nobody is covering]
- [Angle that's underserved]

### Weak Explanations
- [Topic that top videos explain poorly]

### Outdated Information
- [What's changed since top videos were published]

## Blue Ocean Angle for {{CHANNEL_NAME}}

### Recommended Angle
[1-2 sentence description of the unique angle]

### Why This Works
- [Reason 1 — based on gap analysis]
- [Reason 2 — based on viewer pain points]
- [Reason 3 — based on AI-First Framework positioning]

### Differentiation
- vs [Top Competitor 1]: [how {{CHANNEL_NAME}}'s angle differs]
- vs [Top Competitor 2]: [how {{CHANNEL_NAME}}'s angle differs]

## Recommended Titles (5 options)

1. [Title option — matches winning patterns + unique angle]
2. ...
3. ...
4. ...
5. ...

## Recommended Hooks (3 options)

### Hook A: [Type]
[15-30 second hook text]

### Hook B: [Type]
[15-30 second hook text]

### Hook C: [Type]
[15-30 second hook text]

---

*Feed this brief into `/write-script` for a full video script.*
```

## API Quota Notes

Each research run uses approximately:
- 2 search requests (relevance + viewCount) = 200 units
- 1 videos.list request (up to 50 IDs) = 3 units
- 5 commentThreads.list requests = 25 units
- 1 channels.list request = 3 units
- **Total: ~231 units** (free tier = 10,000/day = ~43 research runs/day)

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `YOUTUBE_API_KEY not set` | Missing env var | `export YOUTUBE_API_KEY=your-key` |
| `HttpError 403` on comments | Comments disabled on video | Script handles this — returns `[Comments disabled]` |
| `HttpError 403` quota | Daily quota exceeded | Wait until midnight Pacific, or use a different API key |
| `ModuleNotFoundError` | Missing dependency | `pip install google-api-python-client` |
