---
name: gdrive-upload
description: Upload files to Google Drive as Google Docs. Converts markdown, text, or any file content into a formatted Google Doc and returns the shareable link. Use when the user wants to save something to Google Drive, create a Google Doc, or share a document.
argument-hint: [file path or "last output" or description of what to upload]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
effort: low
---

# Google Drive Upload Skill

Upload files to Google Drive as Google Docs using existing OAuth2 credentials.

## How It Works

**ALWAYS use the formatted uploader** (`upload_formatted.py`) for text/markdown files. This converts markdown to proper Google Docs formatting (headings, bold, bullets, code blocks, links, tables) instead of dumping raw markdown text.

Only fall back to `upload.py` (plain text) for non-text content or if the formatted uploader fails.

## Usage

```bash
# Upload a file as a FORMATTED Google Doc (default - always use this)
python3 ~/.claude/skills/gdrive-upload/upload_formatted.py --file /path/to/file.md --title "Document Title"

# Upload with a specific folder ID (optional)
python3 ~/.claude/skills/gdrive-upload/upload_formatted.py --file /path/to/file.md --title "Document Title" --folder FOLDER_ID

# Upload raw text from stdin
echo "Some content" | python3 ~/.claude/skills/gdrive-upload/upload_formatted.py --title "Quick Note" --stdin

# Plain text fallback (only if formatted upload fails)
python3 ~/.claude/skills/gdrive-upload/upload.py --file /path/to/file.md --title "Document Title"
```

## What To Do

1. Determine what the user wants to upload:
   - If they give a file path, use that
   - If they say "upload this" referring to recent output, find or create the relevant file first
   - If they describe content, create a temp file first then upload

2. Run `upload_formatted.py` (NOT `upload.py`) with the appropriate arguments

3. Return the Google Doc URL to the user

## Output

The script prints the shareable Google Doc URL on success. Always show this URL to the user.

## Dependencies

- OAuth token: `~/.claude/.gdrive/token.json` (created by `authorize.py`)
- Credentials: `~/.claude/.gdrive/credentials.json` (downloaded from Google Cloud)
- Override locations with `GDRIVE_CONFIG_DIR` / `GDRIVE_TOKEN_PATH` / `GDRIVE_CREDENTIALS_PATH`
- Required scopes: `drive`, `documents`
- Python packages: `google-api-python-client`, `google-auth`, `google-auth-oauthlib`

## First-time setup (one time only)

This skill talks to Google Drive + Google Docs, so it needs a Google OAuth token.

1. Create a project at https://console.cloud.google.com/
2. Enable the **Google Drive API** and **Google Docs API**
3. APIs & Services -> Credentials -> Create OAuth client ID -> **Desktop app**
4. Download the JSON, save it as `credentials.json` in `~/.claude/.gdrive/`
5. Run the authorizer once:
   ```bash
   python3 ~/.claude/skills/gdrive-upload/authorize.py
   ```
   A browser opens, you log in, and `token.json` is written next to it.

After that, the upload scripts just work.

## Error Handling

- If token is expired, the script auto-refreshes it automatically
- If no token exists, the script tells the user to run `authorize.py`
