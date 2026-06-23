#!/usr/bin/env python3
"""
Google Drive Upload — Create a Google Doc from a local file or stdin.

Usage:
    python3 upload.py --file /path/to/file.md --title "My Document"
    python3 upload.py --file /path/to/file.md --title "My Document" --folder FOLDER_ID
    echo "content" | python3 upload.py --title "Quick Note" --stdin

Outputs the shareable Google Doc URL on success.
"""

import argparse
import json
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Config dir holds your Google OAuth files. Override with env vars if you keep
# them elsewhere. Run authorize.py once to create token.json from credentials.json.
CONFIG_DIR = os.environ.get(
    "GDRIVE_CONFIG_DIR", os.path.expanduser("~/.claude/.gdrive")
)
TOKEN_PATH = os.environ.get("GDRIVE_TOKEN_PATH", os.path.join(CONFIG_DIR, "token.json"))


def get_services():
    """Initialize Google Drive and Docs services with existing OAuth2 credentials."""
    if not os.path.exists(TOKEN_PATH):
        sys.exit(
            f"No OAuth token found at {TOKEN_PATH}.\n"
            "Run the one-time authorizer first:\n"
            "    python3 ~/.claude/skills/gdrive-upload/authorize.py"
        )
    with open(TOKEN_PATH, "r") as f:
        token_data = json.load(f)
    scopes = token_data.get("scopes", [])

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    drive_service = build("drive", "v3", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)
    return drive_service, docs_service


def upload_to_gdoc(title: str, content: str, folder_id: str = None) -> str:
    """Create a Google Doc with the given title and content. Returns the doc URL."""
    drive_service, docs_service = get_services()

    # Create the document
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc.get("documentId")

    # Insert content
    if content.strip():
        requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
        docs_service.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

    # Move to folder if specified
    if folder_id:
        file = drive_service.files().get(fileId=doc_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents", []))
        drive_service.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields="id, parents",
        ).execute()

    # Make shareable (anyone with link can view)
    drive_service.permissions().create(
        fileId=doc_id, body={"type": "anyone", "role": "reader"}
    ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"


def main():
    parser = argparse.ArgumentParser(description="Upload a file to Google Drive as a Google Doc")
    parser.add_argument("--file", help="Path to the file to upload")
    parser.add_argument("--title", required=True, help="Title for the Google Doc")
    parser.add_argument("--folder", help="Google Drive folder ID to place the doc in (optional)")
    parser.add_argument("--stdin", action="store_true", help="Read content from stdin instead of a file")
    args = parser.parse_args()

    if args.stdin:
        content = sys.stdin.read()
    elif args.file:
        with open(args.file, "r") as f:
            content = f.read()
    else:
        print("Error: provide either --file or --stdin", file=sys.stderr)
        sys.exit(1)

    url = upload_to_gdoc(args.title, content, args.folder)
    print(url)


if __name__ == "__main__":
    main()
