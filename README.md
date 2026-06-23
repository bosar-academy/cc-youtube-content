# YouTube Content Creation Skills

> 9 Claude Code skills for YouTube content creation - research, scripting, slides, teleprompter, thumbnails, publishing, and analytics

## Skills Included

| Skill | Description |
|-------|-------------|
| `research-brief` | Research YouTube competitors, analyze top videos, find content gaps |
| `write-script` | Write full YouTube scripts with hooks, retention markers, B-roll cues |
| `generate-title` | Analyze outlier titles and generate 3 high-CTR title options |
| `youtube-thumbnail` | Generate 4 professional thumbnail variations with Gemini AI |
| `generate-diagrams` | Create hand-drawn whiteboard diagram slides from video scripts |
| `gdrive-upload` | Turn a script (with slide cues for your editor) into a formatted Google Doc |
| `script-to-teleprompter` | Strip a script to spoken-only text and upload it as a teleprompter Google Doc |
| `youtube-analytics` | Build interactive analytics dashboards for channel performance |
| `cross-niche-outliers` | Find viral content patterns across YouTube niches |

## Workflow

These skills chain together in a natural content creation pipeline:

```
research-brief -> write-script -> generate-title
                                -> generate-diagrams (whiteboard slides)
                                -> gdrive-upload (editor's Doc with slide cues)
                                -> script-to-teleprompter (spoken-only Doc)
                                -> youtube-thumbnail
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

## Google Drive Setup (for gdrive-upload + script-to-teleprompter)

These two skills create Google Docs, so they need a one-time Google OAuth setup:

1. Create a project at [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Google Drive API** and **Google Docs API**
3. APIs & Services -> Credentials -> Create OAuth client ID -> **Desktop app**
4. Download the JSON and save it as `credentials.json` in `~/.claude/.gdrive/`
5. Run the authorizer once:
   ```bash
   python3 ~/.claude/skills/gdrive-upload/authorize.py
   ```

## Required Dependencies

```bash
pip install google-api-python-client google-auth google-auth-oauthlib   # YouTube + Google Drive
brew install ffmpeg                                                      # youtube-thumbnail (image processing)
```

## Usage

Each skill is invoked as a slash command in Claude Code:

```
/research-brief "Claude Code for business automation"
/write-script (after research brief is ready)
/generate-title (after script is written)
/generate-diagrams (extracts [DIAGRAM] markers from script)
/gdrive-upload (upload the editor's script Doc with slide cues)
/script-to-teleprompter (spoken-only version for your teleprompter)
/youtube-thumbnail "How I Replaced My Team with AI"
/youtube-analytics
/cross-niche-outliers
```

## Also See

- [cc-content-repurposing](https://github.com/bohdan-aif/cc-content-repurposing) - Repurpose long-form content into shorts and social posts

## License

MIT
