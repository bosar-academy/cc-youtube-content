# YouTube Content Creation Skills

> 7 Claude Code skills for YouTube content creation - research, scripting, titles, thumbnails, diagrams, and analytics

## Skills Included

| Skill | Description |
|-------|-------------|
| `research-brief` | Research YouTube competitors, analyze top videos, find content gaps |
| `write-script` | Write full YouTube scripts with hooks, retention markers, B-roll cues |
| `generate-title` | Analyze outlier titles and generate 3 high-CTR title options |
| `youtube-thumbnail` | Generate 4 professional thumbnail variations with Gemini AI |
| `generate-diagrams` | Create hand-drawn whiteboard diagrams from video scripts |
| `youtube-analytics` | Build interactive analytics dashboards for channel performance |
| `cross-niche-outliers` | Find viral content patterns across YouTube niches |

## Workflow

These skills chain together in a natural content creation pipeline:

```
research-brief -> write-script -> generate-title
                                -> youtube-thumbnail
                                -> generate-diagrams
                       publish -> youtube-analytics
```

## Installation

```bash
git clone https://github.com/bohdan-aif/cc-youtube-content.git
cd cc-youtube-content
./install.sh --all
```

Or install individual skills:

```bash
./install.sh research-brief
./install.sh write-script
```

## Required API Keys

| Key | Used By | How to Get |
|-----|---------|------------|
| `YOUTUBE_API_KEY` | research-brief, youtube-analytics | [Google Cloud Console](https://console.cloud.google.com/) - YouTube Data API v3 |
| `YOUTUBE_CHANNEL_ID` | youtube-analytics | [youtube.com/account_advanced](https://youtube.com/account_advanced) |
| `GEMINI_API_KEY` | youtube-thumbnail, generate-diagrams | [Google AI Studio](https://aistudio.google.com/) |
| `SCRAPECREATORS_API_KEY` | youtube-thumbnail (optional) | [scrapecreators.com](https://scrapecreators.com/) |

## Required Dependencies

```bash
pip install google-api-python-client   # research-brief, youtube-analytics
brew install ffmpeg                     # youtube-thumbnail (image processing)
```

## Usage

Each skill is invoked as a slash command in Claude Code:

```
/research-brief "Claude Code for business automation"
/write-script (after research brief is ready)
/generate-title (after script is written)
/youtube-thumbnail "How I Replaced My Team with AI"
/generate-diagrams (extracts [DIAGRAM] markers from script)
/youtube-analytics
/cross-niche-outliers
```

## Also See

- [cc-content-repurposing](https://github.com/bohdan-aif/cc-content-repurposing) - Repurpose long-form content into shorts and social posts

## License

MIT
